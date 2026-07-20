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
from src.utils.singleton_meta import Singleton

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

        Raises NotValidOperation if the ApplicationConfig singleton has already been instantiated - writing
        the variable at that point would be silently ignored by the cached instance (it never re-reads this
        variable), which is an ordering trap. Call Singleton.reset() first (test-only) to re-open the
        legitimate "before instantiation" window if a reset-then-reconfigure sequence is intended.

        ApplicationConfig, NotValidOperation and ExceptionExecutioner are imported lazily inside this method
        rather than at module level, because ApplicationConfig itself imports Envs - a module-level import
        here would create an import cycle.
        :param value: str. Value to be set without .conf.
        """
        from src.exceptions.development_exception import NotValidOperation  # noqa: PLC0415
        from src.exceptions.exception_executioner import ExceptionExecutioner  # noqa: PLC0415
        from src.utils.application_config import ApplicationConfig  # noqa: PLC0415

        if ApplicationConfig in Singleton._instances:
            ExceptionExecutioner(NotValidOperation).log_and_raise(
                "Envs.set_config() was called after ApplicationConfig was already instantiated - the new "
                "value would be silently ignored by the cached singleton. Call Singleton.reset() first if a "
                "reset-then-reconfigure sequence is intended (test-only)."
            )
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

        Raises NotValidOperation if the Logger singleton has already been instantiated, mirroring
        set_config's guard against the same silent-no-op ordering trap. Logger is imported lazily inside this
        method for the same reason ApplicationConfig is imported lazily in set_config: Logger imports Envs at
        module level, so a module-level import here would create an import cycle.
        :param value: str. Value to be set without .conf.
        """
        from src.exceptions.development_exception import NotValidOperation  # noqa: PLC0415
        from src.exceptions.exception_executioner import ExceptionExecutioner  # noqa: PLC0415
        from src.utils.logger import Logger  # noqa: PLC0415

        if Logger in Singleton._instances:
            ExceptionExecutioner(NotValidOperation).log_and_raise(
                "Envs.set_logger() was called after Logger was already instantiated - the new value would be "
                "silently ignored by the cached singleton. Call Singleton.reset() first if a "
                "reset-then-reconfigure sequence is intended (test-only)."
            )
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
