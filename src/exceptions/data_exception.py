"""
Exception for data purpose.
"""

from src.exceptions.custom_exception import CustomException


class DataException(CustomException):
    """
    Exception for working with data.
    """

    def __init__(self) -> None:
        CustomException.__init__(self, "Data.")


class NoData(DataException):
    """
    Exception for data not available.
    """

    def __init__(self, description: str = "Data not available.") -> None:
        DataException.__init__(self)
        self._code = 101
        self._description = description


class IncorrectDataStructure(DataException):
    """
    Exception for not passing the proper data strucrue.
    """

    def __init__(self, description: str = "Incorrect data structure.") -> None:
        DataException.__init__(self)
        self._code = 102
        self._description = description


class FileNotFound(DataException):
    """
    Exception for the case when file was not found.
    """

    def __init__(self, description: str = "File not found.") -> None:
        DataException.__init__(self)
        self._code = 103
        self._description = description


class MismatchedDimension(DataException):
    """
    Exception for the case when the dimension of data does not match.
    """

    def __init__(self, description: str = "Dimension does not fit.") -> None:
        DataException.__init__(self)
        self._code = 104
        self._description = description


class WrongSorting(DataException):
    """
    Exception for the case when the dimension of data does not match.
    """

    def __init__(self, description: str = "Wrong sorting.") -> None:
        DataException.__init__(self)
        self._code = 105
        self._description = description
