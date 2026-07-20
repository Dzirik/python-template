"""
Tests guarding against drift between the config NamedTuple trees and their hand-maintained JSON Schema IDE aids.

The schemas under configurations/schemas/ exist purely for PyCharm autocomplete - typedload validates the TOML
profiles at runtime and never loads them - so a field added to (or removed from) a NamedTuple can silently
leave the matching schema stale. These tests turn that manual "remember to update the schema too" chore into
an enforced invariant by comparing field names/structure only; JSON-Schema type fidelity is out of scope.
"""

import json
from typing import Any, get_args, get_origin, get_type_hints

import pytest
import typedload

from src.configurations.watchdog_config_data import SupervisionTimingData, WatchdogConfigData
from src.utils.application_config_data import ApplicationConfigData
from src.utils.project_paths import ProjectPaths

SCHEMA_DRIFT_CASES = [
    pytest.param(ApplicationConfigData, "application_config", id="application_config"),
    pytest.param(WatchdogConfigData, "watchdog_config", id="watchdog_config"),
]


def _as_nested_namedtuple(type_hint: Any) -> type[Any] | None:
    """
    Determines whether type_hint names a NamedTuple class, unwrapping a list[...] container first so that
    array-of-tables fields such as list[WorkerData] are recognised as nested too.
    :param type_hint: Any. A resolved type hint for one NamedTuple field, e.g. Path, list[WorkerData], str,
        or bool.
    :return: Optional[type[Any]]. The nested NamedTuple class if type_hint names one (directly or via
        list[...]), else None for a scalar/leaf field.
    """
    target = type_hint
    if get_origin(type_hint) in (list, tuple):
        args = get_args(type_hint)
        target = args[0] if args else None

    if isinstance(target, type) and issubclass(target, tuple) and hasattr(target, "_fields"):
        return target

    return None


def _collect_namedtuple_field_tree(namedtuple_type: type[Any]) -> dict[str, Any]:
    """
    Recursively collects the field-name tree of namedtuple_type, descending into any field whose type is
    itself a NamedTuple (directly or wrapped in list[...]).
    :param namedtuple_type: type[Any]. Root or nested NamedTuple class to walk.
    :return: dict[str, Any]. Maps each field name to its own field tree (dict) for nested NamedTuple fields,
        or to None for leaf/scalar fields.
    """
    hints = get_type_hints(namedtuple_type)
    tree: dict[str, Any] = {}
    for field_name in namedtuple_type._fields:
        nested_type = _as_nested_namedtuple(hints[field_name])
        tree[field_name] = _collect_namedtuple_field_tree(nested_type) if nested_type is not None else None

    return tree


def _resolve_schema_object(schema_root: dict[str, Any], node: dict[str, Any]) -> dict[str, Any] | None:
    """
    Resolves node (a property's own schema fragment) to the object schema it points at, following a local
    "$ref" into schema_root["definitions"] and unwrapping an "array" wrapper to its "items" schema.
    :param schema_root: dict[str, Any]. Full parsed JSON Schema document, used to resolve "$ref" pointers.
    :param node: dict[str, Any]. The property's own schema fragment.
    :return: Optional[dict[str, Any]]. The resolved object schema (containing "properties") if node describes
        a nested object - directly, via "$ref", or via an array of such objects - else None for a scalar leaf.
    """
    if "$ref" in node:
        ref_name = node["$ref"].rsplit("/", maxsplit=1)[-1]
        resolved: dict[str, Any] = schema_root["definitions"][ref_name]
        return resolved

    if node.get("type") == "array":
        return _resolve_schema_object(schema_root, node.get("items", {}))

    if node.get("type") == "object" and "properties" in node:
        return node

    return None


def _collect_schema_field_tree(schema_root: dict[str, Any], node: dict[str, Any]) -> dict[str, Any]:
    """
    Recursively collects the property-name tree of node, descending into any property that resolves -
    directly, via "$ref", or via an array of such - to another object schema.
    :param schema_root: dict[str, Any]. Full parsed JSON Schema document, used to resolve "$ref" pointers.
    :param node: dict[str, Any]. An object schema fragment with a "properties" mapping (the root document
        itself qualifies, since it has "properties" at the top level).
    :return: dict[str, Any]. Maps each property name to its own field tree (dict) for nested object
        properties, or to None for leaf/scalar properties.
    """
    tree: dict[str, Any] = {}
    for prop_name, prop_schema in node.get("properties", {}).items():
        nested_object = _resolve_schema_object(schema_root, prop_schema)
        tree[prop_name] = _collect_schema_field_tree(schema_root, nested_object) if nested_object is not None else None

    return tree


