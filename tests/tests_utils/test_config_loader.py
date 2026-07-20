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


class _NestedTable(NamedTuple):
    """NamedTuple nested table used by _NestedFixtureTarget to exercise recursive table merging."""

    label: str
    value: int


class _NestedFixtureTarget(NamedTuple):
    """NamedTuple target with a nested table, used to exercise base+overlay merging."""

    name: str
    amount: int
    nested: _NestedTable


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


def test_load_config_base_overlay_falls_back_to_base_for_omitted_keys(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Tests that a partial overlay deep-merged over a base (via base_name) falls back to the base's value for any
    key - including a nested-table key - that the overlay omits, while keys the overlay does set win.
    """
    configurations_folder = _set_project_root(tmp_path, monkeypatch)
    (configurations_folder / "base_profile.toml").write_text(
        'name = "base"\namount = 1\n\n[nested]\nlabel = "base-label"\nvalue = 1\n'
    )
    (configurations_folder / "overlay_profile.toml").write_text("amount = 2\n\n[nested]\nvalue = 2\n")

    result = load_config("overlay_profile", _NestedFixtureTarget, base_name="base_profile")

    assert result == _NestedFixtureTarget(name="base", amount=2, nested=_NestedTable(label="base-label", value=2))


def test_load_config_base_overlay_missing_base_raises_file_not_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Tests that a missing base_name file raises FileNotFound naming the base profile, the same way a missing
    config_name file does.
    """
    configurations_folder = _set_project_root(tmp_path, monkeypatch)
    (configurations_folder / "overlay_profile.toml").write_text("amount = 2\n")

    with pytest.raises(FileNotFound) as exc_info:
        load_config("overlay_profile", _FixtureTarget, base_name="does_not_exist_base")

    assert "does_not_exist_base" in exc_info.value.get_description()


def test_load_config_base_overlay_typo_key_raises_incorrect_data_structure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Tests that a misspelled key in the overlay is rejected by failonextra=True: once merged over the base it
    becomes an extra key with no matching field on the target.
    """
    configurations_folder = _set_project_root(tmp_path, monkeypatch)
    (configurations_folder / "base_profile.toml").write_text('name = "base"\namount = 1\n')
    (configurations_folder / "overlay_profile.toml").write_text("amonut = 2\n")

    with pytest.raises(IncorrectDataStructure) as exc_info:
        load_config("overlay_profile", _FixtureTarget, base_name="base_profile")

    assert "_FixtureTarget" in exc_info.value.get_description()


def test_load_config_base_overlay_wrong_typed_value_raises_incorrect_data_structure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Tests that a wrong-typed scalar in the overlay is rejected by basiccast=False once deep-merged over the
    base, rather than being silently coerced.
    """
    configurations_folder = _set_project_root(tmp_path, monkeypatch)
    (configurations_folder / "base_profile.toml").write_text('name = "base"\namount = 1\n')
    (configurations_folder / "overlay_profile.toml").write_text('amount = "not-an-int"\n')

    with pytest.raises(IncorrectDataStructure) as exc_info:
        load_config("overlay_profile", _FixtureTarget, base_name="base_profile")

    assert "_FixtureTarget" in exc_info.value.get_description()


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
