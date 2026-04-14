"""
Code for health check using healthcheck.io
"""

import logging
import threading
import time
from dataclasses import dataclass

import requests

logger = logging.getLogger(__name__)


@dataclass
class HealthcheckHeartbeatConfig:
    """
    Configuration for Healthchecks heartbeat sender.

    :param name: str. Human-readable service name for logs
    :param ping_url: str. Healthchecks ping URL
    :param interval_seconds: float. Target interval between pings
    :param max_extra_delay_seconds: float. Warn if ping is later than interval + this value
    :param request_timeout_seconds: float. HTTP timeout for requests
    :param startup_ping: bool. Whether to send an immediate ping on startup
    """

    name: str
    ping_url: str
    interval_seconds: float = 60.0
    max_extra_delay_seconds: float = 10.0
    request_timeout_seconds: float = 5.0
    startup_ping: bool = True


class HealthcheckHeartbeat:
    """
    Background heartbeat sender for long-running Python services.
    """

    def __init__(self, config: HealthcheckHeartbeatConfig) -> None:
        self.config = config
        self._session = requests.Session()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_ping_monotonic: float | None = None
        self._lock = threading.Lock()

    def start(self) -> None:
        """
        Start the heartbeat thread.

        :return: None.
        """
        with self._lock:
            if self._thread is not None:
                return

            if self.config.startup_ping:
                self._send_ping()
                self._last_ping_monotonic = time.monotonic()
            else:
                self._last_ping_monotonic = time.monotonic()

            self._thread = threading.Thread(
                target=self._run,
                name=f"heartbeat-{self.config.name}",
                daemon=True,
            )
            self._thread.start()

            logger.info("Heartbeat started for %s", self.config.name)

    def stop(self) -> None:
        """
        Stop the heartbeat thread.

        :return: None.
        """
        with self._lock:
            self._stop_event.set()
            thread = self._thread

        if thread is not None:
            thread.join(timeout=2.0)

        logger.info("Heartbeat stopped for %s", self.config.name)

    def ping_now(self) -> None:
        """
        Force an immediate heartbeat ping.

        :return: None.
        """
        self._send_ping()
        self._last_ping_monotonic = time.monotonic()

    def _run(self) -> None:
        """
        Heartbeat loop.

        :return: None.
        """
        while not self._stop_event.is_set():
            now = time.monotonic()
            last = self._last_ping_monotonic or now
            elapsed = now - last

            if elapsed >= self.config.interval_seconds:
                delay = elapsed - self.config.interval_seconds

                if delay > self.config.max_extra_delay_seconds:
                    logger.warning(
                        "Heartbeat for %s delayed by %.2f seconds",
                        self.config.name,
                        delay,
                    )

                self._send_ping()
                self._last_ping_monotonic = time.monotonic()

            self._stop_event.wait(1.0)

    def _send_ping(self) -> None:
        """
        Send ping to Healthchecks.

        :return: None.
        """
        try:
            response = self._session.get(
                self.config.ping_url,
                timeout=self.config.request_timeout_seconds,
            )
            response.raise_for_status()
        except Exception as exc:
            logger.exception("Heartbeat failed: %s", exc)
