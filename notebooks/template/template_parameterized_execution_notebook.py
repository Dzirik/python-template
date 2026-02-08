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
# *Version:* `1.1` *(Jupytext, time measurements, logger, param notebook execution)*

# <a name="ToC"></a>
# # Table of Content
#
# - [Notebook Description](#0)
# - [General Settings](#1)
#     - [Paths](#1-1)
#     - [Notebook Functionality and Appearance](#1-2)
#     - [External Libraries](#1-3)
#     - [Internal Code](#1-4)
#     - [Constants](#1-5)   
# - [Analysis](#2)   
#     - [Data Generation](#2-1)   
#     - [Data Plotting](#2-2)  
#     - [Data Saving](#2-3)
#     - [Models Params Dictionary Printing](#2-4)
# - [Final Timestamp](#3)  

# <a name="0"></a>
# # Notebook Description
# [ToC](#ToC) 

# ### THERE WERE  ERRORS DURING SCRIPT RUN
# First One:
# - Errors:
#     - ImportError: DLL load failed while importing _sqlite3: The specified module could not be found.
#     - papermill RuntimeError: Kernel died before replying to kernel_info.
# - The solution is [here](https://stackoverflow.com/questions/54876404/unable-to-import-sqlite3-using-anaconda-python)
#     - Download [sqlite3.dll](https://www.sqlite.org/download.html)
#     - Copy into C:\Users\YOURUSER\Anaconda3\DLLs (or C:\ProgramData\Anaconda3\DLLs).  
#
# Error running final notebook - fixed in template_notebook_final v1.1 and above:
# - Error:
#     - ImportError: DLL load failed while importing _ssl: The specified module could not be found.
# - The solution: 
#     - Comment out import of get_notebook_name() and create_button().
#     - Comment out its usage and replace with string.
#     
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
#
# > **INSTALATION NOTE:** Problems with pywin32 library was encountered with Anaconda 3.8. Downgrade to pywin32==225 helped.

# <a name="1"></a>
# # GENERAL SETTINGS
# [ToC](#ToC)  
# General settings for the notebook (paths, python libraries, own code, notebook constants). 
#
# > *NOTE: All imports and constants for the notebook settings shoud be here. Nothing should be imported in the analysis section.*

# <a name="1-1"></a>
# ### Paths
# [ToC](#ToC)  
#
# Adding paths that are necessary to import code from within the repository.

import sys
import os
sys.path+=[os.path.join(os.getcwd(), ".."), os.path.join(os.getcwd(), "../..")] # one and two up

# <a name="1-2"></a>
# ### Notebook Functionality and Appearance
# [ToC](#ToC)  
# Necessary libraries for notebook functionality:
# - A button for hiding/showing the code. By default it is deactivated and can be activated by setting CREATE_BUTTON constant to True. 
# > **NOTE: This way, using the function, the button works only in active notebook. If the functionality needs to be preserved in html export, then the code has to be incluced directly into notebook.**
# - Set notebook width to 100%.
# - Notebook data frame setting for better visibility.
# - Initial timestamp setting and logging the start of the execution.

try:
    from src.utils.notebook_support_functions import create_button, get_notebook_name
    NOTEBOOK_NAME = get_notebook_name()
    SUPPORT_FUNCTIONS_READ = True
except:
    NOTEBOOK_NAME = "NO_NAME"
    SUPPORT_FUNCTIONS_READ = False  

from src.utils.logger import Logger
from src.utils.envs import Envs
from src.utils.config import Config
from pandas import options
from IPython.display import display, HTML

# > Constants for overall behaviour.

LOGGER_CONFIG_NAME = "logger_file"
CREATE_BUTTON = False
ADDAPT_WIDTH = False

options.display.max_rows = 500
options.display.max_columns = 500
envs = Envs()
envs.set_logger(LOGGER_CONFIG_NAME)
Logger().start_timer(f"NOTEBOOK; Notebook name: {NOTEBOOK_NAME}")
if SUPPORT_FUNCTIONS_READ and CREATE_BUTTON:
    create_button()
if ADDAPT_WIDTH:
    display(HTML("<style>.container { width:100% !important; }</style>")) # notebook width

# <a name="1-3"></a>
# ### External Libraries
# [ToC](#ToC)  

from datetime import datetime
from pandas import DataFrame
from pprint import pprint
from time import sleep

# <a name="1-4"></a>
# ### Internal Code
# [ToC](#ToC)  
# Code, libraries, classes, functions from within the repository.

from src.data.saver_and_loader import SaverAndLoader
from src.utils.date_time_functions import create_datetime_id

# <a name="1-5"></a>
# ### Constants
# [ToC](#ToC)  
# Constants for the notebook.
#
# > *NOTE: Please use all letters upper.*

# #### General Constants
# [ToC](#ToC)  

# from src.global_constants import *  # Remember to import only the constants in use
N_ROWS_TO_DISPLAY = 2
FIGURE_SIZE_SETTING = {"autosize": False, "width": 2200, "height": 750}


# #### Constants for Setting Automatic Run
# [ToC](#ToC)  

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
# [ToC](#ToC)  



# <a name="2"></a>
# # ANALYSIS
# [ToC](#ToC)  

saver_and_loader = SaverAndLoader()

sleep(sleep_seconds)

# <a name="2-1"></a>
# ## Data Generation
# [ToC](#ToC)  


n = int(n) # when using config, there is a trouble with conversion
X = list(range(1, n+1))
Y = [a*x + b for x in X]

# <a name="2-2"></a>
# ## Data Plotting
# [ToC](#ToC)  


print(n)
print(X)
print(Y)

# <a name="2-3"></a>
# ## Data Saving
# [ToC](#ToC) 

print(PYTHON_CONFIG_NAME)
print(Config().get_data().path.data)
print(ID)

df = DataFrame(data=[[1, 2], [3, 4]], columns=["ONE", "TWO"])
df

saver_and_loader.save_dataframe_to_pickle(df=df, file_name=f"{ID}_{n}_{sleep_seconds}", where="data")

# <a name="2-4"></a>
# ## Models Params Dictionary Printing
# [ToC](#ToC) 

pprint(MODEL_PARAMS)

# <a name="3"></a>
# # Final Timestamp
# [ToC](#ToC)  

Logger().end_timer()
