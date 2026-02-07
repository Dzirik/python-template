"""
Tests
"""

from src.utils.meta_class import MetaClass, TransformerDescription

TEST_CLASS_TYPE = "type_of_class"
TEST_CLASS_NAME = "name_of_class"


class MetaClassTestClass(MetaClass):
    """
    Class for testing metaclass functionality.
    """

    def __init__(self) -> None:
        MetaClass.__init__(self, class_type=TEST_CLASS_TYPE, class_name=TEST_CLASS_NAME)


def test_class_type_getter() -> None:
    """
    Tests the getter.
    """
    class_instance = MetaClassTestClass()
    assert class_instance.get_class_type() == TEST_CLASS_TYPE


def test_class_name_getter() -> None:
    """
    Tests the getter.
    """
    class_instance = MetaClassTestClass()
    assert class_instance.get_class_name() == TEST_CLASS_NAME


def test_class_type_and_name_getter() -> None:
    """
    Tests the getter.
    """
    class_instance = MetaClassTestClass()
    assert class_instance.get_class_type_and_name() == f"{TEST_CLASS_TYPE}_{TEST_CLASS_NAME}"


def test_default_base_transformer() -> None:
    """
    Tests the default behaviour of base transformer.
    """
    class_instance = MetaClassTestClass()
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
    class_instance = MetaClassTestClass()
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
