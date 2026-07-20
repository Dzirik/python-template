"""
Tests for the HealthcheckHeartbeat background ping sender (healthchecks.io client).

Focuses on the risk surface that has no coverage yet: pings must hit the configured URL
with the configured timeout, network failures must be swallowed (never propagate out of
the background thread), and the underlying ``requests.Session`` must be reused rather than
recreated on every ping. No real network calls are made anywhere in this module.
"""

import time
from unittest.mock import MagicMock, patch

from src.scripts_production.heartbeat import HealthcheckHeartbeat, HealthcheckHeartbeatConfig


def _make_heartbeat(**overrides: object) -> HealthcheckHeartbeat:
    """
    Builds a HealthcheckHeartbeat with a minimal valid config, overriding selected fields.

    :param overrides: object. Keyword overrides merged onto the default config fields.
    :return: HealthcheckHeartbeat. Instance ready for ping/session mocking in tests.
    """
    defaults: dict[str, object] = {
        "name": "test-service",
        "ping_url": "https://hc-ping.com/some-uuid",
        "interval_seconds": 60.0,
        "max_extra_delay_seconds": 10.0,
        "request_timeout_seconds": 5.0,
        "startup_ping": True,
    }
    defaults.update(overrides)
    config = HealthcheckHeartbeatConfig(**defaults)  # type: ignore[arg-type]
    return HealthcheckHeartbeat(config)


# ---------------------------------------------------------------------------
# _send_ping / ping_now
# ---------------------------------------------------------------------------
class TestSendPing:
    """Tests for HealthcheckHeartbeat._send_ping (via ping_now)."""

    def test_successful_ping_calls_url_with_configured_timeout(self) -> None:
        """A successful ping calls session.get with the configured URL and timeout."""
        heartbeat = _make_heartbeat(ping_url="https://hc-ping.com/abc123", request_timeout_seconds=5.0)
        mock_response = MagicMock()
        with patch.object(heartbeat, "_session") as mock_session:
            mock_session.get.return_value = mock_response
            heartbeat.ping_now()

        mock_session.get.assert_called_once_with("https://hc-ping.com/abc123", timeout=5.0)
        mock_response.raise_for_status.assert_called_once()

    def test_custom_timeout_is_forwarded(self) -> None:
        """A non-default request_timeout_seconds is passed through to session.get."""
        heartbeat = _make_heartbeat(request_timeout_seconds=2.5)
        with patch.object(heartbeat, "_session") as mock_session:
            mock_session.get.return_value = MagicMock()
            heartbeat.ping_now()

        _, kwargs = mock_session.get.call_args
        assert kwargs["timeout"] == 2.5

    def test_network_exception_is_swallowed_and_logged(self) -> None:
        """A network exception raised by session.get does not propagate out of ping_now."""
        heartbeat = _make_heartbeat()
        with patch.object(heartbeat, "_session") as mock_session:
            mock_session.get.side_effect = ConnectionError("network is unreachable")
            with patch("src.scripts_production.heartbeat.logger") as mock_logger:
                heartbeat.ping_now()  # must not raise

        mock_logger.exception.assert_called_once()

    def test_raise_for_status_exception_is_swallowed_and_logged(self) -> None:
        """An HTTP error surfaced via raise_for_status is swallowed, not propagated."""
        heartbeat = _make_heartbeat()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = ValueError("500 Server Error")
        with patch.object(heartbeat, "_session") as mock_session:
            mock_session.get.return_value = mock_response
            with patch("src.scripts_production.heartbeat.logger") as mock_logger:
                heartbeat.ping_now()  # must not raise

        mock_logger.exception.assert_called_once()

    def test_ping_now_updates_last_ping_monotonic(self) -> None:
        """ping_now records the monotonic timestamp of the ping it just sent."""
        heartbeat = _make_heartbeat()
        with patch.object(heartbeat, "_session") as mock_session:
            mock_session.get.return_value = MagicMock()
            before = time.monotonic()
            heartbeat.ping_now()
            after = time.monotonic()

        assert heartbeat._last_ping_monotonic is not None
        assert before <= heartbeat._last_ping_monotonic <= after


# ---------------------------------------------------------------------------
# session reuse
# ---------------------------------------------------------------------------
class TestSessionReuse:
    """Tests that the requests.Session is created once and reused across pings."""

    def test_session_created_once_in_init(self) -> None:
        """A single requests.Session instance is created in __init__."""
        with patch("src.scripts_production.heartbeat.requests.Session") as mock_session_cls:
            mock_session_cls.return_value = MagicMock()
            heartbeat = _make_heartbeat()

        mock_session_cls.assert_called_once()
        assert heartbeat._session is mock_session_cls.return_value

    def test_multiple_pings_reuse_the_same_session_object(self) -> None:
        """Repeated ping_now calls all go through the same session object, not a new one each time."""
        heartbeat = _make_heartbeat()
        with patch.object(heartbeat, "_session") as mock_session:
            mock_session.get.return_value = MagicMock()
            heartbeat.ping_now()
            heartbeat.ping_now()
            heartbeat.ping_now()

            assert mock_session.get.call_count == 3
            # Every call used the exact same (mocked) session object - none were replaced.
            assert heartbeat._session is mock_session


# ---------------------------------------------------------------------------
# start / stop (thread lifecycle, still without any real network calls)
# ---------------------------------------------------------------------------
class TestStartStop:
    """Tests for the start/stop thread lifecycle around the mocked ping."""

    def test_start_sends_startup_ping_when_configured(self) -> None:
        """start() sends an immediate ping when startup_ping is True."""
        heartbeat = _make_heartbeat(startup_ping=True, interval_seconds=999.0)
        with patch.object(heartbeat, "_session") as mock_session:
            mock_session.get.return_value = MagicMock()
            heartbeat.start()
            try:
                mock_session.get.assert_called_once()
                assert heartbeat._last_ping_monotonic is not None
            finally:
                heartbeat.stop()

    def test_start_skips_startup_ping_when_disabled(self) -> None:
        """start() does not ping immediately when startup_ping is False."""
        heartbeat = _make_heartbeat(startup_ping=False, interval_seconds=999.0)
        with patch.object(heartbeat, "_session") as mock_session:
            mock_session.get.return_value = MagicMock()
            heartbeat.start()
            try:
                mock_session.get.assert_not_called()
                assert heartbeat._last_ping_monotonic is not None
            finally:
                heartbeat.stop()

    def test_start_is_idempotent(self) -> None:
        """Calling start() a second time while already running is a no-op (no second thread)."""
        heartbeat = _make_heartbeat(startup_ping=False, interval_seconds=999.0)
        with patch.object(heartbeat, "_session") as mock_session:
            mock_session.get.return_value = MagicMock()
            heartbeat.start()
            first_thread = heartbeat._thread
            heartbeat.start()
            try:
                assert heartbeat._thread is first_thread
            finally:
                heartbeat.stop()

    def test_stop_joins_thread_and_does_not_raise(self) -> None:
        """stop() signals the background thread to end and joins it without error."""
        heartbeat = _make_heartbeat(startup_ping=False, interval_seconds=999.0)
        with patch.object(heartbeat, "_session") as mock_session:
            mock_session.get.return_value = MagicMock()
            heartbeat.start()
            heartbeat.stop()

        assert heartbeat._thread is not None
        assert not heartbeat._thread.is_alive()
