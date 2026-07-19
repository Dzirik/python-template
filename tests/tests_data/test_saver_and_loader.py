"""
Tests for the config-snapshot round-trip in SaverAndLoader.
"""

import ast
import inspect
import json
from pathlib import Path
from typing import NamedTuple

import pytest

from src.data import saver_and_loader as saver_and_loader_module
from src.data.saver_and_loader import SaverAndLoader
from src.exceptions.data_exception import FileNotFound


class _FixtureConfigData(NamedTuple):
    """NamedTuple target used to exercise the config-snapshot round-trip in these tests."""

    name: str
    amount: int
    values: list[str]


def _patch_get_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """
    Redirects the module-level get_path helper to resolve inside tmp_path.

    This decouples the test from ApplicationConfig and the real data folder - only the extension chosen by
    the caller (save_config_data / load_config_data) matters for these tests.
    :param monkeypatch: pytest.MonkeyPatch. Used to patch the module-level function.
    :param tmp_path: Path. Pytest-provided temporary directory to resolve paths against.
    """

    def _fake_get_path(file_name: str, where: str = "raw_data", extension: str = ".pkl") -> str:  # noqa: ARG001
        return str(tmp_path / (file_name + extension))

    monkeypatch.setattr(saver_and_loader_module, "get_path", _fake_get_path)


def test_save_config_data_writes_json_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests that save_config_data writes the dumped named tuple as JSON to a .json file.
    """
    _patch_get_path(monkeypatch, tmp_path)
    config_data = _FixtureConfigData(name="hello", amount=3, values=["a", "b"])

    SaverAndLoader.save_config_data(config_data, "snapshot")

    snapshot_path = tmp_path / "snapshot.json"
    assert snapshot_path.exists()
    assert json.loads(snapshot_path.read_text(encoding="utf8")) == {
        "name": "hello",
        "amount": 3,
        "values": ["a", "b"],
    }


def test_load_config_data_round_trip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests that dumping a config named tuple and reloading it returns an equal instance from a .json snapshot.
    """
    _patch_get_path(monkeypatch, tmp_path)
    config_data = _FixtureConfigData(name="hello", amount=3, values=["a", "b"])

    SaverAndLoader.save_config_data(config_data, "snapshot")
    result = SaverAndLoader.load_config_data("snapshot", _FixtureConfigData)

    assert result == config_data
    assert (tmp_path / "snapshot.json").suffix == ".json"


def test_load_config_data_missing_file_raises_file_not_found(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests that loading a missing snapshot raises FileNotFound naming the resolved path.
    """
    _patch_get_path(monkeypatch, tmp_path)

    with pytest.raises(FileNotFound) as exc_info:
        SaverAndLoader.load_config_data("does_not_exist", _FixtureConfigData)

    description = exc_info.value.get_description()
    assert str(tmp_path / "does_not_exist.json") in description


def test_saver_and_loader_module_imports_no_pyhocon() -> None:
    """
    Tests that the saver_and_loader module never imports pyhocon.

    Only the actual import statements are inspected (not the docstrings) - the config-snapshot round-trip
    must be symmetric on stdlib json only, with no remaining pyhocon dependency.
    """
    tree = ast.parse(inspect.getsource(saver_and_loader_module))
    imported_modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.append(node.module)
        elif isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)

    assert not any("pyhocon" in module.lower() for module in imported_modules)
