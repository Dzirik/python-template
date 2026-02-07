"""
Tests
"""

from datetime import datetime

import pytest

from src.utils.date_time_functions import (
    add_zeros_in_front_and_convert_to_string,
    convert_datetime_to_string_date,
    convert_string_date_to_datetime,
)

DATES_DATETIME = [
    datetime(2000, 1, 1, 1, 1, 1),
    datetime(1990, 9, 16, 12, 59, 59),
    datetime(2005, 12, 12, 23, 59, 59),
    datetime(2013, 1, 2, 3, 4, 5),
]
DATES_STRING = ["2000-01-01-01-01-01", "1990-09-16-12-59-59", "2005-12-12-23-59-59", "2013-01-02-03-04-05"]
ADD_ZEROS_TEST_CASES = [(1, 10, "1"), (10, 10, "0"), (5, 100, "05"), (1, 1000, "001"), (18, 10, "8")]


@pytest.mark.parametrize("date_datetime, date_string_right", zip(DATES_DATETIME, DATES_STRING, strict=True))
def test_datetime_to_string_conversion(date_datetime: datetime, date_string_right: str) -> None:
    """
    Tests datetime to string conversion.
    :param date_datetime: datetime.
    :param date_string_right: str.
    """
    date_string = convert_datetime_to_string_date(date_datetime)
    assert date_string == date_string_right


@pytest.mark.parametrize("date_string, date_datetime_right", zip(DATES_STRING, DATES_DATETIME, strict=True))
def test_convert_string_date_to_datetime(date_string: str, date_datetime_right: datetime) -> None:
    """
    Tests string to datetime conversion.
    :param date_string: str.
    :param date_datetime_right: datetime.
    """
    date_datetime = convert_string_date_to_datetime(date_string)
    assert date_datetime == date_datetime_right


@pytest.mark.parametrize("number, order, str_right", ADD_ZEROS_TEST_CASES)
def test_add_zeros_function(number: int, order: int, str_right: str) -> None:
    """
    Tests adding zeros in front of the number, and return without the first digit.
    Usage: number=5, order=100 -> "05"
    :param number: int.
    :param order: int.
    :return: str.
    """
    assert add_zeros_in_front_and_convert_to_string(number, order) == str_right
