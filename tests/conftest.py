"""
Pytest configuration and fixtures for all tests.

This file contains shared fixtures and setup/teardown logic for the test suite.
"""

import os
from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment() -> None:
    """
    Set up the test environment before running any tests.

    This fixture:
    - Sets logger to console-only mode (avoids file path issues)
    - Creates the logs directory if it doesn't exist
    - Sets environment variable to indicate tests are running
    """
    # Use console-only logger for tests (avoids file path issues with relative paths)
    os.environ["ENV_LOGGER"] = "logger_console"

    # Create logs directory if it doesn't exist (for other purposes)
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Set environment variable to indicate tests are running
    os.environ["ENV_RUNNING_UNIT_TESTS"] = "True"
