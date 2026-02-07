"""
Exceptions

SW Pattern: Strategy
"""

from src.exceptions.custom_exception import CustomException
from src.exceptions.development_exception import NoProperOptionInIf
from src.utils.envs import Envs
from src.utils.logger import Logger


class ExceptionExecutioner:
    """
    Class for executing and logging custom exceptions in unified way.

    Note: When running unit tests, logging is automatically disabled by checking the ENV_RUNNING_UNIT_TESTS
    environment variable. This prevents logger initialization issues during test execution.
    """

    def __init__(self, exception_class: type[CustomException]) -> None:
        self._exception_class = exception_class

    def log_and_raise(self, description: str | None = None) -> None:
        """
        Logs the exception and after raises it.
        :param description:
        """
        env = Envs()
        exc = self._exception_class() if description is None else self._exception_class(description)  # type: ignore[call-arg]
        if not env.get_running_unit_tests():
            Logger().error(exc.get_description())
        raise exc


if __name__ == "__main__":
    ExceptionExecutioner(NoProperOptionInIf).log_and_raise()
    print("THIS SHOULD NOT BE PRINTED")
