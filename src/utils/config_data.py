"""
Data structure for config.
"""

from typing import NamedTuple


class Path(NamedTuple):
    """
    Configuration tuple for paths to data files.
    """

    data: str


class ConfigData(NamedTuple):
    """
    Overall configuration tuple for everything.
    """

    name: str
    path: Path
