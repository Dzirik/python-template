"""
Printing documentation for make commands.
"""

import sys
from pathlib import Path


class Markdown:
    """
    Class for printing section of markdown README.md file.
    """

    FILE_NAME = "README.md"

    def __init__(self) -> None:
        self._file: list[str]

    def read_file(self) -> None:
        """
        Reads the file.
        """
        with Path(self.FILE_NAME).open(encoding="utf8") as file:
            self._file = file.readlines()

    @staticmethod
    def _get_section_level(line: str) -> int:
        """
        Returns number of # tags at the beginning of the line. 0 - no header,
          1 - first level header
          2 - second level header
          ...
        :param line: str. Line to be investigated
        :return: int. 0 - it is not header. >1 - header level in markdown.
        """
        section_level = 0
        if line[0] == "#":
            split = line.split(" ")
            section_level = len(split[0])
        return section_level

    def print_section(self, section_name: str) -> None:
        """
        Prints the whole section - from section name to the next section name.
        :param section_name: str. Section name without hashes and space before.
        """
        print_line = False
        for line in self._file:
            if print_line and self._get_section_level(line) == 0:
                if line[0] == "@":
                    if len(line) == 2:
                        print("#" * 100)
                    else:
                        n = 100 - 2 - len(line[1:-1])
                        print("#" * 100)
                        print(f"{'#' * int(n / 2)} {line[1:-1]} {'#' * (n - int(n / 2))}")
                        print("#" * 100)
                else:
                    print(line[:-1].replace("`", ""))

            section_level = self._get_section_level(line)
            if section_level > 0:
                print_line = bool(line == "#" * section_level + " " + section_name + "\n")


if __name__ == "__main__":
    md = Markdown()
    md.read_file()
    if len(sys.argv) > 1:
        md.print_section(section_name=sys.argv[1])
    else:
        print("No section for printing were selected.")
