"""
Supporting functions used across the project.

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

import re
from pathlib import Path

from termcolor import colored

# Fallback branch name returned by get_git_branch() when no branch can be determined.
UNKNOWN_BRANCH_NAME = "unknown"


def _find_dot_git(start: Path) -> Path | None:
    """
    Walks up from start to find the first parent directory (including itself) containing a .git entry.
    :param start: Path. Directory to start the upward search from.
    :return: Path | None. The .git path if found, otherwise None.
    """
    for candidate in (start, *start.parents):
        git_path = candidate / ".git"
        if git_path.exists():
            return git_path
    return None


def get_git_branch() -> str:
    """
    Returns the active git branch name, read directly from .git/HEAD using the standard library only.

    Walks up from this module's own source file location to find the first parent directory containing a
    ``.git`` directory, then parses its ``HEAD`` file for a line of the form ``ref: refs/heads/<branch>``. Falls
    back to "unknown" on a detached HEAD, a missing/unreadable ``.git`` directory, or any parsing error - this
    function must never raise.
    :return: str. The active branch name, or "unknown" if it cannot be determined.
    """
    try:
        git_path = _find_dot_git(Path(__file__).resolve().parent)
        if git_path is None or not git_path.is_dir():
            return UNKNOWN_BRANCH_NAME

        head_content = (git_path / "HEAD").read_text(encoding="utf-8").strip()
        match = re.match(r"^ref:\s*refs/heads/(.+)$", head_content)
        if match is None:
            return UNKNOWN_BRANCH_NAME

        return match.group(1)
    except OSError:
        return UNKNOWN_BRANCH_NAME


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
        try:
            print(colored(message, color, on_color, attrs))
        except Exception:
            print(message)
    else:
        print(message)
