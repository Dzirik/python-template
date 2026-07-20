"""
Code for handling configurations through the repository.

The interface should be the same as in other configs, inheritance is not possible - cyrcular dependency.

A singleton pattern is used for that.

Usage can be found in the end of the file and in jupyter notebook
/notebooks/documentation/low_level_tools_documentation.py or
/docs/ low_level_tools_documentation.html.
"""

from pathlib import Path as FilePath
from typing import Any

from src.utils.application_config_data import ApplicationConfigData
from src.utils.config_loader import load_config
from src.utils.envs import Envs
from src.utils.project_paths import ProjectPaths
from src.utils.singleton_meta import Singleton


def _resolve_path(value: str, root: FilePath) -> str:
    """
    Resolves a config-supplied path value to an absolute path.

    Already-absolute values (e.g. a personal override like "E:/DATA") are returned unchanged; root-relative
    values (the bare, repo-relative values shipped in the tracked ``.conf`` files) are resolved against root.
    :param value: str. Path value as read from a config file, either absolute or root-relative.
    :param root: FilePath. Project root to resolve root-relative values against.
    :return: str. Absolute path.
    """
    candidate = FilePath(value)
    return str(candidate) if candidate.is_absolute() else str(root / candidate)


class ApplicationConfig(metaclass=Singleton):
    """
    Class for storing or configuration options for the repository.

    Singleton class.

    Takes settings from environmental variables or uses default "python_local.conf".

    Methods should the same as in src/utils/base_component_config.py

    The selected profile (Envs().get_config()) is deep-merged, as a partial overlay, over the tracked
    "python_repo" base profile - see ADR 0006. ``name`` on the resulting data is set authoritatively from the
    selection itself, not read from the TOML file: a partial overlay never needs to restate ``name``, and a
    mislabelled profile file cannot misreport its identity.
    """

    def __init__(self) -> None:
        self._env: Envs = Envs()
        self._data: ApplicationConfigData = load_config(
            self._env.get_config(), ApplicationConfigData, base_name="python_repo"
        )
        self._data = self._data._replace(name=self._env.get_config())

        root = ProjectPaths().root
        self._data = self._data._replace(
            path=self._data.path._replace(data=_resolve_path(self._data.path.data, root)),
            param_ntb_execution=self._data.param_ntb_execution._replace(
                ntb_path=_resolve_path(self._data.param_ntb_execution.ntb_path, root),
                output_folder=_resolve_path(self._data.param_ntb_execution.output_folder, root),
            ),
        )

    def get_data(self) -> ApplicationConfigData:
        """
        Gets the _profile as Profile NamedTuple class.
        :return: Profile. NamedTuple containing settings.
        """
        return self._data

    def get_data_as_dict(self) -> dict[Any, Any]:
        """
        Gets the data (named tuple) into dictionary.
        :return: Dict[Any, Any].
        """
        return dict(self._data._asdict())


if __name__ == "__main__":
    # change this variable if you want to test default
    USE_DEFAULT = True
    NONE_DEFAULT_PYTHON_CONFIG_NAME = "python_local"

    if not USE_DEFAULT:
        env = Envs()
        env.set_config(NONE_DEFAULT_PYTHON_CONFIG_NAME)

    config_1 = ApplicationConfig()
    config_2 = ApplicationConfig()
    c = ApplicationConfig()

    print("\n")
    print(f"Is it just one object? {config_1 is config_2}")

    print("\n")
    print(c.get_data().name)
    print(c.get_data().path.data)
