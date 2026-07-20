"""
Tests for NotebookExecutioner class.
"""

import subprocess
import sys
from pathlib import Path
from typing import Any

import papermill
import pytest

from src.exceptions.development_exception import IncorrectValue
from src.utils.notebooks_executioner import NotebookExecutioner, NotebookExecutionerNamedTuple


def _make_params(**overrides: Any) -> NotebookExecutionerNamedTuple:
    """
    Builds a NotebookExecutionerNamedTuple with sensible test defaults.

    config_name defaults to "None" so construction never calls Envs.set_config, which would raise if the
    ApplicationConfig singleton has already been instantiated elsewhere in the test session.
    :param overrides: Any. Field overrides applied on top of the defaults.
    :return: NotebookExecutionerNamedTuple.
    """
    defaults: dict[str, Any] = {
        "config_name": "None",
        "keep_name_static": False,
        "add_datetime_id": False,
        "add_file_name_to_notebook_name": False,
        "file_name": "test_file",
        "add_params_to_name": False,
        "convert_to_html": False,
        "notebook_name": "notebook",
        "notebook_path": "unused.ipynb",
        "output_folder": "unused_output",
        "number_of_processes": 1,
        "shuffle_before_processing": False,
        "list_of_ntb_params": [],
    }
    defaults.update(overrides)
    return NotebookExecutionerNamedTuple(**defaults)


def _make_base(output_folder: str, **overrides: Any) -> dict[str, Any]:
    """
    Builds the picklable "base" dict consumed by _build_output_path / _worker_execute_one.
    :param output_folder: str. Folder the resolved output path should live under.
    :param overrides: Any. Field overrides applied on top of the defaults.
    :return: dict[str, Any].
    """
    base: dict[str, Any] = {
        "keep_name_static": False,
        "add_datetime_id": False,
        "add_file_name_to_notebook_name": False,
        "file_name": "test_file",
        "add_params_to_name": False,
        "convert_to_html": False,
        "notebook_name": "notebook",
        "notebook_path": "unused.ipynb",
        "output_folder": output_folder,
    }
    base.update(overrides)
    return base


def test_notebook_executioner_construction_stores_params() -> None:
    """
    Tests that constructing NotebookExecutioner with config_name="None" succeeds and stores the given params
    without touching the Envs/ApplicationConfig singletons.
    """
    params = _make_params(number_of_processes=2)

    executioner = NotebookExecutioner(params=params)

    assert executioner._params.number_of_processes == 2


def test_set_list_of_notebook_params_replaces_params() -> None:
    """
    Tests that set_list_of_notebook_params replaces the list_of_ntb_params field on the stored params.
    """
    executioner = NotebookExecutioner(params=_make_params())
    new_list: list[dict[str, int]] = [{"a": 1}, {"a": 2}]

    executioner.set_list_of_notebook_params(list_of_ntb_params=new_list)

    assert executioner._params.list_of_ntb_params == new_list


def test_build_output_path_keep_name_static_ignores_params_and_datetime_id(tmp_path: Path) -> None:
    """
    Tests that keep_name_static uses the static "<notebook_name>_notebook_executioner.ipynb" name.

    exec_params and datetime_id are entirely ignored in that branch.
    """
    base = _make_base(str(tmp_path), keep_name_static=True, notebook_name="nb")

    result = NotebookExecutioner._build_output_path(base, {"ID": "irrelevant"}, "irrelevant")

    assert result == str((tmp_path / "nb_notebook_executioner.ipynb").resolve())


def test_build_output_path_dynamic_name_uses_notebook_name_and_file_name(tmp_path: Path) -> None:
    """
    Tests that a non-empty notebook_name combined with add_file_name_to_notebook_name appends the file name.
    """
    base = _make_base(
        str(tmp_path),
        notebook_name="run",
        add_file_name_to_notebook_name=True,
        file_name="script",
    )

    result = NotebookExecutioner._build_output_path(base, {"ID": "id"}, "id")

    assert result == str((tmp_path / "run_script.ipynb").resolve())


