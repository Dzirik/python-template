"""
Supporting functions for trades.

termcolor: https://pypi.org/project/termcolor/

Examples
--------
- https://pypi.org/project/termcolor/
- https://www.codegrepper.com/code-examples/python/python+color+text+on+windows
- https://www.programcreek.com/python/example/78943/termcolor.colored
properties:
- text colors:
  - grey
  - red
  - green
  - yellow
  - blue
  - magenta
  - cyan
  - white
- text highlights:
  - on_grey
  - on_red
  - on_green
  - on_yellow
  - on_blue
  - on_magenta
  - on_cyan
  - on_white
- attributes:
  - bold
  - dark
  - underline
  - blink
  - reverse
  - concealed
"""

from datetime import datetime
from os import system

from termcolor import colored

from src.utils.logger import Logger


def print_in_color(
    message: str, color: str | None = None, on_color: str | None = None, attrs: list[str] | None = None
) -> None:
    """
    Prints the message and optionally change a colour.
    :param message: str. Message.
    :param color: str. Termcolor color string. See src/utils/color_console_print.py for more information.
    :param on_color: str. Termcolor color string. See src/utils/color_console_print.py for more information.
    :param attrs: Optional[List[str]] = None. Termcolor color strings. See src/utils/color_console_print.py for
                                              more information.
    """
    if color is not None:
        # pylint: disable=bare-except
        try:
            system("color")  # noqa: S605, S607
            print(colored(message, color, on_color, attrs))
        except Exception:
            print(message)
        # pylint: enable=bare-except
    else:
        print(message)


def log_and_print(
    message: str,
    color: str | None = None,
    on_color: str | None = None,
    attrs: list[str] | None = None,
    log_only: bool = False,
) -> None:
    """
    Logs and print message.
    :param message: str. Message.
    :param color: str. Termcolor color string. See src/utils/color_console_print.py for more information.
    :param on_color: str. Termcolor color string. See src/utils/color_console_print.py for more information.
    :param attrs: Optional[List[str]] = None. Termcolor color strings. See src/utils/color_console_print.py for
                                              more information.
    :param log_only: bool. This is added because in some situations both options are needed, especially for debugging.
    """
    Logger().info(message)  # time is in the logger
    if not log_only:
        message = f"{datetime.now().strftime('%y-%m-%d %H:%M:%S')}: {message}"  # adding time for console print
        print_in_color(message, color, on_color, attrs)
