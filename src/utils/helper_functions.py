"""
Supporting functions for trades.

Console colouring is provided by termcolor; see print_in_color in this module.

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

from termcolor import colored


def print_in_color(
    message: str, color: str | None = None, on_color: str | None = None, attrs: list[str] | None = None
) -> None:
    """
    Prints the message and optionally change a colour.
    :param message: str. Message.
    :param color: str. Termcolor color string. See the termcolor docs at the top of this module for more information.
    :param on_color: str. Termcolor color string. See the termcolor docs at the top of this module for more
                          information.
    :param attrs: Optional[List[str]] = None. Termcolor color strings. See the termcolor docs at the top of this
                                              module for more information.
    """
    if color is not None:
        # pylint: disable=bare-except
        try:
            print(colored(message, color, on_color, attrs))
        except Exception:
            print(message)
        # pylint: enable=bare-except
    else:
        print(message)
