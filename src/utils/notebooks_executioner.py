"""
Code for automatically execution of notebooks based on parameters.

Uses a spawn-based multiprocessing context (the default multiprocessing start method on Windows, and the more
robust choice for Jupyter kernels on Linux/macOS too) together with ``imap_unordered`` for better load balancing
across notebook parameter sets of varying runtime. HTML conversion is invoked via ``python -m jupyter nbconvert``
through ``subprocess`` (passing args as a list, avoiding PATH/shell-quoting issues).

NOTE: Joblib could be used instead of multiprocessing.
"""

# Bandit exception: subprocess is invoked with a fixed argument list and no shell.
import subprocess  # nosec B404
import sys
from datetime import datetime
from multiprocessing import cpu_count, get_context
from pathlib import Path
from random import shuffle
from typing import Any, NamedTuple

import jupytext
import papermill

from src.exceptions.development_exception import IncorrectValue
from src.utils.application_config import ApplicationConfig
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

    Parallel runs use a spawn-based multiprocessing context and ``imap_unordered`` scheduling, one notebook
    execution per task, for better load balancing than static batching.
    """

    def __init__(self, params: NotebookExecutionerNamedTuple) -> None:
        """
        :param params: NotebookExecutionerNamedTuple.
        """
        self._params: NotebookExecutionerNamedTuple
        self._timer = Timer()

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
        self._config = ApplicationConfig()

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
            except Exception as exc:
                raise RuntimeError(f"Failed to convert '{py_path}' to '{ipynb_path}' via jupytext: {exc}") from exc
        else:
            raise FileNotFoundError(f"Python notebook source not found: '{py_path}'")

    @staticmethod
    def _build_output_path(base: dict[str, Any], exec_params: dict[str, Any], datetime_id: str) -> str:
        """
        Builds the output .ipynb path based on configuration and parameters.

        :param base: dict[str, Any]. Picklable subset of the executioner params needed by a worker process.
        :param exec_params: dict[str, Any]. Parameters for this particular notebook run (including "ID").
        :param datetime_id: str. Datetime id generated for this run, used when add_datetime_id is set.
        :return: str. Absolute path of the notebook to write.
        """
        if base["keep_name_static"]:
            name = f"{base['notebook_name']}_notebook_executioner"
            return str((Path(base["output_folder"]) / f"{name}.ipynb").resolve())

        name = base["notebook_name"]
        name = (
            (f"{base['file_name']}" if name == "" else f"{name}_{base['file_name']}")
            if base["add_file_name_to_notebook_name"]
            else name
        )
        if base["add_datetime_id"]:
            name = f"{datetime_id}_{name}"
        if base["add_params_to_name"]:
            for key, value in exec_params.items():
                if key != "ID":
                    name = f"{name}_{value}"
        return str((Path(base["output_folder"]) / f"{name}.ipynb").resolve())

    def _worker_execute_one(self, args: tuple[dict[str, Any], dict[str, Any]]) -> str:
        """
        Executes a single parameterized notebook run. Top-level-callable, so it is pickle-safe under spawn.

        :param args: tuple[dict[str, Any], dict[str, Any]]. Picklable base params and this run's exec params.
        :return: str. Path of the executed output notebook.
        """
        base, exec_params = args

        datetime_id = create_datetime_id(now=datetime.now(), add_micro=False)
        exec_params = dict(exec_params)
        exec_params["ID"] = datetime_id

        path_out = self._build_output_path(base, exec_params, datetime_id)

        papermill.execute_notebook(base["notebook_path"], path_out, exec_params)

        if base["convert_to_html"]:
            # Call via the current interpreter to avoid PATH issues; pass args as list to avoid quoting problems.
            subprocess.run(  # noqa: S603  # nosec B603
                [sys.executable, "-m", "jupyter", "nbconvert", "--to", "html", path_out],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        return path_out

    def execute(self) -> None:
        """
        Executes the notebook for defined parameters using spawn-based parallel computing.
        """
        self._timer = Timer()

        self._timer.start()

        number_of_processes = self._params.number_of_processes
        list_of_ntb_params = list(self._params.list_of_ntb_params)

        self._ensure_ipynb_from_py()

        print(f"\n{'#' * 50} EXECUTING FOR {number_of_processes} PROCESSES {'#' * 50}")
        print(f" - len of params: {len(list_of_ntb_params)}")
        print(f" - number of threads is: {cpu_count()}")
        print(f" - running {number_of_processes} processes")

        if number_of_processes < 1:
            raise IncorrectValue(f"The value of number_of_processes {number_of_processes} has to be integer >= 1.")

        base = {
            "keep_name_static": self._params.keep_name_static,
            "add_datetime_id": self._params.add_datetime_id,
            "add_file_name_to_notebook_name": self._params.add_file_name_to_notebook_name,
            "file_name": self._params.file_name,
            "add_params_to_name": self._params.add_params_to_name,
            "convert_to_html": self._params.convert_to_html,
            "notebook_name": self._params.notebook_name,
            "notebook_path": self._params.notebook_path,
            "output_folder": self._params.output_folder,
        }

        if number_of_processes == 1:
            for exec_params in list_of_ntb_params:
                self._worker_execute_one((base, exec_params))
        else:
            # Multiprocess execution with spawn context.
            if self._params.shuffle_before_processing:
                shuffle(list_of_ntb_params)
            ctx = get_context("spawn")
            with ctx.Pool(number_of_processes) as pool:
                # Use imap_unordered for better load balancing with varying notebook runtimes.
                for _ in pool.imap_unordered(
                    self._worker_execute_one, [(base, p) for p in list_of_ntb_params], chunksize=1
                ):
                    pass
                pool.close()
                pool.join()

        self._timer.end(label=f"End of Notebook Executioner for {len(list_of_ntb_params)} parameters")
