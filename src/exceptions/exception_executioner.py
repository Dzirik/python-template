"""
Exceptions

SW Pattern: Strategy
"""

from typing import NoReturn

from src.exceptions.custom_exception import CustomException
from src.exceptions.development_exception import NoProperOptionInIf
from src.utils.logger import Logger


class ExceptionExecutioner:
    """
    Class for executing and logging custom exceptions in unified way.
    """

    def __init__(self, exception_class: type[CustomException]) -> None:
        self._exception_class = exception_class

    def log_and_raise(self, description: str | None = None) -> NoReturn:
        """
        Logs the exception together with a real traceback and after raises it.
        :param description: str | None. Optional custom description passed to the exception constructor.
        """
        exc = self._exception_class() if description is None else self._exception_class(description)  # type: ignore[call-arg]
        try:
            raise exc
        except CustomException:
            Logger().exception(exc.get_description())
            raise


if __name__ == "__main__":
    # log_and_raise is now typed NoReturn - any code placed after this call would be flagged unreachable by mypy.
    ExceptionExecutioner(NoProperOptionInIf).log_and_raise()
