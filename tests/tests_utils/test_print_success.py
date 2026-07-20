"""
Tests for print_success.
"""

import pytest

from src.utils.print_success import print_error, print_success


def test_print_success_prints_message(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Tests that print_success prints the given message text to stdout.
    """
    print_success("all good")
    captured = capsys.readouterr()
    assert "all good" in captured.out


def test_print_error_prints_message(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Tests that print_error prints the given message text to stdout.
    """
    print_error("something broke")
    captured = capsys.readouterr()
    assert "something broke" in captured.out
