"""
Tests for Logger class.
"""

import time

from src.utils.logger import Logger


def test_logger_singleton() -> None:
    """
    Tests that Logger follows singleton pattern - same instance returned.
    """
    logger1 = Logger()
    logger2 = Logger()
    assert logger1 is logger2


def test_logger_initialization() -> None:
    """
    Tests that Logger initializes without errors.
    """
    logger = Logger()
    assert logger is not None
    assert logger.get() is not None


def test_logger_debug() -> None:
    """
    Tests debug logging level.
    """
    logger = Logger()
    # Should not raise any exceptions
    logger.debug("Test debug message")


def test_logger_info() -> None:
    """
    Tests info logging level.
    """
    logger = Logger()
    # Should not raise any exceptions
    logger.info("Test info message")


def test_logger_warning() -> None:
    """
    Tests warning logging level.
    """
    logger = Logger()
    # Should not raise any exceptions
    logger.warning("Test warning message")


def test_logger_error() -> None:
    """
    Tests error logging level.
    """
    logger = Logger()
    # Should not raise any exceptions
    logger.error("Test error message")


def test_logger_critical() -> None:
    """
    Tests critical logging level.
    """
    logger = Logger()
    # Should not raise any exceptions
    logger.critical("Test critical message")


def test_logger_timer_integration() -> None:
    """
    Tests timer integration with logger.
    """
    logger = Logger()

    # Start timer
    logger.start_timer("test_process")

    # Add some delay
    time.sleep(0.05)

    # Set meantime checkpoint
    logger.set_meantime("checkpoint_1")

    # Add more delay
    time.sleep(0.05)

    # Set another checkpoint
    logger.set_meantime("checkpoint_2")

    # End timer
    logger.end_timer()

    # If we got here without exceptions, the test passed


def test_logger_multiple_timer_cycles() -> None:
    """
    Tests multiple timer start/end cycles.
    """
    logger = Logger()

    # First cycle
    logger.start_timer("cycle_1")
    time.sleep(0.02)
    logger.set_meantime("cycle_1_checkpoint")
    logger.end_timer()

    # Second cycle
    logger.start_timer("cycle_2")
    time.sleep(0.02)
    logger.set_meantime("cycle_2_checkpoint")
    logger.end_timer()

    # If we got here without exceptions, the test passed


def test_logger_get_method() -> None:
    """
    Tests the get() method returns the underlying logger.
    """
    logger = Logger()
    underlying_logger = logger.get()
    assert underlying_logger is not None
