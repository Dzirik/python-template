r"""
Supervisor script that monitors the watchdog process and performs recovery if it hangs.

Supervision hierarchy:
    Windows Task Scheduler -> checker.py -> watchdog.py -> Worker Processes

(.venv) PS D:\...\src\scripts> python checker.py --config-name=watchdog_cmd_01
(.venv) PS D:\...\src\scripts> python checker.py --config-name=watchdog_cmd_02
"""

import argparse
import logging
import os
import re

# Bandit B404: subprocess is required for controlled Windows process management.
import subprocess  # nosec B404
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR.parent.parent / "logs"

sys.path += [str(BASE_DIR / ".."), str(BASE_DIR / "../..")]

from src.configurations.watchdog_config import WatchdogConfig  # noqa: E402
from src.utils.logger import Logger  # noqa: E402

SCHEDULER_INTERVAL = 30.0
HEARTBEAT_THRESHOLD = (SCHEDULER_INTERVAL * 2) * 1.5
CONFIG_NAME_PATTERN = re.compile(r"[A-Za-z0-9_-]+")
SYSTEM_ROOT = Path(os.environ.get("SYSTEMROOT", r"C:\\Windows"))
SYSTEM32_DIR = SYSTEM_ROOT / "System32"
TASKLIST_EXE = str((SYSTEM32_DIR / "tasklist.exe").resolve())
TASKKILL_EXE = str((SYSTEM32_DIR / "taskkill.exe").resolve())
POWERSHELL_EXE = str((SYSTEM32_DIR / "WindowsPowerShell" / "v1.0" / "powershell.exe").resolve())


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
    if CONFIG_NAME_PATTERN.fullmatch(args.config_name) is None:
        parser.error("--config-name must contain only letters, numbers, '_' or '-'.")
    return args


