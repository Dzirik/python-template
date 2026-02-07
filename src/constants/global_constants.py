"""
File for storing global constants.

Application-level constants that are the same for all users.
User-specific configuration defaults are now in .env file.
"""

# Environmental variable names (keys)
ENV_CONFIG = "ENV_CONFIG"
ENV_LOGGER = "ENV_LOGGER"
ENV_RUNNING_UNIT_TESTS = "ENV_RUNNING_UNIT_TESTS"

# Special variables

# When a bad logger config file is put into logger reading, then a special logger
# is created and the message is added to the following file.
# The file name should be the same as in config files for logger!
SPECIAL_LOGGER_FILE_NAME = "../../logs/logger_file_limit_console.log"

# Folders widely used in repository

FOLDER_CONFIGURATIONS = "configurations"

# Transformer method identifiers
F = "f"  # fit method in transformers
FP = "fp"  # fit_predict method in transformers
P = "p"  # predict method in transformers
INV = "i"  # inverse method
