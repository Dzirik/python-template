# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Template Parameterized Execution Notebook
# *Version:* `2.0` *(Update to notebook 7)*

# # Table of Content
#
# - [Notebook Description](#notebook-description)
# - [General Settings](#general-settings)
#     - [Paths](#paths)
#     - [Notebook Functionality and Appearance](#notebook-functionality-and-appearance)
#     - [External Libraries](#external-libraries)
#     - [Internal Code](#internal-code)
#     - [Constants](#constants)
# - [Analysis](#analysis)
#     - [Data Generation](#data-generation)
#     - [Data Plotting](#data-plotting)
#     - [Data Saving](#data-saving)
#     - [Models Params Dictionary Printing](#models-params-dictionary-printing)
# - [Final Timestamp](#final-timestamp)

# # Notebook Description
# [ToC](#table-of-content)

# Not able to pass dictionary:
# - It is not possible because of some ... converstions. The possibility is shown here in the notebook - conversion of list of lists [key, value] into a dictionary.
#
# ### Parameters Tag
# **Parameters tag can be assigned to only one cells; if assigned to multiple cells, it works only for the first one.**
#
# ### Python Config
# It is diffence between script config (the notebooks are saved based on this one) and notebook config (the results are saved based on paths in notebook config, not script config; of course in case if they are not identical).
#
# ### Usage
#
# There is a usage of the [papermill](https://github.com/nteract/papermill) library in the core of this functionality. Please see the page and read about the usage, it is well written and documented. Hints:
# * First, turn on the tabs option in View/Cells Toolbar/Tags. <img src="..\..\assets\par_ntb_tag.png">.
# * Second, add a *parameters* tag to the cell where the selected variables to be parameterized are and hit enter to add it. If not specified/tagged, the parameters will be added as a separate cell at the top of the notebook. <img src="..\..\assets\par_ntb_tag_add.png">
# * The added tab can be seen at the top of the cell. <img src="..\..\assets\par_ntb_tag_added.png">
# * Run the script; tested from PyCharm and it worked. From console is a problem with the path.

# # GENERAL SETTINGS
# [ToC](#table-of-content)
# General settings for the notebook (paths, python libraries, own code, notebook constants).
#
# > *NOTE: All imports and constants for the notebook settings shoud be here. Nothing should be imported in the analysis section.*

# ### Paths
# [ToC](#table-of-content)
#
# Adding paths that are necessary to import code from within the repository.

import sys
import os
sys.path+=[os.path.join(os.getcwd(), ".."), os.path.join(os.getcwd(), "../..")] # one and two up

# ### Notebook Functionality and Appearance
# [ToC](#table-of-content)
# Necessary libraries for notebook functionality:
# - Set notebook width to 100%.
# - Notebook data frame setting for better visibility.
# - Initial timestamp setting and logging the start of the execution.

try:
    from src.utils.notebook_support_functions import get_notebook_name
    NOTEBOOK_NAME = get_notebook_name()
except (ImportError, AttributeError):
    NOTEBOOK_NAME = "NO_NAME"

from src.utils.logger import Logger
from src.utils.envs import Envs
from src.utils.application_config import ApplicationConfig
from pandas import options
from IPython.display import display, HTML

# > Constants for overall behaviour.

LOGGER_CONFIG_NAME = "logger_file"
ADDAPT_WIDTH = False

options.display.max_rows = 500
options.display.max_columns = 500
envs = Envs()
envs.set_logger(LOGGER_CONFIG_NAME)
Logger().start_timer(f"NOTEBOOK; Notebook name: {NOTEBOOK_NAME}")
if ADDAPT_WIDTH:
    display(HTML("<style>.container { width:100% !important; }</style>")) # notebook width

# ### External Libraries
# [ToC](#table-of-content)

from datetime import datetime
from pandas import DataFrame
from pprint import pprint
from time import sleep

# ### Internal Code
# [ToC](#table-of-content)
# Code, libraries, classes, functions from within the repository.

from src.data.saver_and_loader import SaverAndLoader
from src.utils.date_time_functions import create_datetime_id

# ### Constants
# [ToC](#table-of-content)
# Constants for the notebook.
#
# > *NOTE: Please use all letters upper.*

# #### General Constants
# [ToC](#table-of-content)

N_ROWS_TO_DISPLAY = 2
FIGURE_SIZE_SETTING = {"autosize": False, "width": 2200, "height": 750}


# #### Constants for Setting Automatic Run
# [ToC](#table-of-content)

# + tags=["parameters"]
# MANDATORY FOR CONFIG DEFINITION AND NOTEBOOK AND ITS OUTPUTS IDENTIFICATION #########################################
PYTHON_CONFIG_NAME = "python_personal"
ID = create_datetime_id(now=datetime.now(), add_micro=False)
# (END) MANDATORY FOR CONFIG DEFINITION AND NOTEBOOK AND ITS OUTPUTS IDENTIFICATION ###################################

n = 20
a = 1
b = 0
title = "Title"
sleep_seconds = 0.1

MODEL_CLASS_TYPE = "Name"
MODEL_PARAMS_LIST = [["intercept", True]]
# -

# this construct is here becuase of passing parameters through papermill
MODEL_PARAMS = {}
for items in MODEL_PARAMS_LIST:
    key, value = items
    MODEL_PARAMS[key] = value
MODEL_PARAMS

envs.set_config(PYTHON_CONFIG_NAME)

# #### Notebook Specific Constants
# [ToC](#table-of-content)



# # ANALYSIS
# [ToC](#table-of-content)

saver_and_loader = SaverAndLoader()

sleep(sleep_seconds)

# ## Data Generation
# [ToC](#table-of-content)


n = int(n) # when using config, there is a trouble with conversion
X = list(range(1, n+1))
Y = [a*x + b for x in X]

# ## Data Plotting
# [ToC](#table-of-content)


print(n)
print(X)
print(Y)

# ## Data Saving
# [ToC](#table-of-content)

print(PYTHON_CONFIG_NAME)
print(ApplicationConfig().get_data().path.data)
print(ID)

df = DataFrame(data=[[1, 2], [3, 4]], columns=["ONE", "TWO"])
df

saver_and_loader.save_dataframe_to_pickle(df=df, file_name=f"{ID}_{n}_{sleep_seconds}", where="data")

# ## Models Params Dictionary Printing
# [ToC](#table-of-content)

pprint(MODEL_PARAMS)

# # Final Timestamp
# [ToC](#table-of-content)

Logger().end_timer()
