"""
Class for general interface for configs.
"""

from pathlib import Path
from typing import Any, Generic, Protocol, TypeVar

import typedload
from pyhocon import ConfigFactory

from src.constants.global_constants import FOLDER_CONFIGURATIONS
from src.utils.logger import Logger
from src.utils.meta_class import CONFIG_TYPE_NAME, MetaClass


class _NamedTupleLike(Protocol):
    """Structural protocol satisfied by every NamedTuple (has _asdict)."""

    def _asdict(self) -> dict[str, Any]: ...


_T = TypeVar("_T", bound=_NamedTupleLike)


class BaseConfig(MetaClass, Generic[_T]):
    """
    Parent class for general interface for configs.

    Only src/utils/config is different, but interface is the same.
    """

    def __init__(self, class_name: str, config_file_name: str, data_structure: type[_T]) -> None:
        MetaClass.__init__(self, class_type=CONFIG_TYPE_NAME, class_name=class_name)

        self._config_file_name = config_file_name
        self._data_structure: type[_T] = data_structure
        self._data: _T

        self.parse_config()

    def parse_config(self) -> None:
        """
        Parses the config.
        """
        if self._config_file_name == "":
            raise FileNotFoundError("Empty string as config file name - PLEASE FILL IN THE NAME.")

        config_file_path = Path("../../") / FOLDER_CONFIGURATIONS / f"{self._config_file_name}.conf"

        self._data = typedload.load(ConfigFactory.parse_file(str(config_file_path)), self._data_structure)

        Logger().debug(f"{self.get_class_name} was created from {self._config_file_name}.conf file.")

    def get_data(self) -> _T:
        """
        Returns the config's named tuple.
        :return: _T. Named tuple with data.
        """
        return self._data

    def get_data_as_dict(self) -> dict[Any, Any]:
        """
        Gets the data (named tuple) into dictionary.
        :return: Dict[Any, Any].
        """
        return dict(self._data._asdict())
