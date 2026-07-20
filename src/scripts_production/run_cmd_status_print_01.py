"""
Test script 01
"""

import argparse
import os
import signal
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

sys.path += [str(Path.cwd() / ".."), str(Path.cwd() / "../..")]  # one and two up

from src.scripts_production.heartbeat import HealthcheckHeartbeat, HealthcheckHeartbeatConfig
from src.scripts_production.watchdog import resolve_ping_url, write_pid

_ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_ENV_PATH)

_STOP_EVENT = threading.Event()


def _handle_stop_signal(_signum: int, _frame: Any) -> None:
    """
    Handle the watchdog's graceful-stop signal by requesting a clean exit.

    This is the reference implementation of the stop contract described in ADR 0007: the
    watchdog sends ``CTRL_BREAK_EVENT`` (Windows, delivered here as ``SIGBREAK``) or
    ``SIGTERM`` (POSIX) and waits a grace window before falling back to a hard kill. Setting a
    flag (rather than raising or exiting directly from the handler) lets the main loop finish
    its current iteration, write a final heartbeat, and stop the healthcheck thread before
    exiting.

    :param _signum: int. Signal number received.
    :param _frame: Any. Current stack frame (unused).
    :return: None.
    """
    _STOP_EVENT.set()


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    :return: argparse.Namespace. Parsed arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker-name", required=True, type=str)
    parser.add_argument("--heartbeat-file", required=True, type=str)
    parser.add_argument("--heartbeat-folder", required=True, type=str)
    parser.add_argument("--delay", required=True, type=int)
    parser.add_argument("--healthcheck-url-key", required=True, type=str)
    parser.add_argument("--hello", required=True, type=str)
    parser.add_argument("--minute", required=True, type=int)
    return parser.parse_args()


def update_heartbeat(heartbeat_file: Path) -> None:
    """
    Update heartbeat file modification time.

    :param heartbeat_file: Path. Path to heartbeat file.
    :return: None.
    """
    heartbeat_file.parent.mkdir(parents=True, exist_ok=True)
    heartbeat_file.touch()


def main() -> None:
    """
    Main worker loop.

    :return: None.
    """
    if sys.platform == "win32":
        signal.signal(signal.SIGBREAK, _handle_stop_signal)
    else:
        signal.signal(signal.SIGTERM, _handle_stop_signal)

    args = parse_args()
    heartbeat_file = Path(args.heartbeat_file)
    write_pid(args.worker_name, Path(args.heartbeat_folder))

    ping_url = resolve_ping_url(args.healthcheck_url_key)
    hc_heartbeat = None

    if ping_url:
        hc_heartbeat = HealthcheckHeartbeat(
            HealthcheckHeartbeatConfig(
                name=args.worker_name,
                ping_url=ping_url,
                interval_seconds=args.delay * 60,
            )
        )
        hc_heartbeat.start()

    try:
        while not _STOP_EVENT.is_set():
            print(
                f"{datetime.now()}: Worker={args.worker_name} PID={os.getpid():06d} delay={args.delay} hello={args.hello}"
            )

            update_heartbeat(heartbeat_file)
            _STOP_EVENT.wait(args.delay * 60)
        print(f"{datetime.now()}: Worker={args.worker_name} received stop signal, shutting down cleanly.")
    finally:
        if hc_heartbeat is not None:
            hc_heartbeat.stop()


if __name__ == "__main__":
    main()
