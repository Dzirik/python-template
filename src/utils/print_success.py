"""
Print colored success or error messages.
"""

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path += [str(_SCRIPT_DIR / ".."), str(_SCRIPT_DIR / "../..")]

from src.utils.helper_functions import print_in_color  # noqa: E402


def print_success(message: str) -> None:
    """
    Prints a success message in bold green.
    :param message: str. Message to print.
    """
    print_in_color(message, color="green", attrs=["bold"])


def print_error(message: str) -> None:
    """
    Prints an error message in bold red.
    :param message: str. Message to print.
    """
    print_in_color(message, color="red", attrs=["bold"])


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python print_success.py <success|error> <message>")
        sys.exit(1)

    msg_type = sys.argv[1]
    message = sys.argv[2]

    if msg_type == "success":
        print_success(message)
    elif msg_type == "error":
        print_error(message)
    else:
        print(f"Unknown message type: {msg_type}")
        sys.exit(1)
