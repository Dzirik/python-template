r"""
Watchdog process that monitors and restarts crashed or frozen worker processes.

(.venv) PS D:\...\src\scripts> python watchdog.py --config-name=watchdog_cmd_01
(.venv) PS D:\...\src\scripts> python watchdog.py --config-name=watchdog_cmd_02
"""

import argparse
import json
import logging
import os
import re
import signal

# Bandit B404: subprocess is required to manage worker processes.
import subprocess  # nosec B404
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import IO, Any

# Single-instance lock primitive differs by platform; mypy's sys.platform narrowing keeps
# each branch checked against the stub for its own platform only.
if sys.platform == "win32":
    import msvcrt
else:
    import fcntl

from dotenv import load_dotenv

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path += [str(_SCRIPT_DIR / ".."), str(_SCRIPT_DIR / "../..")]

from src.configurations.watchdog_config import WatchdogConfig  # noqa: E402
from src.configurations.watchdog_config_data import SupervisionTimingData, WorkerData  # noqa: E402
from src.scripts_production.heartbeat import HealthcheckHeartbeat, HealthcheckHeartbeatConfig  # noqa: E402
from src.utils.envs import Envs  # noqa: E402
from src.utils.logger import Logger  # noqa: E402

_ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_ENV_PATH)

BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR.parent.parent / "logs"
LOCK_DIR = BASE_DIR
PYTHON_EXE = sys.executable
CONFIG_NAME_PATTERN = re.compile(r"[A-Za-z0-9_-]+")

PROCESSES: dict[str, subprocess.Popen[bytes]] = {}
HC_HEARTBEAT: HealthcheckHeartbeat | None = None
# Supervision timing tunables (see ADR 0007), read from the watchdog TOML's optional
# [supervision] table and overwritten from config_data.supervision in __main__ before
# watchdog() runs. This default reproduces today's behavior for anything invoked before that
# (e.g. imported for tests), and is the seam every timing-sensitive function below reads through
# instead of a module-level constant.
SUPERVISION: SupervisionTimingData = SupervisionTimingData()
# Per-worker crash-loop backoff bookkeeping, keyed by worker name so one worker's crash-loop
# state never affects another's.
CONSECUTIVE_FAILURES: dict[str, int] = {}
RESTART_TIMES: dict[str, list[float]] = {}
NEXT_RESTART_TIME: dict[str, float] = {}


