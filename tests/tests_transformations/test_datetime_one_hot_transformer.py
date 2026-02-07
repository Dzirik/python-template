"""
Tester

If using an exception assert statement, use following:
    env = Envs()
    env.set_running_unit_tests()
"""

from datetime import datetime
from typing import Any

import pytest
from numpy import array, array_equal, dtype, ndarray, zeros
from numpy.random import default_rng
from pandas import DatetimeIndex

from src.constants.global_constants import FP, P
from src.exceptions.development_exception import NoProperOptionInIf
from src.transformations.datetime_one_hot_transformer import DatetimeOneHotEncoderTransformer
from src.utils.envs import Envs
from src.utils.leap_year import is_leap

# Create a random number generator instance for tests
_rng = default_rng(seed=864)

# Fr-4, Sa-5, Sa-5
# Su-6, Mo-0, Tu-1
# We-2, Th-3, Mo-0
# Tu-1, Tu-1, Tu-1
INPUT_DATA = DatetimeIndex(
    [
        datetime(2016, 1, 1, 0, 1, 0),
        datetime(2016, 10, 1, 1, 1, 0),
        datetime(2016, 12, 24, 2, 1, 0),
        datetime(2017, 1, 1, 10, 1, 0),
        datetime(2017, 10, 6, 11, 1, 0),
        datetime(2017, 12, 5, 12, 1, 0),
        datetime(2018, 1, 3, 20, 1, 0),
        datetime(2018, 10, 4, 21, 1, 0),
        datetime(2018, 12, 24, 22, 1, 0),
        datetime(2019, 1, 1, 23, 1, 0),
        datetime(2019, 10, 1, 11, 1, 0),
        datetime(2019, 12, 24, 12, 1, 0),
    ]
)
NUMBER_OF_DAYS_IN_MONTH_NOT_LEAP_YEAR = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31,
}
NUMBER_OF_DAYS_IN_MONTH_LEAP_YEAR = {
    1: 31,
    2: 29,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31,
}

YEARS = [2019, 2020]
# 1.1.2019 - e.g. 1.1. of the first year is Tuesday - e.g. day_of_week = 1
DAY_OF_THE_WEEK_OF_THE_FIRST_DAY_OF_THE_FIRST_YEAR_FROM_YEARS_LIST = 1


def _generate_dates_and_one_hot_representation() -> tuple[list[datetime], ndarray[Any, dtype[Any]]]:
    """
    Generates dates and one-hot representation for two years.
    :return: Tuple[List[datetime], ndarray[Any, dtype[Any]]]. List of dates and its full one-hot representation.
    """
    # 1.1.2019 - e.g. 1.1. of the first year is Tuesday - e.g. day_of_week = 1
    day_of_week = DAY_OF_THE_WEEK_OF_THE_FIRST_DAY_OF_THE_FIRST_YEAR_FROM_YEARS_LIST
    years_months = []
    n = 0

    for year in YEARS:
        if is_leap(year):
            n = n + 366
            years_months.append(NUMBER_OF_DAYS_IN_MONTH_LEAP_YEAR)
        else:
            n = n + 365
            years_months.append(NUMBER_OF_DAYS_IN_MONTH_NOT_LEAP_YEAR)

    oh_output_corrrect = zeros((n * 24, 24 + 7 + 2 + 12 + len(YEARS)))
    dates = []

    # Reset the random generator for reproducibility
    test_rng = default_rng(seed=864)

    i = 0
    for year_index, year in enumerate(YEARS):
        for month, n_days in years_months[year_index].items():
            for day in range(1, n_days + 1):
                for hour in range(0, 24):
                    minute = test_rng.integers(0, 60)
                    second = test_rng.integers(0, 60)
                    dates.append(datetime(year, month, day, hour, minute, second))
                    oh_output_corrrect[i, hour] = 1  # hour, range 0-23
                    oh_output_corrrect[i, 24 + day_of_week % 7] = 1  # day of week, range 0-6
                    oh_output_corrrect[i, (24 + 7) + (1 if day_of_week % 7 in (5, 6) else 0)] = 1  # weekend
                    oh_output_corrrect[i, (24 + 7 + 2) + (month - 1)] = 1  # month, +(-1) has to be because it starts
                    # from one instead
                    oh_output_corrrect[i, (24 + 7 + 2 + 12) + year_index] = 1  # year index - 0 - (len(YEARS)-1)
                    # of zero range 1-12
                    i = i + 1
                day_of_week = day_of_week + 1
    return DatetimeIndex(dates), oh_output_corrrect


