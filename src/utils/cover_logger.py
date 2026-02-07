"""
Code for logging the overall coverage.
"""

import csv
import pathlib
from datetime import datetime

import git
from bs4 import BeautifulSoup


class CoverageLogger:
    """
    Adds coverage information (branch, time, coverage, comment) into the .csv file.
    """

    COVERAGE_FOLDER_NAME = "coverage"
    COVERAGE_FILE_NAME = "index.html"
    LOG_FOLDER_NAME = "logs"
    LOG_FILE_NAME = "cover_log.csv"

    def __init__(self) -> None:
        self._comment = ""
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
        return str(git.Repo(search_parent_directories=True).active_branch.name)

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

    def get_message(self) -> None:
        """
        Asks for the coverage message.
        """
        self._comment = input("Coverage Comment: ").replace(",", " ")

    def get_coverage_rate(self) -> None:
        """
        Extracts and returns the total coverage rate from the html file generated from the pytest-cov.
        :return: int. Total coverage rate.
        """
        file_path = self._create_path(
            self._get_path_two_folders_up_from_file(),
            self.COVERAGE_FOLDER_NAME,
            self.COVERAGE_FILE_NAME,
        )
        with file_path.open(encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
            coverage = soup.find_all("span", {"class": "pc_cov"})[0].text.replace("%", "")

        self._coverage = int(coverage)

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
                    self._comment,
                ]
            )

    def write_to_log_file(self) -> None:
        """
        Performs the extraction and saving of the coverage rate.
        """
        self.get_message()
        self.get_coverage_rate()
        self.write_in_csv()


if __name__ == "__main__":
    COVERAGE_LOGGER = CoverageLogger()
    COVERAGE_LOGGER.write_to_log_file()
    print("\nSaved\n")
