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
