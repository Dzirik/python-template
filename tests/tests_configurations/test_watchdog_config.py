"""
Tests for Watchdog Config module.
"""

import pytest

from src.configurations.watchdog_config import WatchdogConfig
from src.configurations.watchdog_config_data import WatchdogConfigData


@pytest.mark.parametrize(
    "config_file_name",
    [
        "watchdog_cmd_01",
        "watchdog_cmd_02",
    ],
)
def test_watchdog_config_get_data_returns_expected_name(config_file_name: str) -> None:
    """
    Tests that WatchdogConfig loads the top-level configurations/<name>.toml file and that the returned
    WatchdogConfigData carries the expected name.
    :param config_file_name: str. Name of the watchdog config file, without the .toml extension.
    """
    config_data = WatchdogConfig(config_file_name).get_data()

    assert isinstance(config_data, WatchdogConfigData)
    assert config_data.name == config_file_name


@pytest.mark.parametrize(
    "config_file_name",
    [
        "watchdog_cmd_01",
        "watchdog_cmd_02",
    ],
)
def test_watchdog_config_get_data_returns_non_empty_workers(config_file_name: str) -> None:
    """
    Tests that WatchdogConfig loads a non-empty list of workers for each existing watchdog profile.
    :param config_file_name: str. Name of the watchdog config file, without the .toml extension.
    """
    config_data = WatchdogConfig(config_file_name).get_data()

    assert len(config_data.workers) > 0


@pytest.mark.parametrize(
    "config_file_name",
    [
        "watchdog_cmd_01",
        "watchdog_cmd_02",
    ],
)
def test_watchdog_config_get_class_name_returns_watchdog_config(config_file_name: str) -> None:
    """
    Tests that WatchdogConfig registers its own class name (not a copy-pasted, unrelated identity) at the
    MonitoredBase seam used for unified monitoring/logging.
    :param config_file_name: str. Name of the watchdog config file, without the .toml extension.
    """
    assert WatchdogConfig(config_file_name).get_class_name() == "WatchdogConfig"
