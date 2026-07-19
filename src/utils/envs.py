"""
Simple wrapper for work with environmental variables within repository setting.

Usage can be found in logger and config files and in jupyter notebook
/notebooks/documentation/low_level_tools_documentation.py or
/docs/ low_level_tools_documentation.html.
"""

from os import environ
from pathlib import Path

from dotenv import load_dotenv

from src.constants.env_constants import (
    DEFAULT_CONFIG,
    DEFAULT_LOGGER,
    DEFAULT_RUNNING_UNIT_TESTS,
    ENV_CONFIG,
    ENV_HEALTHCHECK_PING_URL,
    ENV_LOGGER,
    ENV_PROJECT_ROOT,
    ENV_RUNNING_UNIT_TESTS,
)

# Load .env file if it exists
_env_path = Path(__file__).parent.parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)


class Envs:
    """
    Class for handling environmental variables for configuration.

    It tried to get one from environment, if it cannot get it, it uses the default configuration option.
    """

    def __init__(self) -> None:
        pass

    @staticmethod
    def set_config(value: str) -> None:
        """
        Sets the environmental variable for config singleton with value.
        :param value: str. Value to be set without .conf.
        """
        environ[ENV_CONFIG] = value

    @staticmethod
    def get_config() -> str:
        """
        Returns the value of environmental variable for config singleton or none.
        :return: Optional[str]. Value or none.
        """
        value = environ.get(ENV_CONFIG)
        if value is None:
            value = DEFAULT_CONFIG
        return value

    @staticmethod
    def set_logger(value: str) -> None:
        """
        Sets the environmental variable for logger singleton with value.
        :param value: str. Value to be set without .conf.
        """
        environ[ENV_LOGGER] = value

    @staticmethod
    def get_logger() -> str:
        """
        Returns the value of environmental variable for logger singleton or none.
        :return: Optional[str]. Value or none.
        """
        value = environ.get(ENV_LOGGER)
        if value is None:
            value = DEFAULT_LOGGER
        return value

    @staticmethod
    def set_running_unit_tests(value: bool = True) -> None:
        """
        Sets running unit tests.
        """
        environ[ENV_RUNNING_UNIT_TESTS] = str(value)

    @staticmethod
    def get_running_unit_tests() -> bool:
        """
        Returns if currently unit tests are running.
        :return: bool. If running or not
        """
        value = environ.get(ENV_RUNNING_UNIT_TESTS)
        if value is None:
            value = DEFAULT_RUNNING_UNIT_TESTS
        return value.lower() == "true"

    @staticmethod
    def set_project_root_override(value: str) -> None:
        """
        Sets the environmental variable overriding the computed project root with value.
        :param value: str. Absolute or relative path to use as the project root.
        """
        environ[ENV_PROJECT_ROOT] = value

    @staticmethod
    def get_project_root_override() -> str | None:
        """
        Returns the value of environmental variable overriding the computed project root or none.
        :return: Optional[str]. Value or none.
        """
        return environ.get(ENV_PROJECT_ROOT)

    @staticmethod
    def get_healthcheck_ping_url() -> str | None:
        """
        Returns the raw healthcheck ping URL configuration string or none.
        :return: Optional[str]. Raw JSON-formatted value or none. No default is applied.
        """
        return environ.get(ENV_HEALTHCHECK_PING_URL)
