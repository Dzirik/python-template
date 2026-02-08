"""
Data structure for config.
"""

from typing import NamedTuple


class Path(NamedTuple):
    """
    Configuration tuple for paths to data files.
    """

    data: str


class ParamNotebookExecution(NamedTuple):
    """
    Configuration tuple for the parameterized notebook execution.
    """

    use_default: bool
    convert_to_html: bool
    ntb_path: str
    output_folder: str
    notebook_executioner_params: list[dict[str, float | str]]


class ConfigData(NamedTuple):
    """
    Overall configuration tuple for everything.
    """

    name: str
    path: Path
    param_ntb_execution: ParamNotebookExecution
