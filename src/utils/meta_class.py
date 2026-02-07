"""
Metaclass for all my classes schemas to be able to monitor them in unified way in logger, ...
"""

from abc import ABC
from typing import Any, NamedTuple

TRANSFORMER_TYPE_NAME = "transformer"
CONFIG_TYPE_NAME = "config"
RULE_TYPE_NAME = "rule"
PIPELINE_TYPE_NAME = "pipeline"
ML_MODEL_TYPE_NAME = "ml_model"
EXPERIMENT_TYPE_NAME = "mlflow_experiment"


class TransformerDescription(NamedTuple):
    """
    Tuple for storing input and output data type.
    """

    input_type: list[Any] | None
    input_elements_type: list[Any] | None
    output_type: list[Any] | None
    output_elements_type: list[Any] | None


class MLModelDescription(NamedTuple):
    """
    Tuple for storing input and output data type.
    - type_of_model: Optional[str]. Stats model, sk-learn, custom, ...
    - type_of_task: Optional[str]. Regression, classification, ...
    """

    type_of_model: str | None
    type_of_task: str | None


class ClassInfo(NamedTuple):
    """
    Tuple for storing class general information.
    """

    class_type: str  # transformer, ...
    class_name: str
    transformer_description: TransformerDescription
    ml_model_description: MLModelDescription


class MetaClass(ABC):  # noqa: B024
    """
    Metaclass for unified class monitoring (logger, ...).
    """

    def __init__(self, class_type: str, class_name: str) -> None:
        self._class_info = ClassInfo(
            class_type=class_type,
            class_name=class_name,
            transformer_description=TransformerDescription(
                input_type=None, input_elements_type=None, output_type=None, output_elements_type=None
            ),
            ml_model_description=MLModelDescription(type_of_model=None, type_of_task=None),
        )

    def set_transformer_description(self, transformer_description: TransformerDescription) -> None:
        """
        Sets the transformer description.
        :param transformer_description: TransformerDescription.
        """
        self._class_info = self._class_info._replace(transformer_description=transformer_description)

    def set_ml_model_description(self, ml_model_description: MLModelDescription) -> None:
        """
        Sets the transformer description.
        :param ml_model_description: MLModelDescription.
        """
        self._class_info = self._class_info._replace(ml_model_description=ml_model_description)

    def get_class_type(self) -> str:
        """
        Gets the class type.
        :return: str.
        """
        return self._class_info.class_type

    def get_class_name(self) -> str:
        """
        Gets the class name.
        :return: str.
        """
        return self._class_info.class_name

    def get_class_type_and_name(self) -> str:
        """
        Gets class type and name in the format "<class_type>_<class_name>".
        :return: str
        """
        return f"{self._class_info.class_type}_{self._class_info.class_name}"

    def get_class_info(self) -> ClassInfo:
        """
        Gets the class info.
        :return: ClassInfo.
        """
        return self._class_info
