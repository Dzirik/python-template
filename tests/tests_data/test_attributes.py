"""
Tests for the path-anchored attribute loading in the Attributes class.
"""

from pathlib import Path
from typing import Any

import pytest

from src.data.attributes import Attributes
from src.exceptions.development_exception import NoProperOptionInIf


def _assert_attributes_shape(attributes_instance: Any, dict_attrs_groups: dict[str, list[str]]) -> None:
    """
    Asserts that the parsed attributes and groups match the fixture data in attributes.csv/.xlsm.

    :param attributes_instance: Any. The dynamically built attributes NamedTuple instance.
    :param dict_attrs_groups: dict[str, list[str]]. Groups mapping produced by Attributes.get().
    """
    datetime_attr = attributes_instance.datetime
    attr_name_1_attr = attributes_instance.attr_name_1

    assert datetime_attr.name == "DATETIME"
    assert datetime_attr.type == "datetime64[ns]"
    assert attr_name_1_attr.name == "ATTR_NAME_1"
    assert attr_name_1_attr.type is str

    assert dict_attrs_groups == {"GROUP_01": ["DATETIME"]}


def test_attributes_loads_csv_from_arbitrary_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests that Attributes loads the csv file correctly regardless of the current working directory.

    :param tmp_path: Path. Pytest-provided temporary directory used as an arbitrary CWD.
    :param monkeypatch: pytest.MonkeyPatch. Used to change the CWD away from the repository root.
    """
    monkeypatch.chdir(tmp_path)

    attributes_instance, dict_attrs_groups = Attributes(attrs_groups_name=["GROUP_01"], file_type="csv").get()

    _assert_attributes_shape(attributes_instance, dict_attrs_groups)


def test_attributes_loads_xlsm_from_arbitrary_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests that Attributes loads the xlsm file correctly regardless of the current working directory.

    :param tmp_path: Path. Pytest-provided temporary directory used as an arbitrary CWD.
    :param monkeypatch: pytest.MonkeyPatch. Used to change the CWD away from the repository root.
    """
    monkeypatch.chdir(tmp_path)

    attributes_instance, dict_attrs_groups = Attributes(attrs_groups_name=["GROUP_01"], file_type="xlsm").get()

    _assert_attributes_shape(attributes_instance, dict_attrs_groups)


def test_attributes_invalid_file_type_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests that constructing Attributes with an unsupported file_type raises NoProperOptionInIf.

    :param tmp_path: Path. Pytest-provided temporary directory used as an arbitrary CWD.
    :param monkeypatch: pytest.MonkeyPatch. Used to change the CWD away from the repository root.
    """
    monkeypatch.chdir(tmp_path)

    with pytest.raises(NoProperOptionInIf):
        Attributes(attrs_groups_name=["GROUP_01"], file_type="parquet")
