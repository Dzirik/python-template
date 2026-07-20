"""
Tests for Exception classes.
"""

import logging
from collections.abc import Callable

import pytest

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
from src.exceptions.exception_executioner import ExceptionExecutioner


def test_custom_exception_initialization() -> None:
    """
    Tests CustomException initialization.
    """
    exc = CustomException("Test")
    assert exc is not None


def test_no_data_exception_custom_message() -> None:
    """
    Tests NoData exception with custom message.
    """
    custom_msg = "Custom data not found"
    exc = NoData(custom_msg)
    description = exc.get_description()
    assert custom_msg in description


# Each entry is (factory building the exception instance, expected error code or None for group-level
# exceptions that carry no dedicated code, description substrings expected to appear in get_description()).
EXCEPTION_DESCRIPTION_CASES: list[tuple[Callable[[], CustomException], str | None, tuple[str, ...]]] = [
    (lambda: CustomException("TestGroup"), None, ("TestGroup",)),
    (DataException, None, ("Data.",)),
    (NoData, "101", ("Data.", "Data not available.")),
    (IncorrectDataStructure, "102", ("Incorrect data structure.",)),
    (FileNotFound, "103", ("File not found.",)),
    (MismatchedDimension, "104", ("Dimension does not fit.",)),
    (WrongSorting, "105", ("Wrong sorting.",)),
    (DevelopmentException, None, ("Development.",)),
    (NoProperOptionInIf, "301", ("Development.", "Option is not present in the if statement.")),
    (CheckFailed, "302", ("Check failed.",)),
    (NotValidOperation, "303", ("Not valid operation.",)),
    (NotReadyFunctionality, "304", ("Functionality not ready.",)),
    (IncorrectValue, "305", ("Incorrect value.",)),
]

EXCEPTION_DESCRIPTION_IDS = [
    "custom_exception_group_name",
    "data_exception_group",
    "no_data",
    "incorrect_data_structure",
    "file_not_found",
    "mismatched_dimension",
    "wrong_sorting",
    "development_exception_group",
    "no_proper_option_in_if",
    "check_failed",
    "not_valid_operation",
    "not_ready_functionality",
    "incorrect_value",
]


@pytest.mark.parametrize(
    "make_exception, expected_code, expected_fragments", EXCEPTION_DESCRIPTION_CASES, ids=EXCEPTION_DESCRIPTION_IDS
)
def test_exception_description_contains_code_and_fragments(
    make_exception: Callable[[], CustomException], expected_code: str | None, expected_fragments: tuple[str, ...]
) -> None:
    """
    Tests that each exception's get_description() contains its error code (when applicable) and its expected
    description fragments.
    :param make_exception: Callable[[], CustomException]. Factory building the exception instance under test.
    :param expected_code: str | None. Numeric error code expected in the description, or None for group-level
        exceptions (CustomException, DataException, DevelopmentException) that carry no dedicated code.
    :param expected_fragments: tuple[str, ...]. Description substrings expected to appear.
    """
    description = make_exception().get_description()
    assert isinstance(description, str)
    if expected_code is not None:
        assert expected_code in description
    for fragment in expected_fragments:
        assert fragment in description


def test_log_and_raise_raises_correct_exception_type() -> None:
    """
    Tests that ExceptionExecutioner.log_and_raise raises an instance of the exception class it was constructed
    with, proving the method never returns normally (effectively NoReturn).
    """
    with pytest.raises(NoProperOptionInIf):
        ExceptionExecutioner(NoProperOptionInIf).log_and_raise()


def test_log_and_raise_raises_with_custom_description() -> None:
    """
    Tests that log_and_raise passes a custom description through to the raised exception.
    """
    custom_message = "Custom development failure"
    with pytest.raises(NoProperOptionInIf) as exc_info:
        ExceptionExecutioner(NoProperOptionInIf).log_and_raise(custom_message)

    assert custom_message in exc_info.value.get_description()


def test_log_and_raise_logs_with_traceback(caplog: pytest.LogCaptureFixture) -> None:
    """
    Tests that log_and_raise logs the exception's description through Logger.exception, capturing a real
    traceback (exc_info) rather than a plain error message.
    """
    with caplog.at_level(logging.ERROR), pytest.raises(NoProperOptionInIf):
        ExceptionExecutioner(NoProperOptionInIf).log_and_raise()

    expected_text = "Option is not present in the if statement."
    matching_records = [record for record in caplog.records if expected_text in record.message]
    assert len(matching_records) == 1
    assert matching_records[0].exc_info is not None
