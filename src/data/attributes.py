"""
Code for handling attributes across the whole repository
"""

import csv
from pathlib import Path
from typing import Any, ClassVar, NamedTuple

from numpy import float32, float64, int32, int64, isnan
from pandas import read_excel

from src.exceptions.development_exception import NoProperOptionInIf

FILE_NAME_BASE = "../../src/data/attributes"
ATTRS_GROUPS_NAMES = ["GROUP_01"]


class AttributeNamedTuple(NamedTuple):
    """
    For storing attribute and its data type.
    """

    name: str
    type: Any


class Attributes:
    """
    Class for reading and processing attribute from a file.
    """

    _TYPE_MAPPING: ClassVar[dict[str, Any]] = {
        "bool": bool,  # lambda x: x.lower() in ["true", "1"],  # Handling boolean conversion
        "datetime64[ns]": "datetime64[ns]",
        "int": int,
        "float": float,
        "str": str,
        "float32": float32,
        "float64": float64,
        "int32": int32,
        "int64": int64,
        "Any": Any,
    }

    def __init__(self, attrs_groups_name: list[str], file_type: str = "csv") -> None:
        """
        :param file_type: str. "csv" or "xlsm"
        :param attrs_groups_name: list[str].
        """
        self._file_type = file_type
        self._attrs_groups_name = attrs_groups_name

        self._attributes_instance: Any | None = None
        self._dict_attrs_groups: dict[str, list[str]] = {}

        self._read_data()

    def _read_data(self) -> None:
        """
        Reads the data from attributes file.
        """
        dict_attrs_named_tuples: dict[str, list[tuple[int, str]]] = {}
        self._dict_attrs_groups = {}
        dict_attrs_groups_order_name_tuples: dict[str, list[tuple[int, str]]] = {}
        for attr_group_name in self._attrs_groups_name:
            self._dict_attrs_groups[attr_group_name] = []
            dict_attrs_groups_order_name_tuples[attr_group_name] = []

        if self._file_type == "csv":
            dict_attrs_named_tuples, dict_attrs_groups_order_name_tuples = self._read_data_from_csv(
                file_name=f"{FILE_NAME_BASE}.csv",
                dict_attrs_named_tuples=dict_attrs_named_tuples,
                dict_attrs_groups_order_name_tuples=dict_attrs_groups_order_name_tuples,
            )
        elif self._file_type == "xlsm":
            dict_attrs_named_tuples, dict_attrs_groups_order_name_tuples = self._read_data_from_xlsm(
                file_name=f"{FILE_NAME_BASE}.xlsm",
                dict_attrs_named_tuples=dict_attrs_named_tuples,
                dict_attrs_groups_order_name_tuples=dict_attrs_groups_order_name_tuples,
            )
        else:
            NoProperOptionInIf("Not valid option in Attributes class reading.")

        for key, value in dict_attrs_groups_order_name_tuples.items():
            self._dict_attrs_groups[key] = [item[1] for item in sorted(value, key=lambda x: x[0])]

        fields = [(alias, AttributeNamedTuple) for alias in dict_attrs_named_tuples]
        attributes = NamedTuple("Attributes", fields)  # type:ignore
        self._attributes_instance = attributes(**dict_attrs_named_tuples)

    def get(self) -> tuple[Any, dict[str, list[str]]]:
        """
        Returns the data.
        :return: Tuple[Any, Dict[str, List[str]]]. <attributes, dict_attrs_groups>
        """
        return self._attributes_instance, self._dict_attrs_groups

    def _convert_string_to_python_type(self, attr_type_str: str) -> Any:
        """
        Converts string to Python type.
        :param attr_type_str: str.
        :return: Any.
        """
        if attr_type_str in self._TYPE_MAPPING:
            return self._TYPE_MAPPING[attr_type_str]
        raise NoProperOptionInIf(f"String type: {attr_type_str} was not found.")

    def _read_data_from_csv(
        self,
        file_name: str,
        dict_attrs_named_tuples: dict[str, Any],
        dict_attrs_groups_order_name_tuples: dict[str, list[tuple[int, str]]],
    ) -> tuple[dict[str, Any], dict[str, list[tuple[int, str]]]]:
        """
        Reads the data from csv file.
        :param file_name: str.
        :param dict_attrs_named_tuples: dict_attrs_named_tuples: Dict[str, Any].
        :param dict_attrs_groups_order_name_tuples: Dict[str, List[Tuple[int, str]]].
        :return: Tuple[Dict[str, Any], Dict[str, List[Tuple[int, str]]]].
        """
        # this is because of the test
        file_path = Path(file_name)
        if len(str(Path.cwd()).split("\\")) == 2:
            file_path = Path.cwd() / "src" / "data" / "attributes.csv"
        with file_path.open(encoding="utf8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                attr_name_tuple_alias = row["ATTR_NAME_TUPLE_ALIAS"]
                attr_name = row["ATTR_NAME"]
                attr_type = self._convert_string_to_python_type(attr_type_str=row["ATTR_TYPE"])

                dict_attrs_named_tuples[attr_name_tuple_alias] = AttributeNamedTuple(name=attr_name, type=attr_type)

                for key, value in dict_attrs_groups_order_name_tuples.items():
                    if row[key] != "":
                        value.append((int(row[key]), attr_name))

        return dict_attrs_named_tuples, dict_attrs_groups_order_name_tuples

    def _read_data_from_xlsm(
        self,
        file_name: str,
        dict_attrs_named_tuples: dict[str, Any],
        dict_attrs_groups_order_name_tuples: dict[str, list[tuple[int, str]]],
    ) -> tuple[dict[str, Any], dict[str, list[tuple[int, str]]]]:
        """
        Reads the data from xlsm file.
        :param file_name: str.
        :param dict_attrs_named_tuples: dict_attrs_named_tuples: Dict[str, Any].
        :param dict_attrs_groups_order_name_tuples: Dict[str, List[Tuple[int, str]]].
        :return: Tuple[Dict[str, Any], Dict[str, List[Tuple[int, str]]]].
        """
        df = read_excel(file_name, sheet_name="ATTRS", engine="openpyxl")
        for _, row in df.iterrows():
            alias = row["ATTR_NAME_TUPLE_ALIAS"]
            attr_name = row["ATTR_NAME"]
            attr_type = self._convert_string_to_python_type(attr_type_str=row["ATTR_TYPE"])

            attribute_instance = AttributeNamedTuple(name=attr_name, type=attr_type)
            dict_attrs_named_tuples[alias] = attribute_instance

            for key, value in dict_attrs_groups_order_name_tuples.items():
                if not isnan(row[key]) and row[key] != "":
                    value.append((int(row[key]), attr_name))

        return dict_attrs_named_tuples, dict_attrs_groups_order_name_tuples


A, DICT_ATTRS_GROUPS = Attributes(attrs_groups_name=ATTRS_GROUPS_NAMES, file_type="csv").get()
