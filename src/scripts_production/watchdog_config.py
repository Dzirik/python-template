"""
Pipelines configuration file.
"""

from src.scripts.watchdog_config_data import WatchdogConfigData
from src.utils.base_config import BaseConfig


class WatchdogConfig(BaseConfig):
    """
    Pipelines configuration file.
    """

    def __init__(self, config_file_name: str) -> None:
        """
        :param config_file_name: str. Name of the file in configuration folder without that .conf part.
        """
        BaseConfig.__init__(
            self,
            class_name="ColumnsGroupingPipelineConfig",
            config_file_name=config_file_name,
            data_structure=WatchdogConfigData,
        )


if __name__ == "__main__":
    CONFIG_FILE_NAME = "watchdog_cmd_01"

    config_data = WatchdogConfig(CONFIG_FILE_NAME).get_data()

    print("\n")
    print(config_data.name)
    print("\n")
    print(config_data.workers[0])
