"""
Data structure for config.
"""

from typing import NamedTuple


class WorkerData(NamedTuple):
    """
    Parameters of one worked.
    - name: str. Name of the worker/process.
    - script: str. Name of the script with .py.
    - args: list[str]. List of script arguments.
    - timeout: float. Timeout in seconds.
    - healthcheck_url_key: str. Key to look up the ping URL in HEALTHCHECK_PING_URL.
    """

    name: str
    script: str
    args: list[str]
    timeout: float
    healthcheck_url_key: str = ""


class SupervisionTimingData(NamedTuple):
    """
    Supervision timing tunables for the watchdog process supervisor (see ADR 0007).

    Every field defaults to the constant watchdog.py used before these timings moved into
    config, so a watchdog TOML that omits the whole ``[supervision]`` table reproduces today's
    behavior exactly.
    - check_interval: float. Seconds between successive worker health-check passes.
    - startup_grace_period: float. Seconds to wait after starting all workers before the first
      health-check pass.
    - stop_grace_period: float. Seconds to wait for a worker to exit after a graceful-stop signal
      before falling back to a hard kill.
    - watchdog_healthcheck_interval: float. Seconds between the watchdog's own healthchecks.io
      pings.
    - backoff_base: float. Base delay in seconds for the per-worker crash-loop restart backoff.
    - backoff_cap: float. Maximum delay in seconds the crash-loop restart backoff can reach.
    - crash_loop_count: int. Minimum number of restarts within crash_loop_window that counts as
      a crash loop.
    - crash_loop_window: float. Trailing window in seconds used to detect a crash loop.
    """

    check_interval: float = 30.0
    startup_grace_period: float = 5.0
    stop_grace_period: float = 5.0
    watchdog_healthcheck_interval: float = 30.0
    backoff_base: float = 2.0
    backoff_cap: float = 300.0
    crash_loop_count: int = 5
    crash_loop_window: float = 300.0


class WatchdogConfigData(NamedTuple):
    """
    For storing parameters of watchdog config.
    """

    name: str
    healthcheck_url_key: str = ""
    workers: list[WorkerData] = []  # noqa: RUF012
    supervision: SupervisionTimingData = SupervisionTimingData()