DATES, OH_OUTPUT_CORRECT = _generate_dates_and_one_hot_representation()
DATE_ATTR_NAME = "DATE_ATTR_NAME"
DATETIME_ATTR_NAMES = [
    "HOUR_0.0",
    "HOUR_1.0",
    "HOUR_2.0",
    "HOUR_3.0",
    "HOUR_4.0",
    "HOUR_5.0",
    "HOUR_6.0",
    "HOUR_7.0",
    "HOUR_8.0",
    "HOUR_9.0",
    "HOUR_10.0",
    "HOUR_11.0",
    "HOUR_12.0",
    "HOUR_13.0",
    "HOUR_14.0",
    "HOUR_15.0",
    "HOUR_16.0",
    "HOUR_17.0",
    "HOUR_18.0",
    "HOUR_19.0",
    "HOUR_20.0",
    "HOUR_21.0",
    "HOUR_22.0",
    "HOUR_23.0",
    "DAY_OF_WEEK_0.0",
    "DAY_OF_WEEK_1.0",
    "DAY_OF_WEEK_2.0",
    "DAY_OF_WEEK_3.0",
    "DAY_OF_WEEK_4.0",
    "DAY_OF_WEEK_5.0",
    "DAY_OF_WEEK_6.0",
    "WEEKEND_0.0",
    "WEEKEND_1.0",
    "MONTH_1.0",
    "MONTH_2.0",
    "MONTH_3.0",
    "MONTH_4.0",
    "MONTH_5.0",
    "MONTH_6.0",
    "MONTH_7.0",
    "MONTH_8.0",
    "MONTH_9.0",
    "MONTH_10.0",
    "MONTH_11.0",
    "MONTH_12.0",
] + ["YEAR_" + str(year) + ".0" for year in YEARS]
DATETIME_ATTR_NAMES_WITH_DATE_ATTR_NAME = [DATE_ATTR_NAME + "_" + name for name in DATETIME_ATTR_NAMES]


