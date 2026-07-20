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
    min_interval: int


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

    def __init__(self, time_attributes: TimeAttributes, handle_unknown: str = "ignore") -> None:
        """
        Initialises the transformer with the time attributes to encode and the encoder configuration.
        :param time_attributes: TimeAttributes. Which one-hot attributes have to be created.
        :param handle_unknown: str. Passed through to the underlying OneHotEncoder. Default is "ignore".
        """
        transformer_description = TransformerDescription(
            input_type=[DatetimeIndex], input_elements_type=[None], output_type=[ndarray], output_elements_type=[int]
        )
        BaseTransformer.__init__(
            self, class_name="DatetimeOneHotEncoder", transformer_description=transformer_description
        )

        self._do_attribute: TimeAttributes = time_attributes
        self._dt_attr_names: list[str] = []

        self._encoder = OneHotEncoder(handle_unknown=handle_unknown)

    def _convert_datetime_index_to_numerical_attributes(self, dt_index: DatetimeIndex) -> ndarray[Any, dtype[Any]]:
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
        if self._do_attribute.min_interval != 0:
            x = array((dt_index.hour * 60 + dt_index.minute) // self._do_attribute.min_interval).reshape(-1, 1)
            numerical_values = concatenate([numerical_values, x], axis=1)
            self._dt_attr_names.append("MIN" + str(self._do_attribute.min_interval))

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

    def fit(self, dt_index: DatetimeIndex) -> None:
        """
        Fits the one-hot encoder on the numerical attributes derived from dt_index, using the TimeAttributes
        supplied at construction.
        :param dt_index: DatetimeIndex.
        """
        numerical_attributes = self._convert_datetime_index_to_numerical_attributes(dt_index)
        self._encoder.fit(numerical_attributes)
        self._store_params()

    def fit_predict(self, dt_index: DatetimeIndex) -> ndarray[Any, dtype[Any]]:
        """
        Fits the one-hot encoder on dt_index and returns the one-hot encoded prediction for the same data.
        :param dt_index: DatetimeIndex.
        :return: ndarray[Any, dtype[Any]].
        """
        self.fit(dt_index)
        return self.predict(dt_index)

    def predict(self, dt_index: DatetimeIndex) -> ndarray[Any, dtype[Any]]:
        """
        Predicts.
        :param dt_index: DatetimeIndex.
        :return: ndarray[Any, dtype[Any]].
        """
        numerical_attributes = self._convert_datetime_index_to_numerical_attributes(dt_index)
        prediction: ndarray[Any, dtype[Any]]
        prediction = self._encoder.transform(numerical_attributes).toarray()
        return prediction

    def inverse(self, data: ndarray[Any, dtype[Any]]) -> ndarray[Any, dtype[Any]]:
        """
        Does the inverse transformation.
        NOTE: the original DatetimeIndex is NOT recoverable from the one-hot encoded attributes. This returns the
        pre-one-hot numerical attribute columns (e.g. hour, day of week, ... as numbers), not datetimes.
        :param data: ndarray[Any, dtype[Any]]. One-hot encoded data to invert.
        :return: ndarray[Any, dtype[Any]]. The numerical attribute matrix that was one-hot encoded.
        """
        inverted: ndarray[Any, dtype[Any]] = self._encoder.inverse_transform(data)
        return inverted

    def _store_params(self) -> None:
        """
        Stores everything needed to round-trip a fitted encoder into self._params: the TimeAttributes instance,
        the derived attribute names, and the fitted encoder's learned categories.
        """
        self._params = {
            "time_attributes": self._do_attribute,
            "dt_attr_names": self._dt_attr_names,
            "categories_": self._encoder.categories_,
        }

    def restore_from_params(self, params: dict[str, Any]) -> None:
        """
        Restores a fitted state from previously saved params, rebuilding a working OneHotEncoder from the saved
        categories without re-fitting.
        :param params: Dict[str, Any]. Params as produced by get_params() after a fit.
        """
        self._params = params
        self._do_attribute = params["time_attributes"]
        self._dt_attr_names = params["dt_attr_names"]

        categories = params["categories_"]
        self._encoder.categories_ = categories
        self._encoder.n_features_in_ = len(categories)
        self._encoder._n_features_outs = [len(category) for category in categories]
        self._encoder._infrequent_enabled = False
        self._encoder.drop_idx_ = None
        self._encoder._drop_idx_after_grouping = None


if __name__ == "__main__":
    from datetime import datetime

    demo_time_attributes = TimeAttributes(
        hours=True, days_of_week=True, weekend=True, months=True, years=False, min_interval=0
    )
    demo_transformer = DatetimeOneHotEncoderTransformer(demo_time_attributes)
    demo_data = DatetimeIndex([datetime(2024, 1, 15, 10, 30), datetime(2024, 2, 20, 14, 45)])
    demo_output = demo_transformer.fit_predict(demo_data)
    print(demo_output)
    print(demo_transformer.get_encoded_attribute_names())