def _assert_field_trees_match(namedtuple_tree: dict[str, Any], schema_tree: dict[str, Any], level: str) -> None:
    """
    Asserts that namedtuple_tree and schema_tree expose the identical set of keys at every nesting level,
    recursing into shared nested fields so drift is reported at the exact level it occurs at.
    :param namedtuple_tree: dict[str, Any]. Field tree collected from the NamedTuple side.
    :param schema_tree: dict[str, Any]. Field tree collected from the JSON Schema side.
    :param level: str. Human-readable path to the current level, for diagnostics (e.g. "ApplicationConfigData"
        or "ApplicationConfigData.path").
    """
    namedtuple_keys = set(namedtuple_tree)
    schema_keys = set(schema_tree)

    missing_from_schema = sorted(namedtuple_keys - schema_keys)
    extra_in_schema = sorted(schema_keys - namedtuple_keys)

    assert not missing_from_schema and not extra_in_schema, (
        f"Schema drift at '{level}': "
        f"fields on the NamedTuple but missing from the schema: {missing_from_schema or 'none'}; "
        f"keys in the schema but not on the NamedTuple: {extra_in_schema or 'none'}. "
        "Update configurations/schemas/*.schema.json to match the NamedTuple (or vice versa)."
    )

    for field_name in sorted(namedtuple_keys):
        nested_namedtuple = namedtuple_tree[field_name]
        nested_schema = schema_tree[field_name]
        nested_level = f"{level}.{field_name}"

        assert (nested_namedtuple is None) == (nested_schema is None), (
            f"Schema drift at '{nested_level}': one side models it as a nested object and the other as a "
            "scalar - check both the NamedTuple field type and the schema property definition."
        )

        if nested_namedtuple is not None and nested_schema is not None:
            _assert_field_trees_match(nested_namedtuple, nested_schema, nested_level)


@pytest.mark.parametrize("root_namedtuple, schema_stem", SCHEMA_DRIFT_CASES)
def test_schema_field_names_match_namedtuple_tree(root_namedtuple: type[Any], schema_stem: str) -> None:
    """
    Tests that the hand-maintained JSON Schema for schema_stem models exactly the same field names, at every
    nesting level, as root_namedtuple - catching a field added to (or removed from) one side without the
    other being updated to match. Only field names/structure are compared, not JSON-Schema types.
    :param root_namedtuple: type[Any]. Root NamedTuple class describing the config shape.
    :param schema_stem: str. Bare schema file name (without the ".schema.json" suffix) under
        configurations/schemas/.
    """
    schema_path = ProjectPaths().config_file(schema_stem, subfolder="schemas", extension=".schema.json")
    with schema_path.open(encoding="utf-8") as schema_file:
        schema_root = json.load(schema_file)

    namedtuple_tree = _collect_namedtuple_field_tree(root_namedtuple)
    schema_tree = _collect_schema_field_tree(schema_root, schema_root)

    _assert_field_trees_match(namedtuple_tree, schema_tree, level=root_namedtuple.__name__)


def test_supervision_timing_omitted_from_toml_uses_documented_defaults() -> None:
    """
    Tests that a parsed watchdog TOML tree omitting the optional "supervision" table loads
    WatchdogConfigData.supervision as SupervisionTimingData() - i.e. today's watchdog.py module
    constants, reproduced as NamedTuple defaults - via the same strict typedload.load call
    src/utils/config_loader.py uses (basiccast=False, failonextra=True).
    """
    parsed: dict[str, Any] = {"name": "watchdog_test", "workers": []}

    config_data = typedload.load(parsed, WatchdogConfigData, basiccast=False, failonextra=True)

    assert config_data.supervision == SupervisionTimingData()


def test_supervision_timing_override_replaces_only_the_set_field() -> None:
    """
    Tests that a parsed watchdog TOML tree with a partial "supervision" table overrides only the
    field(s) it sets, leaving every other SupervisionTimingData field at its documented default.
    """
    parsed: dict[str, Any] = {
        "name": "watchdog_test",
        "workers": [],
        "supervision": {"check_interval": 10.0},
    }

    config_data = typedload.load(parsed, WatchdogConfigData, basiccast=False, failonextra=True)

    assert config_data.supervision == SupervisionTimingData()._replace(check_interval=10.0)
    assert config_data.supervision.startup_grace_period == SupervisionTimingData().startup_grace_period
