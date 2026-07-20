"""
Tests
"""

from src.utils.monitored_base import MonitoredBase, TransformerDescription

TEST_CLASS_TYPE = "type_of_class"
TEST_CLASS_NAME = "name_of_class"


class MonitoredBaseTestClass(MonitoredBase):
    """
    Class for testing MonitoredBase functionality.
    """

    def __init__(self) -> None:
        MonitoredBase.__init__(self, class_type=TEST_CLASS_TYPE, class_name=TEST_CLASS_NAME)


def test_class_type_getter() -> None:
    """
    Tests the getter.
    """
    class_instance = MonitoredBaseTestClass()
    assert class_instance.get_class_type() == TEST_CLASS_TYPE


def test_class_name_getter() -> None:
    """
    Tests the getter.
    """
    class_instance = MonitoredBaseTestClass()
    assert class_instance.get_class_name() == TEST_CLASS_NAME


def test_class_type_and_name_getter() -> None:
    """
    Tests the getter.
    """
    class_instance = MonitoredBaseTestClass()
    assert class_instance.get_class_type_and_name() == f"{TEST_CLASS_TYPE}_{TEST_CLASS_NAME}"


def test_default_base_transformer() -> None:
    """
    Tests the default behaviour of base transformer.
    """
    class_instance = MonitoredBaseTestClass()
    class_info = class_instance.get_class_info()
    assert (
        class_info.transformer_description.input_type is None
        and class_info.transformer_description.output_type is None
        and class_info.transformer_description.input_elements_type is None
        and class_info.transformer_description.output_elements_type is None
    )


def test_not_default_transformer() -> None:
    """
    Tests not default transformer.
    """
    class_instance = MonitoredBaseTestClass()
    transformer_description = TransformerDescription(
        input_type=["input_type"], input_elements_type=[None], output_type=["output_type"], output_elements_type=[int]
    )
    print(transformer_description)
    class_instance.set_transformer_description(transformer_description=transformer_description)
    class_info = class_instance.get_class_info()
    print(class_info)
    assert (
        class_info.transformer_description.input_type is not None
        and class_info.transformer_description.input_type[0] == "input_type"
        and class_info.transformer_description.input_elements_type is not None
        and class_info.transformer_description.input_elements_type[0] is None
        and class_info.transformer_description.output_type is not None
        and class_info.transformer_description.output_type[0] == "output_type"
        and class_info.transformer_description.output_elements_type is not None
        and class_info.transformer_description.output_elements_type[0] is int
    )
