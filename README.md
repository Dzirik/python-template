# Python Repository - Minimal Template

<a name="table-of-content"></a>
# Table of Content
- [Introduction](#introduction)
- [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Repository Set Up](#repository-set-up)
    - [Configuration](#configuration)
- [Files and Folders Structure](#files-and-folders-structure)
- [Code Quality](#code-quality)
    - [Mypy](#mypy)
    - [Ruff](#ruff)
    - [Pytest](#pytest)
    - [Security (Bandit & pip-audit)](#security)
    - [Git Hooks (Pre-Commit & Pre-Push)](#pre-push-hooks)
    - [GitHub Actions CI/CD](#github-actions)
- [Makefile](#makefile)
- [Core Tools](#core-tools)
    - [Logger](#logger)
    - [Config](#config)
    - [Timer](#timer)
    - [Environment Variables](#environment-variables)
    - [Datetime Functions](#datetime-functions)
    - [Exceptions](#exceptions)
    - [Transformers](#transformers)

<a name="introduction"></a>
# Introduction
[ToC](#table-of-content)

This is a minimal Python repository template with essential tools for professional development:
- **Logger system** with multiple configurations (file, console, size limits)
- **Configuration management** using HOCON format
- **Exception handling** with structured error codes and automatic logging
- **Data transformers** with example datetime one-hot encoder
- **Code quality tools** (mypy, ruff, pytest)
- **Make commands** for common tasks
- **Testing infrastructure** with pytest

**📊 Repository Evaluation:** See [`docs/EVALUATION.md`](docs/EVALUATION.md) for comprehensive evaluation as a base template for data-oriented tasks (Rating: 8.5/10) and [`docs/EVALUATION_SUMMARY.md`](docs/EVALUATION_SUMMARY.md) for quick reference with prioritized recommendations.

<a name="installation"></a>
# Installation
[ToC](#table-of-content)

<a name="prerequisites"></a>
## Prerequisites
[ToC](#table-of-content)

**Required:**
- Windows 10/11 or Linux (Ubuntu 20.04+)
- Make command (Windows: install via [Cygwin](https://www.cygwin.com/) with binutils and make packages)
- UV package manager (see installation below)
- Python 3.12 (recommended) or Python 3.11-3.13 (see `docs/LIBRARIES_LIST.md` for version details)

**UV Installation:**

```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

<a name="repository-set-up"></a>
## Repository Set Up
[ToC](#table-of-content)

**Quick Start:**

```bash
# 1. Clone the repository
git clone <repository-url>
cd <repository-name>

# 2. Test make installation (optional)
make hello

# 3. Create virtual environment (automatically sets up repository files)
make create-venv          # Windows
make create-venv-linux    # Linux/macOS

# 4. Activate virtual environment
.venv\Scripts\activate    # Windows
source .venv/bin/activate # Linux/macOS

# 5. Install Git pre-push hooks (optional but recommended)
make install-hooks        # Windows
make install-hooks-linux  # Linux/macOS

# 6. Run tests to verify setup
make all -i
```

The `make create-venv` command automatically sets up repository files and creates:
- `make_config.mk` (from template)
- `configurations/python_personal.conf` (from python_repo.conf)
- `.env` file (empty, for environment variables)
- Virtual environment with Python 3.12 and all dependencies

<a name="configuration"></a>
## Configuration
[ToC](#table-of-content)

**Configuration Files:**
- `configurations/python_repo.conf` - Template configuration (version controlled)
- `configurations/python_personal.conf` - Personal config (created by setup, not version controlled)
- `configurations/python_local.conf` - Example local development config with custom paths (version controlled)

**Environment Variables (.env file):**

The repository uses a `.env` file for user-specific configuration and sensitive data:

- **`.env.example`** - Template file (version controlled) with all available settings and defaults
- **`.env`** - Your personal environment file (created from `.env.example`, not version controlled)
- Automatically created by `make create-venv` from `.env.example`
- Loaded automatically by `src/utils/envs.py` using `python-dotenv`

**Default settings in `.env.example`:**
```bash
# Configuration file to use (without .conf extension)
ENV_CONFIG=python_personal

# Logger configuration to use (without .conf extension)
ENV_LOGGER=logger_file_limit_console

# Flag for running unit tests
ENV_RUNNING_UNIT_TESTS=False
```

**Customizing your environment:**

1. **Edit `.env` file** to change defaults:
   ```bash
   # Use a different config file
   ENV_CONFIG=python_local

   # Use console-only logger
   ENV_LOGGER=logger_console

   # Add custom variables
   DATABASE_PASSWORD=your_password
   API_KEY=your_api_key
   ```

2. **Or set environment variables** in your shell/IDE (overrides `.env`):
   ```bash
   export ENV_CONFIG=python_local
   export ENV_LOGGER=logger_console
   ```

**Using python_local.conf:**

The `python_local.conf` file provides an example configuration for local development with a custom data directory path (e.g., `E:/DATA` instead of `../../data`).

To use it:
```bash
# Option 1: Edit .env file
ENV_CONFIG=python_local

# Option 2: Set environment variable
export ENV_CONFIG=python_local
```

Or create your own custom configuration:
```bash
cp configurations/python_local.conf configurations/python_custom.conf
# Edit python_custom.conf with your custom settings
# Then set in .env: ENV_CONFIG=python_custom
```

**Logger Configurations:**
Available in `configurations/` folder:
- `logger_console.conf` - Console output only
- `logger_file.conf` - File output only
- `logger_file_console.conf` - Both file and console
- `logger_file_limit.conf` - File with 5MB limit, 2 backups
- `logger_file_limit_console.conf` - File limit + console

Set logger via environment variable: `ENV_LOGGER=logger_file_console`

<a name="files-and-folders-structure"></a>
# Files and Folders Structure
[ToC](#table-of-content)

This minimal repository contains the essential structure for a Python project with logger, configuration system, and testing infrastructure.

<a name="folders"></a>
## Folders
[ToC](#table-of-content)

- *assets*
    - A folder for storing additional content relevant to the project (documentation diagrams, structure visualizations).
    - Contains:
        - *minimal_repo_structure.mmd* - Mermaid diagram of repository structure
        - *minimal_repo_tree.txt* - Text-based tree structure with file descriptions
- *configurations*
    - A folder for configuration files (.conf files using HOCON format).
    - Contains:
        - *logger_console.conf* - Console-only logging configuration
        - *logger_file.conf* - File-only logging configuration
        - *logger_file_console.conf* - File + console logging configuration
        - *logger_file_limit.conf* - File logging with size limit (5MB, 2 backups)
        - *logger_file_limit_console.conf* - File limit + console logging configuration
        - *python_repo.conf* - Python configuration template (paths, database credentials)
- *data*
    - A folder for storing data files. **It is not a good practice to keep large data files in version control**.
    - This folder is empty by default and excluded from version control.
    - Can be used for local data storage during development.
- *docs*
    - For documentation files.
    - Contains:
        - *EVALUATION.md* - **Comprehensive repository evaluation for data-oriented tasks (Rating: 8.5/10, 791 lines)**
        - *EVALUATION_SUMMARY.md* - **Quick reference evaluation summary with prioritized action plan**
- *logs*
    - For log files generated by the logger system.
    - This folder is empty by default and excluded from version control.
    - Log files are created here based on logger configuration.
- *src*
    - Main folder for source code.
    - *constants*
        - Folder for storing constants.
        - *global_constants.py* - Global constants including environment variable names, folder paths, and transformer method identifiers.
        - *\_\_init\_\_.py* - Package initialization file.
    - *exceptions*
        - Custom exception classes for structured error handling.
        - *custom_exception.py* - Base exception class with error codes and descriptions
        - *data_exception.py* - Data-related exceptions (NoData, FileNotFound, IncorrectDataStructure, MismatchedDimension, WrongSorting)
        - *development_exception.py* - Development exceptions (NoProperOptionInIf, CheckFailed, NotValidOperation, NotReadyFunctionality, IncorrectValue)
        - *exception_executioner.py* - Unified exception logging and raising (Strategy pattern)
        - *\_\_init\_\_.py* - Package initialization file.
    - *transformations*
        - Data transformation classes (example: datetime one-hot encoding).
        - *base_transformer.py* - Base class for all transformers (fit/predict/fit_predict/inverse pattern)
        - *datetime_one_hot_transformer.py* - Transforms DatetimeIndex to one-hot encoded arrays
        - *\_\_init\_\_.py* - Package initialization file.
    - *utils*
        - Code used across the whole project (utilities, helpers, core functionality).
        - *config.py* - Main configuration handler (Singleton pattern)
        - *config_data.py* - Configuration data structures (NamedTuples)
        - *date_time_functions.py* - Datetime manipulation utilities (string conversion, unique ID generation)
        - *envs.py* - Environment variables handler
        - *leap_year.py* - Sample utility function (for testing make commands)
        - *logger.py* - Logger implementation (Singleton pattern with Timer integration)
        - *make_print_documentation.py* - Prints sections from README.md for Makefile help commands
        - *meta_class.py* - Metaclass for unified class monitoring
        - *singleton_meta.py* - Singleton pattern implementation
        - *timer.py* - Timer for execution time measurement
        - *\_\_init\_\_.py* - Package initialization file.
    - *\_\_init\_\_.py* - Package initialization file.
    - *Note*: In PyCharm mark this as a source folder.
- *tests*
   - For storing test files. The structure mirrors *src*, but folders start with *tests_*.
   - *tests_exceptions*
       - Tests for exception classes.
       - *\_\_init\_\_.py* - Package initialization file.
   - *tests_transformations*
       - Tests for transformation classes.
       - *test_datetime_one_hot_transformer.py* - Tests for DatetimeOneHotEncoderTransformer (parametrized pytest tests)
       - *test_datetime_one_hot_transformer.txt* - Doctest examples for datetime one-hot encoding
       - *\_\_init\_\_.py* - Package initialization file.
   - *tests_utils*
       - Tests for utilities.
       - *test_date_time_functions.py* - Tests for datetime manipulation functions (parametrized pytest tests)
       - *test_leap_year.py* - Tests for leap_year utility (parametrized pytest tests)
       - *test_meta_class.py* - Tests for meta_class functionality
       - *\_\_init\_\_.py* - Package initialization file.
   - *\_\_init\_\_.py* - Package initialization file.

<a name="files"></a>
## Files
[ToC](#table-of-content)

### Root Directory Files

- *.gitignore*
    - Excludes files and folders from version control. Configured to exclude:
        - Personal configuration files (*python_personal.conf*, *make_config.mk*)
        - Data files and directories (*data/*, *logs/*)
        - Python cache and build artifacts (*\_\_pycache\_\_*, *.pyc*, *.egg-info*)
        - Virtual environments (*.venv/*, *venv/*)
        - Coverage reports (*coverage/*)
        - IDE settings (*.idea/*, *.vscode/*)
- *.editorconfig*
    - Ensures consistent code formatting across different editors (VS Code, PyCharm, Vim, Sublime, etc.).
    - Configured for:
        - UTF-8 encoding and LF line endings by default
        - Python files: 4 spaces indentation, 120 character line length
        - YAML/JSON: 2 spaces indentation
        - Makefiles: Tab indentation (required)
        - Windows scripts (.bat, .ps1): CRLF line endings
    - **Why:** Prevents formatting inconsistencies when team members use different editors.
    - **Usage:** Most modern editors automatically detect and apply these settings.
- *.gitattributes*
    - Controls Git behavior for consistent line endings and file handling across Windows/Linux/Mac.
    - Configured for:
        - Auto-detect text files with LF normalization in repository
        - Python, config, and documentation files: Explicit LF endings
        - Windows scripts: CRLF endings
        - Binary files (images, compiled files, data files): Marked as binary to prevent Git diff/merge attempts
    - **Why:** Prevents "line ending changed" noise in diffs and ensures cross-platform consistency.
    - **Usage:**
        - New files are handled automatically by Git
        - For existing files, apply the rules once with: `git add --renormalize .` then commit the changes
        - This re-normalizes all tracked files according to the new `.gitattributes` rules
- *pyproject.toml*
    - Contains Ruff configuration for code formatting and linting.
    - Configured for 120-character line length, Python 3.11+ target.
    - Includes rules for code style, imports, naming, and simplifications.
- *LICENSE*
    - MIT License file.
- *Makefile*
    - Build automation with make commands for:
        - Virtual environment creation with automatic setup (*make create-venv*)
        - Code quality checks (*make mypy*, *make format-check*, *make lint-check*)
        - Testing (*make test*, *make all*)
        - Coverage reports (*make cover*)
    - Uses UV package manager with *uv run --no-project* commands.
- *make_config_template.mk*
    - Template for make configuration file.
    - Copy this to *make_config.mk* and customize for your local setup.
    - Contains variables for file paths used in make commands.
- *mypy.ini*
    - Configuration file for Python *mypy* static type checker.
    - Configured for strict type checking.
    - Excludes *src/external* from type checking.
- *pyproject.toml*
    - Project configuration file for Python package management.
    - Contains:
        - Project metadata (name, version, description, authors)
        - Python version requirement (*requires-python = ">=3.11,<3.14"*)
        - All project dependencies (7 runtime + 6 dev libraries)
        - Tool configurations (mypy, ruff, pytest, coverage, bandit)
    - Supports Python 3.11, 3.12, and 3.13 (see LIBRARIES_LIST.md for version details)
- *README.md*
    - Main documentation file (this file).
    - Comprehensive guide to repository structure, setup, and usage.

### Files Created During Setup

These files are created by *make create-venv* or during development and are excluded from version control:

- *.env*
    - File for local environment variables (created automatically by *make create-venv*).
    - Used to override default configuration and logger settings.
- *make_config.mk*
    - Local configuration file for make commands (created by copying *make_config_template.mk*).
    - Contains customized paths and settings for your local environment.
- *configurations/python_personal.conf*
    - Personal Python configuration file (created by copying *python_repo.conf*).
    - Customize paths, database credentials, and other settings here.
- *uv.lock*
    - Lock file for Python *UV* package manager (created by *uv sync* or *uv lock*).
    - Ensures reproducible dependency installations.
    - **Note:** Not included in minimal repo - will be generated when you set up the environment.

<a name="code-quality"></a>
# Code Quality
[ToC](#table-of-content)

<a name="mypy"></a>
## Mypy
[ToC](#table-of-content)

Mypy is a static type checker for Python that validates types before runtime.

**Usage:**
- Command line: `mypy --strict your_code.py --config-file mypy.ini`
- Makefile: `make mypy` (see [Makefile](#makefile) section)
- Configuration: `mypy.ini` file in repository root

**Type annotation examples:**
```python
# Variable
x: str = "test"

# Function
def stringify(num: int) -> str:
    return str(num)
```

**Ignoring errors:**
- Single line: `# type: ignore`
- Whole file: Add `# type: ignore` at the beginning
- Config file: Modify settings in `mypy.ini`

See [mypy documentation](https://mypy.readthedocs.io/en/latest/cheat_sheet_py3.html) for more details.

<a name="ruff"></a>
## Ruff
[ToC](#table-of-content)

Ruff is an extremely fast Python linter and code formatter, written in Rust. It replaces multiple tools (Flake8, isort, pyupgrade, etc.) with a single, fast tool.

**Usage:**
- Check formatting: `make format-check` - Check if code is formatted
- Format code: `make format-fix` - Auto-format code
- Lint code: `make lint-check` - Check for code issues
- Auto-fix issues: `make lint-fix` - Fix auto-fixable issues
- Configuration: `[tool.ruff]` section in `pyproject.toml`

**Disabling warnings:**
```python
# Disable for specific line
# ruff: noqa: E501

# Disable specific rule for entire file (at top)
# ruff: noqa: F401

# Disable all checks for a line
# noqa
```

**Key features:**
- 10-100x faster than traditional linters
- Auto-fixes many issues automatically
- Combines linting + formatting + import sorting
- Compatible with existing Python tools

See [Ruff documentation](https://docs.astral.sh/ruff/) for more information.

<a name="pytest"></a>
## Pytest
[ToC](#table-of-content)

Pytest is a testing framework for building simple and scalable tests.

**Usage:**
- Command line: `python -m pytest ./path/test_*.py`
- Makefile: `make test` or `make all` (see [Makefile](#makefile) section)
- PyCharm: Set pytest as default tester in File → Settings → Tools → Python Integrated Tools

**Example tests in repository:**
- `src/utils/leap_year.py` - Sample utility function
- `tests/tests_utils/test_leap_year.py` - Parametrized tests for leap year function
- `tests/tests_utils/test_meta_class.py` - Tests for metaclass functionality

### Coverage
[ToC](#table-of-content)

Code coverage measures the percentage of code lines covered by tests. This repository uses **pytest-cov** for coverage reporting with branch coverage enabled.

**Usage:**
- Makefile: `make cover` (generates HTML coverage report)
- View results: Open HTML files in `coverage/` folder in your browser

See [pytest-cov documentation](https://pypi.org/project/pytest-cov/) for more information.

<a name="security"></a>
## Security (Bandit & pip-audit)
[ToC](#table-of-content)

This repository uses two complementary security tools to protect against vulnerabilities:

### Bandit - Source Code Security Scanner

Bandit is a tool designed to find common security issues in Python code.

**Usage:**
- Command line: `bandit -r src -c pyproject.toml`
- Makefile: `make security-check` (see [Makefile](#makefile) section)
- Configuration: `[tool.bandit]` section in `pyproject.toml`

**What it checks:**
- Hardcoded passwords, tokens, and secrets
- SQL injection vulnerabilities
- Use of insecure functions (`eval`, `exec`, `pickle`)
- Weak cryptographic practices
- Insecure random number generation
- Shell injection risks

**Ignoring false positives:**
```python
# Ignore specific issue on a line
import pickle  # nosec B403

# Ignore all issues in a block
# nosec
def legacy_function():
    eval(user_input)  # This will be ignored
```

See [Bandit documentation](https://bandit.readthedocs.io/) for more details.

### pip-audit - Dependency Vulnerability Scanner

pip-audit scans your Python dependencies for known security vulnerabilities using the PyPI Advisory Database.

**Usage:**
- Command line: `pip-audit`
- Makefile: `make security-check` (see [Makefile](#makefile) section)
- No configuration file needed

**What it checks:**
- Known CVEs in installed packages
- Vulnerable dependency versions
- Transitive dependency vulnerabilities
- Security advisories from PyPI

**Benefits:**
- ✅ No registration required (unlike Safety CLI)
- ✅ Uses official PyPI Advisory Database
- ✅ Fast and lightweight
- ✅ Checks entire dependency tree

See [pip-audit documentation](https://pypi.org/project/pip-audit/) for more information.

### Running Security Checks

**Locally:**
```bash
# Run both Bandit and pip-audit
make security-check

# Run all quality checks including security
make all-secure
```

**In CI/CD:**
- Security checks run automatically on every PR via `make all-secure`
- Prevents vulnerable code from being merged

<a name="pre-push-hooks"></a>
## Git Hooks (Pre-Commit & Pre-Push)
[ToC](#table-of-content)

This repository includes optional **Git hooks** that help maintain code quality and prevent common mistakes. These hooks run automatically at specific points in your Git workflow.

### Installation

```bash
# Windows
make install-hooks

# Linux/macOS
make install-hooks-linux
```

Or manually:
```bash
# Linux/macOS
bash scripts/install-hooks.sh

# Windows PowerShell
powershell -ExecutionPolicy Bypass -File scripts/install-hooks.ps1
```

### What Hooks Are Installed

#### 1. Pre-Commit Hook - Branch Protection 🛡️

**Purpose:** Prevents accidental commits directly to protected branches (main, develop).

**How it works:**
- Runs automatically before every `git commit`
- Checks if you're on a protected branch (main, master, or develop)
- If yes: **Blocks the commit** and shows helpful instructions
- If no: Allows the commit normally

**Why this is helpful:**
- ✅ Prevents accidental commits to main/develop
- ✅ Enforces proper Git workflow (feature branches → PR → merge)
- ✅ Protects your main branch even locally
- ✅ Shows clear instructions on how to create a feature branch

**Example output when blocked:**
```
╔════════════════════════════════════════════════════════════════╗
║                    ❌ COMMIT BLOCKED ❌                        ║
╚════════════════════════════════════════════════════════════════╝

You are trying to commit directly to the 'main' branch.
This is not allowed to prevent accidental commits to protected branches.

✅ Recommended workflow:

  1. Create a feature branch:
     git checkout -b feature/your-feature-name

  2. Make your changes and commit:
     git add .
     git commit -m "Your commit message"

  3. Push your feature branch:
     git push origin feature/your-feature-name

  4. Create a Pull Request on GitHub to merge into 'main'
```

**Proper workflow for beginners:**
```bash
# ❌ WRONG - This will be blocked:
git checkout main
git add .
git commit -m "Add feature"  # ← BLOCKED!

# ✅ CORRECT - Use a feature branch:
git checkout -b feature/add-new-feature  # Create new branch
git add .
git commit -m "Add feature"              # ← Works!
git push origin feature/add-new-feature  # Push to GitHub
# Then create a Pull Request on GitHub
```

#### 2. Pre-Push Hook - Security Checks ⚡

**Purpose:** Runs fast security checks on changed files before pushing to GitHub.

**How it works:**
- Runs automatically before every `git push`
- Detects Python files changed since the last push
- Runs **Bandit** security scanner on those files only
- Blocks the push if security issues are found
- Provides immediate feedback (typically < 5 seconds)

**Why this is helpful:**
- ✅ Catches security issues before they reach GitHub
- ✅ Fast feedback (only scans changed files)
- ✅ Prevents embarrassing security issues in PRs
- ✅ Complements the full security scan in CI/CD

### Layered Protection Strategy

This repository uses **three layers of protection**:

1. **🛡️ Pre-Commit Hook** (Branch Protection)
   - Prevents commits to main/develop
   - Enforces feature branch workflow
   - Can be bypassed with `git commit --no-verify`

2. **⚡ Pre-Push Hook** (Fast Security Check)
   - Runs on changed files only
   - Catches security issues before push
   - Can be bypassed with `git push --no-verify`

3. **🔒 PR Workflow** (Comprehensive Security Check)
   - Runs `make all-secure` on ALL files
   - Includes both Bandit and pip-audit
   - Scans entire codebase and all dependencies
   - **Cannot be bypassed** - required for merge

### Bypassing Hooks (Not Recommended)

If you absolutely need to bypass a hook:

```bash
# Skip pre-commit hook (allows commit to main)
git commit --no-verify -m "Your message"

# Skip pre-push hook (skips security check)
git push --no-verify
```

**⚠️ Warning:** Even if you bypass local hooks, the PR workflow will still enforce all checks before allowing merge!

<a name="github-actions"></a>
## GitHub Actions CI/CD
[ToC](#table-of-content)

This repository includes automated quality checks using **GitHub Actions** that run on every pull request and push to main/develop branches.

### What It Does

The CI workflow (`.github/workflows/ci.yml`) automatically runs `make all-secure` which includes:
- ✅ **MyPy** - Type checking with strict mode
- ✅ **Ruff Format** - Code formatting validation
- ✅ **Ruff Lint** - Code quality checks (excluding docstring rules)
- ✅ **Docstring Check** - Pydocstyle validation with custom ignore rules
- ✅ **Pytest** - All unit tests
- ✅ **Bandit** - Security vulnerability scanning in source code
- ✅ **pip-audit** - Dependency vulnerability scanning

The workflow tests against **Python 3.11, 3.12, and 3.13** to ensure compatibility.

### How to Set It Up

**1. Commit the workflow file:**
```bash
git add .github/workflows/ci.yml
git commit -m "Add GitHub Actions CI workflow"
git push
```

**2. Enable GitHub Actions (if not already enabled):**
- Go to your repository on GitHub
- Click on the **"Actions"** tab
- If prompted, click **"I understand my workflows, go ahead and enable them"**

**3. That's it!** The workflow will now run automatically on:
- Every pull request to `main` or `develop` branches
- Every push to `main` or `develop` branches

### How to Use It

**When creating a pull request:**
1. Create a new branch: `git checkout -b feature/my-feature`
2. Make your changes and commit them
3. Push to GitHub: `git push origin feature/my-feature`
4. Create a pull request on GitHub
5. **The CI checks will run automatically** - you'll see them at the bottom of the PR page
6. Wait for all checks to pass (green checkmarks ✅)
7. If any check fails (red X ❌), click on it to see details and fix the issues

**Viewing results:**
- On the PR page, scroll down to see **"All checks have passed"** or **"Some checks were not successful"**
- Click **"Details"** next to any check to see the full output
- Failed checks will show exactly which command failed (mypy, ruff, pytest, etc.)

**Running checks locally before pushing:**
```bash
# Run all checks with security (same as CI)
make all-secure

# Or run all checks without security (faster)
make all

# Or run individual checks
make mypy
make format-check
make lint-check
make docstring-check
make test
make security-check
```

### Workflow Configuration

The workflow is configured in `.github/workflows/ci.yml`:
- **Triggers:** Pull requests and pushes to `main`/`develop`
- **Python versions:** 3.11, 3.12, 3.13 (matrix testing)
- **Package manager:** UV (with caching for faster runs)
- **Main command:** `make all-secure` (includes security checks)
- **Artifacts:** Coverage reports (uploaded if available)

### Customization

To modify the workflow:
1. Edit `.github/workflows/ci.yml`
2. Change the `branches` list to add/remove target branches
3. Modify the `python-version` matrix to test different Python versions
4. Add additional steps or commands as needed

See [GitHub Actions documentation](https://docs.github.com/en/actions) for more information.


<a name="makefile"></a>
# Makefile
[ToC](#table-of-content)

Common make commands for repository management. Run `make help` for full list.

**Setup:**
- `make hello` - Test make installation
- `make create-venv` - Create virtual environment with automatic repository setup (Windows)
- `make create-venv-linux` - Create virtual environment with automatic repository setup (Linux/macOS)
- `make set-up-repo` - (Optional) Manually create config files only, without virtual environment
- `make install-hooks` - Install Git hooks (pre-commit + pre-push for branch protection & security) - Windows
- `make install-hooks-linux` - Install Git hooks (pre-commit + pre-push for branch protection & security) - Linux/macOS

**Code Quality:**
- `make mypy` - Type checking with mypy
- `make format-check` - Check code formatting without changes
- `make format-fix` - Auto-format code with Ruff
- `make lint-check` - Code linting with Ruff
- `make lint-fix` - Auto-fix linting issues
- `make docstring-check` - Check docstrings with Ruff pydocstyle
- `make docstring-fix` - Auto-fix docstring issues
- `make test` - Run pytest tests (compressed output)
- `make test-detailed` - Run pytest tests (detailed output showing each test)
- `make security-check` - Run security checks (bandit + pip-audit)
- `make all -i` - Run all quality checks (mypy + format-check + lint-check + docstring-check + test)
- `make all-secure -i` - Run all quality checks + security (same as CI/CD pipeline)
- `make cover` - Generate coverage report (HTML in `coverage/` folder)

**Package Management:**
- `make add-lib library=<name>` - Add library (e.g., `make add-lib library=pandas`)
- `make remove-lib library=<name>` - Remove library
- `make sync-deps` - Sync dependencies (update uv.lock from pyproject.toml)
- `make sync-install` - Sync and install all dependencies
- `make sync-install-dev` - Sync and install dev dependencies only

**Single File Quality (configure FILE_NAME and FILE_FOLDER in make_config.mk):**
- `make mypy-f` - Type check single file
- `make format-check-f` - Check formatting for single file
- `make format-fix-f` - Auto-format single file
- `make lint-check-f` - Lint single file with Ruff
- `make lint-fix-f` - Auto-fix linting issues for single file
- `make docstring-check-f` - Check docstrings for single file
- `make docstring-fix-f` - Auto-fix docstring issues for single file
- `make test-f` - Test single file (compressed output)
- `make test-f-detailed` - Test single file (detailed output showing each test)
- `make all-f` - All checks for single file (mypy + format-check + lint-check + docstring-check + test)

## Make Documentation

### help
@HELP

Utils:
 - make hello: Prints hello message.

Repository Set Up & Virtual Environment:
 - make create-venv: Sets up repository files AND creates virtual environment named .venv on Windows.
 - .venv\Scripts\activate: Activates virtual environment on Windows.
 - make create-venv-linux: Sets up repository files AND creates virtual environment named .venv on Linux/macOS.
 - make set-up-repo: (Optional) Manually sets up repository files only, without creating virtual environment.
 - source .venv/bin/activate: Activates virtual environment on Linux/macOS.
 - make add-lib library=<library>[==<version>]: Adds a library to the virtual environment.
 - make add-lib-win library=<library>[==<version>]: Adds a windows only library to the virtual environment.
 - make remove-lib library=<library>: Removes a library from the virtual environment.
 - make remove-lib-win library=<library>: Removes a windows only library from the virtual environment.
 - make sync-deps: Syncs dependencies (updates uv.lock from pyproject.toml).
 - make sync-install: Syncs and installs all dependencies from uv.lock.
 - make sync-install-dev: Syncs and installs dev dependencies only.

Optional Git Hooks:
 - make install-hooks: Installs Git hooks (Windows) - pre-commit: blocks commits to main/develop, pre-push: security checks.
 - make install-hooks-linux: Installs Git hooks (Linux/macOS) - pre-commit: blocks commits to main/develop, pre-push: security checks.

Code Quality:
 - make mypy: MyPy type checking.
 - make format-check: Check code formatting without changes.
 - make format-fix: Auto-format code with Ruff.
 - make lint-check: Ruff code quality checking.
 - make lint-fix: Auto-fix linting issues with Ruff.
 - make docstring-check: Check docstrings with Ruff pydocstyle.
 - make docstring-fix: Auto-fix docstring issues with Ruff pydocstyle.
 - make test: Pytest testing (compressed output).
 - make test-detailed: Pytest testing (detailed output showing each test).
 - make security-check: Security checks (bandit + pip-audit).
 - make all: Runs mypy + format-check + lint-check + docstring-check + test.
 - make all-secure: Runs all + security-check (same as CI/CD pipeline).

File-Specific Quality:
 - make mypy-f FILE_CODE=<path> FILE_TEST=<path>: MyPy for specific file.
 - make format-check-f FILE_CODE=<path> FILE_TEST=<path>: Check formatting for specific file.
 - make format-fix-f FILE_CODE=<path> FILE_TEST=<path>: Auto-format specific file.
 - make lint-check-f FILE_CODE=<path> FILE_TEST=<path>: Ruff linting for specific file.
 - make lint-fix-f FILE_CODE=<path> FILE_TEST=<path>: Auto-fix linting issues for specific file.
 - make docstring-check-f FILE_CODE=<path> FILE_TEST=<path>: Check docstrings for specific file.
 - make docstring-fix-f FILE_CODE=<path> FILE_TEST=<path>: Auto-fix docstring issues for specific file.
 - make test-f FILE_FOLDER=<folder> FILE_NAME=<name>: Pytest for specific file (compressed).
 - make test-f-detailed FILE_FOLDER=<folder> FILE_NAME=<name>: Pytest for specific file (detailed).
 - make all-f FILE_FOLDER=<folder> FILE_NAME=<name>: All checks for specific file (mypy + format-check + lint-check + docstring-check + test).

Coverage:
 - make cover: Generates coverage report in coverage/ folder.
 - make cover-log: Generates coverage and logs overall ratio.

@

### hello
@HAIL TO YOU, HERO!!!
@CONGRATULATIONS TO YOU RUNNING YOUR FIRST MAKE COMMAND!!

### create-venv
@CREATES VIRTUAL ENVIRONMENT WITH AUTOMATIC REPOSITORY SETUP FOR WINDOWS
Automatically sets up repository files and creates virtual environment:
 - Copies make_config_template.mk to make_config.mk
 - Copies python_repo.conf to python_personal.conf
 - Creates .env file
 - Installs Python 3.12
 - Creates venv .venv for Windows (all dependencies: base + [windows] + [dev])
@

### create-venv-linux
@CREATES VIRTUAL ENVIRONMENT WITH AUTOMATIC REPOSITORY SETUP FOR LINUX/MACOS
Automatically sets up repository files and creates virtual environment:
 - Copies make_config_template.mk to make_config.mk
 - Copies python_repo.conf to python_personal.conf
 - Creates .env file
 - Installs Python 3.12
 - Creates venv .venv for Linux/macOS (all dependencies: base + [dev])
@

### set-up-repo
@MANUALLY SETS UP REPOSITORY FILES (OPTIONAL)
Creates necessary files excluded from version control but needed for functionality.
 - Copies make_config_template.mk to make_config.mk
 - Copies python_repo.conf to python_personal.conf
 - Creates .env file
Note: This is now automatically done by create-venv commands.
@

### install-hooks
@INSTALLS GIT HOOKS FOR BRANCH PROTECTION AND SECURITY
Installs two Git hooks to improve workflow and security:

1. Pre-Commit Hook (Branch Protection):
   - Blocks direct commits to main, master, and develop branches
   - Enforces feature branch workflow
   - Shows helpful instructions when blocked
   - Prevents accidental commits to protected branches

2. Pre-Push Hook (Security Checks):
   - Runs Bandit security scanner on changed Python files
   - Fast feedback (< 5 seconds, only scans changes)
   - Catches security issues before push
   - Complements full CI/CD security scan

Installation location:
 - Windows: Uses scripts/install-hooks.ps1
 - Hooks installed to: .git/hooks/

Bypassing hooks (not recommended):
 - Skip pre-commit: git commit --no-verify
 - Skip pre-push: git push --no-verify

Note: Even if bypassed locally, PR workflow still enforces all checks.
@

### install-hooks-linux
@INSTALLS GIT HOOKS FOR BRANCH PROTECTION AND SECURITY
Installs two Git hooks to improve workflow and security:

1. Pre-Commit Hook (Branch Protection):
   - Blocks direct commits to main, master, and develop branches
   - Enforces feature branch workflow
   - Shows helpful instructions when blocked
   - Prevents accidental commits to protected branches

2. Pre-Push Hook (Security Checks):
   - Runs Bandit security scanner on changed Python files
   - Fast feedback (< 5 seconds, only scans changes)
   - Catches security issues before push
   - Complements full CI/CD security scan

Installation location:
 - Linux/macOS: Uses scripts/install-hooks.sh
 - Hooks installed to: .git/hooks/

Bypassing hooks (not recommended):
 - Skip pre-commit: git commit --no-verify
 - Skip pre-push: git push --no-verify

Note: Even if bypassed locally, PR workflow still enforces all checks.
@

### add-lib
@ADDS LIBRARY TO VIRTUAL ENVIRONMENT
Adds a library to the virtual environment, updates pyproject.toml and lock files.

Usage: make add-lib library=<library>[==<version>]

Examples:
 - Exact version: make add-lib library=requests==2.31.0
 - Latest version: make add-lib library=pandas
 - Version range: make add-lib library="numpy>=1.24.0,<2.0.0"
 - Minimum version: make add-lib library="scikit-learn>=1.3.0"

Note: Use quotes for version ranges with special characters (>, <, etc.)
@

### add-lib-win
@ADDS WINDOWS ONLY LIBRARY TO VIRTUAL ENVIRONMENT
Adds a windows only library to the virtual environment, updates pyproject.toml and lock files.

Usage: make add-lib-win library=<library>[==<version>]

Examples:
 - Exact version: make add-lib-win library=pywin32==311
 - Latest version: make add-lib-win library=pypiwin32
 - Version range: make add-lib-win library="pywinpty>=3.0.0,<4.0.0"

Note: Use quotes for version ranges with special characters (>, <, etc.)
@

### remove-lib
@REMOVES LIBRARY FROM VIRTUAL ENVIRONMENT
Removes a library from the virtual environment, updates pyproject.toml and lock files.

Usage: make remove-lib library=<library>

Examples:
 - make remove-lib library=requests
 - make remove-lib library=pandas
 - make remove-lib library=numpy

Note: Do not specify version when removing - just the library name.
@

### remove-lib-win
@REMOVES WINDOWS ONLY LIBRARY FROM VIRTUAL ENVIRONMENT
Removes a windows only library from the virtual environment, updates pyproject.toml and lock files.

Usage: make remove-lib-win library=<library>

Examples:
 - make remove-lib-win library=pywin32
 - make remove-lib-win library=pypiwin32
 - make remove-lib-win library=pywinpty

Note: Do not specify version when removing - just the library name.
@

### sync-deps
@SYNCS DEPENDENCIES (UPDATES UV.LOCK FROM PYPROJECT.TOML)
Updates the uv.lock file based on the current pyproject.toml dependencies.
Use this when you manually edit pyproject.toml or install packages outside of make commands.

Usage: make sync-deps

When to use:
 - After manually editing pyproject.toml dependencies
 - After installing packages with 'uv add' directly
 - When uv.lock is out of sync with pyproject.toml
 - To regenerate lock file with latest compatible versions

This command does NOT install packages - it only updates the lock file.
Use 'make sync-install' or 'make sync-install-dev' to install after syncing.
@

### sync-install
@SYNCS AND INSTALLS ALL DEPENDENCIES
Syncs the lock file and installs ALL dependencies (base + all extras including dev and windows).

Usage: make sync-install

This command:
 1. Updates uv.lock from pyproject.toml
 2. Installs all dependencies from all groups (base, dev, windows, etc.)

Use this when:
 - Setting up a complete development environment
 - After pulling changes that modified dependencies
 - When you want all optional dependencies installed
@

### sync-install-dev
@SYNCS AND INSTALLS DEV DEPENDENCIES
Syncs the lock file and installs base + dev dependencies only.

Usage: make sync-install-dev

This command:
 1. Updates uv.lock from pyproject.toml
 2. Installs base dependencies + dev dependencies (pytest, mypy, ruff, etc.)

Use this when:
 - Setting up a development environment
 - You only need dev tools, not platform-specific extras
 - After the initial 'make create-venv' to update dependencies
@

### mypy-no-clear
@DOES MYPY TYPE CHECKING
MyPy type checking in src and tests folders with strict mode.
A line can be excluded from checking by adding: # type: ignore
@

### format-check-no-clear
@CHECKS CODE FORMATTING
Ruff format checking without making changes.
Returns error if code is not properly formatted.
@

### format-fix-no-clear
@AUTO-FORMATS SOURCE CODE
Ruff code formatting in src and tests folders.
Automatically formats code to consistent style (120 char line length).
@

### lint-check-no-clear
@LINTS SOURCE CODE
Ruff code quality checking in src and tests folders.
A line can be excluded from checking by adding: # noqa
Specific rules can be disabled: # ruff: noqa: E501
@

### lint-fix-no-clear
@AUTO-FIXES LINTING ISSUES
Ruff linting with automatic fixes applied.
Fixes auto-fixable issues like unused imports, formatting, etc.
@

### docstring-check-no-clear
@CHECKS DOCSTRINGS
Ruff pydocstyle (D rules) checking for docstring presence and formatting.
Checks for missing docstrings, formatting issues, and content quality.
Preserves custom Sphinx/reST style (:param:, :return:).
@

### docstring-fix-no-clear
@AUTO-FIXES DOCSTRING ISSUES
Ruff pydocstyle with automatic fixes applied.
Fixes auto-fixable issues like formatting, whitespace, quotes, and punctuation.
Missing docstrings and imperative mood issues require manual fixes.
@

### test-detailed-no-clear
@RUNS PYTEST FOR ALL FILES (DETAILED)
Executes pytest on all test files with verbose output showing each test case.
@

### test-no-clear
@RUNS PYTEST FOR ALL FILES (COMPRESSED)
Executes pytest on all test files with quiet output showing only summary.
@

### security-check-no-clear
@RUNS SECURITY CHECKS
Executes security scanning tools:
 - Bandit: Scans Python code for common security issues
 - pip-audit: Checks dependencies for known security vulnerabilities
@

### security-check
@RUNS SECURITY CHECKS
Clears console and executes security scanning tools:
 - Bandit: Scans Python code for common security issues (hardcoded passwords, SQL injection, etc.)
 - pip-audit: Checks dependencies for known security vulnerabilities (CVEs)

Recommended to run before creating pull requests.
Use 'make all-secure' to run all quality checks including security.
@

### mypy-f
@DOES MYPY TYPE CHECKING FOR SPECIFIC FILE
Type checks both the source file and its corresponding test file.
@

### format-check-f
@CHECKS CODE FORMATTING FOR SPECIFIC FILE
Checks formatting for both the source file and its corresponding test file without making changes.
@

### format-fix-f
@AUTO-FORMATS SPECIFIC FILE
Automatically formats both the source file and its corresponding test file.
@

### lint-check-f
@LINTS SPECIFIC FILE
Runs Ruff code quality checking on both the source file and its corresponding test file.
@

### lint-fix-f
@AUTO-FIXES LINTING ISSUES FOR SPECIFIC FILE
Runs Ruff with automatic fixes on both the source file and its corresponding test file.
@

### docstring-check-f
@CHECKS DOCSTRINGS FOR SPECIFIC FILE
Ruff pydocstyle (D rules) checking for both the source file and its corresponding test file.
Checks for missing docstrings, formatting issues, and content quality.
Preserves custom Sphinx/reST style (:param:, :return:).
@

### docstring-fix-f
@AUTO-FIXES DOCSTRING ISSUES FOR SPECIFIC FILE
Ruff pydocstyle with automatic fixes applied to both the source file and its corresponding test file.
Fixes auto-fixable issues like formatting, whitespace, quotes, and punctuation.
Missing docstrings and imperative mood issues require manual fixes.
@

### test-f-detailed
@RUNS PYTEST FOR SPECIFIC FILE (DETAILED)
Executes pytest on a specific test file with verbose output showing each test case.
@

### test-f
@RUNS PYTEST FOR SPECIFIC FILE (COMPRESSED)
Executes pytest on a specific test file with quiet output showing only summary.
@

### all
@RUNS ALL QUALITY CHECKS
Executes all quality checks in sequence: mypy + format-check + lint-check + docstring-check + test.
Clears console before starting and runs all checks without clearing between steps.
Stops at first failure to quickly identify issues.
@

### all-secure
@RUNS ALL QUALITY CHECKS + SECURITY CHECKS
Executes all quality checks plus security scanning: mypy + format-check + lint-check + docstring-check + test + security-check.
This is the same command used in CI/CD pipeline to ensure code quality and security before merging.
Recommended to run before creating pull requests.
@

### all-f
@RUNS ALL QUALITY CHECKS FOR SPECIFIC FILE
Executes all quality checks for a single file: mypy-f + format-check-f + lint-check-f + docstring-check-f + test-f.
Checks both the source file and its corresponding test file.
Configure FILE_NAME and FILE_FOLDER in make_config.mk before running.
@

### cover-base
@GENERATES COVERAGE REPORT
Creates complete coverage report for the repository.
The HTML report can be found in the coverage/ folder (excluded from git).
@

### cover-save
@SAVES COVERAGE RATIO TO LOG FILE
Saves the overall coverage percentage to reports/cover_log.csv for tracking over time.
@



<a name="core-tools"></a>
# Core Tools
[ToC](#table-of-content)

<a name="logger"></a>
## Logger
[ToC](#table-of-content)

Singleton-based logging system with timer integration. Located in `src/utils/logger.py`.

**Usage:**
```python
from src.utils.logger import Logger

logger = Logger()
logger.info("Application started")
logger.warning("Warning message")
logger.error("Error occurred")

# Timer integration
logger.start_timer("data_processing")
logger.set_meantime("loaded data")
logger.end_timer()
```

**Configuration:** Set via `ENV_LOGGER` environment variable (see [Configuration](#configuration) section).

<a name="config"></a>
## Config
[ToC](#table-of-content)

Singleton-based configuration management using HOCON format. Located in `src/utils/config.py`.

**Configuration Structure:**
- `name` - Project name
- `path.data` - Main data folder path

**Usage:**
```python
from src.utils.config import Config

config = Config()
data = config.get_data()

# Access configuration values
print(data.name)           # "python_repo"
print(data.path.data)      # "../../data"
```

**Configuration File:** `configurations/python_repo.conf` (HOCON format)

**Environment Variable:** Set via `ENV_CONFIG` (default: `python_personal`).

<a name="timer"></a>
## Timer
[ToC](#table-of-content)

Execution time measurement tool. Located in `src/utils/timer.py`.

**Usage:**
```python
from src.utils.timer import Timer

timer = Timer()
timer.start()
# ... your code ...
timer.set_meantime("step 1")
# ... more code ...
timer.end("step 2")

# Get results
results = timer.get_data()
```

**Key Methods:** `start()`, `set_meantime(label)`, `end(label)`, `get_data()`

<a name="environment-variables"></a>
## Environment Variables
[ToC](#table-of-content)

Environment variable management via `src/utils/envs.py`.

**Key Methods:**
- `set_config(value)` / `get_config()` - Config file selection
- `set_logger(value)` / `get_logger()` - Logger config selection
- `set_running_unit_tests(value)` / `get_running_unit_tests()` - Test mode flag

**Defaults** (in `.env` file):
- `ENV_CONFIG=python_personal`
- `ENV_LOGGER=logger_file_limit_console`
- `ENV_RUNNING_UNIT_TESTS=False`

See `.env.example` for the template with all available settings.

<a name="datetime-functions"></a>
## Datetime Functions
[ToC](#table-of-content)

Utility functions for datetime manipulation and unique ID generation. Located in `src/utils/date_time_functions.py`.

**Key Functions:**

```python
from datetime import datetime
from src.utils.date_time_functions import (
    convert_datetime_to_string_date,
    convert_string_date_to_datetime,
    create_datetime_id,
    create_date_id,
    add_zeros_in_front_and_convert_to_string
)

# Convert datetime to string format: yyyy-mm-dd-hh-mm-ss
now = datetime.now()
date_str = convert_datetime_to_string_date(now)
# Output: "2024-01-15-10-30-45"

# With microseconds
date_str_micro = convert_datetime_to_string_date(now, add_micro=True)
# Output: "2024-01-15-10-30-45-123456"

# Custom separator
date_str_custom = convert_datetime_to_string_date(now, sep="_")
# Output: "2024_01_15_10_30_45"

# Convert string back to datetime
dt = convert_string_date_to_datetime("2024-01-15-10-30-45")
# Returns: datetime(2024, 1, 15, 10, 30, 45)

# Create unique datetime ID with random suffix
datetime_id = create_datetime_id()
# Output: "2024-01-15-10-30-45_237"

# Create unique date ID (date only)
date_id = create_date_id()
# Output: "2024-01-15_842"

# Add leading zeros to numbers
padded = add_zeros_in_front_and_convert_to_string(5, 100)
# Output: "05"
```

**Use Cases:**
- **Unique file naming**: Generate timestamped filenames with random suffix to avoid collisions
- **Log file organization**: Create date-based directory structures
- **Data versioning**: Track data snapshots with datetime identifiers
- **String formatting**: Convert datetime objects to consistent string format

**Features:**
- Consistent datetime string format across the project
- Random suffix (000-999) for uniqueness
- Bidirectional conversion (datetime ↔ string)
- Customizable separators and microsecond precision

**Dependencies:**
- `datetime` (standard library)
- `numpy.random.randint` (for random ID generation)

See `tests/tests_utils/test_date_time_functions.py` for comprehensive usage examples.


<a name="exceptions"></a>
## Exceptions
[ToC](#table-of-content)

Custom exception system with error codes and structured error handling. Located in `src/exceptions/`.

**Base Exception:**
```python
from src.exceptions.custom_exception import CustomException

# All custom exceptions inherit from CustomException
# Each exception has:
# - group_name: Category of the exception
# - code: Unique error code
# - description: Error message
```

**Data Exceptions** (`src/exceptions/data_exception.py`):
```python
from src.exceptions.data_exception import (
    NoData,                      # Code 101: Data not available
    IncorrectDataStructure,      # Code 102: Wrong data structure
    FileNotFound,                # Code 103: File not found
    MismatchedDimension,         # Code 104: Dimension mismatch
    WrongSorting                 # Code 105: Incorrect sorting
)

# Usage
raise NoData("Expected data in database table 'users'")
raise FileNotFound("config.json not found in /configs")
```

**Development Exceptions** (`src/exceptions/development_exception.py`):
```python
from src.exceptions.development_exception import (
    NoProperOptionInIf,          # Code 301: Missing if/else branch
    CheckFailed,                 # Code 302: Validation failed
    NotValidOperation,           # Code 303: Invalid operation
    NotReadyFunctionality,       # Code 304: Feature not implemented
    IncorrectValue               # Code 305: Invalid value
)

# Usage
raise NoProperOptionInIf("Status 'pending' not handled in if statement")
raise NotReadyFunctionality("Export to PDF not yet implemented")
```

**Exception Executioner** (`src/exceptions/exception_executioner.py`):

Unified exception handling with automatic logging (Strategy pattern):

```python
from src.exceptions.exception_executioner import ExceptionExecutioner
from src.exceptions.development_exception import CheckFailed

# Automatically logs error and raises exception
ExceptionExecutioner(CheckFailed).log_and_raise("Validation failed: age < 0")

# With custom message
ExceptionExecutioner(NoData).log_and_raise("No records found for user_id=123")
```

**Features:**
- Structured error codes for easy debugging
- Automatic logging integration (skipped during unit tests)
- Consistent error message format: `<code> <group> <description>`
- Example: `"301 Development. Option is not present in the if statement."`

**Note:** Exception logging is automatically disabled during unit tests (when `ENV_RUNNING_UNIT_TESTS="True"`).


<a name="transformers"></a>
## Transformers
[ToC](#table-of-content)

Data transformation classes for preprocessing and feature engineering. Located in `src/transformations/`.

**Base Transformer Pattern:**

All transformers inherit from `BaseTransformer` and implement a consistent interface:

```python
from src.transformations.base_transformer import BaseTransformer

# All transformers implement:
# - fit(data) - Learn transformation parameters from data
# - predict(data) - Apply transformation to new data
# - fit_predict(data) - Fit and transform in one step
# - inverse(data) - Reverse transformation (if applicable)
# - get_params() / restore_from_params() - Save/load transformer state
```

**Example: Datetime One-Hot Encoder**

Transforms DatetimeIndex to one-hot encoded arrays for time-based features:

```python
from pandas import DatetimeIndex
from datetime import datetime
from src.transformations.datetime_one_hot_transformer import DatetimeOneHotEncoderTransformer

# Create sample datetime data
dt_data = DatetimeIndex([
    datetime(2024, 1, 15, 10, 30),
    datetime(2024, 2, 20, 14, 45),
    datetime(2024, 3, 25, 18, 15)
])

# Initialize transformer
transformer = DatetimeOneHotEncoderTransformer()

# Fit and transform with selected time attributes
encoded = transformer.fit_predict(
    dt_index=dt_data,
    add_hours=True,          # Hours: 0-23
    add_days_of_week=True,   # Days: Monday=0, Sunday=6
    add_weekend=True,        # Weekend: 0=weekday, 1=weekend
    add_months=True,         # Months: January=1, December=12
    add_years=False,         # Years: yyyy format
    min_interval=0           # Minute intervals (0=disabled)
)

# Get column names for encoded features
feature_names = transformer.get_encoded_attribute_names()
print(feature_names)
# Output: ['HOUR_10.0', 'HOUR_14.0', 'HOUR_18.0', 'DAY_OF_WEEK_0.0', ...]

# Transform new data using fitted encoder
new_data = DatetimeIndex([datetime(2024, 4, 10, 10, 30)])
new_encoded = transformer.predict(new_data)
```

**Key Features:**
- **Flexible time attributes**: Select hours, days of week, weekend flag, months, years, or minute intervals
- **One-hot encoding**: Uses sklearn's OneHotEncoder with `handle_unknown="ignore"` for unseen values
- **Feature names**: Returns descriptive column names for encoded attributes
- **Sklearn-style API**: Familiar fit/predict pattern for easy integration

**Use Cases:**
- Time series feature engineering
- Cyclical time pattern encoding
- Calendar-based feature extraction
- Machine learning preprocessing

**Dependencies:**
- `pandas.DatetimeIndex` - Datetime handling
- `numpy` - Array operations
- `sklearn.preprocessing.OneHotEncoder` - One-hot encoding

See `tests/tests_transformations/test_datetime_one_hot_transformer.py` for comprehensive usage examples.
