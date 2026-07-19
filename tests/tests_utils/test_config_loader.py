"""
Tests for Config Loader module.
"""

import ast
import inspect
import logging
from pathlib import Path
from typing import NamedTuple

import pytest

from src.constants.env_constants import ENV_PROJECT_ROOT
from src.exceptions.data_exception import FileNotFound, IncorrectDataStructure
from src.utils import config_loader as config_loader_module
from src.utils.config_loader import load_config
from src.utils.envs import Envs
from src.utils.project_paths import FOLDER_CONFIGURATIONS


class _FixtureTarget(NamedTuple):
    """NamedTuple target used to exercise load_config in these tests."""

    name: str
    amount: int


def _set_project_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """
    Points Project Paths at tmp_path for the duration of a test and returns the configurations folder.
    :param tmp_path: Path. Pytest-provided temporary directory to use as the fake project root.
    :param monkeypatch: pytest.MonkeyPatch. Used to guarantee the environment variable is restored.
    :return: Path. The configurations folder under tmp_path.
    """
    monkeypatch.setenv(ENV_PROJECT_ROOT, str(tmp_path))
    Envs.set_project_root_override(str(tmp_path))

    configurations_folder = tmp_path / FOLDER_CONFIGURATIONS
    configurations_folder.mkdir(parents=True, exist_ok=True)
    return configurations_folder


def test_load_config_valid_profile(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests that a valid profile and matching NamedTuple target returns a correctly-typed, correctly-valued
    instance.
    """
    configurations_folder = _set_project_root(tmp_path, monkeypatch)
    (configurations_folder / "test_profile.toml").write_text('name = "hello"\namount = 3\n')

    result = load_config("test_profile", _FixtureTarget)

    assert result == _FixtureTarget(name="hello", amount=3)


def test_load_config_missing_file_raises_file_not_found(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests that a missing file raises FileNotFound naming the profile, the searched folder, and the resolved
    absolute path.
    """
    configurations_folder = _set_project_root(tmp_path, monkeypatch)
    resolved_path = configurations_folder / "does_not_exist.toml"

    with pytest.raises(FileNotFound) as exc_info:
        load_config("does_not_exist", _FixtureTarget)

    description = exc_info.value.get_description()
    assert "does_not_exist" in description
    assert str(configurations_folder) in description
    assert str(resolved_path) in description


def test_load_config_malformed_toml_raises_incorrect_data_structure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Tests that malformed TOML raises IncorrectDataStructure identifying a parse failure.
    """
    configurations_folder = _set_project_root(tmp_path, monkeypatch)
    (configurations_folder / "broken.toml").write_text('name = "unterminated\namount = 3\n')

    with pytest.raises(IncorrectDataStructure) as exc_info:
        load_config("broken", _FixtureTarget)

    assert "broken.toml" in exc_info.value.get_description()


def test_load_config_shape_mismatch_raises_incorrect_data_structure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Tests that a shape mismatch against the target NamedTuple raises IncorrectDataStructure identifying a
    schema/type failure.
    """
    configurations_folder = _set_project_root(tmp_path, monkeypatch)
    (configurations_folder / "mismatched.toml").write_text('name = "hello"\namount = "not-an-int"\n')

    with pytest.raises(IncorrectDataStructure) as exc_info:
        load_config("mismatched", _FixtureTarget)

    description = exc_info.value.get_description()
    assert "_FixtureTarget" in description


def test_load_config_success_produces_no_logging_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """
    Tests that the success path produces no logging output at WARNING level or above.
    """
    configurations_folder = _set_project_root(tmp_path, monkeypatch)
    (configurations_folder / "silent.toml").write_text('name = "hello"\namount = 1\n')

    with caplog.at_level(logging.WARNING):
        load_config("silent", _FixtureTarget)

    assert caplog.records == []


def test_load_config_subfolder_resolves_fixture_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests that the subfolder parameter resolves a fixture file placed under a subfolder.
    """
    configurations_folder = _set_project_root(tmp_path, monkeypatch)
    subfolder = configurations_folder / "loggers"
    subfolder.mkdir(parents=True, exist_ok=True)
    (subfolder / "sub_profile.toml").write_text('name = "nested"\namount = 7\n')

    result = load_config("sub_profile", _FixtureTarget, subfolder="loggers")

    assert result == _FixtureTarget(name="nested", amount=7)


def test_config_loader_module_imports_no_project_logger() -> None:
    """
    Tests that the config_loader module never imports the project Logger singleton.

    Only the actual import statements are inspected (not the docstrings, which are allowed to mention the
    architectural constraint by name) - this would fail if someone added ``from src.utils.logger import Logger``.
    """
    tree = ast.parse(inspect.getsource(config_loader_module))
    imported_modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.append(node.module)
        elif isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)

    assert not any("logger" in module.lower() for module in imported_modules)
