"""
Saver and loader.

Class for simplification of saving and loading.
"""

import json
import pickle  # nosec: B403 - pickle used only with trusted internal data files
from pathlib import Path
from typing import Any

import typedload
from pandas import DataFrame, read_csv, read_pickle
from pyhocon import ConfigFactory

from src.exceptions.data_exception import FileNotFound
from src.utils.config import Config


def get_path(file_name: str, where: str = "raw_data", extension: str = ".pkl") -> str:
    """
    Returns a path of a file from the config file based of where.

    :param file_name: str. File name without .pkl.
    :param where: str. Name of the path from the config file.
    :param extension: str. File extension. Default is .pkl.
    :return: str. Path as string.
    """
    dir_path = getattr(Config().get_data().path, where)

    return str((Path(dir_path) / (file_name + extension)).resolve())


class SaverAndLoader:
    """
    Class for simplification of saving and loading.
    """

    def __init__(self) -> None:
        self._decimal = "."
        self._sep = ","
        self._csv_date_time_format = "%Y/%m/%d %H:%M:%S"

    @staticmethod
    def is_file(file_name: str, where: str = "raw_data", extension: str = ".pkl") -> bool:
        """
        Tests if file exists.

        :param file_name: str. File name without .pkl.
        :param where: str. Name of the path from the config file.
        :param extension: str. File extension. Default is .pkl.
        :return: bool.
        """
        return Path(get_path(file_name, where, extension)).exists()

    def set_csv_params(self, decimal: str, sep: str) -> None:
        """
        Sets the parameters for read_csv function.

        :param decimal: str.
        :param sep: str.
        """
        self._decimal = decimal
        self._sep = sep

    def save_dataframe_to_csv(self, df: DataFrame, file_name: str, where: str = "raw_data") -> None:
        """
        Saves a DataFrame to a csv file.

        :param df: DataFrame to be saved.
        :param file_name: str. File name without .csv
        :param where: str. Name of the path from the config file.
        """
        path = get_path(file_name, where, ".csv")
        df.to_csv(path, index=False, decimal=self._decimal, sep=self._sep, date_format=self._csv_date_time_format)

    def load_dataframe_from_csv(self, file_name: str, where: str = "raw_data", min_size: int = 2) -> DataFrame:
        """
        Loads a DataFrame from a csv file.

        :param file_name: str. File name without .csv
        :param where: str. Name of the path from the config file.
        :param min_size: int. Minimum size of the file.
        :return: DataFrame
        """
        path = get_path(file_name, where, ".csv")
        path_obj = Path(path)
        if path_obj.exists():
            # zero len doesn't work with csv files in some cases when small
            if path_obj.stat().st_size > min_size:
                return read_csv(path, decimal=self._decimal, sep=self._sep)
        else:
            raise FileNotFound(description=f"File {path} was not found on selected path.")
        return DataFrame()

    @staticmethod
    def save_dataframe_to_pickle(df: DataFrame, file_name: str, where: str = "raw_data") -> None:
        """
        Saves a DataFrame to a pickle file.

        :param df: DataFrame to be saved.
        :param file_name: str. File name without .pkl.
        :param where: str. Name of the path from the config file.
        """
        path = get_path(file_name, where)
        df.to_pickle(path, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load_dataframe_from_pickle(file_name: str, where: str = "raw_data", min_size: int = 0) -> DataFrame:
        """
        Loads a DataFrame from a pickle file.

        :param file_name: str. File name without .pkl.
        :param where: str. Name of the path from the config file.
        :param min_size: int. Minimum size of the file.
        :return: DataFrame. Loaded data frame.
        """
        path = get_path(file_name, where)
        path_obj = Path(path)
        if path_obj.exists():
            if path_obj.stat().st_size > min_size:
                return read_pickle(path)  # noqa: S301 - trusted internal pickle files only
        else:
            raise FileNotFound(description=f"File {path} was not found on selected path.")
        return DataFrame()

    @staticmethod
    def save_to_pickle(data: Any, file_name: str, where: str = "raw_data") -> None:
        """
        Saves data to pickle file.

        :param data: Any. Python data to be saved.
        :param file_name: str. File name without .pkl.
        :param where: str. Name of the path from the config file.
        """
        path = get_path(file_name, where)

        with Path(path).open("wb") as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load_from_pickle(file_name: str, where: str = "raw_data", min_size: int = 0) -> Any:
        """
        Loads a pickle file.

        :param file_name: str. File name without .pkl.
        :param where: str. Name of the path from the config file.
        :param min_size: int. Minimum size of the file.
        :return: Any. Loaded data from the pickle file.
        """
        path = get_path(file_name, where)
        path_obj = Path(path)
        if path_obj.exists():
            if path_obj.stat().st_size > min_size:
                with path_obj.open("rb") as handle:
                    return pickle.load(handle)  # noqa: S301 - trusted internal pickle files only
        else:
            raise FileNotFound(description=f"File {path} was not found on selected path.")
        return None

    @staticmethod
    def delete_pickle(file_name: str, where: str = "raw_data") -> None:
        """
        Deletes a pickle file.

        :param file_name: str. File name without .pkl.
        :param where: str. Name of the path from the config file.
        """
        path = get_path(file_name, where)
        path_obj = Path(path)
        if path_obj.exists():
            path_obj.unlink()

    @staticmethod
    def save_config_data(config_data: Any, file_name: str, where: str = "raw_data") -> None:
        """
        Converts the config data to a dictionary and saves it as .conf file.

        :param config_data: Any. Configuration's named tuple (see FEConfig, MMTradingConfig, ...)
        :param file_name: str. File name without .pkl.
        :param where: str. Name of the path from the config file.
        """
        path = get_path(file_name, where, ".conf")
        data = typedload.dump(config_data)
        with Path(path).open("w", encoding="utf8") as outfile:
            json.dump(data, outfile)

    @staticmethod
    def load_config_data(file_name: str, config_data_structure: Any, where: str = "raw_data") -> Any:
        """
        Loads the config data.

        :param file_name: str. File name without .pkl.
        :param config_data_structure: Any. Named tuple of the config.
        :param where: str. Name of the path from the config file.
        """
        path = get_path(file_name, where, ".conf")
        path_obj = Path(path)
        if path_obj.exists():
            return typedload.load(ConfigFactory.parse_file(path), config_data_structure)
        raise FileNotFound(description=f"File {path} was not found on selected path.")

    @staticmethod
    def delete_file(file_name: str, where: str = "raw_data") -> None:
        """
        Deletes the file from the location, the file needs to be fully specified.

        :param file_name: str. Full file name.
        :param where: str. Name of the path from the config file.
        """
        path = get_path(file_name, where, "")
        Path(path).unlink()


if __name__ == "__main__":
    SAVER_AND_LOADER: SaverAndLoader
    SAVER_AND_LOADER = SaverAndLoader()
