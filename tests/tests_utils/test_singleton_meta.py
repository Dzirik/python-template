"""
Tests for Singleton metaclass.
"""

from collections.abc import Iterator
from typing import Any

import pytest

from src.utils.singleton_meta import Singleton


class _DummySingleton(metaclass=Singleton):
    """
    Minimal Singleton-based class used to exercise Singleton.reset() in isolation from the repository's real
    Singleton classes (ApplicationConfig, Logger).
    """

    def __init__(self) -> None:
        """
        Assigns a unique marker per instance so identity can be asserted trivially.
        """
        self.marker: object = object()


@pytest.fixture(autouse=True)
def _restore_singleton_instances() -> Iterator[None]:
    """
    Snapshots and restores Singleton._instances around each test in this module.

    Singleton._instances is process-wide, shared metaclass state - clearing it via Singleton.reset() (as
    these tests deliberately do) would otherwise leak into other test modules that rely on the repository's
    real Singleton classes (ApplicationConfig, Logger) staying cached across the pytest session.
    :return: Iterator[None]. Yields once, restoring the snapshot on resume.
    """
    snapshot: dict[Any, Any] = dict(Singleton._instances)
    yield
    Singleton._instances.clear()
    Singleton._instances.update(snapshot)


def test_singleton_returns_same_instance_before_reset() -> None:
    """
    Tests baseline Singleton behavior: repeated construction returns the identical instance.
    """
    instance_1 = _DummySingleton()
    instance_2 = _DummySingleton()

    assert instance_1 is instance_2


def test_reset_clears_instances_dict() -> None:
    """
    Tests that Singleton.reset() empties the shared _instances cache for every Singleton-based class.
    """
    _DummySingleton()
    assert _DummySingleton in Singleton._instances

    Singleton.reset()

    assert Singleton._instances == {}


def test_reset_then_instantiate_produces_fresh_instance() -> None:
    """
    Tests that a reset-then-instantiate sequence produces a new object rather than the previously cached one,
    and that the new object then becomes the cached instance for subsequent calls.
    """
    instance_1 = _DummySingleton()

    Singleton.reset()
    instance_2 = _DummySingleton()

    assert instance_1 is not instance_2
    assert instance_2 is _DummySingleton()
