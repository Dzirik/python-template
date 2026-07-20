"""
Code for logging the overall coverage.
"""

import csv
import json
import pathlib
import sys
from datetime import datetime
from typing import Any

from coverage import Coverage

# This module is invoked directly (uv run python ./src/utils/cover_logger.py, see the Makefile's
# cover-save target), so the repo root must be added to sys.path before the absolute "from src..."
# import below can resolve - mirrors the same bootstrap used in src/scripts_production/checker.py.
_BASE_DIR = pathlib.Path(__file__).resolve().parent
sys.path += [str(_BASE_DIR / ".."), str(_BASE_DIR / "../..")]

from src.utils.helper_functions import get_git_branch  # noqa: E402


class CoverageLogger:
    """
    Adds coverage information (branch, time, coverage) into the .csv file.
    """

    COVERAGE_FOLDER_NAME = "coverage"
    COVERAGE_JSON_FILE_NAME = "coverage.json"
    COVERAGE_DATA_FILE_NAME = ".coverage"
    LOG_FOLDER_NAME = "logs"
    LOG_FILE_NAME = "cover_log.csv"

    def __init__(self) -> None:
        self._coverage: int = -1  # -1 to see when something is wrong - coverage must be >=0

    @staticmethod
    def _get_current_time() -> str:
        """
        Returns the current time.
        :return: str. Current time (hh:mm:ss).
        """
        now = datetime.now()
        return now.strftime("%d-%m-%Y %H:%M:%S")

    @staticmethod
    def _get_branch_name() -> str:
        """
        Returns the current branch name.
        :return: str. Current repository.
        """
        return get_git_branch()

    @staticmethod
    def _create_path(folder_path: pathlib.Path, folder_name: str, file_name: str) -> pathlib.Path:
        """
        Creates a path from following information.
        :param folder_path: str. Repository folder path.
        :param folder_name: str. Folder name in the repository.
        :param file_name: str. Name of the file.
        :return: pathlib.Path. The path to the file.
        """
        return folder_path / folder_name / file_name

    @staticmethod
    def _get_path_two_folders_up_from_file() -> pathlib.Path:
        """
        :return: pathlib.Path. Returns relative path two folders up from the file.
        """
        return pathlib.Path(__file__).parent.parent.parent.absolute()

    def get_coverage_rate(self) -> None:
        """
        Generates a JSON coverage report from the .coverage data file (produced by pytest-cov) and extracts the
        total coverage rate from it, using only the coverage package and the stdlib json module.
        :return: int. Total coverage rate.
        """
        repo_folder = self._get_path_two_folders_up_from_file()
        json_path = self._create_path(repo_folder, self.COVERAGE_FOLDER_NAME, self.COVERAGE_JSON_FILE_NAME)
        data_path = repo_folder / self.COVERAGE_DATA_FILE_NAME

        cov = Coverage(data_file=str(data_path))
        cov.load()
        cov.json_report(outfile=str(json_path))

        with json_path.open(encoding="utf-8") as file:
            report: dict[str, Any] = json.load(file)

        self._coverage = round(report["totals"]["percent_covered"])

    def write_in_csv(self) -> None:
        """
        Adds a new line of coverage information at the end of the file.
        """
        file_path = self._create_path(
            self._get_path_two_folders_up_from_file(),
            self.LOG_FOLDER_NAME,
            self.LOG_FILE_NAME,
        )
        with file_path.open("a", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    self._get_branch_name(),
                    self._get_current_time(),
                    self._coverage,
                ]
            )

    def write_to_log_file(self) -> None:
        """
        Performs the extraction and saving of the coverage rate.
        """
        self.get_coverage_rate()
        self.write_in_csv()


if __name__ == "__main__":
    COVERAGE_LOGGER = CoverageLogger()
    COVERAGE_LOGGER.write_to_log_file()
    print("\nSaved\n")
