"""
Tests for Timer class.
"""

import time

from pandas import DataFrame

from src.utils.timer import Timer


def test_timer_initialization() -> None:
    """
    Tests that Timer initializes without errors.
    """
    timer = Timer()
    assert timer is not None


def test_timer_start() -> None:
    """
    Tests that timer starts without errors.
    """
    timer = Timer()
    timer.start(print_results_local=False)


def test_timer_set_meantime() -> None:
    """
    Tests setting meantime checkpoint.
    """
    timer = Timer()
    timer.start(print_results_local=False)
    time.sleep(0.05)
    timer.set_meantime("checkpoint_1", print_results_local=False)


def test_timer_get_meantime() -> None:
    """
    Tests get_meantime returns tuple of floats.
    """
    timer = Timer()
    timer.start(print_results_local=False)
    time.sleep(0.05)
    diff_s, diff_m = timer.get_meantime("checkpoint_1")

    assert isinstance(diff_s, float)
    assert isinstance(diff_m, float)
    assert diff_s > 0


def test_timer_end() -> None:
    """
    Tests ending timer.
    """
    timer = Timer()
    timer.start(print_results_local=False)
    time.sleep(0.05)
    timer.end("final", print_results_local=False)


def test_timer_get_data() -> None:
    """
    Tests get_data returns correct structure.
    """
    timer = Timer()
    timer.start(print_results_local=False)
    time.sleep(0.02)
    timer.set_meantime("step_1", print_results_local=False)
    time.sleep(0.02)
    timer.end("step_2", print_results_local=False)

    mean_times, cumulative_times, labels, df = timer.get_data()

    assert isinstance(mean_times, list)
    assert isinstance(cumulative_times, list)
    assert isinstance(labels, list)
    assert isinstance(df, DataFrame)
    assert len(mean_times) == 2
    assert len(cumulative_times) == 2
    assert len(labels) == 2


def test_timer_multiple_checkpoints() -> None:
    """
    Tests timer with multiple checkpoints.
    """
    timer = Timer()
    timer.start(print_results_local=False)

    time.sleep(0.02)
    timer.set_meantime("checkpoint_1", print_results_local=False)

    time.sleep(0.02)
    timer.set_meantime("checkpoint_2", print_results_local=False)

    time.sleep(0.02)
    timer.set_meantime("checkpoint_3", print_results_local=False)

    timer.end("final", print_results_local=False)

    mean_times, _cumulative_times, labels, _df = timer.get_data()

    assert len(mean_times) == 4
    assert len(labels) == 4
    assert "checkpoint_1" in labels
    assert "checkpoint_2" in labels
    assert "checkpoint_3" in labels
    assert "final" in labels
