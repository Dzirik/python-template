"""
Singleton
"""

from typing import Any, ClassVar


class Singleton(type):
    """
    Singleton base class.
    """

    _instances: ClassVar[dict[Any, Any]] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """
        Controls instance creation to ensure only one instance exists per class.

        :param args: Any. Positional arguments for class instantiation.
        :param kwargs: Any. Keyword arguments for class instantiation.
        :return: Any. The singleton instance of the class.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    @classmethod
    def reset(cls) -> None:
        """
        Clears all cached singleton instances.

        Test-only: production code must never call this. It exists so tests can force a class built on this
        metaclass (e.g. ApplicationConfig, Logger) to construct a fresh instance on its next call - typically
        to exercise a different environment-variable selection - instead of paying the cost of an isolated
        subprocess. It clears the shared, process-wide cache for every Singleton-based class at once, not just
        one class, so any object references a test already holds keep pointing at the now-uncached old
        instance; only a subsequent call to the class re-triggers construction. See ``Envs.set_config`` for the
        counterpart that treats "already instantiated" as an error - calling this first re-opens that
        "before instantiation" window.
        :return: None.
        """
        cls._instances.clear()
