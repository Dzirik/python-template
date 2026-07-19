"""
Project Paths service - foundational, CWD-independent path resolution anchored to the project root.

Computes the project root once by walking up from this module's own source file to a marker directory
(``pyproject.toml`` or ``.git``), then exposes the canonical repository locations built on top of it. This module
is foundational per ADR 0002 and must never import the project ``Logger`` - only stdlib logging may be used here.

Usage can be found at the end of the file.
"""

from functools import lru_cache
from pathlib import Path

from src.utils.envs import Envs

_MARKER_FILE_NAMES = ("pyproject.toml", ".git")

# Name of the configurations folder under the project root.
FOLDER_CONFIGURATIONS = "configurations"


@lru_cache(maxsize=1)
def _compute_project_root() -> Path:
    """
    Walks up from this module's resolved source file location to find the first parent directory (including
    itself) containing a marker (``pyproject.toml`` or ``.git``). Memoized so the walk only happens once per
    process and always returns the identical resolved path.
    :return: Path. Resolved absolute path of the marker directory.
    """
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if any((candidate / marker).exists() for marker in _MARKER_FILE_NAMES):
            return candidate

    error_msg = f"Could not locate project root: none of {_MARKER_FILE_NAMES} found in any parent of {current}."
    raise FileNotFoundError(error_msg)


class ProjectPaths:
    """
    Foundational service exposing canonical, CWD-independent input/output locations anchored to the project root.

    The root is computed once (memoized) by walking up from this module's own source file to a marker
    (``pyproject.toml`` or ``.git``), unless overridden through Envs. Resolution never depends on
    Path.cwd(). Must not import the project Logger - see ADR 0002.
    """

    def __init__(self) -> None:
        self._root: Path
        override = Envs.get_project_root_override()
        if override is not None:
            self._root = Path(override).resolve()
        else:
            self._root = _compute_project_root()

        self.logs.mkdir(parents=True, exist_ok=True)

    @property
    def root(self) -> Path:
        """
        Gets the project root path.
        :return: Path. Absolute path to the project root.
        """
        return self._root

    @property
    def data(self) -> Path:
        """
        Gets the data folder path.
        :return: Path. Absolute path to root/data.
        """
        return self._root / "data"

    @property
    def logs(self) -> Path:
        """
        Gets the logs folder path.
        :return: Path. Absolute path to root/logs.
        """
        return self._root / "logs"

    @property
    def reports(self) -> Path:
        """
        Gets the reports folder path.
        :return: Path. Absolute path to root/reports.
        """
        return self._root / "reports"

    @property
    def configurations(self) -> Path:
        """
        Gets the configurations folder path.
        :return: Path. Absolute path to root/configurations.
        """
        return self._root / FOLDER_CONFIGURATIONS

    def config_file(self, name: str, subfolder: str | None = None, extension: str = ".toml") -> Path:
        """
        Resolves the absolute path of a named configuration file under the configurations folder.

        Defaults to the ``.toml`` extension used by every application/component profile - see ADR 0003 - and by
        the Logger's own ``dictConfig`` profiles, which pass it explicitly for clarity.
        :param name: str. Bare profile name, without the extension.
        :param subfolder: Optional[str]. Per-kind subfolder under configurations (e.g. "loggers", "watchdogs").
            Default value is None.
        :param extension: str. File extension (including the leading dot) to append to name. Default is ".toml".
        :return: Path. Absolute path to configurations/[subfolder/]<name><extension>.
        """
        base = self.configurations if subfolder is None else self.configurations / subfolder
        return base / f"{name}{extension}"


if __name__ == "__main__":
    project_paths = ProjectPaths()

    print(f"root: {project_paths.root}")
    print(f"data: {project_paths.data}")
    print(f"logs: {project_paths.logs}")
    print(f"reports: {project_paths.reports}")
    print(f"configurations: {project_paths.configurations}")
