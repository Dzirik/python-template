"""
Tests
"""

import pytest

from src.utils.leap_year import is_leap


def test_standard_leap_year() -> None:
    """
    Tests standard leap year.
    """
    assert is_leap(1996)


def test_non_standard_leap_year() -> None:
    """
    Tests non standard leap year.
    """
    assert is_leap(2000)


@pytest.mark.parametrize("year", [1997, 2001, 1867])
def test_non_leap_year(year: int) -> None:
    """
    Tests normal, non leap year.
    """
    assert not is_leap(year)


def test_non_standard_non_leap_year() -> None:
    """
    Tests non standard not leap year.
    """
    assert not is_leap(1900)
