"""
Transformer

Creates one-hot encoding from datetime format depending on definition.

Converts the datetime index array into columns of numerical values for requested time attributes:
hours: 0-23,
days_of_week: Monday=0, Sunday=6,
weekend: 0: weekday, 1: weekend,
months: January=1, December=12,
years: yyyy format.
min_interval - For 60 minutes the same as for hours. In general division of the day per min_interval window.

Does not test validity of input except empty configuration - raises error.
"""

from typing import Any, NamedTuple

from numpy import array, concatenate, dtype, ndarray, zeros
from pandas import DatetimeIndex
from sklearn.preprocessing import OneHotEncoder

from src.exceptions.development_exception import NoProperOptionInIf
from src.exceptions.exception_executioner import ExceptionExecutioner
from src.transformations.base_transformer import BaseTransformer, TransformerDescription


class TimeAttributes(NamedTuple):
    """
    Tuple for storing which attributes should be created.
    """

    hours: bool
    days_of_week: bool
    weekend: bool
    months: bool
    years: bool
    min_inerval: int


class DatetimeOneHotEncoderTransformer(BaseTransformer):
    """
    Transforms a DatetimeIndex array to one-hot array. Options are:
    - attribute HOUR: 0-23,
    - attribute DAY_OF_WEEK: Monday=0, Sunday=6,
    - attribute WEEKEND: 0: weekday, 1: weekend,
    - attribute MONTH: January=1, December=12,
    - attribute YEAR: yyyy format.
    - attribute MINxx - For 60 minutes the same as for hours. In general division of the day per min_interval window.

    In addition, the class can return the captions for columns in format:
    <optional date time index attribute name>_<TIME_ATTRIBUTE_NAME>(HOUR, DAY_OF_WEEK, ... as specified above)_<number>.
    Example:
        'SOME_TIME_ATTRIBUTE_HOUR_0.0', 'SOME_TIME_ATTRIBUTE_HOUR_1.0', 'SOME_TIME_ATTRIBUTE_HOUR_2.0',
    """

    def __init__(self, handle_unknown: str = "ignore") -> None:
        transformer_description = TransformerDescription(
            input_type=[DatetimeIndex], input_elements_type=[None], output_type=[ndarray], output_elements_type=[int]
        )
        BaseTransformer.__init__(
            self, class_name="DatetimeOneHotEncoder", transformer_description=transformer_description
        )

        self._do_attribute: TimeAttributes
        self._dt_attr_names: list[str] = []

        self._encoder = OneHotEncoder(handle_unknown=handle_unknown)

    def _set_configuration(
        self,
        add_hours: bool,
        add_days_of_week: bool,
        add_weekend: bool,
        add_months: bool,
        add_years: bool,
        min_interval: int = 0,
    ) -> None:
        """
        Sets which one hot attributes have to be created.
        :param add_hours: bool. If include hours.
        :param add_days_of_week: bool. If include days of the week.
        :param add_weekend: bool. If include weekend.
        :param add_months: bool. If include months.
        :param add_years: bool. If include years.
        :param min_interval: int. For 60 minutes the same as for hours. In general division of the day per min_interval
                             window.
        """
        self._do_attribute = TimeAttributes(
            hours=add_hours,
            days_of_week=add_days_of_week,
            weekend=add_weekend,
            months=add_months,
            years=add_years,
            min_inerval=min_interval,
        )

    def _convert_datetime_index_to_numberical_attributes(self, dt_index: DatetimeIndex) -> ndarray[Any, dtype[Any]]:
        """
        Converts the datetime index array into columns of numerical values for requested time attributes:
        hours: 0-23,
        days_of_week: Monday=0, Sunday=6,
        weekend: 0: weekday, 1: weekend,
        months: January=1, December=12,
        years: yyyy format.
        min_interval - For 60 minutes the same as for hours. In general division of the day per min_interval window.
        :param dt_index: DatetimeIndex.
        :return: ndarray[Any, dtype[Any]].
        """
        self._dt_attr_names = []
        numerical_values = zeros((len(dt_index), 1))
        x: ndarray[Any, dtype[Any]]
        if self._do_attribute.hours:
            x = array(dt_index.hour).reshape(-1, 1)
            numerical_values = concatenate([numerical_values, x], axis=1)
            self._dt_attr_names.append("HOUR")
        if self._do_attribute.days_of_week:
            x = array(dt_index.dayofweek).reshape(-1, 1)
            numerical_values = concatenate([numerical_values, x], axis=1)
            self._dt_attr_names.append("DAY_OF_WEEK")
        if self._do_attribute.weekend:
            x = dt_index.dayofweek.isin([5, 6]).reshape((-1, 1))
            numerical_values = concatenate([numerical_values, x], axis=1)
            self._dt_attr_names.append("WEEKEND")
        if self._do_attribute.months:
            x = array(dt_index.month).reshape(-1, 1)
            numerical_values = concatenate([numerical_values, x], axis=1)
            self._dt_attr_names.append("MONTH")
        if self._do_attribute.years:
            x = array(dt_index.year).reshape(-1, 1)
            numerical_values = concatenate([numerical_values, x], axis=1)
            self._dt_attr_names.append("YEAR")
        if self._do_attribute.min_inerval != 0:
            x = array((dt_index.hour * 60 + dt_index.minute) // self._do_attribute.min_inerval).reshape(-1, 1)
            numerical_values = concatenate([numerical_values, x], axis=1)
            self._dt_attr_names.append("MIN" + str(self._do_attribute.min_inerval))

        if numerical_values.shape[1] == 1:
            ExceptionExecutioner(NoProperOptionInIf).log_and_raise(
                description=self._class_info.class_type + " " + self._class_info.class_name
            )

        return numerical_values[:, 1:]

    def get_encoded_attribute_names(self, attr_name: str | None = None) -> list[str]:
        """
        Returns the encoded attribute names of the fitted data.
        One-hot encoder's get_feature_names_out() method returns ['x0_0', 'x0_1', 'x1_0', 'x1_1', 'x1_2', 'x1_3']
        for following array for lets say
         [[0, 1],
          [1, 0],
          [0, 2],
          [0, 3]].
        This class converts it to <attr_name>
        :param attr_name: str. Name of general attribute to be added at the beginning. Otherwise nothing is added.
        :return: List[str].
        """
        prefix = "" if attr_name is None else attr_name + "_"
        encoded_attributes: list[str] = self._encoder.get_feature_names_out()
        for i, dt_attr_name in enumerate(self._dt_attr_names):
            encoded_attributes = [attr.replace("x" + str(i), prefix + dt_attr_name) for attr in encoded_attributes]
        return encoded_attributes

    # pylint: disable=arguments-differ
    # pylint: disable=too-many-arguments
    # pylint: disable=arguments-renamed
    def fit(
        self,
        dt_index: DatetimeIndex,
        add_hours: bool = False,
        add_days_of_week: bool = True,
        add_weekend: bool = False,
        add_months: bool = False,
        add_years: bool = False,
        min_interval: int = 0,
    ) -> None:
        """
        Fits.
        :param dt_index: DatetimeIndex.
        :param add_hours: bool. If include hours.
        :param add_days_of_week: bool. If include days of the week.
        :param add_weekend: bool. If include weekend.
        :param add_months: bool. If include months.
        :param add_years: bool. If include years.
        :param min_interval: int. For 60 minutes the same as for hours. In general division of the day per min_interval
                     window.
        :return: ndarray.
        """
        self._set_configuration(add_hours, add_days_of_week, add_weekend, add_months, add_years, min_interval)
        numerical_attributes = self._convert_datetime_index_to_numberical_attributes(dt_index)
        self._encoder.fit(numerical_attributes)

    def fit_predict(
        self,
        dt_index: DatetimeIndex,
        add_hours: bool = False,
        add_days_of_week: bool = True,
        add_weekend: bool = False,
        add_months: bool = False,
        add_years: bool = False,
        min_interval: int = 0,
    ) -> ndarray[Any, dtype[Any]]:
        """
        Fit predicts.
        :param dt_index: DatetimeIndex.
        :param add_hours: bool. If include hours.
        :param add_days_of_week: bool. If include days of the week.
        :param add_weekend: bool. If include weekend.
        :param add_months: bool. If include months.
        :param add_years: bool. If include years.
        :param min_interval: int. For 60 minutes the same as for hours. In general division of the day per min_interval
                             window.
        :return: ndarray[Any, dtype[Any]].
        """
        self._set_configuration(add_hours, add_days_of_week, add_weekend, add_months, add_years, min_interval)
        numerical_attributes = self._convert_datetime_index_to_numberical_attributes(dt_index)
        prediction: ndarray[Any, dtype[Any]]
        prediction = self._encoder.fit_transform(numerical_attributes).toarray()
        return prediction

    # pylint: enable=too-many-arguments

    def predict(self, dt_index: DatetimeIndex) -> ndarray[Any, dtype[Any]]:
        """
        Predicts.
        :param dt_index: DatetimeIndex.
        :return: ndarray[Any, dtype[Any]].
        """
        numerical_attributes = self._convert_datetime_index_to_numberical_attributes(dt_index)
        prediction: ndarray[Any, dtype[Any]]
        prediction = self._encoder.transform(numerical_attributes).toarray()
        return prediction

    def inverse(self, data: Any) -> Any:  # noqa: ARG002
        """
        Does the inverse transformation.
        """
        return None

    # pylint: enable=arguments-differ
    # pylint: enable=arguments-renamed
