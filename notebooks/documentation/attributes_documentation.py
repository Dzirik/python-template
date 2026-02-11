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

# # Attributes Refactoring
# *Version:* `1.2` *(Jupytext, time measurements, logger, param notebook execution, fixes)*

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
#     - [Functions](#2-1)   
#     - [CSV](#2-2)
#     - [XLSM](#2-3)
#     - [Comparison](#2-4)
#         - [Compare Attributes Order](#2-4-1)
#         - [Compare Attr Names and Types](#2-4-2)
#         - [Compare Lists of Attributes](#2-4-3)
# - [Final Timestamp](#3)  

# <a name="0"></a>
# # Notebook Description
# [ToC](#ToC) 

# Reads attributes from the table in csv or xlsm file.
# - **CSV is faster (2ms to 297 ms)**

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

# #### Overall Setting Specification

LOGGER_CONFIG_NAME = "logger_file_limit_console"
ADDAPT_WIDTH = True

# #### Overall Behaviour Setting

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

options.display.max_rows = 500
options.display.max_columns = 500
envs = Envs()
envs.set_logger(LOGGER_CONFIG_NAME)
Logger().start_timer(f"NOTEBOOK; Notebook name: {NOTEBOOK_NAME}")
if ADDAPT_WIDTH:
    display(HTML("<style>.container { width:100% !important; }</style>")) # notebook width

# +
# create_button()
# -

# <a name="1-3"></a>
# ### External Libraries
# [ToC](#ToC)  

from datetime import datetime

# <a name="1-4"></a>
# ### Internal Code
# [ToC](#ToC)  
# Code, libraries, classes, functions from within the repository.

# +
from src.utils.date_time_functions import create_datetime_id

from src.utils.timer import Timer

from src.data.attributes import Attributes, ATTRS_GROUPS_NAMES
# from src.data.cry_attributes import A
# -

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
PYTHON_CONFIG_NAME = "python_local"
ID = create_datetime_id(now=datetime.now(), add_micro=False)
# (END) MANDATORY FOR CONFIG DEFINITION AND NOTEBOOK AND ITS OUTPUTS IDENTIFICATION ###################################
# -

# #### Python Config Initialisation
# [ToC](#ToC)  

envs.set_config(PYTHON_CONFIG_NAME)

# #### Notebook Specific Constants
# [ToC](#ToC)  



# <a name="2"></a>
# # ANALYSIS
# [ToC](#ToC)  

timer = Timer()
timer.start()


# <a name="2-1"></a>
# ## Functions
# [ToC](#ToC) 

def compare_attributes(attrs_01, attrs_02):
    correct_output_name = []
    correct_output_type = []
    for field, data_01 in attrs_01._asdict().items():
        data_02 = getattr(attrs_02, field)
        
        # attribute names
        if data_01.name != data_02.name:
            correct_output_name.append(0)
            # print(f"{csv_data}: {A_data}")
        else:
            correct_output_name.append(1)
        
        # attribute types
        if data_01.type != data_02.type:
            correct_output_type.append(0)
            print(f"Incorrect Types: {data_01}, {data_02}")
        else:
            correct_output_type.append(1)
    print(f"Fraction of corrects names is: {round(sum(correct_output_name) / len(correct_output_name), 4)}")
    print(f"Fraction of corrects tpyes is: {round(sum(correct_output_type) / len(correct_output_type), 4)}")


# <a name="2-2"></a>
# ## CSV
# [ToC](#ToC)

# +
file_type = "csv"

timer.set_meantime("", False)
attributes_csv, dict_attrs_groups_csv = Attributes(attrs_groups_name=ATTRS_GROUPS_NAMES, file_type=file_type).get()
timer.set_meantime("CSV", True)

timer.get_data()[3]
# -

dict_attrs_groups_csv["GROUP_01"][0:20]

attributes_csv[0:10]

# <a name="2-3"></a>
# ## XLSM
# [ToC](#ToC)

# +
file_type = "xlsm"
timer.set_meantime("", False)
attributes_xlsm, dict_attrs_groups_xlsm = Attributes(attrs_groups_name=ATTRS_GROUPS_NAMES, file_type=file_type).get()
timer.set_meantime("XLSM", True)

timer.get_data()[3]
# -

# <a name="2-4"></a>
# ## Comparison
# [ToC](#ToC)

# <a name="2-4-1"></a>
# ### Compare Attributes Order
# [ToC](#ToC)

# +
# from src.data.cry_attributes import ATTRS_CT_2_1_1, ATTRS_CT_2_1_5

# print(dict_attrs_groups_csv["CT_2-1-1"] == ATTRS_CT_2_1_1)
# print(dict_attrs_groups_csv["CT_2-1-5"] == ATTRS_CT_2_1_5)
# -

# <a name="2-4-2"></a>
# ### Compare Attr Names and Types
# [ToC](#ToC)

# +
# compare_attributes(attributes_csv, A)

# +
# compare_attributes(attributes_xlsm, A)

# +
# compare_attributes(attributes_csv, attributes_xlsm)
# -

# <a name="2-4-3"></a>
# ### Compare Lists of Attributes
# [ToC](#ToC)

# +
# import src.data.cry_attributes as CA
# import src.data.attributes as AA

# +
# assert CA.ATTRS_CT_2_1_1 == AA.ATTRS_CT_2_1_1

# +
# assert CA.ATTRS_CT_2_1_5 == AA.ATTRS_CT_2_1_5
# -

# <a name="3"></a>
# # Final Timestamp
# [ToC](#ToC)  

Logger().end_timer()
