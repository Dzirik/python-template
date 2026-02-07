"""
Code for logging.

A singleton pattern is used for that.
"""

import logging.config
import platform
from pathlib import Path
from time import sleep
from typing import Any

import git

from src.constants.global_constants import FOLDER_CONFIGURATIONS, SPECIAL_LOGGER_FILE_NAME
from src.utils.envs import Envs
from src.utils.singleton_meta import Singleton
from src.utils.timer import Timer


class Logger(metaclass=Singleton):
    """
    Class for logging. Extends the functionality of standard logger with:
    - Possibility of setting different logger configurations from the config file based on the value of
      environment variable.
    - Allows add time measurements from the timerer.
    """

    _is_logger = False
    _logger: Any

    def __init__(self) -> None:
        self._env = Envs()
        self._timer = Timer()
        self._process_name: str

        if not self._is_logger:
            profile_file_name = f"{self._env.get_logger()}.conf"
            # Try relative path from src/utils directory
            profile_file_path = Path(__file__).parent.parent.parent / FOLDER_CONFIGURATIONS / profile_file_name

            if not profile_file_path.exists():
                # Try from current working directory
                profile_file_path = Path.cwd() / FOLDER_CONFIGURATIONS / profile_file_name

                if not profile_file_path.exists():
                    self._log_bad_file()
                    raise ValueError("Logger profile does not exit in the selected path.")

            logging.config.fileConfig(fname=str(profile_file_path), disable_existing_loggers=False)

            self._logger = logging.getLogger(self._env.get_logger().replace("logger_", ""))
            self._is_logger = True

            try:
                branch_name = str(git.Repo(search_parent_directories=True).active_branch.name)
            except (git.exc.InvalidGitRepositoryError, git.exc.GitCommandError, TypeError):
                branch_name = "ERROR"
            self._logger.info("Logger was created on %s in branche %s.", platform.node(), branch_name)

    @staticmethod
    def _log_bad_file() -> None:
        """
        Logs the problem with logger config file reading.
        """
        logger = logging.getLogger("error_logger_class")
        file_handler = logging.FileHandler(SPECIAL_LOGGER_FILE_NAME)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
        logger.error("Logger profile does not exit in the selected path.")

    def start_timer(self, process_name: str) -> None:
        """
        Starts the timer.
        :param process_name: str. Process name to measure the time for.
        """
        self._process_name = process_name
        self._timer.set_results_printing(False)
        self._timer.start()
        self._logger.info("Process: %s; Timer started;", self._process_name)

    def set_meantime(self, message: str) -> None:
        """
        Adds meantime.
        :param message: str. Log message.
        """
        diff_s, diff_m = self._timer.get_meantime(message)
        self._logger.info(
            "Process: %s; Timer meantime; Meantime of: %s; Duration [s]: %s; Duration [m]: %s",
            self._process_name,
            message,
            diff_s,
            diff_m,
        )

    def end_timer(self) -> None:
        """
        Ends the timer.
        :param message: str. Log message.
        """
        _, _, duration_s, duration_m = self._timer.get_end("Process ended")
        self._logger.info(
            "Process: %s; Timer ended; Process Duration [s]: %s; Process Duration [m]: %s",
            self._process_name,
            duration_s,
            duration_m,
        )
        self._process_name = ""

    def debug(self, message: str) -> None:
        """
        Creates debug message.
        :param message: str. Log message.
        """
        self._logger.debug(message)

    def info(self, message: str) -> None:
        """
        Creates info message.
        :param message: str. Log message.
        """
        self._logger.info(message)

    def warning(self, message: str) -> None:
        """
        Creates warning message.
        :param message: str. Log message.
        """
        self._logger.warning(message)

    def error(self, message: str) -> None:
        """
        Creates error message.
        :param message: str. Log message.
        """
        self._logger.error(message)

    def critical(self, message: str) -> None:
        """
        Creates critical message.
        :param message: str. Log message.
        """
        self._logger.critical(message)

    def get(self) -> Any:
        """
        Gets the profile as Profile NamedTuple class.
        :return: Profile. NamedTuple containing settings.
        """
        return self._logger


if __name__ == "__main__":
    # change this variable if you want to test default
    USE_DEFAULT = True
    NON_DEFAULT_LOGGER_CONFIG_NAME = "logger_console"

    if not USE_DEFAULT:
        env = Envs()
        env.set_logger(NON_DEFAULT_LOGGER_CONFIG_NAME)

    logger_1 = Logger()
    logger_2 = Logger()
    my_logger = Logger()

    print("\n")
    print(f"Is it just one object? {logger_1 is logger_2}")

    print("\n")
    my_logger.debug("debug")
    my_logger.info("info")
    my_logger.warning("warning")
    my_logger.error("error")
    my_logger.critical("error")

    # timer
    my_logger.start_timer("Simple timer test")
    sleep(0.1)
    my_logger.set_meantime("First interval")
    sleep(0.2)
    my_logger.set_meantime("Second interval")
    my_logger.end_timer()
