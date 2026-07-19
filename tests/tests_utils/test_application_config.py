"""
Tests for ApplicationConfig class.
"""

import ast
import inspect

from src.utils import application_config as config_module
from src.utils.application_config import ApplicationConfig
from src.utils.application_config_data import ApplicationConfigData
from src.utils.envs import Envs


def test_config_singleton() -> None:
    """
    Tests that ApplicationConfig follows singleton pattern - same instance returned.
    """
    config_1 = ApplicationConfig()
    config_2 = ApplicationConfig()
    assert config_1 is config_2


def test_config_get_data_returns_config_data_with_expected_name() -> None:
    """
    Tests that get_data returns an ApplicationConfigData instance whose name matches the active profile resolved
    through Envs - each shipped python_*.toml file sets its own name field to its own profile name.
    """
    config = ApplicationConfig()
    data = config.get_data()

    assert isinstance(data, ApplicationConfigData)
    assert data.name == Envs().get_config()


def test_config_get_data_as_dict_matches_get_data_name() -> None:
    """
    Tests that get_data_as_dict returns a dict whose name key/value matches get_data().name.
    """
    config = ApplicationConfig()

    data_as_dict = config.get_data_as_dict()

    assert isinstance(data_as_dict, dict)
    assert data_as_dict["name"] == config.get_data().name


def test_config_module_imports_no_project_logger() -> None:
    """
    Tests that the config module never imports the project Logger singleton.

    Only the actual import statements are inspected (not the docstrings, which are allowed to mention the
    architectural constraint by name) - this would fail if someone added ``from src.utils.logger import Logger``.
    """
    tree = ast.parse(inspect.getsource(config_module))
    imported_modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.append(node.module)
        elif isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)

    assert not any("logger" in module.lower() for module in imported_modules)
