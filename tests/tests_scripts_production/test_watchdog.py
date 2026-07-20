"""
Tests for the watchdog.py pure decision logic: restart backoff, crash-loop detection, and the
single-instance lock (ADR 0007).
"""

import json
import os
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.scripts_production import watchdog
from src.scripts_production.watchdog import (
    acquire_single_instance_lock,
    build_command,
    compute_backoff_delay,
    heartbeat_age_seconds,
    heartbeat_path,
    is_crash_loop,
    process_alive,
    resolve_ping_url,
    write_pid,
)
from src.utils.envs import Envs


# ---------------------------------------------------------------------------
# compute_backoff_delay
# ---------------------------------------------------------------------------
class TestComputeBackoffDelay:
    """Tests for compute_backoff_delay."""

    @pytest.mark.parametrize(
        ("consecutive_failures", "base", "cap", "expected"),
        [
            (0, 2.0, 300.0, 2.0),
            (1, 2.0, 300.0, 4.0),
            (2, 2.0, 300.0, 8.0),
            (3, 2.0, 300.0, 16.0),
            (10, 2.0, 300.0, 300.0),
            (3, 5.0, 60.0, 40.0),
            (0, 5.0, 60.0, 5.0),
        ],
    )
    def test_expected_delay(self, consecutive_failures: int, base: float, cap: float, expected: float) -> None:
        """Delay follows min(base * 2**consecutive_failures, cap)."""
        assert compute_backoff_delay(consecutive_failures, base, cap) == expected

    def test_delay_is_clamped_at_cap(self) -> None:
        """A very large failure count never produces a delay above the cap."""
        assert compute_backoff_delay(1000, 2.0, 300.0) == 300.0


# ---------------------------------------------------------------------------
# is_crash_loop
# ---------------------------------------------------------------------------
class TestIsCrashLoop:
    """Tests for is_crash_loop."""

    def test_below_threshold_is_not_crash_loop(self) -> None:
        """Fewer restarts than n within the window → not a crash loop."""
        now = 1_000.0
        restart_times = [now - 10, now - 5]
        assert is_crash_loop(restart_times, now, n=3, window=60.0) is False

    def test_at_threshold_is_crash_loop(self) -> None:
        """Exactly n restarts within the window → crash loop."""
        now = 1_000.0
        restart_times = [now - 30, now - 20, now - 10]
        assert is_crash_loop(restart_times, now, n=3, window=60.0) is True

    def test_above_threshold_is_crash_loop(self) -> None:
        """More than n restarts within the window → still a crash loop."""
        now = 1_000.0
        restart_times = [now - 40, now - 30, now - 20, now - 10]
        assert is_crash_loop(restart_times, now, n=3, window=60.0) is True

    def test_restarts_outside_window_are_excluded(self) -> None:
        """Restarts older than the trailing window don't count toward the threshold."""
        now = 1_000.0
        restart_times = [now - 500, now - 400, now - 10]
        assert is_crash_loop(restart_times, now, n=3, window=60.0) is False

    def test_no_restarts_is_not_crash_loop(self) -> None:
        """Empty restart history → never a crash loop."""
        assert is_crash_loop([], 1_000.0, n=1, window=60.0) is False


