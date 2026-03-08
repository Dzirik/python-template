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

COLORS = {
    "line": ["#0f0f0f", "#011936", "#2F3E46", "#354F52"],  # black, oxford  blue, charcoal, dask slate gray
    "fill": ["#087E8B", "#99AA38", "#F58A07", "#F7F5FB", "#FFBB00"],  # metallic seaweed (B), citron (G), dark orange,
    # ghost white, sunflower
    "error": ["#ED254E", "#C81D25"],  # red crayola, lava
    "dot": ["#99AA38", "#ED254E", "#ACD2ED"],  # green "#99AA38", yello "#F9DC5C", blue, grass "#3F681C",
    # red crayola "#ED254E"
    "paper_background": {"color": "#000000", "opacity": 0},  # outside of the plot, black with 0 opacity
    "grid_background": {"color": "#858B97", "opacity": 0.4},
    "vertical_line": ["#000000"],
    # "vertical_line": ["#000000"]
}
