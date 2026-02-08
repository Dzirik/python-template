"""
Code for automatically execution of notebooks based on parameters.

NOTE: Joblib could be used instead of multiprocessing.
"""

import subprocess  # nosec: B404 - used only with hardcoded safe commands
import sys
from datetime import datetime
from multiprocessing import Pool, cpu_count
from pathlib import Path
from random import shuffle
from typing import Any, NamedTuple

import jupytext
import papermill

from src.exceptions.development_exception import IncorrectValue
from src.utils.config import Config
from src.utils.date_time_functions import create_datetime_id
from src.utils.envs import Envs
from src.utils.timer import Timer


class NotebookExecutionerNamedTuple(NamedTuple):
    """
    Configuration tuple for notebook executioner.

    - config_name: str. "None" or config file name.
    - number_of_processes: int. Number of processes to use (>= 1).
    """

    config_name: str
    keep_name_static: bool
    add_datetime_id: bool
    add_file_name_to_notebook_name: bool
    file_name: str
    add_params_to_name: bool
    convert_to_html: bool
    notebook_name: str
    notebook_path: str
    output_folder: str
    number_of_processes: int
    shuffle_before_processing: bool
    list_of_ntb_params: list[Any]


class NotebookExecutioner:
    """
    Class for execution of the parameterized notebook with different set of parameters for each run.
    """

    def __init__(self, params: NotebookExecutionerNamedTuple) -> None:
        """
        :param params: NotebookExecutionerNamedTuple.
        """
        self._params: NotebookExecutionerNamedTuple
        self._timer = Timer()
        self._win_or_linux = "Windows"

        self.set_executioner_params(params=params)

    def set_executioner_params(self, params: NotebookExecutionerNamedTuple) -> None:
        """
        Sets the executioner parameters as NamedTuple.

        :param params: NotebookExecutionerNamedTuple.
        """
        self._params = params

        if self._params.config_name != "None":
            envs = Envs()
            envs.set_config(self._params.config_name)
        self._config = Config()

        if not self._config.get_data().param_ntb_execution.use_default:
            self._params = self._params._replace(notebook_path=self._config.get_data().param_ntb_execution.ntb_path)
            self._params = self._params._replace(
                output_folder=self._config.get_data().param_ntb_execution.output_folder
            )
            self._params = self._params._replace(
                list_of_ntb_params=self._config.get_data().param_ntb_execution.notebook_executioner_params
            )

    def set_list_of_notebook_params(self, list_of_ntb_params: list[Any]) -> None:
        """
        Sets the list of parameters for notebook execution.

        :param list_of_ntb_params: List[Any].
        """
        self._params = self._params._replace(list_of_ntb_params=list_of_ntb_params)

    def _ensure_ipynb_from_py(self) -> None:
        """
        Ensures an .ipynb exists by deleting any existing one and recreating it from the corresponding .py file.
        """
        ipynb_path = self._params.notebook_path
        py_path = self._params.notebook_path[:-6] + ".py"

        ipynb_obj = Path(ipynb_path)
        if ipynb_obj.exists():
            ipynb_obj.unlink()

        py_obj = Path(py_path)
        if py_obj.exists():
            try:
                nb = jupytext.read(py_path)
                jupytext.write(nb, ipynb_path)
            except Exception as exc:  # pylint: disable=broad-except
                raise RuntimeError(f"Failed to convert '{py_path}' to '{ipynb_path}' via jupytext: {exc}") from exc
        else:
            raise FileNotFoundError(f"Python notebook source not found: '{py_path}'")

    def _run_notebooks_with_params(self, list_of_ntb_params: list[Any]) -> None:
        """
        Executes the notebook based on default params or config params.

        Note: The list_of_params is given as a parameter because it can differ based on parallel computations.
        :param list_of_ntb_params: List[Any].
        """
        for exec_params in list_of_ntb_params:
            datetime_id = create_datetime_id(now=datetime.now(), add_micro=False)
            exec_params["ID"] = datetime_id
            if self._params.keep_name_static:
                path_out = str(
                    (
                        Path(self._params.output_folder) / f"{self._params.notebook_name}_{Path(__file__).stem}.ipynb"
                    ).resolve()
                )
            else:
                name = self._params.notebook_name
                name = (
                    (f"{self._params.file_name}" if name == "" else f"{name}_{self._params.file_name}")
                    if self._params.add_file_name_to_notebook_name
                    else name
                )
                if self._params.add_datetime_id:
                    name = f"{datetime_id}_{name}"
                if self._params.add_params_to_name:
                    for key, value in exec_params.items():
                        if key != "ID":
                            name = f"{name}_{value}"
                path_out = str((Path(self._params.output_folder) / f"{name}.ipynb").resolve())
            papermill.execute_notebook(self._params.notebook_path, path_out, exec_params)
            if self._params.convert_to_html:
                subprocess.run(  # noqa: S603 - hardcoded command with no user input
                    [sys.executable, "-m", "jupyter", "nbconvert", "--to", "html", path_out],
                    check=True,
                    capture_output=True,
                )

    def execute(self) -> None:
        """
        Executes the notebook for defined parameters using parallel computing.
        """
        self._timer = Timer()

        self._timer.start()

        number_of_processes = self._params.number_of_processes
        list_of_ntb_params = self._params.list_of_ntb_params

        self._ensure_ipynb_from_py()

        print(f"\n{'#' * 50} EXECUTING FOR {number_of_processes} PROCESSES {'#' * 50}")
        print(f" - win or linux: {self._win_or_linux}")
        print(f" - len of params: {len(list_of_ntb_params)}")
        print(f" - number of threads is: {cpu_count()}")
        print(f" - running {number_of_processes} processes")

        if number_of_processes == 1:
            self._run_notebooks_with_params(list_of_ntb_params)
        elif number_of_processes > 1:
            if self._params.shuffle_before_processing:
                shuffle(list_of_ntb_params)
            if len(list_of_ntb_params) < number_of_processes:
                number_of_processes = len(list_of_ntb_params)
                print(
                    f" - updating number of processes to: {number_of_processes} for length: {len(list_of_ntb_params)}"
                )
            batch_size = len(list_of_ntb_params) // number_of_processes
            params_batches = [
                list_of_ntb_params[i : i + batch_size] for i in range(0, len(list_of_ntb_params), batch_size)
            ]

            with Pool(number_of_processes) as notebook_pool:
                notebook_pool.map(self._run_notebooks_with_params, params_batches)
                notebook_pool.close()
                notebook_pool.join()
        else:
            raise IncorrectValue(
                f"The value of number_of_processes {number_of_processes}has to be integer bigger or equal to 1."
            )

        self._timer.end(label=f"End of Notebook Executioner for {len(list_of_ntb_params)} parameters")
