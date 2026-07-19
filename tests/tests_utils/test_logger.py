"""
Tests for Logger class.
"""

import ast
import inspect
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest

from src.utils import logger as logger_module
from src.utils.logger import Logger

ECHO_TIMESTAMP_PATTERN = re.compile(r"\d{2}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}: msg")


def test_logger_singleton() -> None:
    """
    Tests that Logger follows singleton pattern - same instance returned.
    """
    logger1 = Logger()
    logger2 = Logger()
    assert logger1 is logger2


def test_logger_initialization() -> None:
    """
    Tests that Logger initializes without errors.
    """
    logger = Logger()
    assert logger is not None
    assert logger.get() is not None


def test_logger_debug() -> None:
    """
    Tests debug logging level.
    """
    logger = Logger()
    # Should not raise any exceptions
    logger.debug("Test debug message")


def test_logger_info() -> None:
    """
    Tests info logging level.
    """
    logger = Logger()
    # Should not raise any exceptions
    logger.info("Test info message")


def test_logger_warning() -> None:
    """
    Tests warning logging level.
    """
    logger = Logger()
    # Should not raise any exceptions
    logger.warning("Test warning message")


def test_logger_error() -> None:
    """
    Tests error logging level.
    """
    logger = Logger()
    # Should not raise any exceptions
    logger.error("Test error message")


def test_logger_critical() -> None:
    """
    Tests critical logging level.
    """
    logger = Logger()
    # Should not raise any exceptions
    logger.critical("Test critical message")


def test_logger_timer_integration() -> None:
    """
    Tests timer integration with logger.
    """
    logger = Logger()

    # Start timer
    logger.start_timer("test_process")

    # Add some delay
    time.sleep(0.05)

    # Set meantime checkpoint
    logger.set_meantime("checkpoint_1")

    # Add more delay
    time.sleep(0.05)

    # Set another checkpoint
    logger.set_meantime("checkpoint_2")

    # End timer
    logger.end_timer()

    # If we got here without exceptions, the test passed


def test_logger_multiple_timer_cycles() -> None:
    """
    Tests multiple timer start/end cycles.
    """
    logger = Logger()

    # First cycle
    logger.start_timer("cycle_1")
    time.sleep(0.02)
    logger.set_meantime("cycle_1_checkpoint")
    logger.end_timer()

    # Second cycle
    logger.start_timer("cycle_2")
    time.sleep(0.02)
    logger.set_meantime("cycle_2_checkpoint")
    logger.end_timer()

    # If we got here without exceptions, the test passed


def test_logger_get_method() -> None:
    """
    Tests the get() method returns the underlying logger.

    Kept - not leaky low-value surface after all - because src/scripts_production/watchdog.py and checker.py
    call Logger().get() for stdlib-only functionality (addHandler, exc_info=True) the wrapper does not expose.
    """
    logger = Logger()
    underlying_logger = logger.get()
    assert underlying_logger is not None


