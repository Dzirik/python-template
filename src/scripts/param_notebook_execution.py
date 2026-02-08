"""
Code for automatic parameterized notebook execution.

- Based on papermill library.
- The notebook has to be in *.ipynb instead of *.py.
- The script works being run from PyCharm. There is a problem with paths running it from console.
Version: 2.0
- Parallelization.
- Class extraction + NamedTuple params definition.

src/scripts> python param_notebook_execution.py
"""

import platform
import sys
from pathlib import Path
from typing import Any

sys.path += [str(Path.cwd() / ".."), str(Path.cwd() / "../..")]  # one and two up

from src.utils.notebooks_executioner import NotebookExecutioner, NotebookExecutionerNamedTuple
from src.utils.notebooks_executioner_linux import NotebookExecutionerLinux

# OVERALL SETTING ######################################################################################################
NOTEBOOK_PATH = "../../notebooks/template/template_parameterized_execution_notebook.ipynb"
OUTPUT_FOLDER = "../../data/auto_notebooks_results"
NUMBER_OF_PROCESSES = 3  # 1, 3, 20
WIN_OR_LINUX = platform.system()  # platform.system() # platform.system() "Linux" "Windows"
# (END) OVERALL SETTING ################################################################################################

# LIST_OF_NTB_PARAMS DEFINITION ########################################################################################
PYTHON_CONFIG_NAME = "python_personal"  # None

N_SLEEP_SECONDSS = [(10, 11), (15, 19), (20, 29)]

A_B_TITLE_MODEL_CLASS_TYPE_MODEL_PARAMS_LIST = [
    (1, 1, "Positive", "LinearModel", [["intercept", True]]),
    (-1, -1, "Negative", "LassoModel", [["alpha", 0.5], ["max_iter", 500]]),
    (0, 1, "Zero", "LassoModel", [["alpha", 0.75], ["max_iter", 1000]]),
]

LIST_OF_NTB_PARAMS: list[dict[str, str | int | float | list[Any] | list[list[Any]] | None]] = []
for n, sleep_seconds in N_SLEEP_SECONDSS:
    for a, b, title, model_class_type, model_params_list in A_B_TITLE_MODEL_CLASS_TYPE_MODEL_PARAMS_LIST:
        LIST_OF_NTB_PARAMS.append(
            {
                "PYTHON_CONFIG_NAME": PYTHON_CONFIG_NAME,
                "ID": None,
                "n": n,
                "a": a,
                "b": b,
                "title": title,
                "sleep_seconds": sleep_seconds,
                "MODEL_CLASS_TYPE": model_class_type,
                "MODEL_PARAMS_LIST": model_params_list,
            }
        )

# when run with no threading, the execution time is: 4.98 m
# when run with 3 threads, the execution time is: 2.18 m in no shuffle mode
# when run for equal or more than 9 processes the time is: 0.68 m
# (END) LIST_OF_NTB_PARAMS DEFINITION ##################################################################################

NOTEBOOK_EXECUTIONER_NAMED_TUPLE = NotebookExecutionerNamedTuple(
    config_name="python_personal",
    keep_name_static=False,
    add_datetime_id=True,
    add_file_name_to_notebook_name=True,
    file_name=Path(__file__).stem,
    add_params_to_name=False,
    convert_to_html=True,
    notebook_name="notebook",
    notebook_path=NOTEBOOK_PATH,
    output_folder=OUTPUT_FOLDER,
    number_of_processes=NUMBER_OF_PROCESSES,  # 1, 3, 20
    shuffle_before_processing=False,
    list_of_ntb_params=[],
)

if __name__ == "__main__":
    notebook_executioner: NotebookExecutionerLinux | NotebookExecutioner
    if WIN_OR_LINUX == "Linux":
        notebook_executioner = NotebookExecutionerLinux(params=NOTEBOOK_EXECUTIONER_NAMED_TUPLE)
    else:
        notebook_executioner = NotebookExecutioner(params=NOTEBOOK_EXECUTIONER_NAMED_TUPLE)
    notebook_executioner.set_list_of_notebook_params(list_of_ntb_params=LIST_OF_NTB_PARAMS)
    notebook_executioner.execute()
