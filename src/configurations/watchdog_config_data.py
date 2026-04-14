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


class WatchdogConfigData(NamedTuple):
    """
    For storing parameters of watchdog config.
    """

    name: str
    healthcheck_url_key: str = ""
    workers: list[WorkerData] = []  # noqa: RUF012
