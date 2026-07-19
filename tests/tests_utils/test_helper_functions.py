"""
Tests for helper functions.
"""

import pytest

from src.utils.helper_functions import print_in_color


def test_print_in_color_plain_message(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Tests that a message without a colour is printed to stdout verbatim.
    """
    print_in_color("plain message")
    captured = capsys.readouterr()
    assert captured.out == "plain message\n"


def test_print_in_color_valid_color(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Tests that passing a valid colour still prints the message text to stdout.
    """
    print_in_color("green message", color="green")
    captured = capsys.readouterr()
    assert "green message" in captured.out


def test_print_in_color_bad_color_falls_back(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Tests that an unsupported colour falls back to a plain print and does not raise.
    """
    print_in_color("fallback message", color="not_a_real_color")
    captured = capsys.readouterr()
    assert "fallback message" in captured.out


def test_print_in_color_color_none_plain_prints(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Tests that an explicit None colour plain-prints the message verbatim.
    """
    print_in_color("none color message", color=None)
    captured = capsys.readouterr()
    assert captured.out == "none color message\n"
