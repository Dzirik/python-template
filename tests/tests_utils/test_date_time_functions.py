"""
Tests
"""

import re
from datetime import datetime

import pytest

from src.utils.date_time_functions import (
    convert_datetime_to_string_date,
    convert_string_date_to_datetime,
    create_date_id,
    create_datetime_id,
)

DATES_DATETIME = [
    datetime(2000, 1, 1, 1, 1, 1),
    datetime(1990, 9, 16, 12, 59, 59),
    datetime(2005, 12, 12, 23, 59, 59),
    datetime(2013, 1, 2, 3, 4, 5),
]
DATES_STRING = ["2000-01-01-01-01-01", "1990-09-16-12-59-59", "2005-12-12-23-59-59", "2013-01-02-03-04-05"]
SEPARATORS = ["-", "_", "."]


@pytest.mark.parametrize("date_datetime, date_string_right", list(zip(DATES_DATETIME, DATES_STRING, strict=True)))
def test_datetime_to_string_conversion(date_datetime: datetime, date_string_right: str) -> None:
    """
    Tests datetime to string conversion, checking single-digit fields are zero-padded.
    :param date_datetime: datetime.
    :param date_string_right: str.
    """
    date_string = convert_datetime_to_string_date(date_datetime)
    assert date_string == date_string_right


@pytest.mark.parametrize("date_string, date_datetime_right", list(zip(DATES_STRING, DATES_DATETIME, strict=True)))
def test_convert_string_date_to_datetime(date_string: str, date_datetime_right: datetime) -> None:
    """
    Tests string to datetime conversion with the default separator.
    :param date_string: str.
    :param date_datetime_right: datetime.
    """
    date_datetime = convert_string_date_to_datetime(date_string)
    assert date_datetime == date_datetime_right


def test_convert_datetime_to_string_date_microseconds_are_six_digits() -> None:
    """
    Tests that the microseconds field is zero-padded to exactly six digits.
    """
    now = datetime(2024, 1, 2, 3, 4, 5, 7)
    date_string = convert_datetime_to_string_date(now, add_micro=True)
    micro_part = date_string.split("-")[-1]
    assert micro_part == "000007"
    assert len(micro_part) == 6


@pytest.mark.parametrize("sep", SEPARATORS)
def test_sep_is_honored_on_both_sides(sep: str) -> None:
    """
    Tests that a non-default separator is honored both when formatting and when parsing.
    :param sep: str.
    """
    now = datetime(2013, 1, 2, 3, 4, 5)
    date_string = convert_datetime_to_string_date(now, sep=sep)
    assert date_string == f"2013{sep}01{sep}02{sep}03{sep}04{sep}05"
    round_tripped = convert_string_date_to_datetime(date_string, sep=sep)
    assert round_tripped == now


@pytest.mark.parametrize("sep", SEPARATORS)
@pytest.mark.parametrize("now", DATES_DATETIME)
def test_round_trip_to_the_second(now: datetime, sep: str) -> None:
    """
    Tests that formatting then parsing round-trips a datetime to the second, for several separators.
    :param now: datetime.
    :param sep: str.
    """
    date_string = convert_datetime_to_string_date(now, add_micro=False, sep=sep)
    round_tripped = convert_string_date_to_datetime(date_string, sep=sep, add_micro=False)
    assert round_tripped == now.replace(microsecond=0)


@pytest.mark.parametrize("sep", SEPARATORS)
@pytest.mark.parametrize("now", DATES_DATETIME)
def test_round_trip_to_the_microsecond(now: datetime, sep: str) -> None:
    """
    Tests that formatting then parsing round-trips a datetime to the microsecond, when add_micro is True.
    :param now: datetime.
    :param sep: str.
    """
    now_with_micro = now.replace(microsecond=123456)
    date_string = convert_datetime_to_string_date(now_with_micro, add_micro=True, sep=sep)
    round_tripped = convert_string_date_to_datetime(date_string, sep=sep, add_micro=True)
    assert round_tripped == now_with_micro


def test_create_datetime_id_shape() -> None:
    """
    Tests that create_datetime_id produces yyyy-mm-dd-hh-mm-ss_xxx.
    """
    now = datetime(2013, 1, 2, 3, 4, 5)
    datetime_id = create_datetime_id(now)
    assert re.fullmatch(r"2013-01-02-03-04-05_\d{3}", datetime_id) is not None


def test_create_datetime_id_shape_with_micro() -> None:
    """
    Tests that create_datetime_id with add_micro produces yyyy-mm-dd-hh-mm-ss-micro_xxx.
    """
    now = datetime(2013, 1, 2, 3, 4, 5, 7)
    datetime_id = create_datetime_id(now, add_micro=True)
    assert re.fullmatch(r"2013-01-02-03-04-05-000007_\d{3}", datetime_id) is not None


def test_create_date_id_shape() -> None:
    """
    Tests that create_date_id produces yyyy-mm-dd_xxx.
    """
    now = datetime(2013, 1, 2, 3, 4, 5)
    date_id = create_date_id(now)
    assert re.fullmatch(r"2013-01-02_\d{3}", date_id) is not None
