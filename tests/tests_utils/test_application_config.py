"""
Tests for ApplicationConfig class.
"""

import ast
import inspect
import os
import subprocess
import sys
from pathlib import Path

from src.utils import application_config as config_module
from src.utils.application_config import ApplicationConfig
from src.utils.application_config_data import ApplicationConfigData
from src.utils.envs import Envs

_REPO_ROOT = Path(__file__).resolve().parents[2]


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
    through Envs - name is set authoritatively from the selection (see ADR 0006), not read from the TOML file,
    so this holds regardless of what (if anything) a profile's own name field says.
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


def test_config_partial_overlay_round_trip(tmp_path: Path) -> None:
    """
    Tests that a partial overlay - one that sets only some keys - deep-merges over the tracked "python_repo"
    base (base_name="python_repo", see ADR 0006): a key the overlay omits (param_ntb_execution) falls back to
    the base, a key it does set (path.data) wins, and the resulting name is the selection itself rather than
    anything read from either TOML file - the overlay file never even sets a name field.

    Runs in a subprocess (mirroring test_cwd_independence.py) because ApplicationConfig is a Singleton cached
    for the whole pytest session, so instantiating it in-process would just return whatever instance an earlier
    test already created instead of exercising this profile.
    """
    configurations_folder = tmp_path / "configurations"
    configurations_folder.mkdir(parents=True)
    (configurations_folder / "python_repo.toml").write_text(
        'name = "python_repo"\n'
        "\n"
        "[path]\n"
        'data = "data"\n'
        "\n"
        "[param_ntb_execution]\n"
        "use_default = true\n"
        "convert_to_html = true\n"
        'ntb_path = "notebooks/template/template_parameterized_execution_notebook.ipynb"\n'
        'output_folder = "reports"\n'
        'notebook_executioner_params = [{ n = 1.0, a = 1.0, b = 1.0, title = "Only" }]\n'
    )
    (configurations_folder / "partial_overlay.toml").write_text('[path]\ndata = "overlay-data"\n')

    script = (
        "from src.utils.envs import Envs\n"
        f"Envs.set_project_root_override({str(tmp_path)!r})\n"
        "Envs.set_config('partial_overlay')\n"
        "from src.utils.application_config import ApplicationConfig\n"
        "c = ApplicationConfig().get_data()\n"
        "print(c.name)\n"
        "print(c.path.data)\n"
        "print(c.param_ntb_execution.use_default)\n"
        "print(c.param_ntb_execution.output_folder)\n"
    )

    subprocess_env = dict(os.environ, PYTHONPATH=str(_REPO_ROOT))
    result = subprocess.run(  # noqa: S603  # nosec B603
        [sys.executable, "-c", script],
        cwd=str(tmp_path),
        env=subprocess_env,
        capture_output=True,
        text=True,
        check=True,
    )

    name, data_path, use_default, output_folder = result.stdout.strip().splitlines()
    assert name == "partial_overlay"
    assert Path(data_path) == tmp_path / "overlay-data"
    assert use_default == "True"
    assert output_folder == str(tmp_path / "reports")


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
