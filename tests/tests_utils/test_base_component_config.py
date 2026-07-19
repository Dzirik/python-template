"""
Tests for Base Component Config module.
"""

import ast
import inspect

from src.utils import base_component_config as base_component_config_module


def test_base_component_config_module_imports_no_project_logger() -> None:
    """
    Tests that the base_component_config module never imports the project Logger singleton.

    Only the actual import statements are inspected (not the docstrings, which are allowed to mention the
    architectural constraint by name) - this would fail if someone added ``from src.utils.logger import Logger``.
    Per ADR 0001, loading a Component Config must never drag in the logging stack.
    """
    tree = ast.parse(inspect.getsource(base_component_config_module))
    imported_modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.append(node.module)
        elif isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)

    assert not any("logger" in module.lower() for module in imported_modules)
