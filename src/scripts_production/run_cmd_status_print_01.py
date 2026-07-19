"""
Test script 01
"""

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

sys.path += [str(Path.cwd() / ".."), str(Path.cwd() / "../..")]  # one and two up

from src.scripts_production.heartbeat import HealthcheckHeartbeat, HealthcheckHeartbeatConfig
from src.scripts_production.watchdog import resolve_ping_url, write_pid

_ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_ENV_PATH)


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
        while True:
            print(
                f"{datetime.now()}: Worker={args.worker_name} PID={os.getpid():06d} delay={args.delay} hello={args.hello}"
            )

            update_heartbeat(heartbeat_file)
            time.sleep(args.delay * 60)
    finally:
        if hc_heartbeat is not None:
            hc_heartbeat.stop()


if __name__ == "__main__":
    main()