def test_logger_info_echo_prints_timestamped_line(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Tests that info with a color echoes a timestamp-prefixed copy of the message to stdout.
    """
    logger = Logger()
    logger.info("msg", color="green")
    captured = capsys.readouterr()
    assert "msg" in captured.out
    assert ECHO_TIMESTAMP_PATTERN.search(captured.out) is not None


def test_logger_info_without_color_no_echo(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Tests that info without a color prints no timestamp-prefixed echo line, staying log-only.

    The console log handler may still emit the message, so the assertion targets the absence of the echo's
    own ``NN-NN-NN NN:NN:NN: msg`` format specifically, not the mere absence of the word ``msg``.
    """
    logger = Logger()
    logger.info("msg")
    captured = capsys.readouterr()
    assert ECHO_TIMESTAMP_PATTERN.search(captured.out) is None


def test_logger_echo_does_not_raise_across_levels(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Tests that the colored echo path does not raise for debug, warning, error and critical levels.
    """
    logger = Logger()
    logger.debug("msg", color="green")
    logger.warning("msg", color="yellow")
    logger.error("msg", color="red")
    logger.critical("msg", color="magenta")
    captured = capsys.readouterr()
    assert ECHO_TIMESTAMP_PATTERN.search(captured.out) is not None


def test_logger_module_imports_no_config_loader_or_config() -> None:
    """
    Tests that the logger module never imports ConfigLoader or ApplicationConfig.

    Only the actual import statements are inspected (not the docstrings) - this would fail if someone added
    ``from src.utils.config_loader import load_config`` or ``from src.utils.application_config import
    ApplicationConfig``. Logger must stay independently usable without the config-loading mechanism or the
    Application Config.
    """
    tree = ast.parse(inspect.getsource(logger_module))
    imported_modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.append(node.module)
        elif isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)

    assert not any(module in ("src.utils.config_loader", "src.utils.application_config") for module in imported_modules)


def test_logger_file_handler_lands_in_project_paths_logs(tmp_path: Path) -> None:
    """
    Tests that a file-backed logger profile writes its log file under the real, CWD-independent ProjectPaths logs
    folder, even when the process is spawned from a completely different working directory.

    Runs in a subprocess because Logger is a Singleton cached for the whole pytest session - other tests may
    already have created it with a console-only profile before this test runs, so asserting on the in-process
    instance would be unreliable.
    """
    repo_root = Path(__file__).resolve().parents[2]
    script = (
        "from src.utils.envs import Envs\n"
        "Envs.set_logger('logger_file_limit_console')\n"
        "from src.utils.logger import Logger\n"
        "Logger().info('probe')\n"
        "from src.utils.project_paths import ProjectPaths\n"
        "print(ProjectPaths().logs)\n"
    )
    # "src" is not installed into the venv - it is only importable when the repo root is on sys.path, which
    # normally happens implicitly because commands are run from the repo root. The whole point of this test is
    # to run from a different cwd, so the repo root is added via PYTHONPATH instead.
    subprocess_env = dict(os.environ, PYTHONPATH=str(repo_root))
    result = subprocess.run(  # noqa: S603  # nosec B603
        [sys.executable, "-c", script],
        cwd=str(tmp_path),
        env=subprocess_env,
        capture_output=True,
        text=True,
        check=True,
    )

    logs_dir = Path(result.stdout.strip().splitlines()[-1])
    assert any(logs_dir.glob("*.log"))


def test_logger_file_limit_console_configures_rotating_file_handler() -> None:
    """
    Tests that the logger_file_limit_console profile produces a RotatingFileHandler whose baseFilename lands
    under ProjectPaths().logs and whose maxBytes/backupCount match the profile's dictConfig values.

    Proves the INI-to-TOML named-key translation landed correctly (as opposed to, say, silently dropping the
    rotation settings and falling back to a plain FileHandler). Runs in a subprocess for the same Singleton
    reason as test_logger_file_handler_lands_in_project_paths_logs above.
    """
    repo_root = Path(__file__).resolve().parents[2]
    script = (
        "import logging\n"
        "import logging.handlers\n"
        "from src.utils.envs import Envs\n"
        "Envs.set_logger('logger_file_limit_console')\n"
        "from src.utils.logger import Logger\n"
        "Logger().info('probe')\n"
        "from src.utils.project_paths import ProjectPaths\n"
        "handlers = [h for h in logging.getLogger().handlers if isinstance(h, logging.handlers.RotatingFileHandler)]\n"
        "handler = handlers[0]\n"
        "print(ProjectPaths().logs)\n"
        "print(handler.baseFilename)\n"
        "print(handler.maxBytes)\n"
        "print(handler.backupCount)\n"
    )
    subprocess_env = dict(os.environ, PYTHONPATH=str(repo_root))
    result = subprocess.run(  # noqa: S603  # nosec B603
        [sys.executable, "-c", script],
        env=subprocess_env,
        capture_output=True,
        text=True,
        check=True,
    )

    # The profile's own console_handler also writes its two init/probe log lines to stdout, so only the last
    # four lines (our four explicit prints) are the ones under test.
    logs_dir_line, base_filename_line, max_bytes_line, backup_count_line = result.stdout.strip().splitlines()[-4:]
    assert Path(base_filename_line).parent == Path(logs_dir_line)
    assert int(max_bytes_line) == 5_242_880
    assert int(backup_count_line) == 2
