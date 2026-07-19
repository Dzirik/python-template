"""
File for storing the environment-variable key names and their canonical defaults.

This is deliberately kept separate from `src/utils/envs.py`, even though `Envs` is the only place
env vars should be read/written. Importing `envs.py` triggers `load_dotenv` as an import-time side
effect, so foundational code (such as `project_paths.py`) and tests that only need the key names or
defaults would unintentionally boot the whole env layer just to read a string constant. Keeping these
as pure data with no side-effecting imports lets that foundational code stay foundational. Do not fold
this module back into `envs.py` - `Envs` should import from here, not the other way around.
"""

# Environmental variable names (keys)
ENV_CONFIG = "ENV_CONFIG"
ENV_LOGGER = "ENV_LOGGER"
ENV_RUNNING_UNIT_TESTS = "ENV_RUNNING_UNIT_TESTS"
ENV_PROJECT_ROOT = "ENV_PROJECT_ROOT"
# Symbol is ENV_-prefixed by convention, but the live env var deliberately has no ENV_ prefix -
# name != value, do not "fix" this by renaming the variable.
ENV_HEALTHCHECK_PING_URL = "HEALTHCHECK_PING_URL"

# Canonical default values (fallback if not present in the environment or .env)
DEFAULT_CONFIG = "python_personal"
DEFAULT_LOGGER = "logger_file_limit_console"
DEFAULT_RUNNING_UNIT_TESTS = "False"
