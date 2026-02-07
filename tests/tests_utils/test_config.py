"""
Tests for Config class.
"""

from src.utils.config import Config
from src.utils.config_data import ConfigData


def test_config_singleton() -> None:
    """
    Tests that Config follows singleton pattern - same instance returned.
    """
    config1 = Config()
    config2 = Config()
    assert config1 is config2


def test_config_initialization() -> None:
    """
    Tests that Config initializes without errors.
    """
    config = Config()
    assert config is not None


def test_config_get_data() -> None:
    """
    Tests that get_data() returns ConfigData instance.
    """
    config = Config()
    data = config.get_data()
    assert data is not None
    assert isinstance(data, ConfigData)


def test_config_get_data_as_dict() -> None:
    """
    Tests that get_data_as_dict() returns dictionary.
    """
    config = Config()
    data_dict = config.get_data_as_dict()
    assert data_dict is not None
    assert isinstance(data_dict, dict)


def test_config_has_name() -> None:
    """
    Tests that config data has name field.
    """
    config = Config()
    data = config.get_data()
    assert hasattr(data, "name")
    assert data.name is not None
    assert isinstance(data.name, str)


def test_config_has_path() -> None:
    """
    Tests that config data has path field.
    """
    config = Config()
    data = config.get_data()
    assert hasattr(data, "path")
    assert data.path is not None


def test_config_has_path_data() -> None:
    """
    Tests that config data has path.data field.
    """
    config = Config()
    data = config.get_data()
    assert hasattr(data.path, "data")
    assert data.path.data is not None
    assert isinstance(data.path.data, str)


def test_config_dict_contains_name() -> None:
    """
    Tests that dictionary representation contains name.
    """
    config = Config()
    data_dict = config.get_data_as_dict()
    assert "name" in data_dict
    assert isinstance(data_dict["name"], str)


def test_config_dict_contains_path() -> None:
    """
    Tests that dictionary representation contains path.
    """
    config = Config()
    data_dict = config.get_data_as_dict()
    assert "path" in data_dict


def test_config_data_consistency() -> None:
    """
    Tests that get_data() and get_data_as_dict() return consistent data.
    """
    config = Config()
    data = config.get_data()
    data_dict = config.get_data_as_dict()

    # Name should match
    assert data.name == data_dict["name"]
