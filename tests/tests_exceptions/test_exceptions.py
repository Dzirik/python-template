"""
Tests for Exception classes.
"""

from src.exceptions.custom_exception import CustomException
from src.exceptions.data_exception import (
    DataException,
    FileNotFound,
    IncorrectDataStructure,
    MismatchedDimension,
    NoData,
    WrongSorting,
)
from src.exceptions.development_exception import (
    CheckFailed,
    DevelopmentException,
    IncorrectValue,
    NoProperOptionInIf,
    NotReadyFunctionality,
    NotValidOperation,
)


def test_custom_exception_initialization() -> None:
    """
    Tests CustomException initialization.
    """
    exc = CustomException("Test")
    assert exc is not None


def test_custom_exception_get_description() -> None:
    """
    Tests CustomException get_description method.
    """
    exc = CustomException("TestGroup")
    description = exc.get_description()
    assert isinstance(description, str)
    assert "TestGroup" in description


def test_data_exception_initialization() -> None:
    """
    Tests DataException initialization.
    """
    exc = DataException()
    assert exc is not None
    assert "Data." in exc.get_description()


def test_no_data_exception() -> None:
    """
    Tests NoData exception.
    """
    exc = NoData()
    description = exc.get_description()
    assert "101" in description
    assert "Data." in description
    assert "Data not available." in description


def test_no_data_exception_custom_message() -> None:
    """
    Tests NoData exception with custom message.
    """
    custom_msg = "Custom data not found"
    exc = NoData(custom_msg)
    description = exc.get_description()
    assert custom_msg in description


def test_incorrect_data_structure_exception() -> None:
    """
    Tests IncorrectDataStructure exception.
    """
    exc = IncorrectDataStructure()
    description = exc.get_description()
    assert "102" in description
    assert "Incorrect data structure." in description


def test_file_not_found_exception() -> None:
    """
    Tests FileNotFound exception.
    """
    exc = FileNotFound()
    description = exc.get_description()
    assert "103" in description
    assert "File not found." in description


def test_mismatched_dimension_exception() -> None:
    """
    Tests MismatchedDimension exception.
    """
    exc = MismatchedDimension()
    description = exc.get_description()
    assert "104" in description
    assert "Dimension does not fit." in description


def test_wrong_sorting_exception() -> None:
    """
    Tests WrongSorting exception.
    """
    exc = WrongSorting()
    description = exc.get_description()
    assert "105" in description
    assert "Wrong sorting." in description


def test_development_exception_initialization() -> None:
    """
    Tests DevelopmentException initialization.
    """
    exc = DevelopmentException()
    assert exc is not None
    assert "Development." in exc.get_description()


def test_no_proper_option_in_if_exception() -> None:
    """
    Tests NoProperOptionInIf exception.
    """
    exc = NoProperOptionInIf()
    description = exc.get_description()
    assert "301" in description
    assert "Development." in description
    assert "Option is not present in the if statement." in description


def test_check_failed_exception() -> None:
    """
    Tests CheckFailed exception.
    """
    exc = CheckFailed()
    description = exc.get_description()
    assert "302" in description
    assert "Check failed." in description


def test_not_valid_operation_exception() -> None:
    """
    Tests NotValidOperation exception.
    """
    exc = NotValidOperation()
    description = exc.get_description()
    assert "303" in description
    assert "Not valid operation." in description


def test_not_ready_functionality_exception() -> None:
    """
    Tests NotReadyFunctionality exception.
    """
    exc = NotReadyFunctionality()
    description = exc.get_description()
    assert "304" in description
    assert "Functionality not ready." in description


def test_incorrect_value_exception() -> None:
    """
    Tests IncorrectValue exception.
    """
    exc = IncorrectValue()
    description = exc.get_description()
    assert "305" in description
    assert "Incorrect value." in description
