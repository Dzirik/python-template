r"""
Watchdog process that monitors and restarts crashed or frozen worker processes.

(.venv) PS D:\...\src\scripts> python watchdog.py --config-name=watchdog_cmd_01
(.venv) PS D:\...\src\scripts> python watchdog.py --config-name=watchdog_cmd_02
"""

import argparse
import json
import logging
import os
import signal
import subprocess
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path += [str(_SCRIPT_DIR / ".."), str(_SCRIPT_DIR / "../..")]

from src.scripts.heartbeat import HealthcheckHeartbeat, HealthcheckHeartbeatConfig  # noqa: E402
from src.scripts.watchdog_config import WatchdogConfig  # noqa: E402
from src.scripts.watchdog_config_data import WorkerData  # noqa: E402
from src.utils.logger import Logger  # noqa: E402

_ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_ENV_PATH)

BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR.parent.parent / "logs"
PYTHON_EXE = sys.executable
CHECK_INTERVAL = 30.0
STARTUP_GRACE_PERIOD = 5.0
WATCHDOG_HEALTHCHECK_INTERVAL = 60.0

PROCESSES: dict[str, subprocess.Popen[bytes]] = {}
HC_HEARTBEAT: HealthcheckHeartbeat | None = None


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
    raw = os.getenv("HEALTHCHECK_PING_URL")
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
        help="Name of the watchdog configuration file (without .conf extension).",
    )
    args = parser.parse_args()
    if not args.config_name.strip():
        parser.error("--config-name must not be an empty or blank string.")
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
    script_path = str(BASE_DIR / script)
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
    return subprocess.Popen(command, cwd=str(BASE_DIR))  # noqa: S603


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

    Attempts a soft termination first (``process.terminate()``), giving
    the worker up to 5 seconds to shut down cleanly (e.g. flush logs,
    send a final healthcheck ping).  If the process does not exit within
    that window, it is forcefully killed with ``process.kill()``.

    :param process: subprocess.Popen. Process handle.
    :param name: str. Worker name for logging.
    :return: None.
    """
    if not process_alive(process):
        Logger().info(f"Worker {name} is already terminated (exit code: {process.returncode}).")
        return

    Logger().info(f"Stopping {name} (graceful)...")
    process.terminate()
    try:
        process.wait(timeout=5)
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

    Logger().info(f"All workers started. Waiting {STARTUP_GRACE_PERIOD:.0f}s before first check...")
    time.sleep(STARTUP_GRACE_PERIOD)

    while True:
        for config in workers:
            name = config.name
            timeout = config.timeout
            process = PROCESSES.get(name)

            if process is None:
                try:
                    PROCESSES[name] = start_worker(config, heartbeat_dir)
                except Exception as e:
                    Logger().get().error(f"Retry failed for {name}: {e}", exc_info=True)
                continue

            try:
                crashed = not process_alive(process)
                frozen = heartbeat_age_seconds(name, heartbeat_dir) > timeout

                if crashed:
                    Logger().warning(f"{name} crashed. Restarting...")
                    PROCESSES[name] = start_worker(config, heartbeat_dir)
                    continue

                if frozen:
                    # TODO: Add pushover notification here
                    Logger().warning(f"{name} frozen. Restarting...")
                    stop_worker(process, name)
                    PROCESSES[name] = start_worker(config, heartbeat_dir)

            except Exception as e:
                Logger().get().error(f"Error managing worker {name}: {e}", exc_info=True)

        (heartbeat_dir / "watchdog.hb").touch()
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    args = parse_args()
    _add_script_file_handler(args.config_name)

    try:
        config_data = WatchdogConfig(args.config_name).get_data()
    except Exception as exc:
        Logger().error(f"Could not load configuration '{args.config_name}': {exc}")
        sys.exit(1)

    heartbeat_dir = BASE_DIR / f"heartbeats_{args.config_name}"
    heartbeat_dir.mkdir(exist_ok=True)

    ping_url = resolve_ping_url(config_data.healthcheck_url_key)
    if ping_url:
        HC_HEARTBEAT = HealthcheckHeartbeat(
            HealthcheckHeartbeatConfig(
                name=f"watchdog-{config_data.name}",
                ping_url=ping_url,
                interval_seconds=WATCHDOG_HEALTHCHECK_INTERVAL,
            )
        )
        HC_HEARTBEAT.start()

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    Logger().info(f"Watchdog Name: {config_data.name}, PID: {os.getpid()}")
    watchdog(config_data.workers, heartbeat_dir)