def test_build_output_path_falls_back_to_file_name_when_notebook_name_empty(tmp_path: Path) -> None:
    """
    Tests that an empty notebook_name falls back to the bare file name.

    No leading underscore or empty segment is left behind when combined with add_file_name_to_notebook_name.
    """
    base = _make_base(
        str(tmp_path),
        notebook_name="",
        add_file_name_to_notebook_name=True,
        file_name="script",
    )

    result = NotebookExecutioner._build_output_path(base, {"ID": "id"}, "id")

    assert result == str((tmp_path / "script.ipynb").resolve())


def test_build_output_path_prepends_datetime_id(tmp_path: Path) -> None:
    """
    Tests that add_datetime_id prepends the datetime id to the already-resolved name.
    """
    base = _make_base(str(tmp_path), notebook_name="run", add_datetime_id=True)

    result = NotebookExecutioner._build_output_path(base, {"ID": "20260101-000000_001"}, "20260101-000000_001")

    assert result == str((tmp_path / "20260101-000000_001_run.ipynb").resolve())


def test_build_output_path_appends_params_excluding_id_key(tmp_path: Path) -> None:
    """
    Tests that add_params_to_name appends every exec_params value in insertion order, skipping the "ID" key.
    """
    base = _make_base(str(tmp_path), notebook_name="run", add_params_to_name=True)
    exec_params = {"ID": "id", "a": 1, "b": "x"}

    result = NotebookExecutioner._build_output_path(base, exec_params, "id")

    assert result == str((tmp_path / "run_1_x.ipynb").resolve())


def test_worker_execute_one_skips_nbconvert_when_convert_to_html_is_false(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Tests that _worker_execute_one runs papermill and skips nbconvert when convert_to_html is False.

    It calls papermill.execute_notebook with the resolved output path, stamps "ID" into the params, and never
    invokes subprocess (nbconvert) when convert_to_html is False.
    """
    recorded_calls: list[tuple[str, str, dict[str, Any]]] = []
    monkeypatch.setattr(
        papermill,
        "execute_notebook",
        lambda notebook_path, path_out, params: recorded_calls.append((notebook_path, path_out, params)),
    )

    def _fail_if_called(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("subprocess.run should not be called when convert_to_html is False")

    monkeypatch.setattr(subprocess, "run", _fail_if_called)

    executioner = NotebookExecutioner(params=_make_params())
    base = _make_base(str(tmp_path), notebook_name="run", notebook_path="input.ipynb", convert_to_html=False)

    path_out = executioner._worker_execute_one((base, {"a": 1}))

    assert path_out == str((tmp_path / "run.ipynb").resolve())
    assert len(recorded_calls) == 1
    notebook_path, recorded_path_out, params = recorded_calls[0]
    assert notebook_path == "input.ipynb"
    assert recorded_path_out == path_out
    assert params["a"] == 1
    assert "ID" in params


def test_worker_execute_one_converts_to_html_with_expected_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Tests that _worker_execute_one invokes nbconvert with the expected argument list.

    The command runs through the current interpreter (``sys.executable -m jupyter nbconvert``), avoiding PATH
    issues, when convert_to_html is True.
    """
    monkeypatch.setattr(papermill, "execute_notebook", lambda *_args: None)

    recorded_commands: list[list[str]] = []

    def _fake_run(command: list[str], **_kwargs: Any) -> None:
        recorded_commands.append(command)

    monkeypatch.setattr(subprocess, "run", _fake_run)

    executioner = NotebookExecutioner(params=_make_params())
    base = _make_base(str(tmp_path), notebook_name="run", notebook_path="input.ipynb", convert_to_html=True)

    path_out = executioner._worker_execute_one((base, {"a": 1}))

    assert len(recorded_commands) == 1
    assert recorded_commands[0] == [sys.executable, "-m", "jupyter", "nbconvert", "--to", "html", path_out]


def test_execute_raises_incorrect_value_for_non_positive_number_of_processes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Tests that execute() raises IncorrectValue for a number_of_processes below 1.

    _ensure_ipynb_from_py is stubbed out since it is unrelated to this guard and would otherwise require a real
    notebook file on disk.
    """
    params = _make_params(number_of_processes=0, output_folder=str(tmp_path))
    executioner = NotebookExecutioner(params=params)
    monkeypatch.setattr(executioner, "_ensure_ipynb_from_py", lambda: None)

    with pytest.raises(IncorrectValue):
        executioner.execute()