def _generate_data_for_min_intervals(min_interval: int = 24) -> tuple[list[datetime], ndarray[Any, dtype[Any]]]:
    """
    Generates data for testing minute intervals encoding.
    :param min_interval: int. Number of minutes in window.
    :return: Tuple[List[datetime], ndarray[Any, dtype[Any]]]. List of dates and its minutes interval one hot
                                                              representation.
    """
    dates = []
    n = 1000
    p = 60 * 24 // min_interval if 60 * 24 % min_interval == 0 else 60 * 24 // min_interval + 1
    oh_output_correct = zeros((n, p))

    # Reset the random generator for reproducibility
    test_rng = default_rng(seed=864)

    for i in range(n):
        hour = test_rng.integers(0, 24)
        minutes = test_rng.integers(0, 60)
        dates.append(datetime(2019, 10, 1, hour, minutes, test_rng.integers(0, 60)))
        oh_output_correct[i, (hour * 60 + minutes) // min_interval] = 1
    return DatetimeIndex(dates), oh_output_correct


@pytest.mark.parametrize(
    "min_interval, correct_n_of_intervals",
    [(59, 25), (60, 24), (61, 24), (119, 13), (120, 12), (121, 12), (29, 50), (30, 48), (31, 47)],
)
def test_min_intervals(min_interval: int, correct_n_of_intervals: int) -> None:
    """
    Test minutes window intervals during the day.
    :param min_interval: int.
    :param correct_n_of_intervals: int.
    """
    data, oh_output_correct = _generate_data_for_min_intervals(min_interval)
    t = DatetimeOneHotEncoderTransformer()
    oh_output_predicted = t.fit_predict(data, False, False, False, False, False, min_interval)
    assert oh_output_predicted.shape[1] == correct_n_of_intervals and array_equal(
        oh_output_correct, oh_output_predicted
    )


# pylint: disable=too-many-arguments
def _do_one_hot_encoding(
    type_of_method: str,
    fit_data: DatetimeIndex,
    prediction_data: DatetimeIndex,
    add_hours: bool,
    add_days_of_week: bool,
    add_weekend: bool,
    add_months: bool,
    add_years: bool,
) -> tuple[ndarray[Any, dtype[Any]], list[str], list[str]]:
    """
    Does one hot encoding based on settings.
    :param type_of_method: Type of transformation ("f" for fit, "p" for predict, "fp" for fit_predict).
    :param fit_data: DatetimeIndex. Data for fitting the transformation.
    :param prediction_data: DatetimeIndex. Data for prediction after the model is fitted.
    :param add_hours: bool. If include hours.
    :param add_days_of_week: bool. If include days of the week.
    :param add_weekend: bool. If include weekend.
    :param add_months: bool. If include months.
    :param add_years: bool. If include years.
    :return: Tuple[ndarray, List[str], List[str]]. One-hot transformation output matrix, column names without and
        with the original attribute name.
    """
    transformer = DatetimeOneHotEncoderTransformer()
    if type_of_method == FP:
        oh_output_predicted = transformer.fit_predict(
            fit_data, add_hours, add_days_of_week, add_weekend, add_months, add_years
        )
    elif type_of_method == P:
        transformer.fit(fit_data, add_hours, add_days_of_week, add_weekend, add_months, add_years)
        oh_output_predicted = transformer.predict(prediction_data)
    else:
        raise NoProperOptionInIf("test_datetime_one_hot_transformer")
    encoded_data_attributes_names = transformer.get_encoded_attribute_names()
    encoded_data_attributes_names_with_attr_name = transformer.get_encoded_attribute_names(DATE_ATTR_NAME)

    return oh_output_predicted, encoded_data_attributes_names, encoded_data_attributes_names_with_attr_name


# pylint: enable=too-many-arguments


def _generate_columns_indices(
    add_hours: bool, add_days_of_week: bool, add_weekend: bool, add_months: bool, add_years: bool
) -> list[int]:
    """
    # OH_OUTPUT_CORRECT[:, 0:24] hours
    # OH_OUTPUT_CORRECT[:, 24:(24+7)] days_of_week
    # OH_OUTPUT_CORRECT[:, (24+7):(24+7+2)] weekends
    # OH_OUTPUT_CORRECT[:, (24+7+2):(24+7+2+12)] months
    # OH_OUTPUT_CORRECT[:, (24+7+2+12):(24+7+2+12+len(YEARS)] years
    :param add_hours: bool. If include hours.
    :param add_days_of_week: bool. If include days of the week.
    :param add_weekend: bool. If include weekend.
    :param add_months: bool. If include months.
    :param add_years: bool. If include years.
    :return: List[int]. List of columns/indices to be selected.
    """
    column_indices: list[int] = []
    if add_hours:
        column_indices = column_indices + list(range(0, 24))
    if add_days_of_week:
        column_indices = column_indices + list(range(24, 24 + 7))
    if add_weekend:
        column_indices = column_indices + list(range(24 + 7, 24 + 7 + 2))
    if add_months:
        column_indices = column_indices + list(range(24 + 7 + 2, 24 + 7 + 2 + 12))
    if add_years:
        column_indices = column_indices + list(range(24 + 7 + 2 + 12, 24 + 7 + 2 + 12 + len(YEARS)))
    return column_indices


TEST_CONFIGURATIONS = [
    (P, DATES, True, True, True, True, True, OH_OUTPUT_CORRECT),
    (FP, DATES, True, True, True, True, True, OH_OUTPUT_CORRECT),
    (P, DATES, True, True, True, True, False, OH_OUTPUT_CORRECT),
    (FP, DATES, True, True, True, True, False, OH_OUTPUT_CORRECT),
    (P, DATES, True, True, True, False, True, OH_OUTPUT_CORRECT),
    (FP, DATES, True, True, True, False, True, OH_OUTPUT_CORRECT),
    (P, DATES, True, True, False, True, True, OH_OUTPUT_CORRECT),
    (FP, DATES, True, True, False, True, True, OH_OUTPUT_CORRECT),
    (P, DATES, True, False, True, True, True, OH_OUTPUT_CORRECT),
    (FP, DATES, True, False, True, True, True, OH_OUTPUT_CORRECT),
    (P, DATES, False, True, True, True, True, OH_OUTPUT_CORRECT),
    (FP, DATES, False, True, True, True, True, OH_OUTPUT_CORRECT),
    (P, DATES, True, True, True, False, False, OH_OUTPUT_CORRECT),
    (FP, DATES, True, True, True, False, False, OH_OUTPUT_CORRECT),
    (P, DATES, True, True, False, True, False, OH_OUTPUT_CORRECT),
    (FP, DATES, True, True, False, True, False, OH_OUTPUT_CORRECT),
    (P, DATES, True, False, True, True, False, OH_OUTPUT_CORRECT),
    (FP, DATES, True, False, True, True, False, OH_OUTPUT_CORRECT),
    (P, DATES, False, True, True, True, False, OH_OUTPUT_CORRECT),
    (FP, DATES, False, True, True, True, False, OH_OUTPUT_CORRECT),
    (P, DATES, True, True, False, False, True, OH_OUTPUT_CORRECT),
    (FP, DATES, True, True, False, False, True, OH_OUTPUT_CORRECT),
    (P, DATES, True, False, True, False, True, OH_OUTPUT_CORRECT),
    (FP, DATES, True, False, True, False, True, OH_OUTPUT_CORRECT),
    (P, DATES, False, True, True, False, True, OH_OUTPUT_CORRECT),
    (FP, DATES, False, True, True, False, True, OH_OUTPUT_CORRECT),
    (P, DATES, True, False, False, True, True, OH_OUTPUT_CORRECT),
    (FP, DATES, True, False, False, True, True, OH_OUTPUT_CORRECT),
    (P, DATES, False, True, False, True, True, OH_OUTPUT_CORRECT),
    (FP, DATES, False, True, False, True, True, OH_OUTPUT_CORRECT),
    (P, DATES, False, False, True, True, True, OH_OUTPUT_CORRECT),
    (FP, DATES, False, False, True, True, True, OH_OUTPUT_CORRECT),
    (P, DATES, True, True, False, False, False, OH_OUTPUT_CORRECT),
    (FP, DATES, True, True, False, False, False, OH_OUTPUT_CORRECT),
    (P, DATES, True, False, True, False, False, OH_OUTPUT_CORRECT),
    (FP, DATES, True, False, True, False, False, OH_OUTPUT_CORRECT),
    (P, DATES, True, False, False, True, False, OH_OUTPUT_CORRECT),
    (FP, DATES, True, False, False, True, False, OH_OUTPUT_CORRECT),
    (P, DATES, True, False, False, False, True, OH_OUTPUT_CORRECT),
    (FP, DATES, True, False, False, False, True, OH_OUTPUT_CORRECT),
    (P, DATES, False, True, True, False, False, OH_OUTPUT_CORRECT),
    (FP, DATES, False, True, True, False, False, OH_OUTPUT_CORRECT),
    (P, DATES, False, True, False, True, False, OH_OUTPUT_CORRECT),
    (FP, DATES, False, True, False, True, False, OH_OUTPUT_CORRECT),
    (P, DATES, False, True, False, False, True, OH_OUTPUT_CORRECT),
    (FP, DATES, False, True, False, False, True, OH_OUTPUT_CORRECT),
    (P, DATES, False, False, True, True, False, OH_OUTPUT_CORRECT),
    (FP, DATES, False, False, True, True, False, OH_OUTPUT_CORRECT),
    (P, DATES, False, False, True, False, True, OH_OUTPUT_CORRECT),
    (FP, DATES, False, False, True, False, True, OH_OUTPUT_CORRECT),
    (P, DATES, False, False, False, True, True, OH_OUTPUT_CORRECT),
    (FP, DATES, False, False, False, True, True, OH_OUTPUT_CORRECT),
    (P, DATES, True, False, False, False, False, OH_OUTPUT_CORRECT),
    (FP, DATES, True, False, False, False, False, OH_OUTPUT_CORRECT),
    (P, DATES, False, True, False, False, False, OH_OUTPUT_CORRECT),
    (FP, DATES, False, True, False, False, False, OH_OUTPUT_CORRECT),
    (P, DATES, False, False, True, False, False, OH_OUTPUT_CORRECT),
    (FP, DATES, False, False, True, False, False, OH_OUTPUT_CORRECT),
    (P, DATES, False, False, False, True, False, OH_OUTPUT_CORRECT),
    (FP, DATES, False, False, False, True, False, OH_OUTPUT_CORRECT),
    (P, DATES, False, False, False, False, True, OH_OUTPUT_CORRECT),
    (FP, DATES, False, False, False, False, True, OH_OUTPUT_CORRECT),
]


# pylint: disable=too-many-arguments
@pytest.mark.parametrize(
    "type_of_method, data, add_hours, add_days_of_week, add_weekend, add_months, add_years, correct_output",
    TEST_CONFIGURATIONS,
)
def test_output(
    type_of_method: str,
    data: DatetimeIndex,
    add_hours: bool,
    add_days_of_week: bool,
    add_weekend: bool,
    add_months: bool,
    add_years: bool,
    correct_output: ndarray[Any, dtype[Any]],
) -> None:
    """
    Tests correctness of ndarray output after transformation.
    :param type_of_method: str. Transformation type ("f" for fit, "p" for predict, "fp" for fit_predict).
    :param add_hours: bool. If include hours.
    :param add_days_of_week: bool. If include days of the week.
    :param add_weekend: bool. If include weekend.
    :param add_months: bool. If include months.
    :param add_years: bool. If include years.
    :correct_output: ndarray[Any, dtype[Any]].
    """
    oh_output_predicted, encoded_data_attributes_names, encoded_data_attributes_names_with_attr_name = (
        _do_one_hot_encoding(
            type_of_method, data, data, add_hours, add_days_of_week, add_weekend, add_months, add_years
        )
    )
    column_indices = _generate_columns_indices(add_hours, add_days_of_week, add_weekend, add_months, add_years)
    assert (
        array_equal(oh_output_predicted, correct_output[:, column_indices])
        and [DATETIME_ATTR_NAMES[i] for i in column_indices] == encoded_data_attributes_names
        and [DATETIME_ATTR_NAMES_WITH_DATE_ATTR_NAME[i] for i in column_indices]
        == encoded_data_attributes_names_with_attr_name
    )


# pylint: enable=too-many-arguments


def test_incorrect_input() -> None:
    """
    Tests exception raise situation when there is no option selected.
    """
    env = Envs()
    env.set_running_unit_tests()
    transformer = DatetimeOneHotEncoderTransformer()
    with pytest.raises(NoProperOptionInIf):
        transformer.fit(DATES, False, False, False, False, False)


def test_handle_unknown() -> None:
    """
    Tests correct output when prediction data is not present in the unseen data.
    """
    transformer = DatetimeOneHotEncoderTransformer()
    data = DatetimeIndex([datetime(2019, 1, 1, 1, 0, 0)])
    unseen_data = DatetimeIndex([datetime(2020, 2, 2, 2, 0, 0)])
    correct_output: ndarray[Any, dtype[Any]] = array([[0, 0, 0, 0, 0]])
    transformer.fit(data, True, True, True, True, True)
    output = transformer.predict(unseen_data)
    assert array_equal(output, correct_output)


def test_inverse() -> None:
    """
    Tests empty (returns None) inverse.
    """
    transformer = DatetimeOneHotEncoderTransformer()
    assert transformer.inverse(data=None) is None
