"""
Capstone acceptance test for the config/logger decoupling project.

Proves the headline property of the whole feature - launch method / current working directory is irrelevant -
by exercising the public APIs (``ApplicationConfig``, ``Logger``, ``WatchdogConfig``, ``ProjectPaths``) from a
working directory far away from the repository and asserting identical resolution to a repo-root run.

``ApplicationConfig`` and ``Logger`` are Singletons (``src/utils/singleton_meta.py``) cached for the whole pytest
session - by the time this module runs, many other test files have almost certainly already instantiated them
from whatever CWD was active at the time. Calling ``ApplicationConfig()``/``Logger()`` in-process after a
``monkeypatch.chdir()`` would therefore just return the pre-existing cached instance, proving nothing about
CWD-independence. Those two are instead exercised in fresh subprocesses (mirroring
``tests/tests_utils/test_logger.py::test_logger_file_handler_lands_in_project_paths_logs``), one launched with
``cwd=<repo_root>`` and one with ``cwd=<tmp_path>``, comparing their stdout. ``WatchdogConfig`` and
``ProjectPaths`` are plain classes re-parsed on every construction, so they are safe to compare in-process via
``monkeypatch.chdir()``.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from src.configurations.watchdog_config import WatchdogConfig
from src.utils.project_paths import ProjectPaths

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_probe_script(script: str, cwd: Path) -> str:
    """
    Runs script in a fresh Python subprocess rooted at cwd and returns its stdout.

    "src" is not installed into the venv - it is only importable when the repo root is on sys.path, which
    normally happens implicitly because commands are run from the repo root. The whole point of these tests is
    to run from a different cwd, so the repo root is added via PYTHONPATH instead.
    :param script: str. Python source to execute via ``python -c``.
    :param cwd: Path. Working directory to launch the subprocess from.
    :return: str. Captured standard output of the subprocess.
    """
    subprocess_env = dict(os.environ, PYTHONPATH=str(_REPO_ROOT))
    result = subprocess.run(  # noqa: S603  # nosec B603
        [sys.executable, "-c", script],
        cwd=str(cwd),
        env=subprocess_env,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def test_config_resolves_identically_regardless_of_cwd(tmp_path: Path) -> None:
    """
    Tests that ApplicationConfig() resolves the same profile name and the same absolute I/O paths whether the
    process was launched from the repo root or from a directory far away from it.

    Runs in two subprocesses (rather than in-process with monkeypatch.chdir) because ApplicationConfig is a
    Singleton cached for the whole pytest session - other tests may already have instantiated it before this
    test runs, so asserting on the in-process instance after a chdir would not prove anything about
    CWD-independence. The profile is pinned to "python_repo" (tracked in git, unlike the personal profile) so
    both runs are guaranteed to load the exact same source file.
    """
    script = (
        "from src.utils.envs import Envs\n"
        "Envs.set_config('python_repo')\n"
        "from src.utils.application_config import ApplicationConfig\n"
        "c = ApplicationConfig().get_data()\n"
        "print(c.name)\n"
        "print(c.path.data)\n"
        "print(c.param_ntb_execution.ntb_path)\n"
        "print(c.param_ntb_execution.output_folder)\n"
    )

    stdout_from_repo_root = _run_probe_script(script, cwd=_REPO_ROOT)
    stdout_from_far_away_cwd = _run_probe_script(script, cwd=tmp_path)

    assert stdout_from_repo_root == stdout_from_far_away_cwd

    name, data_path, ntb_path, output_folder = stdout_from_repo_root.strip().splitlines()
    assert name == "python_repo"
    assert Path(data_path).is_absolute()
    assert Path(ntb_path).is_absolute()
    assert Path(output_folder).is_absolute()


def test_logger_resolves_identically_regardless_of_cwd(tmp_path: Path) -> None:
    """
    Tests that Logger() redirects a file-backed profile to the same absolute ProjectPaths logs folder, and that
    an actual log file lands there, whether the process was launched from the repo root or from a directory far
    away from it.

    Runs in two subprocesses for the same Singleton-caching reason as test_config_resolves_identically_regardless
    _of_cwd above - see also test_logger_file_handler_lands_in_project_paths_logs in test_logger.py, whose
    subprocess-invocation approach this mirrors.
    """
    script = (
        "from src.utils.envs import Envs\n"
        "Envs.set_logger('logger_file_limit_console')\n"
        "from src.utils.logger import Logger\n"
        "Logger().info('probe')\n"
        "from src.utils.project_paths import ProjectPaths\n"
        "print(ProjectPaths().logs)\n"
    )

    logs_dir_from_repo_root = Path(_run_probe_script(script, cwd=_REPO_ROOT).strip().splitlines()[-1])
    logs_dir_from_far_away_cwd = Path(_run_probe_script(script, cwd=tmp_path).strip().splitlines()[-1])

    assert logs_dir_from_repo_root == logs_dir_from_far_away_cwd
    assert logs_dir_from_repo_root.is_absolute()
    assert any(logs_dir_from_repo_root.glob("*.log"))


def test_watchdog_config_resolves_identically_regardless_of_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Tests that WatchdogConfig(name).get_data() returns identical data whether constructed from the default CWD
    or from a directory far away from it.

    Safe to test in-process (unlike ApplicationConfig/Logger above): WatchdogConfig is a plain BaseComponentConfig
    subclass, not a Singleton - src/configurations/watchdog_config.py and src/utils/base_component_config.py show
    every construction independently re-parses the .conf file via load_config, which resolves the file path through
    ProjectPaths rather than the CWD, so there is no cross-test caching to work around.
    """
    baseline = WatchdogConfig("watchdog_cmd_01").get_data()

    monkeypatch.chdir(tmp_path)
    from_far_away_cwd = WatchdogConfig("watchdog_cmd_01").get_data()

    assert from_far_away_cwd.name == baseline.name
    assert from_far_away_cwd.workers == baseline.workers


def test_project_paths_io_locations_resolve_identically_regardless_of_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Tests that root, data, logs, reports, and configurations all resolve to identical absolute paths whether
    ProjectPaths() is constructed from the default CWD or from a directory far away from it.

    Safe to test in-process: ProjectPaths is not a Singleton either, so constructing a second instance after
    monkeypatch.chdir independently recomputes the root instead of returning a cached value.
    """
    baseline = ProjectPaths()

    monkeypatch.chdir(tmp_path)
    from_far_away_cwd = ProjectPaths()

    assert from_far_away_cwd.root == baseline.root
    assert from_far_away_cwd.data == baseline.data
    assert from_far_away_cwd.logs == baseline.logs
    assert from_far_away_cwd.reports == baseline.reports
    assert from_far_away_cwd.configurations == baseline.configurations
