"""
Config Loader - foundational, Logger-free loading of TOML configuration files into typed NamedTuples.

Resolves a bare profile name through Project Paths, parses it with the standard-library tomllib, and loads the
parsed tree into a target NamedTuple with typedload. This is the single loading mechanism shared by Application
Config, Component Config, and the Logger's own profile file - see ADR 0001 and ADR 0003. Per ADR 0001, this
module must never import the project Logger: it is silent on success and reports every failure through
diagnostic-rich exceptions instead.

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


def load_config[T: _NamedTupleLike](config_name: str, target: type[T], subfolder: str | None = None) -> T:
    """
    Loads a TOML configuration profile into a typed NamedTuple instance.

    Resolves the file through Project Paths, parses it with the standard-library tomllib, and loads the parsed
    tree into target with typedload. Silent on success - never logs, never prints. Every failure mode raises a
    diagnostic-rich exception from the existing exception system instead: a missing file, malformed TOML, and a
    shape mismatch against target are each reported distinctly.
    :param config_name: str. Bare profile name, without the .toml extension.
    :param target: type[T]. NamedTuple type the parsed file is loaded into.
    :param subfolder: Optional[str]. Per-kind subfolder under configurations (e.g. "loggers", "watchdogs").
        Default value is None.
    :return: T. Instance of target populated from the resolved configuration file.
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
            parsed = tomllib.load(config_file)
    except tomllib.TOMLDecodeError as exc:
        error_msg = f"Failed to parse '{resolved_path}' as TOML - malformed syntax. Underlying error: {exc}"
        raise IncorrectDataStructure(description=error_msg) from exc

    try:
        return typedload.load(parsed, target)
    except TypedloadException as exc:
        error_msg = (
            f"Contents of '{resolved_path}' do not match the shape of {target.__name__}. Underlying error: {exc}"
        )
        raise IncorrectDataStructure(description=error_msg) from exc


if __name__ == "__main__":
    from src.utils.application_config_data import ApplicationConfigData

    config_data = load_config("python_repo", ApplicationConfigData)

    print(f"name: {config_data.name}")
