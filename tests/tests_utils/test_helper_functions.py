"""
Tests for helper functions.
"""

from pathlib import Path

import pytest

from src.utils import helper_functions
from src.utils.helper_functions import get_git_branch, print_in_color


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


def test_get_git_branch_parses_ref_head(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests that get_git_branch parses a standard "ref: refs/heads/<branch>" HEAD file and returns the branch name.
    """
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "HEAD").write_text("ref: refs/heads/feature/my-branch\n", encoding="utf-8")

    monkeypatch.setattr(helper_functions, "__file__", str(tmp_path / "helper_functions.py"))

    assert get_git_branch() == "feature/my-branch"


def test_get_git_branch_detached_head_returns_unknown(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests that get_git_branch falls back to "unknown" for a detached HEAD (a raw commit SHA, no ref line).
    """
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "HEAD").write_text("a" * 40 + "\n", encoding="utf-8")

    monkeypatch.setattr(helper_functions, "__file__", str(tmp_path / "helper_functions.py"))

    assert get_git_branch() == "unknown"


def test_get_git_branch_missing_git_dir_returns_unknown(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests that get_git_branch falls back to "unknown" when no .git directory is found in any parent directory.
    """
    isolated = tmp_path / "isolated"
    isolated.mkdir()

    monkeypatch.setattr(helper_functions, "__file__", str(isolated / "helper_functions.py"))

    assert get_git_branch() == "unknown"
