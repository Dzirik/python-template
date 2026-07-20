"""
Watchdog configuration file.
"""

from src.configurations.watchdog_config_data import WatchdogConfigData
from src.utils.base_component_config import BaseComponentConfig


class WatchdogConfig(BaseComponentConfig[WatchdogConfigData]):
    """
    Configures the watchdog process supervisor from a TOML file under configurations/watchdogs/.
    """

    def __init__(self, config_file_name: str) -> None:
        """
        :param config_file_name: str. Name of the file in configuration folder without that .toml part.
        """
        BaseComponentConfig.__init__(
            self,
            class_name="WatchdogConfig",
            config_file_name=config_file_name,
            data_structure=WatchdogConfigData,
            config_subfolder="watchdogs",
        )


if __name__ == "__main__":
    CONFIG_FILE_NAME = "watchdog_cmd_01"

    config_data = WatchdogConfig(CONFIG_FILE_NAME).get_data()

    print("\n")
    print(config_data.name)
    print("\n")
    print(config_data.workers[0])
