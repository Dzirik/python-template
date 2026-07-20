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

# # Template for Final Notebook
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
#     - [Chapter](#chapter)
#         - [Sub-chapter](#sub-chapter)
# - [Final Timestamp](#final-timestamp)

# # Notebook Description
# [ToC](#table-of-content)

# > *Please put your comments about the notebook functionality here.*

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

# #### Overall Setting Specification

LOGGER_CONFIG_NAME = "logger_file_limit_console"
ADDAPT_WIDTH = True

# #### Overall Behaviour Setting

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

# ### Internal Code
# [ToC](#table-of-content)
# Code, libraries, classes, functions from within the repository.

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
# -

# #### Python Config Initialisation
# [ToC](#table-of-content)

envs.set_config(PYTHON_CONFIG_NAME)

# #### Notebook Specific Constants
# [ToC](#table-of-content)



# # ANALYSIS
# [ToC](#table-of-content)

# +
config_data = ApplicationConfig().get_data()

print(config_data.path.data)
# -

# ## Chapter
# [ToC](#table-of-content)


Logger().set_meantime("Chapter one")

# ### Sub-Chapter
# [ToC](#table-of-content)


# # Final Timestamp
# [ToC](#table-of-content)

Logger().end_timer()