# ---------------------------------------------------------------------------
# acquire_single_instance_lock
# ---------------------------------------------------------------------------
class TestAcquireSingleInstanceLock:
    """Tests for acquire_single_instance_lock."""

    def test_acquire_once_succeeds(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """A single acquisition for a config succeeds and returns an open, unclosed handle."""
        monkeypatch.setattr(watchdog, "LOCK_DIR", tmp_path)

        handle = acquire_single_instance_lock("test_config_a")
        try:
            assert not handle.closed
        finally:
            handle.close()

    def test_second_acquire_for_same_config_fails(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """A second acquisition for the same config, while the first is held, raises OSError."""
        monkeypatch.setattr(watchdog, "LOCK_DIR", tmp_path)

        first_handle = acquire_single_instance_lock("test_config_b")
        try:
            # OSError itself: msvcrt raises PermissionError on Windows, fcntl raises
            # BlockingIOError on POSIX - both are OSError subtypes, so the exact subtype
            # (and its message) is platform-dependent and intentionally not pinned down here.
            with pytest.raises(OSError):  # noqa: PT011
                acquire_single_instance_lock("test_config_b")
        finally:
            first_handle.close()

    def test_lock_is_released_after_close(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Once the first handle is closed, a new acquisition for that config succeeds again."""
        monkeypatch.setattr(watchdog, "LOCK_DIR", tmp_path)

        first_handle = acquire_single_instance_lock("test_config_c")
        first_handle.close()

        second_handle = acquire_single_instance_lock("test_config_c")
        try:
            assert not second_handle.closed
        finally:
            second_handle.close()

    def test_different_configs_do_not_conflict(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Locks for two distinct config names can be held concurrently."""
        monkeypatch.setattr(watchdog, "LOCK_DIR", tmp_path)

        handle_a = acquire_single_instance_lock("test_config_d")
        handle_b = acquire_single_instance_lock("test_config_e")
        try:
            assert not handle_a.closed
            assert not handle_b.closed
        finally:
            handle_a.close()
            handle_b.close()


# ---------------------------------------------------------------------------
# heartbeat_path
# ---------------------------------------------------------------------------
class TestHeartbeatPath:
    """Tests for heartbeat_path."""

    def test_returns_hb_file_under_heartbeat_dir(self, tmp_path: Path) -> None:
        """The heartbeat path is <heartbeat_dir>/<worker_name>.hb."""
        assert heartbeat_path("worker1", tmp_path) == tmp_path / "worker1.hb"

    def test_different_worker_names_produce_different_paths(self, tmp_path: Path) -> None:
        """Two distinct worker names never collide on the same heartbeat file."""
        assert heartbeat_path("worker1", tmp_path) != heartbeat_path("worker2", tmp_path)


# ---------------------------------------------------------------------------
# write_pid
# ---------------------------------------------------------------------------
class TestWritePid:
    """Tests for write_pid."""

    def test_writes_current_pid_to_expected_file(self, tmp_path: Path) -> None:
        """write_pid creates <name>.pid containing the current process's PID."""
        write_pid("watchdog", tmp_path)

        pid_path = tmp_path / "watchdog.pid"
        assert pid_path.exists()
        assert pid_path.read_text(encoding="utf-8") == str(os.getpid())

    def test_overwrites_existing_pid_file(self, tmp_path: Path) -> None:
        """A pre-existing .pid file is overwritten, not appended to."""
        pid_path = tmp_path / "watchdog.pid"
        pid_path.write_text("999999", encoding="utf-8")

        write_pid("watchdog", tmp_path)

        assert pid_path.read_text(encoding="utf-8") == str(os.getpid())


# ---------------------------------------------------------------------------
# heartbeat_age_seconds
# ---------------------------------------------------------------------------
class TestHeartbeatAgeSeconds:
    """Tests for heartbeat_age_seconds."""

    def test_missing_heartbeat_file_returns_infinity(self, tmp_path: Path) -> None:
        """No .hb file on disk → age is reported as infinite (never "fresh")."""
        assert heartbeat_age_seconds("missing_worker", tmp_path) == float("inf")

    def test_fresh_heartbeat_reports_small_age(self, tmp_path: Path) -> None:
        """A heartbeat file touched just now reports an age close to zero."""
        hb_file = heartbeat_path("worker1", tmp_path)
        hb_file.touch()

        age = heartbeat_age_seconds("worker1", tmp_path)
        assert 0.0 <= age < 5.0

    def test_stale_heartbeat_reports_expected_age(self, tmp_path: Path) -> None:
        """A heartbeat file whose mtime is set to the past reports an age near that offset."""
        hb_file = heartbeat_path("worker1", tmp_path)
        hb_file.touch()
        old_time = time.time() - 120.0
        os.utime(hb_file, (old_time, old_time))

        age = heartbeat_age_seconds("worker1", tmp_path)
        assert 115.0 <= age <= 125.0


# ---------------------------------------------------------------------------
# process_alive
# ---------------------------------------------------------------------------
class TestProcessAlive:
    """Tests for process_alive."""

    def test_poll_none_means_alive(self) -> None:
        """process.poll() returning None (still running) → True."""
        process = MagicMock()
        process.poll.return_value = None
        assert process_alive(process) is True

    def test_poll_exit_code_means_not_alive(self) -> None:
        """process.poll() returning an exit code (process has exited) → False."""
        process = MagicMock()
        process.poll.return_value = 0
        assert process_alive(process) is False

    def test_poll_nonzero_exit_code_still_means_not_alive(self) -> None:
        """A non-zero exit code is still "not alive" - poll() returning anything but None means exited."""
        process = MagicMock()
        process.poll.return_value = 1
        assert process_alive(process) is False


# ---------------------------------------------------------------------------
# resolve_ping_url
# ---------------------------------------------------------------------------
class TestResolvePingUrl:
    """Tests for resolve_ping_url."""

    def test_no_env_var_returns_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When HEALTHCHECK_PING_URL is unset, resolution returns None."""
        monkeypatch.setattr(Envs, "get_healthcheck_ping_url", staticmethod(lambda: None))
        assert resolve_ping_url("worker1") is None

    def test_matching_key_returns_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A JSON list containing the requested key returns its url."""
        raw = json.dumps([{"key": "worker1", "url": "https://hc-ping.com/aaa"}])
        monkeypatch.setattr(Envs, "get_healthcheck_ping_url", staticmethod(lambda: raw))
        assert resolve_ping_url("worker1") == "https://hc-ping.com/aaa"

    def test_non_matching_key_returns_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A JSON list without the requested key returns None."""
        raw = json.dumps([{"key": "other_worker", "url": "https://hc-ping.com/aaa"}])
        monkeypatch.setattr(Envs, "get_healthcheck_ping_url", staticmethod(lambda: raw))
        assert resolve_ping_url("worker1") is None

    def test_invalid_json_returns_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Malformed JSON in the env var returns None rather than raising."""
        monkeypatch.setattr(Envs, "get_healthcheck_ping_url", staticmethod(lambda: "not-json{"))
        assert resolve_ping_url("worker1") is None

    def test_non_list_json_returns_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Valid JSON that isn't a list (e.g. a dict) returns None."""
        raw = json.dumps({"key": "worker1", "url": "https://hc-ping.com/aaa"})
        monkeypatch.setattr(Envs, "get_healthcheck_ping_url", staticmethod(lambda: raw))
        assert resolve_ping_url("worker1") is None

    def test_first_matching_entry_wins(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When multiple entries share a key, the first match in list order is returned."""
        raw = json.dumps(
            [
                {"key": "worker1", "url": "https://hc-ping.com/first"},
                {"key": "worker1", "url": "https://hc-ping.com/second"},
            ]
        )
        monkeypatch.setattr(Envs, "get_healthcheck_ping_url", staticmethod(lambda: raw))
        assert resolve_ping_url("worker1") == "https://hc-ping.com/first"


# ---------------------------------------------------------------------------
# build_command
# ---------------------------------------------------------------------------
class TestBuildCommand:
    """Tests for build_command."""

    def test_builds_expected_argument_list(self, tmp_path: Path) -> None:
        """The command line includes the resolved script path, worker flags, and trailing args."""
        command = build_command(
            script="run_cmd_status_print_01.py",
            worker_name="worker1",
            args=[1, "two"],
            heartbeat_dir=tmp_path,
            healthcheck_url_key="key1",
        )

        expected_script_path = str((watchdog.BASE_DIR / "run_cmd_status_print_01.py").resolve())
        expected_hb_path = str(heartbeat_path("worker1", tmp_path))
        assert command == [
            watchdog.PYTHON_EXE,
            "-u",
            expected_script_path,
            "--worker-name",
            "worker1",
            "--heartbeat-file",
            expected_hb_path,
            "--heartbeat-folder",
            str(tmp_path),
            "--healthcheck-url-key",
            "key1",
            "1",
            "two",
        ]

    def test_empty_args_produce_no_trailing_arguments(self, tmp_path: Path) -> None:
        """An empty args list adds no extra trailing command-line arguments."""
        command = build_command(
            script="run_cmd_status_print_01.py",
            worker_name="worker1",
            args=[],
            heartbeat_dir=tmp_path,
            healthcheck_url_key="key1",
        )
        assert command[-1] == "key1"

    def test_script_outside_base_dir_raises_value_error(self, tmp_path: Path) -> None:
        """A script path that escapes BASE_DIR is rejected rather than launched."""
        with pytest.raises(ValueError, match="must be inside"):
            build_command(
                script="../../outside.py",
                worker_name="worker1",
                args=[],
                heartbeat_dir=tmp_path,
                healthcheck_url_key="key1",
            )

    def test_missing_script_raises_file_not_found(self, tmp_path: Path) -> None:
        """A script name that resolves inside BASE_DIR but doesn't exist raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            build_command(
                script="definitely_does_not_exist.py",
                worker_name="worker1",
                args=[],
                heartbeat_dir=tmp_path,
                healthcheck_url_key="key1",
            )
