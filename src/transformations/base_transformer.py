"""
Parent/base class for transformers as parent class.

Transformers are classes for data transformation and manipulation. They are not intended to be machine learning models.

IMPORTANT NOTE: Data consistency is not checked here, the data input can be any and needs to be specified in child
classes. Solution which would handle it in general in python environment would be too time-consuming.
"""

from abc import abstractmethod
from typing import Any

from src.utils.meta_class import TRANSFORMER_TYPE_NAME, MetaClass, TransformerDescription

__all__ = ["BaseTransformer", "TransformerDescription"]


class BaseTransformer(MetaClass):
    """
    Parent/base class for all transformers to ensure the same interface.
    """

    def __init__(self, class_name: str, transformer_description: TransformerDescription) -> None:
        MetaClass.__init__(self, class_type=TRANSFORMER_TYPE_NAME, class_name=class_name)
        self.set_transformer_description(transformer_description=transformer_description)
        self._params: dict[str, Any] = {}

    @abstractmethod
    def fit(self, data: Any) -> None:
        """
        Fits a transformation based on the data - analogy to sklearn style.
        :param data: Any. Not specified here.
        """

    @abstractmethod
    def predict(self, data: Any) -> Any:
        """
        Does the transformation based on the fit - analogy to sklearn style.
        """

    @abstractmethod
    def fit_predict(self, data: Any) -> Any:
        """
        Does both fit and predict together - analogy to sklearn style.
        """

    @abstractmethod
    def inverse(self, data: Any) -> Any:
        """
        Does the inverse transformation.
        """

    def restore_from_params(self, params: dict[str, Any]) -> None:
        """
        Sets the params for transformer.
        :param params: Dict[str, Any].
        """
        self._params = params
        # restore here the external transformer if needed in child class

    def get_params(self) -> dict[str, Any]:
        """
        Gets the params.
        :return: Dict[str, Any]. Params.
        """
        return self._params
