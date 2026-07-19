"""
Tests for ProjectPaths class.
"""

import ast
import inspect
from pathlib import Path

import pytest

from src.constants.env_constants import ENV_PROJECT_ROOT
from src.utils import project_paths as project_paths_module
from src.utils.envs import Envs
from src.utils.project_paths import ProjectPaths


def test_project_paths_root_independent_of_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests that root resolves to the real project root regardless of the process current working directory.
    """
    monkeypatch.chdir(tmp_path)

    paths = ProjectPaths()

    assert (paths.root / "pyproject.toml").exists()


def test_project_paths_data_folder() -> None:
    """
    Tests that data resolves as root / "data".
    """
    paths = ProjectPaths()

    assert paths.data == paths.root / "data"


def test_project_paths_logs_folder() -> None:
    """
    Tests that logs resolves as root / "logs".
    """
    paths = ProjectPaths()

    assert paths.logs == paths.root / "logs"


def test_project_paths_reports_folder() -> None:
    """
    Tests that reports resolves as root / "reports".
    """
    paths = ProjectPaths()

    assert paths.reports == paths.root / "reports"


def test_project_paths_configurations_folder() -> None:
    """
    Tests that configurations resolves as root / "configurations".
    """
    paths = ProjectPaths()

    assert paths.configurations == paths.root / "configurations"


def test_project_paths_config_file_without_subfolder() -> None:
    """
    Tests that config_file resolves configurations/<name>.toml (the default extension) when no subfolder is
    given, matching how the Config Loader and the Logger resolve their own profiles.
    """
    paths = ProjectPaths()

    assert paths.config_file("arbitrary_profile") == paths.root / "configurations" / "arbitrary_profile.toml"


def test_project_paths_config_file_with_subfolder() -> None:
    """
    Tests that config_file resolves configurations/<subfolder>/<name>.toml when a subfolder is given, matching
    how the Logger resolves its own profile under configurations/loggers/.
    """
    paths = ProjectPaths()

    expected = paths.root / "configurations" / "loggers" / "logger_console.toml"
    assert paths.config_file("logger_console", subfolder="loggers") == expected


def test_project_paths_config_file_with_explicit_extension() -> None:
    """
    Tests that config_file resolves configurations/<name>.txt when an explicit extension is passed, matching
    how callers may override the default extension.
    """
    paths = ProjectPaths()

    expected = paths.root / "configurations" / "python_repo.txt"
    assert paths.config_file("python_repo", extension=".txt") == expected


def test_project_paths_root_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests that the ENV_PROJECT_ROOT override (set through Envs) repoints root to the given path.
    """
    # Register cleanup for the original (pre-test) environment state first, then let Envs perform the
    # actual write - monkeypatch restores whatever was present before this test regardless of the
    # direct os.environ write performed by Envs.set_project_root_override below.
    monkeypatch.setenv(ENV_PROJECT_ROOT, str(tmp_path))
    Envs.set_project_root_override(str(tmp_path))

    paths = ProjectPaths()

    assert paths.root == tmp_path.resolve()


def test_envs_get_project_root_override_round_trip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests that Envs.set_project_root_override / get_project_root_override round-trip correctly.
    """
    monkeypatch.delenv(ENV_PROJECT_ROOT, raising=False)
    assert Envs.get_project_root_override() is None

    monkeypatch.setenv(ENV_PROJECT_ROOT, str(tmp_path))
    Envs.set_project_root_override(str(tmp_path))

    assert Envs.get_project_root_override() == str(tmp_path)


def test_project_paths_creates_logs_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests that the logs directory is created under the overridden root if it does not already exist.
    """
    monkeypatch.setenv(ENV_PROJECT_ROOT, str(tmp_path))
    Envs.set_project_root_override(str(tmp_path))

    ProjectPaths()

    assert (tmp_path / "logs").exists()


def test_project_paths_module_imports_no_project_logger() -> None:
    """
    Tests that the project_paths module never imports the project Logger singleton.

    Only the actual import statements are inspected (not the docstrings, which are allowed to mention the
    architectural constraint by name) - this would fail if someone added ``from src.utils.logger import Logger``.
    """
    tree = ast.parse(inspect.getsource(project_paths_module))
    imported_modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.append(node.module)
        elif isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)

    assert not any("logger" in module.lower() for module in imported_modules)
