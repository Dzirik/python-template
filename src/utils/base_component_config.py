"""
Class for general interface for configs.
"""

from typing import Any, Protocol

from src.utils.config_loader import load_config
from src.utils.monitored_base import CONFIG_TYPE_NAME, MonitoredBase


class _NamedTupleLike(Protocol):
    """Structural protocol satisfied by every NamedTuple (has _asdict)."""

    def _asdict(self) -> dict[str, Any]: ...


class BaseComponentConfig[T: _NamedTupleLike](MonitoredBase):
    """
    Parent class for general interface for configs.

    Only src/utils/application_config is different, but interface is the same.
    """

    def __init__(
        self, class_name: str, config_file_name: str, data_structure: type[T], config_subfolder: str | None = None
    ) -> None:
        MonitoredBase.__init__(self, class_type=CONFIG_TYPE_NAME, class_name=class_name)

        self._config_file_name = config_file_name
        self._data_structure: type[T] = data_structure
        self._config_subfolder = config_subfolder
        self._data: T

        self.parse_config()

    def parse_config(self) -> None:
        """
        Parses the config.
        """
        if self._config_file_name == "":
            raise FileNotFoundError("Empty string as config file name - PLEASE FILL IN THE NAME.")

        self._data = load_config(self._config_file_name, self._data_structure, subfolder=self._config_subfolder)

    def get_data(self) -> T:
        """
        Returns the config's named tuple.
        :return: T. Named tuple with data.
        """
        return self._data

    def get_data_as_dict(self) -> dict[Any, Any]:
        """
        Gets the data (named tuple) into dictionary.
        :return: Dict[Any, Any].
        """
        return dict(self._data._asdict())
