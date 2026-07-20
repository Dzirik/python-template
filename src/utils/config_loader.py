"""
Config Loader - foundational, Logger-free loading of TOML configuration files into typed NamedTuples.

Resolves a bare profile name through Project Paths, parses it with the standard-library tomllib, and loads the
parsed tree into a target NamedTuple with typedload. This is the single loading mechanism shared by Application
Config, Component Config, and the Logger's own profile file - see ADR 0001 and ADR 0003. Per ADR 0001, this
module must never import the project Logger: it is silent on success and reports every failure through
diagnostic-rich exceptions instead.

An optional ``base_name`` turns a single-file load into a base+overlay one: ``base_name`` is parsed as the
tracked base profile, ``config_name`` is parsed as a partial overlay, and the overlay is deep-merged over the
base - nested tables merge recursively, scalars and lists are replaced wholesale - before a single strict
``typedload.load`` call validates the merged result. See ADR 0006. Application Config is the only caller that
passes ``base_name`` today; Component Config and the Logger's own profile file pass none and keep loading a
single file, now under the same strictness.

Usage can be found at the end of the file.
"""

import tomllib
from typing import Any, Protocol

import typedload
from typedload.exceptions import TypedloadException

from src.exceptions.data_exception import FileNotFound, IncorrectDataStructure
from src.utils.project_paths import ProjectPaths


class _NamedTupleLike(Protocol):
    """Structural protocol satisfied by every NamedTuple (has _asdict)."""

    def _asdict(self) -> dict[str, Any]: ...


def _parse_toml_profile(config_name: str, subfolder: str | None) -> dict[str, Any]:
    """
    Resolves a bare profile name through Project Paths and parses it into a plain dict with tomllib.
    :param config_name: str. Bare profile name, without the .toml extension.
    :param subfolder: Optional[str]. Per-kind subfolder under configurations (e.g. "loggers", "watchdogs").
    :return: dict[str, Any]. Parsed TOML content as a plain, nested dict.
    """
    resolved_path = ProjectPaths().config_file(config_name, subfolder=subfolder, extension=".toml")

    if not resolved_path.exists():
        error_msg = (
            f"Config profile '{config_name}' not found. Searched folder: {resolved_path.parent}. "
            f"Resolved absolute path: {resolved_path}."
        )
        raise FileNotFound(description=error_msg)

    try:
        with resolved_path.open("rb") as config_file:
            parsed: dict[str, Any] = tomllib.load(config_file)
    except tomllib.TOMLDecodeError as exc:
        error_msg = f"Failed to parse '{resolved_path}' as TOML - malformed syntax. Underlying error: {exc}"
        raise IncorrectDataStructure(description=error_msg) from exc

    return parsed


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """
    Deep-merges override onto base: nested tables (dicts) merge recursively key by key, while scalars and lists
    are replaced wholesale by the override's value. Neither input is mutated.
    :param base: dict[str, Any]. Base mapping, e.g. the parsed tracked base profile.
    :param override: dict[str, Any]. Override mapping, e.g. the parsed partial overlay profile.
    :return: dict[str, Any]. New mapping with override applied on top of base.
    """
    merged = dict(base)
    for key, override_value in override.items():
        base_value = merged.get(key)
        if isinstance(base_value, dict) and isinstance(override_value, dict):
            merged[key] = _deep_merge(base_value, override_value)
        else:
            merged[key] = override_value
    return merged


def load_config[T: _NamedTupleLike](
    config_name: str, target: type[T], subfolder: str | None = None, base_name: str | None = None
) -> T:
    """
    Loads a TOML configuration profile into a typed NamedTuple instance.

    Resolves the file through Project Paths, parses it with the standard-library tomllib, and loads the parsed
    tree into target with typedload. Silent on success - never logs, never prints. Every failure mode raises a
    diagnostic-rich exception from the existing exception system instead: a missing file, malformed TOML, and a
    shape mismatch against target are each reported distinctly. When base_name is given, base_name is parsed as
    the base profile and config_name is parsed and deep-merged over it as a partial overlay (see ADR 0006)
    before the single, strict typedload call; a missing base_name file raises the same FileNotFound-style error
    as a missing config_name file. Loading is always strict (basiccast=False, failonextra=True), whether or not
    base_name is given.
    :param config_name: str. Bare profile name, without the .toml extension.
    :param target: type[T]. NamedTuple type the parsed file is loaded into.
    :param subfolder: Optional[str]. Per-kind subfolder under configurations (e.g. "loggers", "watchdogs").
        Default value is None.
    :param base_name: Optional[str]. Bare name of a base profile, parsed from the same subfolder, that
        config_name is deep-merged over as a partial overlay. Default value is None (single-file load).
    :return: T. Instance of target populated from the resolved, possibly merged configuration.
    """
    parsed = _parse_toml_profile(config_name, subfolder)

    if base_name is not None:
        base_parsed = _parse_toml_profile(base_name, subfolder)
        parsed = _deep_merge(base_parsed, parsed)

    try:
        return typedload.load(parsed, target, basiccast=False, failonextra=True)
    except TypedloadException as exc:
        error_msg = (
            f"Contents of profile '{config_name}' do not match the shape of {target.__name__}. Underlying error: {exc}"
        )
        raise IncorrectDataStructure(description=error_msg) from exc


if __name__ == "__main__":
    from src.utils.application_config_data import ApplicationConfigData

    config_data = load_config("python_repo", ApplicationConfigData)

    print(f"name: {config_data.name}")
