# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Template for Repo Notebook
#
# Simple notebook with minimum necessary functionality and import to be usable within the repository.  
# *NOTE: This notebook is using jupytext.*   

# +
import sys
import os

sys.path+=[os.path.join(os.getcwd(), ".."), os.path.join(os.getcwd(), "../..")] # one and two up
# -

from src.utils.notebook_support_functions import create_button, get_notebook_name
from src.utils.logger import Logger
from src.utils.envs import Envs
from src.utils.config import Config
from pandas import options
from IPython.display import display, HTML

LOGGER_CONFIG_NAME = "logger_file_limit_console" # default
PYTHON_CONFIG_NAME = "python_personal" # default
CREATE_BUTTON = False
ADDAPT_WIDTH = False
NOTEBOOK_NAME = get_notebook_name()

options.display.max_rows = 500
options.display.max_columns = 500
envs = Envs()
envs.set_logger(LOGGER_CONFIG_NAME)
envs.set_config(PYTHON_CONFIG_NAME)
Logger().start_timer(f"NOTEBOOK; Notebook name: {NOTEBOOK_NAME}")
if CREATE_BUTTON:
    create_button()
if ADDAPT_WIDTH:
    display(HTML("<style>.container { width:100% !important; }</style>")) # notebook width

from src.utils.notebook_support_functions import get_notebook_name
from src.utils.logger import Logger

Logger().start_timer(f"NOTEBOOK; Notebook name: {get_notebook_name()}")
Logger().set_meantime("Chapter one")

# +
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt

from importlib import reload

# # %matplotlib notebook
# # %matplotlib inline
# -

N_ROWS_TO_DISPLAY = 2
FIGURE_SIZE_SETTING = {"autosize": False, "width": 2200, "height": 750}

# # Problem Caption



# # Final Timestamp

Logger().end_timer()
