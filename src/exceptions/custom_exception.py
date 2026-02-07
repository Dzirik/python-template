"""
Exception

Usage can be found in development_exception file.
Executionar, which represents usage in classes, is in exception_executionar file.
"""


class CustomException(Exception):  # noqa: N818
    """
    Parent class for all exceptions.
    """

    def __init__(self, group_name: str) -> None:
        """
        :param group_name: str. Name of the group of exceptions.
        """
        Exception.__init__(self)

        self._group_name = group_name
        self._code: int = 0  # Code of the exception.
        self._description: str = ""  # Description of the exception.

    def get_description(self) -> str:
        """
        Returns the description of the exception.
        :return: str
        """
        return str(self._code) + " " + self._group_name + " " + self._description

    def __str__(self) -> str:
        """
        Overrides the print method.
        :return: str. The description of the exception.
        """
        return self.get_description()
