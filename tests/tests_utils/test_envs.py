"""
Tests for Envs class.
"""

from collections.abc import Iterator
from typing import Any

import pytest

from src.exceptions.development_exception import NotValidOperation
from src.utils.application_config import ApplicationConfig
from src.utils.envs import Envs
from src.utils.logger import Logger
from src.utils.singleton_meta import Singleton


@pytest.fixture(autouse=True)
def _restore_singleton_instances() -> Iterator[None]:
    """
    Snapshots and restores Singleton._instances around each test in this module.

    Envs.set_config's and Envs.set_logger's guards (and Singleton.reset(), used here to re-open the "before
    instantiation" window) all read or mutate the shared, process-wide Singleton._instances cache - restoring
    it afterwards keeps this module from leaking state into other test modules that rely on
    ApplicationConfig/Logger staying cached across the pytest session.
    :return: Iterator[None]. Yields once, restoring the snapshot on resume.
    """
    snapshot: dict[Any, Any] = dict(Singleton._instances)
    yield
    Singleton._instances.clear()
    Singleton._instances.update(snapshot)


def test_set_config_succeeds_before_application_config_instantiated() -> None:
    """
    Tests that Envs.set_config writes the environment variable when ApplicationConfig has not been
    instantiated yet - the legitimate, pre-instantiation window.
    """
    Singleton.reset()
    assert ApplicationConfig not in Singleton._instances

    Envs.set_config("python_repo")

    assert Envs.get_config() == "python_repo"


def test_set_config_raises_after_application_config_instantiated() -> None:
    """
    Tests that Envs.set_config raises NotValidOperation once ApplicationConfig has already been
    instantiated, instead of silently writing an environment variable the cached instance will never
    re-read.
    """
    ApplicationConfig()
    assert ApplicationConfig in Singleton._instances

    with pytest.raises(NotValidOperation):
        Envs.set_config("python_repo")


def test_reset_then_set_config_reopens_the_window() -> None:
    """
    Tests that Singleton.reset() reopens the legitimate "before instantiation" window: a reset-then-
    set_config sequence succeeds even though ApplicationConfig had already been instantiated.
    """
    ApplicationConfig()
    with pytest.raises(NotValidOperation):
        Envs.set_config("python_repo")

    Singleton.reset()
    Envs.set_config("python_repo")

    assert Envs.get_config() == "python_repo"


def test_set_logger_succeeds_before_logger_instantiated() -> None:
    """
    Tests that Envs.set_logger writes the environment variable when Logger has not been instantiated yet -
    the legitimate, pre-instantiation window.
    """
    Singleton.reset()
    assert Logger not in Singleton._instances

    Envs.set_logger("logger_console")

    assert Envs.get_logger() == "logger_console"


def test_set_logger_raises_after_logger_instantiated() -> None:
    """
    Tests that Envs.set_logger raises NotValidOperation once Logger has already been instantiated, mirroring
    the set_config guard.
    """
    Logger()
    assert Logger in Singleton._instances

    with pytest.raises(NotValidOperation):
        Envs.set_logger("logger_console")
