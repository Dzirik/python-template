"""
Tests for Python version consistency across the version-bearing project files.
"""

import re
import tomllib
from typing import Any

import pytest

from src.utils.project_paths import ProjectPaths

FORBIDDEN_PYTHON_VERSIONS = ("3.11", "3.12")
VERSION_BEARING_RELATIVE_PATHS = ("pyproject.toml", ".python-version", ".github/workflows/ci.yml")
EXPECTED_REQUIRES_PYTHON = ">=3.13,<3.15"
EXPECTED_CLASSIFIER_VERSIONS = frozenset({"3.13", "3.14"})
EXPECTED_MYPY_PYTHON_VERSION = "3.13"
EXPECTED_RUFF_TARGET_VERSION = "py313"
EXPECTED_PYTHON_VERSION_FILE_CONTENT = "3.13"
EXPECTED_CI_MATRIX_PYTHON_VERSIONS = ["3.13", "3.14"]

FORBIDDEN_VERSION_CASES = [
    (relative_path, forbidden_version)
    for relative_path in VERSION_BEARING_RELATIVE_PATHS
    for forbidden_version in FORBIDDEN_PYTHON_VERSIONS
]


def _load_pyproject() -> dict[str, Any]:
    """
    Loads pyproject.toml from the project root via stdlib tomllib.
    :return: dict[str, Any]. Parsed TOML document.
    """
    root = ProjectPaths().root
    with (root / "pyproject.toml").open("rb") as file:
        return tomllib.load(file)


@pytest.mark.parametrize("relative_path, forbidden_version", FORBIDDEN_VERSION_CASES)
def test_forbidden_python_version_absent_from_version_bearing_files(relative_path: str, forbidden_version: str) -> None:
    """
    Tests that forbidden_version does not appear anywhere in relative_path, guarding against a retired
    interpreter silently reappearing in any of the version-bearing project files.
    :param relative_path: str. Path (relative to the project root) of a version-bearing file.
    :param forbidden_version: str. Retired Python version that must never reappear.
    """
    root = ProjectPaths().root
    content = (root / relative_path).read_text(encoding="utf-8")

    assert forbidden_version not in content


def test_pyproject_requires_python_matches_agreed_floor_and_ceiling() -> None:
    """
    Tests that pyproject.toml requires-python matches the agreed target of >=3.13,<3.15.
    """
    data = _load_pyproject()

    assert data["project"]["requires-python"] == EXPECTED_REQUIRES_PYTHON


def test_pyproject_classifiers_list_exactly_3_13_and_3_14() -> None:
    """
    Tests that pyproject.toml trove classifiers advertise exactly Python 3.13 and 3.14, with no other
    Python version classifier present.
    """
    data = _load_pyproject()
    classifiers: list[str] = data["project"]["classifiers"]

    version_classifiers = {
        classifier.removeprefix("Programming Language :: Python :: ")
        for classifier in classifiers
        if re.fullmatch(r"Programming Language :: Python :: \d+\.\d+", classifier)
    }

    assert version_classifiers == EXPECTED_CLASSIFIER_VERSIONS


def test_pyproject_mypy_python_version_matches_interpreter_floor() -> None:
    """
    Tests that [tool.mypy] python_version matches the interpreter floor.
    """
    data = _load_pyproject()

    assert data["tool"]["mypy"]["python_version"] == EXPECTED_MYPY_PYTHON_VERSION


def test_pyproject_ruff_target_version_matches_interpreter_floor() -> None:
    """
    Tests that [tool.ruff] target-version matches the interpreter floor.
    """
    data = _load_pyproject()

    assert data["tool"]["ruff"]["target-version"] == EXPECTED_RUFF_TARGET_VERSION


def test_python_version_file_pins_interpreter_floor() -> None:
    """
    Tests that .python-version pins the same interpreter floor used by uv/pyenv.
    """
    root = ProjectPaths().root
    content = (root / ".python-version").read_text(encoding="utf-8").strip()

    assert content == EXPECTED_PYTHON_VERSION_FILE_CONTENT


def test_ci_matrix_python_version_is_exactly_3_13_and_3_14() -> None:
    """
    Tests that the CI workflow's python-version matrix is exactly ["3.13", "3.14"], with neither a retired
    interpreter nor an undeclared new one sneaking into the build matrix.
    """
    root = ProjectPaths().root
    content = (root / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    match = re.search(r"python-version:\s*\[(?P<versions>[^]]*)]", content)
    assert match is not None

    versions = [item.strip().strip('"').strip("'") for item in match.group("versions").split(",")]

    assert versions == EXPECTED_CI_MATRIX_PYTHON_VERSIONS