def _add_script_file_handler(config_name: str) -> None:
    """
    Attach a per-config ``RotatingFileHandler`` to the centralized :class:`Logger`.

    Log file: ``logs/watchdog_{config_name}.log`` (5 MB, 3 backups).
    This supplements whatever handlers the ``Logger`` singleton already has
    (e.g. console output from the default logger config) with a dedicated
    rotating log file for this watchdog instance.

    :param config_name: str. Configuration name used to derive the log filename.
    :return: None.
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / f"watchdog_{config_name}.log"

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5_242_880,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    Logger().get().addHandler(file_handler)


def resolve_ping_url(healthcheck_url_key: str) -> str | None:
    """
    Look up a healthcheck ping URL by key from the HEALTHCHECK_PING_URL env var.

    The environment variable must be a JSON-formatted list of dictionaries,
    each with a ``key`` and a ``url`` field.

    :param healthcheck_url_key: str. Key to match against.
    :return: str | None. The matching ping URL, or None if not found.
    """
    raw = Envs.get_healthcheck_ping_url()
    if not raw:
        return None

    try:
        entries = json.loads(raw)
    except json.JSONDecodeError:
        Logger().warning(f"HEALTHCHECK_PING_URL is not valid JSON: {raw}")
        return None

    if not isinstance(entries, list):
        Logger().warning(f"HEALTHCHECK_PING_URL must be a JSON list, got {type(entries).__name__}")
        return None

    for entry in entries:
        if isinstance(entry, dict) and entry.get("key") == healthcheck_url_key:
            return entry.get("url")

    Logger().warning(f"No healthcheck entry found for key '{healthcheck_url_key}'")
    return None


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Exits with an error message if --config-name is absent or blank.

    :return: argparse.Namespace. Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Watchdog process monitor.")
    parser.add_argument(
        "--config-name",
        required=True,
        type=str,
        help="Name of the watchdog configuration file (without .toml extension).",
    )
    args = parser.parse_args()
    if not args.config_name.strip():
        parser.error("--config-name must not be an empty or blank string.")
    if CONFIG_NAME_PATTERN.fullmatch(args.config_name) is None:
        parser.error("--config-name must contain only letters, numbers, '_' or '-'.")
    return args


def heartbeat_path(worker_name: str, heartbeat_dir: Path) -> Path:
    """
    Return the heartbeat file path for a worker instance.

    :param worker_name: str. Unique worker instance name.
    :param heartbeat_dir: Path. Directory where heartbeat files are stored.
    :return: Path. Heartbeat file path.
    """
    return heartbeat_dir / f"{worker_name}.hb"


def write_pid(name: str, heartbeat_dir: Path) -> None:
    """
    Write a worker's PID to a .pid file.

    :param name: str. Worker name, used to derive the .pid filename.
    :param heartbeat_dir: Path. Directory where PID files are stored.
    :return: None.
    """
    pid_path = heartbeat_dir / f"{name}.pid"
    pid_path.write_text(str(os.getpid()), encoding="utf-8")


def _resolve_worker_script(script: str) -> Path:
    """Resolve and validate worker scripts so watchdog only launches files under BASE_DIR."""
    script_path = (BASE_DIR / script).resolve()
    try:
        script_path.relative_to(BASE_DIR)
    except ValueError as exc:
        raise ValueError(f"Worker script must be inside {BASE_DIR}: {script!r}") from exc
    if not script_path.is_file():
        raise FileNotFoundError(f"Worker script does not exist: {script_path}")
    return script_path


def build_command(
    script: str,
    worker_name: str,
    args: list[Any],
    heartbeat_dir: Path,
    healthcheck_url_key: str,
) -> list[str]:
    """
    Build the command line for a worker process.

    :param script: str. Worker script filename.
    :param worker_name: str. Unique worker instance name.
    :param args: list[Any]. Additional command-line arguments for the worker.
    :param heartbeat_dir: Path. Directory where heartbeat files are stored.
    :param healthcheck_url_key: str. Key to look up the ping URL in HEALTHCHECK_PING_URL.
    :return: list[str]. Full subprocess command.
    """
    script_path = str(_resolve_worker_script(script))
    hb_path = str(heartbeat_path(worker_name, heartbeat_dir))

    return [
        PYTHON_EXE,
        "-u",
        script_path,
        "--worker-name",
        worker_name,
        "--heartbeat-file",
        hb_path,
        "--heartbeat-folder",
        str(heartbeat_dir),
        "--healthcheck-url-key",
        healthcheck_url_key,
        *[str(a) for a in args],
    ]


def start_worker(config: WorkerData, heartbeat_dir: Path) -> subprocess.Popen[bytes]:
    """
    Start a worker process from configuration.

    On Windows the worker is started in a new process group (``CREATE_NEW_PROCESS_GROUP``) so
    that a later ``CTRL_BREAK_EVENT`` can be delivered to it alone via :func:`stop_worker`
    without also signalling the watchdog itself.

    :param config: WorkerData. Worker configuration named tuple.
    :param heartbeat_dir: Path. Directory where heartbeat files are stored.
    :return: subprocess.Popen. Started process handle.
    """
    command = build_command(
        script=config.script,
        worker_name=config.name,
        args=config.args,
        heartbeat_dir=heartbeat_dir,
        healthcheck_url_key=config.healthcheck_url_key,
    )
    Logger().info(f"Starting {config.name}: {' '.join(command)}")
    if sys.platform == "win32":
        return subprocess.Popen(  # noqa: S603  # nosec
            command, cwd=str(BASE_DIR), creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
    else:  # noqa: RET505 - branch kept explicit so mypy's sys.platform narrowing checks both sides
        return subprocess.Popen(command, cwd=str(BASE_DIR))  # noqa: S603  # nosec


def heartbeat_age_seconds(worker_name: str, heartbeat_dir: Path) -> float:
    """
    Return the age of the worker heartbeat in seconds.

    :param worker_name: str. Unique worker instance name.
    :param heartbeat_dir: Path. Directory where heartbeat files are stored.
    :return: float. Seconds since last heartbeat update, or infinity if missing.
    """
    hb = heartbeat_path(worker_name, heartbeat_dir)

    if not hb.exists():
        return float("inf")

    return time.time() - hb.stat().st_mtime


def process_alive(process: subprocess.Popen[bytes]) -> bool:
    """
    Check whether a subprocess is still alive.

    Uses process.poll(), which calls the OS-level waitpid() (POSIX) or
    GetExitCodeProcess() (Windows) against the process HANDLE, not the PID.
    This is more reliable than looking up the process by PID in the OS, because
    PIDs are recycled: once a process exits and its exit status has been collected,
    the OS may assign the same PID number to a completely different process. The
    Popen handle retains an OS-level reference to the original process, so poll()
    accurately reflects that specific process's state regardless of PID reuse.

    A process may appear "missing" from the system PID list (e.g. in Task Manager
    or via psutil) while its Popen handle is still present in PROCESSES when a
    restart attempt failed after the previous handle was detected as crashed. In
    that case the stale dead handle remains in the dict until the next successful
    restart. poll() will correctly return the cached exit code for that handle.

    :param process: subprocess.Popen. Process handle.
    :return: bool. True if running, otherwise False.
    """
    return process.poll() is None


def stop_worker(process: subprocess.Popen[bytes], name: str) -> None:
    """
    Stop a worker process gracefully, falling back to a hard kill.

    Sends the worker's process group a real graceful-stop signal — ``CTRL_BREAK_EVENT`` on
    Windows (the worker must have been started with ``CREATE_NEW_PROCESS_GROUP``, see
    :func:`start_worker`), ``SIGTERM`` on POSIX — giving it up to
    ``SUPERVISION.stop_grace_period`` seconds to shut down cleanly (e.g. flush logs, send a final
    healthcheck ping). If the process does not exit within that window, it is forcefully killed
    with ``process.kill()``. This is the signal contract every worker is expected to honour; see
    ``run_cmd_status_print_01.py``/``run_cmd_status_print_02.py`` for the reference handler.

    :param process: subprocess.Popen. Process handle.
    :param name: str. Worker name for logging.
    :return: None.
    """
    if not process_alive(process):
        Logger().info(f"Worker {name} is already terminated (exit code: {process.returncode}).")
        return

    Logger().info(f"Stopping {name} (graceful)...")
    if sys.platform == "win32":
        os.kill(process.pid, signal.CTRL_BREAK_EVENT)
    else:
        process.send_signal(signal.SIGTERM)
    try:
        process.wait(timeout=SUPERVISION.stop_grace_period)
        Logger().info(f"Worker {name} terminated gracefully.")
    except subprocess.TimeoutExpired:
        Logger().warning(f"Worker {name} did not exit in time, forcing kill...")
        process.kill()
        process.wait()


def shutdown_handler(_signum: int, _frame: Any) -> None:
    """
    Gracefully stop all managed worker processes and exit.

    Called automatically when SIGINT (Ctrl+C) or SIGTERM is received.

    :param _signum: int. Signal number received.
    :param _frame: Any. Current stack frame (unused).
    :return: None.
    """
    Logger().info("Shutdown signal received. Stopping all workers...")
    for name, process in PROCESSES.items():
        stop_worker(process, name)
    if HC_HEARTBEAT is not None:
        HC_HEARTBEAT.stop()
    Logger().info("All workers stopped. Exiting.")
    sys.exit(0)


def compute_backoff_delay(consecutive_failures: int, base: float, cap: float) -> float:
    """
    Computes the exponential-backoff restart delay for a worker, clamped at a cap.

    Pure function: ``min(base * 2**consecutive_failures, cap)``. Used so a repeatedly
    crashing worker is retried with growing spacing instead of hammering a still-broken
    dependency every check interval, while never exceeding ``cap``.

    :param consecutive_failures: int. Number of restarts already attempted back-to-back.
    :param base: float. Base delay in seconds before the first backoff doubling.
    :param cap: float. Maximum delay in seconds; the result never exceeds this.
    :return: float. Delay in seconds to wait before the next restart attempt.
    """
    return min(base * (2.0**consecutive_failures), cap)


def is_crash_loop(restart_times: list[float], now: float, n: int, window: float) -> bool:
    """
    Determines whether a worker's restart history constitutes a crash loop.

    Pure function: True if at least ``n`` restarts occurred within the trailing ``window``
    seconds ending at ``now``. Restarts older than the window are ignored, so a worker that
    crashed repeatedly long ago but has since stabilised is not considered crash-looping.

    :param restart_times: list[float]. Timestamps (``time.time()``-style) of past restarts.
    :param now: float. Current timestamp, defining the end of the trailing window.
    :param n: int. Minimum number of restarts within the window to count as a crash loop.
    :param window: float. Trailing window size in seconds.
    :return: bool. True if a crash loop is in progress, otherwise False.
    """
    recent_restarts = [t for t in restart_times if now - t <= window]
    return len(recent_restarts) >= n


def acquire_single_instance_lock(config_name: str) -> IO[bytes]:
    """
    Acquires an exclusive, non-blocking OS-level lock so only one watchdog runs per config.

    The lock lives at ``LOCK_DIR/.watchdog_{config_name}.lock`` and must be held for the
    lifetime of the process: the caller is expected to keep a reference to the returned
    handle alive until exit, since closing (or garbage-collecting) it releases the lock
    immediately. Windows uses ``msvcrt.locking(LK_NBLCK)`` on a one-byte region of the file;
    POSIX uses ``fcntl.flock(LOCK_EX | LOCK_NB)`` on the whole file. Both raise ``OSError``
    immediately if another process already holds the lock, rather than blocking, so two
    watchdogs started for the same config near-simultaneously cannot both win the race.

    :param config_name: str. Configuration name; used to derive the per-config lockfile.
    :return: IO[bytes]. Open file handle holding the exclusive lock.
    :raises OSError: If the lock is already held by another process.
    """
    lock_path = LOCK_DIR / f".watchdog_{config_name}.lock"
    lock_file = lock_path.open("a+b")

    try:
        if sys.platform == "win32":
            lock_file.seek(0)
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        lock_file.close()
        raise

    return lock_file


def _reset_heartbeat_on_restart(name: str, heartbeat_dir: Path) -> None:
    """
    Resets a worker's heartbeat file to "now" immediately after (re)starting it.

    Without this, a freshly restarted worker that is slow to write its first heartbeat would
    be judged against the previous process's stale ``.hb`` mtime and could be re-flagged as
    frozen before it has had any chance to run.

    :param name: str. Unique worker instance name.
    :param heartbeat_dir: Path. Directory where heartbeat files are stored.
    :return: None.
    """
    heartbeat_path(name, heartbeat_dir).touch()


def _attempt_restart(config: WorkerData, heartbeat_dir: Path, now: float) -> None:
    """
    Restarts a worker if its per-worker crash-loop backoff window has elapsed.

    On success, records the restart time and consecutive-failure count, then schedules the
    next allowed restart via :func:`compute_backoff_delay`. If :func:`is_crash_loop` finds
    the worker has restarted too often too recently, a ``CRITICAL`` log is emitted noting that
    the worker's healthcheck ping will lapse while the watchdog backs off — but the worker is
    never permanently abandoned, only retried more slowly, capped at
    ``SUPERVISION.backoff_cap``. Other workers' backoff state is untouched, since all bookkeeping
    is keyed by worker name.

    :param config: WorkerData. Worker configuration named tuple.
    :param heartbeat_dir: Path. Directory where heartbeat and PID files are stored.
    :param now: float. Current time (``time.time()``), passed in for deterministic bookkeeping.
    :return: None.
    """
    name = config.name
    if now < NEXT_RESTART_TIME.get(name, 0.0):
        return

    try:
        PROCESSES[name] = start_worker(config, heartbeat_dir)
    except Exception as e:
        Logger().get().error(f"Failed to restart worker {name}: {e}", exc_info=True)
        return

    _reset_heartbeat_on_restart(name, heartbeat_dir)

    crash_loop_window = SUPERVISION.crash_loop_window

    restarts = [*RESTART_TIMES.get(name, []), now]
    restarts = [t for t in restarts if now - t <= crash_loop_window]
    RESTART_TIMES[name] = restarts
    CONSECUTIVE_FAILURES[name] = CONSECUTIVE_FAILURES.get(name, 0) + 1

    delay = compute_backoff_delay(CONSECUTIVE_FAILURES[name], SUPERVISION.backoff_base, SUPERVISION.backoff_cap)
    NEXT_RESTART_TIME[name] = now + delay

    if is_crash_loop(restarts, now, SUPERVISION.crash_loop_count, crash_loop_window):
        Logger().critical(
            f"{name} is crash-looping ({len(restarts)} restarts within {crash_loop_window:.0f}s). "
            f"Its healthcheck ping will lapse while the watchdog backs off; retrying every "
            f"{delay:.0f}s (capped at {SUPERVISION.backoff_cap:.0f}s) without giving up."
        )


def watchdog(workers: list[WorkerData], heartbeat_dir: Path) -> None:
    """
    Monitor all configured workers and restart crashed or frozen ones.

    :param workers: list[WorkerData]. List of worker configurations to manage.
    :param heartbeat_dir: Path. Directory where heartbeat and PID files are stored.
    :return: None.
    """
    write_pid("watchdog", heartbeat_dir)

    for config in workers:
        try:
            PROCESSES[config.name] = start_worker(config, heartbeat_dir)
        except Exception as e:
            Logger().get().error(f"Failed to start worker {config.name} on startup: {e}", exc_info=True)

    Logger().info(f"All workers started. Waiting {SUPERVISION.startup_grace_period:.0f}s before first check...")
    time.sleep(SUPERVISION.startup_grace_period)

    while True:
        for config in workers:
            name = config.name
            timeout = config.timeout
            process = PROCESSES.get(name)
            now = time.time()

            if process is None:
                _attempt_restart(config, heartbeat_dir, now)
                continue

            try:
                crashed = not process_alive(process)
                frozen = heartbeat_age_seconds(name, heartbeat_dir) > timeout

                if crashed:
                    Logger().warning(f"{name} crashed. Restarting...")
                    _attempt_restart(config, heartbeat_dir, now)
                    continue

                if frozen:
                    # TODO: Add pushover notification here
                    Logger().warning(f"{name} frozen. Restarting...")
                    stop_worker(process, name)
                    _attempt_restart(config, heartbeat_dir, now)

            except Exception as e:
                Logger().get().error(f"Error managing worker {name}: {e}", exc_info=True)

        (heartbeat_dir / "watchdog.hb").touch()
        time.sleep(SUPERVISION.check_interval)


if __name__ == "__main__":
    args = parse_args()
    _add_script_file_handler(args.config_name)

    try:
        instance_lock = acquire_single_instance_lock(args.config_name)
    except OSError:
        Logger().critical(f"Another watchdog instance is already running for config '{args.config_name}'. Exiting.")
        sys.exit(0)

    try:
        config_data = WatchdogConfig(args.config_name).get_data()
    except Exception as exc:
        Logger().error(f"Could not load configuration '{args.config_name}': {exc}")
        sys.exit(1)

    SUPERVISION = config_data.supervision

    heartbeat_dir = BASE_DIR / f"heartbeats_{args.config_name}"
    heartbeat_dir.mkdir(exist_ok=True)

    ping_url = resolve_ping_url(config_data.healthcheck_url_key)
    if ping_url:
        HC_HEARTBEAT = HealthcheckHeartbeat(
            HealthcheckHeartbeatConfig(
                name=f"watchdog-{config_data.name}",
                ping_url=ping_url,
                interval_seconds=SUPERVISION.watchdog_healthcheck_interval,
            )
        )
        HC_HEARTBEAT.start()

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    Logger().info(f"Watchdog Name: {config_data.name}, PID: {os.getpid()}")
    watchdog(config_data.workers, heartbeat_dir)
