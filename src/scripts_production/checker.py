r"""
Supervisor script that monitors the watchdog process and performs recovery if it hangs.

Supervision hierarchy:
    Windows Task Scheduler -> checker.py -> watchdog.py -> Worker Processes

(.venv) PS D:\...\src\scripts> python checker.py --config-name=watchdog_cmd_01
"""

import argparse
import logging
import os
import subprocess
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR.parent.parent / "logs"

sys.path += [str(BASE_DIR / ".."), str(BASE_DIR / "../..")]

from src.scripts.watchdog_config import WatchdogConfig  # noqa: E402
from src.utils.logger import Logger  # noqa: E402

SCHEDULER_INTERVAL = 30.0
HEARTBEAT_THRESHOLD = (SCHEDULER_INTERVAL * 2) * 1.5


def _add_script_file_handler(config_name: str) -> None:
    """
    Attach a per-config ``RotatingFileHandler`` to the centralized :class:`Logger`.

    Log file: ``logs/checker_{config_name}.log`` (5 MB, 3 backups).
    This supplements whatever handlers the ``Logger`` singleton already has
    (e.g. console output from the default logger config) with a dedicated
    rotating log file for this checker instance.

    :param config_name: str. Configuration name used to derive the log filename.
    :return: None.
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / f"checker_{config_name}.log"

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


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    :return: argparse.Namespace. Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Watchdog supervisor / checker.")
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


def is_process_alive(pid: int) -> bool:
    """
    Check whether a process with the given PID is currently running (Windows).

    :param pid: int. Process ID to check.
    :return: bool. True if process is alive, False otherwise.
    """
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _get_process_cmdline(pid: int) -> str | None:
    """
    Retrieve the command line of a running process via WMIC (Windows).

    :param pid: int. Process ID to query.
    :return: str | None. The command line string, or None if the process
        does not exist or the query fails.
    """
    try:
        result = subprocess.run(  # noqa: S603
            ["wmic", "process", "where", f"ProcessId={pid}", "get", "CommandLine"],  # noqa: S607
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode != 0:
            return None
        # WMIC output: header line ("CommandLine"), then the value line(s).
        lines = [ln.strip() for ln in result.stdout.strip().splitlines() if ln.strip()]
        # First non-empty line is the header; the rest is the command line.
        if len(lines) < 2:
            return None
        return " ".join(lines[1:])
    except Exception:
        return None


def is_watchdog_process(pid: int, config_name: str) -> bool:
    """
    Verify that *pid* belongs to a running watchdog.py instance for *config_name*.

    First checks basic process existence with ``os.kill(pid, 0)``, then
    queries the process command line via WMIC to confirm it is actually a
    ``watchdog.py`` process launched with the expected ``--config-name``.
    This prevents false-positive "healthy" results caused by PID recycling
    on Windows.

    :param pid: int. Process ID read from the .pid file.
    :param config_name: str. Expected ``--config-name`` value.
    :return: bool. True only if the process exists AND its command line
        matches the expected watchdog instance.
    """
    if not is_process_alive(pid):
        return False

    cmdline = _get_process_cmdline(pid)
    if cmdline is None:
        # WMIC failed — fall back to the basic alive check so that a
        # transient WMI error doesn't trigger an unnecessary recovery.
        Logger().warning(f"Could not verify command line for PID {pid}; assuming alive (WMIC unavailable).")
        return True

    if "watchdog.py" not in cmdline:
        Logger().warning(f"PID {pid} is alive but is not a watchdog process (cmdline: {cmdline!r}).")
        return False

    if config_name not in cmdline:
        Logger().warning(f"PID {pid} is a watchdog process but for a different config (cmdline: {cmdline!r}).")
        return False

    return True


def read_pid(pid_file: Path) -> int | None:
    """
    Read a PID from a .pid file.

    :param pid_file: Path. Path to the .pid file.
    :return: int | None. The PID, or None if the file is missing or invalid.
    """
    if not pid_file.exists():
        return None
    try:
        return int(pid_file.read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        return None


def is_watchdog_healthy(heartbeat_dir: Path, config_name: str) -> bool:
    """
    Determine whether the watchdog process is healthy.

    Uses :func:`is_watchdog_process` to verify the PID actually belongs to a
    ``watchdog.py`` instance for *config_name*, guarding against PID recycling.

    :param heartbeat_dir: Path. Heartbeat directory for this config.
    :param config_name: str. Expected ``--config-name`` value.
    :return: bool. True if the watchdog is healthy.
    """
    pid_file = heartbeat_dir / "watchdog.pid"
    hb_file = heartbeat_dir / "watchdog.hb"

    pid = read_pid(pid_file)
    if pid is None:
        Logger().warning("Watchdog unhealthy: watchdog.pid missing or invalid.")
        return False

    if not is_watchdog_process(pid, config_name):
        Logger().warning(f"Watchdog unhealthy: PID {pid} is not running (or belongs to another process).")
        return False

    if not hb_file.exists():
        Logger().warning("Watchdog unhealthy: watchdog.hb missing.")
        return False

    age = time.time() - hb_file.stat().st_mtime
    if age > HEARTBEAT_THRESHOLD:
        Logger().warning(f"Watchdog unhealthy: heartbeat stale ({age:.0f}s old, threshold {HEARTBEAT_THRESHOLD:.0f}s).")
        return False

    return True


def kill_process(pid: int) -> None:
    """
    Force-terminate a process and its children via taskkill (Windows).

    :param pid: int. Process ID to kill.
    :return: None.
    """
    subprocess.run(  # noqa: S603
        ["taskkill", "/PID", str(pid), "/T", "/F"],  # noqa: S607
        capture_output=True,
        check=False,
    )


def recover_watchdog(heartbeat_dir: Path, config_name: str) -> None:
    """
    Perform a full recovery: kill the watchdog tree, clean up zombie workers,
    and restart the watchdog.

    :param heartbeat_dir: Path. Heartbeat directory for this config.
    :param config_name: str. Configuration name to pass to watchdog.py.
    :return: None.
    """
    watchdog_pid = read_pid(heartbeat_dir / "watchdog.pid")

    # Step 1: Kill watchdog tree
    if watchdog_pid is not None:
        Logger().info(f"Terminating watchdog tree (PID {watchdog_pid})...")
        kill_process(watchdog_pid)

    # Step 2: Cleanup zombie workers
    for pid_file in heartbeat_dir.glob("*.pid"):
        pid = read_pid(pid_file)
        if pid is not None and pid != watchdog_pid:
            Logger().info(f"Terminating orphaned worker (PID {pid}, file {pid_file.name})...")
            kill_process(pid)

    # Step 3: Wait for the OS to fully reclaim the killed process tree and
    # release file handles before starting a new watchdog instance.
    Logger().info("Waiting for process tree to be reclaimed...")
    time.sleep(2.0)

    # Step 4: Restart watchdog
    Logger().info(f"Starting new watchdog instance with config '{config_name}'...")
    subprocess.Popen(  # noqa: S603
        [sys.executable, "-u", "watchdog.py", "--config-name", config_name],
        cwd=str(BASE_DIR),
    )
    Logger().info("Watchdog restarted.")


if __name__ == "__main__":
    args = parse_args()
    _add_script_file_handler(args.config_name)

    try:
        WatchdogConfig(args.config_name).get_data()
    except Exception as exc:
        Logger().error(f"Could not load configuration '{args.config_name}': {exc}")
        sys.exit(1)

    heartbeat_dir = BASE_DIR / f"heartbeats_{args.config_name}"
    heartbeat_dir.mkdir(exist_ok=True)

    Logger().info(f"Checker invoked for config '{args.config_name}'. Heartbeat threshold: {HEARTBEAT_THRESHOLD:.0f}s.")

    if is_watchdog_healthy(heartbeat_dir, args.config_name):
        Logger().info("Watchdog healthy.")
    else:
        recover_watchdog(heartbeat_dir, args.config_name)
