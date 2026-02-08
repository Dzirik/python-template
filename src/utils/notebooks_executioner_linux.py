"""
Linux-friendly notebook executioner.

Key differences vs notebooks_executioner.NotebookExecutioner:
- Uses multiprocessing with 'spawn' start method (more robust with Jupyter kernels on Linux)
- Uses subprocess to call `python -m jupyter nbconvert` (avoids PATH/quoting issues)
- Uses a top-level worker function (pickle-safe under spawn)

Inherits from NotebookExecutioner and overrides only the execute() method.
"""
from __future__ import annotations

import subprocess  # nosec: B404 - used only with hardcoded safe commands
import sys
from datetime import datetime
from multiprocessing import cpu_count, get_context
from pathlib import Path
from random import shuffle
from typing import Any

import papermill

from src.exceptions.development_exception import IncorrectValue
from src.utils.date_time_functions import create_datetime_id
from src.utils.notebooks_executioner import NotebookExecutioner, NotebookExecutionerNamedTuple


class NotebookExecutionerLinux(NotebookExecutioner):
    """
    Linux-oriented notebook executioner using spawn multiprocessing and robust nbconvert.

    Inherits from NotebookExecutioner and overrides only the execute() method to use:
    - spawn-based multiprocessing context (more reliable with Jupyter kernels on Linux)
    - subprocess-based nbconvert invocation (avoids shell Add PATH/quoting issues)
    - top-level worker function (pickle-safe under spawn)
    """

    def __init__(self, params: NotebookExecutionerNamedTuple) -> None:
        """
        :param params: NotebookExecutionerNamedTuple.
        """
        NotebookExecutioner.__init__(self, params=params)
        self._win_or_linux = "Linux"

    @staticmethod
    def _build_output_path(base: dict[str, Any], exec_params: dict[str, Any], datetime_id: str) -> str:
        """
        Build output .ipynb path based on configuration and parameters.
        """
        if base["keep_name_static"]:
            name = f"{base['notebook_name']}_notebook_executioner_linux"
            return str((Path(base["output_folder"]) / f"{name}.ipynb").resolve())

        name = base["notebook_name"]
        name = (f"{base['file_name']}" if name == ""
                else f"{name}_{base['file_name']}") if base["add_file_name_to_notebook_name"] else name
        if base["add_datetime_id"]:
            name = f"{datetime_id}_{name}"
        if base["add_params_to_name"]:
            for key, value in exec_params.items():
                if key != "ID":
                    name = f"{name}_{value}"
        return str((Path(base["output_folder"]) / f"{name}.ipynb").resolve())

    def _worker_execute_one(self, args: tuple[dict[str, Any], dict[str, Any]]) -> str:
        """
        Top-level worker for a single parameter set. Returns output notebook path.
        """
        base, exec_params = args

        datetime_id = create_datetime_id(now=datetime.now(), add_micro=False)
        exec_params = dict(exec_params)
        exec_params["ID"] = datetime_id

        path_out = self._build_output_path(base, exec_params, datetime_id)

        papermill.execute_notebook(base["notebook_path"], path_out, exec_params)

        if base["convert_to_html"]:
            # Call via the current interpreter to avoid PATH issues; pass args as list to avoid quoting problems
            subprocess.run(  # noqa: S603  # nosec
                [sys.executable, "-m", "jupyter", "nbconvert", "--to", "html", path_out],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        return path_out

    def execute(self) -> None:
        """
        Executes the notebook for defined parameters using spawn-based parallel computing.

        Overrides parent execute() to use spawn context and per-task parallelization.
        """
        self._timer.start()

        number_of_processes = self._params.number_of_processes
        list_of_ntb_params = list(self._params.list_of_ntb_params)

        self._ensure_ipynb_from_py()

        print(f"\n{'#' * 50} EXECUTING FOR {number_of_processes} PROCESSES {'#' * 50}")
        print(f" - win or linux: {self._win_or_linux}")
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
            # Multiprocess execution with spawn context
            if self._params.shuffle_before_processing:
                shuffle(list_of_ntb_params)
            ctx = get_context("spawn")
            with ctx.Pool(number_of_processes) as pool:
                # Use imap_unordered for better load balancing with varying notebook runtimes
                for _ in pool.imap_unordered(
                        self._worker_execute_one,
                        [(base, p) for p in list_of_ntb_params],
                        chunksize=1
                ):
                    pass
                pool.close()
                pool.join()

        self._timer.end(label=f"End of Notebook Executioner for {len(list_of_ntb_params)} parameters")
