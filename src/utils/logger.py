"""
Code for logging.

A singleton pattern is used for that.
"""

import logging.config
import platform
import tomllib
from datetime import datetime
from pathlib import Path
from time import sleep

from src.utils.envs import Envs
from src.utils.helper_functions import get_git_branch, print_in_color
from src.utils.project_paths import ProjectPaths
from src.utils.singleton_meta import Singleton
from src.utils.timer import Timer

# Error-path fallback log destination used when the selected logger profile file is missing.
SPECIAL_LOGGER_FILE_NAME = "logger_file_limit_console.log"


class Logger(metaclass=Singleton):
    """
    Class for logging. Extends the functionality of standard logger with:
    - Possibility of setting different logger configurations from the config file based on the value of
      environment variable.
    - Allows add time measurements from the timer.
    """

    _logger: logging.Logger

    def __init__(self) -> None:
        self._env = Envs()
        self._timer = Timer()
        self._process_name: str

        profile_file_path = ProjectPaths().config_file(self._env.get_logger(), subfolder="loggers", extension=".toml")

        if not profile_file_path.exists():
            self._log_bad_file()
            raise ValueError("Logger profile does not exist in the selected path.")

        self._load_profile(profile_file_path)

        self._logger = logging.getLogger(self._env.get_logger().replace("logger_", ""))

        branch_name = get_git_branch()
        self._logger.info("Logger was created on %s in branch %s.", platform.node(), branch_name)

    @staticmethod
    def _load_profile(profile_file_path: Path) -> None:
        """
        Loads profile_file_path via logging.config.dictConfig.

        The shipped ``.toml`` files carry file handler paths relative to the process current working directory
        (e.g. ``"logs/python_log.log"``), which may not exist for a CWD other than the one the profile was
        authored against. Before the parsed document is handed to ``dictConfig``, every handler carrying a
        ``filename`` key is rewritten in place to keep its basename but force the containing directory onto
        :class:`ProjectPaths`, whose ``__init__`` already ``mkdir``s the logs folder - so the file always opens
        into an existing directory regardless of CWD.
        :param profile_file_path: Path. Absolute path to the logger .toml file to load.
        """
        with profile_file_path.open("rb") as profile_file:
            config = tomllib.load(profile_file)

        logs_folder = ProjectPaths().logs
        for handler in config.get("handlers", {}).values():
            if "filename" in handler:
                handler["filename"] = str(logs_folder / Path(handler["filename"]).name)

        logging.config.dictConfig(config)

    @staticmethod
    def _log_bad_file() -> None:
        """
        Logs the problem with logger config file reading.
        """
        logger = logging.getLogger("error_logger_class")
        file_handler = logging.FileHandler(str(ProjectPaths().logs / SPECIAL_LOGGER_FILE_NAME))
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
        logger.error("Logger profile does not exist in the selected path.")

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
        """
        _, _, duration_s, duration_m = self._timer.get_end("Process ended")
        self._logger.info(
            "Process: %s; Timer ended; Process Duration [s]: %s; Process Duration [m]: %s",
            self._process_name,
            duration_s,
            duration_m,
        )
        self._process_name = ""

    def debug(
        self, message: str, color: str | None = None, on_color: str | None = None, attrs: list[str] | None = None
    ) -> None:
        """
        Creates debug message.
        :param message: str. Log message.
        :param color: str | None. Text color for the optional console echo; when None no echo is printed. Default None.
        :param on_color: str | None. Background color for the optional console echo. Default None.
        :param attrs: list[str] | None. Text attributes for the optional console echo. Default None.
        """
        self._logger.debug(message)
        self._echo(message, color, on_color, attrs)

    def info(
        self, message: str, color: str | None = None, on_color: str | None = None, attrs: list[str] | None = None
    ) -> None:
        """
        Creates info message.
        :param message: str. Log message.
        :param color: str | None. Text color for the optional console echo; when None no echo is printed. Default None.
        :param on_color: str | None. Background color for the optional console echo. Default None.
        :param attrs: list[str] | None. Text attributes for the optional console echo. Default None.
        """
        self._logger.info(message)
        self._echo(message, color, on_color, attrs)

    def warning(
        self, message: str, color: str | None = None, on_color: str | None = None, attrs: list[str] | None = None
    ) -> None:
        """
        Creates warning message.
        :param message: str. Log message.
        :param color: str | None. Text color for the optional console echo; when None no echo is printed. Default None.
        :param on_color: str | None. Background color for the optional console echo. Default None.
        :param attrs: list[str] | None. Text attributes for the optional console echo. Default None.
        """
        self._logger.warning(message)
        self._echo(message, color, on_color, attrs)

    def error(
        self, message: str, color: str | None = None, on_color: str | None = None, attrs: list[str] | None = None
    ) -> None:
        """
        Creates error message.
        :param message: str. Log message.
        :param color: str | None. Text color for the optional console echo; when None no echo is printed. Default None.
        :param on_color: str | None. Background color for the optional console echo. Default None.
        :param attrs: list[str] | None. Text attributes for the optional console echo. Default None.
        """
        self._logger.error(message)
        self._echo(message, color, on_color, attrs)

    def exception(
        self, message: str, color: str | None = None, on_color: str | None = None, attrs: list[str] | None = None
    ) -> None:
        """
        Creates an error message together with the traceback of the exception currently being handled.

        Mirrors error(), but delegates to the stdlib logger's exception() method (implying exc_info=True), so it
        should be called from within an except block to capture a real traceback.
        :param message: str. Log message.
        :param color: str | None. Text color for the optional console echo; when None no echo is printed. Default None.
        :param on_color: str | None. Background color for the optional console echo. Default None.
        :param attrs: list[str] | None. Text attributes for the optional console echo. Default None.
        """
        self._logger.exception(message)
        self._echo(message, color, on_color, attrs)

    def critical(
        self, message: str, color: str | None = None, on_color: str | None = None, attrs: list[str] | None = None
    ) -> None:
        """
        Creates critical message.
        :param message: str. Log message.
        :param color: str | None. Text color for the optional console echo; when None no echo is printed. Default None.
        :param on_color: str | None. Background color for the optional console echo. Default None.
        :param attrs: list[str] | None. Text attributes for the optional console echo. Default None.
        """
        self._logger.critical(message)
        self._echo(message, color, on_color, attrs)

    @staticmethod
    def _echo(message: str, color: str | None, on_color: str | None, attrs: list[str] | None) -> None:
        """
        Prints a timestamp-prefixed colored copy of message to the console.

        The echo is emitted only when color is not None; otherwise the level method stays log-only. The timestamp
        prefix is built here (not in print_in_color), and the colored print is delegated to print_in_color.
        :param message: str. Message to echo.
        :param color: str | None. Text color; when None no echo is printed.
        :param on_color: str | None. Background color.
        :param attrs: list[str] | None. Text attributes.
        """
        if color is None:
            return
        stamped = f"{datetime.now().strftime('%y-%m-%d %H:%M:%S')}: {message}"
        print_in_color(stamped, color, on_color, attrs)

    def get(self) -> logging.Logger:
        """
        Gets the underlying stdlib logger instance.

        Used by callers that need stdlib-only functionality this wrapper does not expose (e.g. attaching a
        supplemental handler, or logging with ``exc_info=True``) - see ``src/scripts_production/watchdog.py`` and
        ``src/scripts_production/checker.py``.
        :return: logging.Logger. The underlying stdlib logger.
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

    try:
        raise ValueError("demo error")
    except ValueError:
        my_logger.exception("exception with traceback")

    # colored console echo demonstration
    my_logger.info("info with echo", color="green")

    # timer
    my_logger.start_timer("Simple timer test")
    sleep(0.1)
    my_logger.set_meantime("First interval")
    sleep(0.2)
    my_logger.set_meantime("Second interval")
    my_logger.end_timer()
