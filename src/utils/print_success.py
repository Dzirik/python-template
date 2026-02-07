"""
Print colored success or error messages.
"""

import sys


def print_success(message: str) -> None:
    """
    Print a success message in green.
    :param message: str. Message to print.
    """
    # ANSI color codes: \033[1;92m = bold green, \033[0m = reset
    print(f"\033[1;92m{message}\033[0m")


def print_error(message: str) -> None:
    """
    Print an error message in red.
    :param message: str. Message to print.
    """
    # ANSI color codes: \033[1;91m = bold red, \033[0m = reset
    print(f"\033[1;91m{message}\033[0m")


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
