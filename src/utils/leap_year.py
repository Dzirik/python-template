"""
Sample function for testing the make test commands.
"""


def is_leap(year: int) -> bool:
    """
    Tests if the year is leap.
    :param year: int. Year to be tested.
    :return: bool. If the year is leap.
    """
    if (year % 4) == 0:
        if (year % 100) == 0:
            return bool((year % 400) == 0)
        return True
    return False


if __name__ == "__main__":
    print(is_leap(2000))