def is_process_alive(pid: int) -> bool:
    """
    Check whether a process with the given PID is currently running (Windows).

    **Why not ``os.kill(pid, 0)``?**
    On Windows, ``os.kill`` calls ``OpenProcess`` which can fail with
    ``PermissionError`` (ERROR_ACCESS_DENIED) **or** ``OSError``
    [WinError 87] (ERROR_INVALID_PARAMETER) for processes spawned by
    ``WmiPrvSE.exe`` in a different session.  The latter is
    indistinguishable from "process does not exist" in Python's
    exception hierarchy, so ``os.kill`` cannot reliably detect
    cross-session WMI-spawned processes.

    This implementation uses ``tasklist /FI "PID eq {pid}" /NH`` which
    queries the Windows kernel process table directly and works
    regardless of session boundaries or security context.

    :param pid: int. Process ID to check.
    :return: bool. True if process is alive, False otherwise.
    """
    try:
        result = subprocess.run(  # noqa: S603  # nosec B603
            [TASKLIST_EXE, "/FI", f"PID eq {pid}", "/NH"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        # When a matching process exists, tasklist prints a line like:
        #   python.exe                39904 Console                    3     98,948 K
        # When no process matches, it prints:
        #   INFO: No tasks are running which match the specified criteria.
        # We check for the PID as a substring in the output.
        return str(pid) in result.stdout
    except Exception:
        # Timeout or other failure — assume not alive to be safe.
        return False


def _get_process_cmdline(pid: int) -> str | None:
    """
    Retrieve the command line of a running process via PowerShell CIM.

    Uses ``Get-CimInstance Win32_Process`` which, unlike the deprecated
    ``wmic.exe``, works reliably across session boundaries and security
    contexts (e.g. processes spawned by ``WmiPrvSE.exe``).

    :param pid: int. Process ID to query.
    :return: str | None. The command line string, or None if the process
        does not exist or the query fails.
    """
    ps_cmd = f'Get-CimInstance Win32_Process -Filter "ProcessId={pid}" | Select-Object -ExpandProperty CommandLine'
    try:
        result = subprocess.run(  # noqa: S603  # nosec B603
            [POWERSHELL_EXE, "-NoProfile", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if result.returncode != 0:
            return None
        cmdline = result.stdout.strip()
        return cmdline or None
    except Exception:
        return None


def read_pid(pid_file: Path) -> int | None:
    """
    Read a PID from a .pid file.

    :param pid_file: Path. Path to the .pid file.
    :return: int | None. The PID, or None if the file is missing or invalid.
    """
    if not pid_file.exists():
        return None
    try:
        pid = int(pid_file.read_text(encoding="utf-8").strip())
        return pid if pid > 0 else None
    except (ValueError, OSError):
        return None


def is_watchdog_healthy(heartbeat_dir: Path, config_name: str) -> bool:
    """
    Determine whether the watchdog process is healthy.

    The check requires **all three** conditions to be met:

    1. ``watchdog.pid`` exists and contains a valid PID.
    2. That PID belongs to a live process (``is_process_alive``).
    3. ``watchdog.hb`` exists and was updated within
       ``HEARTBEAT_THRESHOLD`` seconds.

    Command-line verification (``is_watchdog_process``) is used as a
    secondary guard against PID recycling, but a fresh heartbeat
    combined with a live PID is accepted even when the command-line
    query fails (cross-session / WMI access issues).

    :param heartbeat_dir: Path. Heartbeat directory for this config.
    :param config_name: str. Expected ``--config-name`` value.
    :return: bool. True if the watchdog is healthy.
    """
    pid_file = heartbeat_dir / "watchdog.pid"
    hb_file = heartbeat_dir / "watchdog.hb"

    # --- PID file ---
    pid = read_pid(pid_file)
    if pid is None:
        Logger().warning("Watchdog unhealthy: watchdog.pid missing or invalid.")
        return False

    # --- Basic process liveness ---
    if not is_process_alive(pid):
        Logger().warning(f"Watchdog unhealthy: PID {pid} is not running.")
        return False

    # --- Heartbeat freshness ---
    if not hb_file.exists():
        Logger().warning("Watchdog unhealthy: watchdog.hb missing.")
        return False

    age = time.time() - hb_file.stat().st_mtime
    if age > HEARTBEAT_THRESHOLD:
        Logger().warning(f"Watchdog unhealthy: heartbeat stale ({age:.0f}s old, threshold {HEARTBEAT_THRESHOLD:.0f}s).")
        return False

    # --- Command-line identity check (PID recycling guard) ---
    # Windows paths are case-insensitive and WMI/CMD may alter casing
    # or quoting.  Normalise to lower-case for reliable substring matching.
    cmdline = _get_process_cmdline(pid)
    if cmdline is not None:
        cmdline_lower = cmdline.lower()
        if "watchdog.py" not in cmdline_lower:
            unhealthy_reason = f"PID {pid} is not a watchdog process (cmdline: {cmdline!r})"
        elif config_name.lower() not in cmdline_lower:
            unhealthy_reason = f"PID {pid} is a watchdog for a different config (cmdline: {cmdline!r})"
        else:
            unhealthy_reason = None
        if unhealthy_reason is not None:
            Logger().warning(f"Watchdog unhealthy: {unhealthy_reason}.")
            return False
    else:
        # CIM query failed — process is alive and heartbeat is fresh,
        # so we accept it to avoid false-positive recovery.
        Logger().info(f"CIM command-line query unavailable for PID {pid}; heartbeat fresh — accepting as healthy.")

    return True


def kill_process(pid: int) -> None:
    """
    Force-terminate a process and its children via taskkill (Windows).

    :param pid: int. Process ID to kill.
    :return: None.
    """
    subprocess.run(  # noqa: S603  # nosec B603
        [TASKKILL_EXE, "/PID", str(pid), "/T", "/F"],
        capture_output=True,
        check=False,
    )


def _spawn_via_wmi(config_name: str) -> None:
    """
    Start the watchdog process via WMI ``Win32_Process.Create``.

    **Why not subprocess.Popen?**
    When Task Scheduler runs ``checker.py``, it wraps the process in a
    Windows Job Object.  Every child created with ``subprocess.Popen``
    inherits that Job Object.  When the task completes (``checker.py``
    exits), Task Scheduler kills the entire Job Object — including the
    newly spawned watchdog.

    ``CREATE_BREAKAWAY_FROM_JOB`` does **not** solve this because the
    Task Scheduler Job Object does not set
    ``JOB_OBJECT_LIMIT_BREAKAWAY_OK``; the flag is silently ignored.

    **Solution:** Use ``Invoke-CimMethod`` to ask ``WmiPrvSE.exe`` to
    create the process on our behalf.  Because ``WmiPrvSE.exe`` is not
    part of the Task Scheduler Job Object, the new process is completely
    independent.

    The Python command is wrapped inside ``cmd.exe /c`` with
    ``>> logfile 2>&1`` I/O redirection.  ``cmd.exe`` handles console
    allocation correctly and redirects Python's stdout/stderr to a real
    file, providing valid handles regardless of the parent's window
    station.

    :param config_name: str. Configuration name to pass to watchdog.py.
    :return: None.
    :raises RuntimeError: If WMI process creation fails.
    """
    if CONFIG_NAME_PATTERN.fullmatch(config_name) is None:
        raise ValueError("config_name must contain only letters, numbers, '_' or '-'.")

    python_exe = str(Path(sys.executable).resolve())
    watchdog_script = str((BASE_DIR / "watchdog.py").resolve())
    cwd = str(BASE_DIR.resolve())

    # Ensure the logs directory exists for the redirected output.
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    wmi_log = str((LOGS_DIR / f"watchdog_{config_name}_wmi.log").resolve())

    # Wrap in cmd.exe /c with I/O redirection so that the Python
    # process has valid stdout/stderr handles (the log file).
    inner = f'"{python_exe}" -u "{watchdog_script}" --config-name {config_name} >> "{wmi_log}" 2>&1'
    cmd_value = f'cmd.exe /c "{inner}"'

    # Escape single quotes for PowerShell single-quoted string literals.
    ps_q = str.maketrans({"'": "''"})

    ps_script = (
        "$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create "
        "-Arguments @{"
        f"CommandLine='{cmd_value.translate(ps_q)}';"
        f"CurrentDirectory='{cwd.translate(ps_q)}'"
        "}; "
        "if ($r.ReturnValue -ne 0) { "
        'throw "Win32_Process.Create failed: ReturnValue=$($r.ReturnValue)" '
        "} "
        "Write-Output $r.ProcessId"
    )

    Logger().info(f"WMI spawn command: {cmd_value}")

    result = subprocess.run(  # noqa: S603  # nosec B603
        [POWERSHELL_EXE, "-NoProfile", "-Command", ps_script],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(f"WMI process creation failed (rc={result.returncode}): {stderr}")

    wmi_pid = result.stdout.strip()
    Logger().info(f"WMI spawned cmd.exe wrapper with PID {wmi_pid}.")


def recover_watchdog(heartbeat_dir: Path, config_name: str) -> None:
    """
    Perform a full recovery: kill the watchdog tree, clean up zombie workers,
    and restart the watchdog via WMI.

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

    # Step 4: Restart watchdog via WMI so it is NOT part of the Task
    # Scheduler Job Object (see _spawn_via_wmi docstring for details).
    Logger().info(f"Starting new watchdog instance with config '{config_name}'...")
    _spawn_via_wmi(config_name)
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
