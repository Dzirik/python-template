########################################################################################################################
# BEWARE OF TABS IN FRONT - PYCHARM CHANGE IT TO FOUR SPACES ###########################################################
# NEED TO REPLACE IT - FOR EXAMPLE NOTEPAD #############################################################################
########################################################################################################################

.PHONY: help

-include make_config.mk

FILE_CODE = src/$(FILE_FOLDER)/$(FILE_NAME).py
FILE_TEST = tests/tests_$(FILE_FOLDER)/test_$(FILE_NAME).py
FILE_DOCTEST = tests/tests_$(FILE_FOLDER)/test_$(FILE_NAME).txt
UV_ENV_DIR = .venv

# UTILS ----------------------------------------------------------------------------------------------------------------

.DEFAULT: help
help: clear-console
	@python ./src/utils/make_print_documentation.py help

hello: clear-console
	@python ./src/utils/make_print_documentation.py hello

clear-console:
	@echo ""
	@# Skip clear when TERM is not set (e.g., CI)
	@if [ -n "$$TERM" ]; then clear; fi

# ENVIRONMENT ----------------------------------------------------------------------------------------------------------

set-up-repo: clear-console
	@python ./src/utils/make_print_documentation.py set-up-repo
	@echo "Setting up repository ..."
	@echo "Copying configuration files..."
	cp make_config_template.mk make_config.mk
	cp ./configurations/python_repo.conf ./configurations/python_personal.conf
	@echo "Creating .env file from template..."
	@cp .env.example .env 2>/dev/null || echo ".env already exists"
	@echo "Repository setup completed successfully!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Create virtual environment by:"
	@echo "     - Running 'make create-venv' on windows."
	@echo "     - Running 'make create-venv-linux' on Linux/macOS."
	@echo "  2. Run 'make all -i' to test the repository."
	@echo ""

install-hooks: clear-console
	@python ./src/utils/make_print_documentation.py install-hooks
	@echo "Installing Git pre-push hooks..."
	@powershell -ExecutionPolicy Bypass -File scripts/install-hooks.ps1

install-hooks-linux: clear-console
	@python ./src/utils/make_print_documentation.py install-hooks-linux
	@echo "Installing Git pre-push hooks..."
	@bash scripts/install-hooks.sh

create-venv: clear-console
	@python ./src/utils/make_print_documentation.py create-venv
	@echo "Setting up repository files..."
	@cp make_config_template.mk make_config.mk 2>/dev/null || echo "make_config.mk already exists"
	@cp ./configurations/python_repo.conf ./configurations/python_personal.conf 2>/dev/null || echo "python_personal.conf already exists"
	@python -c "from pathlib import Path; p=Path('configurations/python_personal.conf'); p.write_text(p.read_text().replace('name: \"python_repo\"','name: \"python_personal\"')) if p.exists() else None"
	@cp .env.example .env 2>/dev/null || echo ".env already exists"
	@echo "Repository setup completed!"
	@echo ""
	@echo "Creating virtual environment with Python 3.12..."
	uv python install 3.12
	uv python pin 3.12
	test -d $(UV_ENV_DIR) || uv venv $(UV_ENV_DIR)
	uv sync --all-extras --no-install-project
	@echo ""
	@echo "✅ Setup complete! Virtual environment created successfully."
	@echo "Next step: Activate the environment with: .venv\Scripts\activate"

create-venv-linux: clear-console
	@python ./src/utils/make_print_documentation.py create-venv-linux
	@echo "Setting up repository files..."
	@cp make_config_template.mk make_config.mk 2>/dev/null || echo "make_config.mk already exists"
	@cp ./configurations/python_repo.conf ./configurations/python_personal.conf 2>/dev/null || echo "python_personal.conf already exists"
	@python -c "from pathlib import Path; p=Path('configurations/python_personal.conf'); p.write_text(p.read_text().replace('name: \"python_repo\"','name: \"python_personal\"')) if p.exists() else None"
	@cp .env.example .env 2>/dev/null || echo ".env already exists"
	@echo "Repository setup completed!"
	@echo ""
	@echo "Creating virtual environment with Python 3.12..."
	uv python install 3.12
	uv python pin 3.12
	test -d $(UV_ENV_DIR) || uv venv $(UV_ENV_DIR)
	uv sync --all-extras --no-install-project
	@echo ""
	@echo "✅ Setup complete! Virtual environment created successfully."
	@echo "Next step: Activate the environment with: source .venv/bin/activate"

check-venv:
ifdef VIRTUAL_ENV
	@echo "WARNING: You are currently in a virtual environment: $(VIRTUAL_ENV)"
	@echo "Please exit the virtual environment first by running: deactivate"
	@echo "Then run the command again."
	@exit 1
endif

add-lib: clear-console check-venv
ifdef library
	@python ./src/utils/make_print_documentation.py add-lib
	@echo "Adding library: $(library)"
	uv add $(library) --frozen
	@echo "Syncing dependencies..."
	uv sync --extra windows --no-install-project
	@echo "Locking dependencies..."
	uv lock
else
	@echo "Error: Please specify library name with library=<library>[==<version>]"
endif

add-lib-win: clear-console check-venv
ifdef library
	@python ./src/utils/make_print_documentation.py add-lib-win
	@echo "Adding Windows-only library: $(library)"
	uv add $(library) --frozen --optional windows
	@echo "Syncing dependencies..."
	uv sync --extra windows --no-install-project
	@echo "Windows library $(library) added successfully!"
else
	@echo "Error: Please specify library name with library=<library>"
endif

remove-lib: clear-console check-venv
ifdef library
	@python ./src/utils/make_print_documentation.py remove-lib
	@echo "Removing library: $(library)"
	uv remove $(library) --frozen
	@echo "Syncing dependencies..."
	uv sync --extra windows --no-install-project
	@echo "Locking dependencies..."
	uv lock
else
	@echo "Error: Please specify library name with library=<library>"
endif

remove-lib-win: clear-console check-venv
ifdef library
	@python ./src/utils/make_print_documentation.py remove-lib-win
	@echo "Removing Windows-only library: $(library)"
	uv remove $(library) --frozen --optional windows
	@echo "Syncing dependencies..."
	uv sync --extra windows --no-install-project
	@echo "Windows library $(library) removed successfully!"
else
	@echo "Error: Please specify library name with library=<library>"
endif

sync-deps: clear-console
	@python ./src/utils/make_print_documentation.py sync-deps
	@echo "Syncing dependencies from pyproject.toml to uv.lock..."
	uv lock
	@echo ""
	@echo "✅ Dependencies synced successfully!"
	@echo "This updated uv.lock based on pyproject.toml"

sync-install: clear-console
	@python ./src/utils/make_print_documentation.py sync-install
	@echo "Syncing and installing all dependencies..."
	uv sync --all-extras
	@echo ""
	@echo "✅ All dependencies installed successfully!"

sync-install-dev: clear-console
	@python ./src/utils/make_print_documentation.py sync-install-dev
	@echo "Syncing and installing dev dependencies..."
	uv sync --extra dev
	@echo ""
	@echo "✅ Dev dependencies installed successfully!"

# SOURCE CODE QUALITY --------------------------------------------------------------------------------------------------

mypy-no-clear:
	@uv run --no-project python ./src/utils/make_print_documentation.py mypy-no-clear
	@uv run --no-project mypy --strict src tests --config-file mypy.ini

mypy: clear-console mypy-no-clear

format-check-no-clear:
	@uv run --no-project python ./src/utils/make_print_documentation.py format-check-no-clear
	@uv run --no-project ruff format --check src tests
	@echo ""
	@uv run --no-project python ./src/utils/print_success.py success "Success: code is already formatted"

format-check: clear-console format-check-no-clear

format-fix-no-clear:
	@uv run --no-project python ./src/utils/make_print_documentation.py format-fix-no-clear
	@uv run --no-project ruff format src tests
	@echo ""
	@uv run --no-project python ./src/utils/print_success.py success "Success: code formatted successfully"

format-fix: clear-console format-fix-no-clear

lint-check-no-clear:
	@uv run --no-project python ./src/utils/make_print_documentation.py lint-check-no-clear
	@uv run --no-project ruff check --extend-ignore D src tests
	@echo ""
	@uv run --no-project python ./src/utils/print_success.py success "Success: no linting issues found"

lint-check: clear-console lint-check-no-clear

lint-fix-no-clear:
	@uv run --no-project python ./src/utils/make_print_documentation.py lint-fix-no-clear
	@uv run --no-project ruff check --extend-ignore D --fix src tests
	@echo ""
	@uv run --no-project python ./src/utils/print_success.py success "Success: linting issues fixed"

lint-fix: clear-console lint-fix-no-clear

docstring-check-no-clear:
	@uv run --no-project python ./src/utils/make_print_documentation.py docstring-check-no-clear
	@uv run --no-project ruff check --select D --ignore D104 --ignore D200 --ignore D205 --ignore D400 --ignore D401 src tests
	@echo ""
	@uv run --no-project python ./src/utils/print_success.py success "Success: no docstring issues found"

docstring-check: clear-console docstring-check-no-clear

docstring-fix-no-clear:
	@uv run --no-project python ./src/utils/make_print_documentation.py docstring-fix-no-clear
	@uv run --no-project ruff check --select D --ignore D104 --ignore D200 --ignore D205 --ignore D400 --ignore D401 --fix src tests
	@echo ""
	@uv run --no-project python ./src/utils/print_success.py success "Success: docstring issues fixed"

docstring-fix: clear-console docstring-fix-no-clear

test-detailed-no-clear:
	@uv run --no-project python ./src/utils/make_print_documentation.py test-detailed-no-clear
	@uv run --no-project python -m pytest --verbose

test-detailed: clear-console test-detailed-no-clear

test-no-clear:
	@uv run --no-project python ./src/utils/make_print_documentation.py test-no-clear
	@uv run --no-project python -m pytest --quiet

test: clear-console test-no-clear

security-check-no-clear:
	@uv run --no-project python ./src/utils/make_print_documentation.py security-check-no-clear
	@uv run --no-project bandit -r src -c pyproject.toml
	@echo ""
	@uv run --no-project pip-audit
	@echo ""
	@uv run --no-project python ./src/utils/print_success.py success "✅ Success: no security issues found"

security-check: clear-console security-check-no-clear

all: clear-console mypy-no-clear format-check-no-clear lint-check-no-clear docstring-check-no-clear test-no-clear

all-secure: clear-console mypy-no-clear format-check-no-clear lint-check-no-clear docstring-check-no-clear test-no-clear security-check-no-clear

# ONE FILE QUALITY -----------------------------------------------------------------------------------------------------

mypy-f: clear-console
	@uv run --no-project python ./src/utils/make_print_documentation.py mypy-f
	@echo "  - File Name: $(FILE_CODE)"
	@echo ""
	@uv run --no-project mypy --strict $(FILE_CODE) --config-file mypy.ini
	@uv run --no-project python ./src/utils/make_print_documentation.py mypy-f
	@echo "  - File Name: $(FILE_TEST)"
	@echo ""
	@uv run --no-project mypy --strict $(FILE_TEST) --config-file mypy.ini
	@echo ""
	@uv run --no-project python ./src/utils/print_success.py success "Success: no type issues found"

format-check-f: clear-console
	@uv run --no-project python ./src/utils/make_print_documentation.py format-check-f
	@echo "  - File Name: $(FILE_CODE)"
	@echo ""
	@uv run --no-project ruff format --check $(FILE_CODE)
	@uv run --no-project python ./src/utils/make_print_documentation.py format-check-f
	@echo "  - File Name: $(FILE_TEST)"
	@echo ""
	@uv run --no-project ruff format --check $(FILE_TEST)
	@echo ""
	@uv run --no-project python ./src/utils/print_success.py success "Success: code is already formatted"

format-fix-f: clear-console
	@uv run --no-project python ./src/utils/make_print_documentation.py format-fix-f
	@echo "  - File Name: $(FILE_CODE)"
	@echo ""
	@uv run --no-project ruff format $(FILE_CODE)
	@uv run --no-project python ./src/utils/make_print_documentation.py format-fix-f
	@echo "  - File Name: $(FILE_TEST)"
	@echo ""
	@uv run --no-project ruff format $(FILE_TEST)

lint-check-f: clear-console
	@uv run --no-project python ./src/utils/make_print_documentation.py lint-check-f
	@echo "  - File Name: $(FILE_CODE)"
	@echo ""
	@uv run --no-project ruff check --extend-ignore D $(FILE_CODE)
	@uv run --no-project python ./src/utils/make_print_documentation.py lint-check-f
	@echo "  - File Name: $(FILE_TEST)"
	@echo ""
	@uv run --no-project ruff check --extend-ignore D $(FILE_TEST)
	@echo ""
	@uv run --no-project python ./src/utils/print_success.py success "Success: no linting issues found"

lint-fix-f: clear-console
	@uv run --no-project python ./src/utils/make_print_documentation.py lint-fix-f
	@echo "  - File Name: $(FILE_CODE)"
	@echo ""
	@uv run --no-project ruff check --extend-ignore D --fix $(FILE_CODE)
	@uv run --no-project python ./src/utils/make_print_documentation.py lint-fix-f
	@echo "  - File Name: $(FILE_TEST)"
	@echo ""
	@uv run --no-project ruff check --extend-ignore D --fix $(FILE_TEST)

docstring-check-f: clear-console
	@uv run --no-project python ./src/utils/make_print_documentation.py docstring-check-f
	@echo "  - File Name: $(FILE_CODE)"
	@echo ""
	@uv run --no-project ruff check --select D --ignore D104 --ignore D200 --ignore D205 --ignore D400 --ignore D401 $(FILE_CODE)
	@uv run --no-project python ./src/utils/make_print_documentation.py docstring-check-f
	@echo "  - File Name: $(FILE_TEST)"
	@echo ""
	@uv run --no-project ruff check --select D --ignore D104 --ignore D200 --ignore D205 --ignore D400 --ignore D401 $(FILE_TEST)
	@echo ""
	@uv run --no-project python ./src/utils/print_success.py success "Success: no docstring issues found"

docstring-fix-f: clear-console
	@uv run --no-project python ./src/utils/make_print_documentation.py docstring-fix-f
	@echo "  - File Name: $(FILE_CODE)"
	@echo ""
	@uv run --no-project ruff check --select D --ignore D104 --ignore D200 --ignore D205 --ignore D400 --ignore D401 --fix $(FILE_CODE)
	@uv run --no-project python ./src/utils/make_print_documentation.py docstring-fix-f
	@echo "  - File Name: $(FILE_TEST)"
	@echo ""
	@uv run --no-project ruff check --select D --ignore D104 --ignore D200 --ignore D205 --ignore D400 --ignore D401 --fix $(FILE_TEST)

test-f-detailed: clear-console
	@uv run --no-project python ./src/utils/make_print_documentation.py test-f-detailed
	@echo "  - File Folder: $(FILE_FOLDER)"
	@echo "  - File Name: $(FILE_NAME)"
ifeq ($(shell test -e $(FILE_TEST) && echo -n yes),yes)
	@uv run --no-project python -m pytest --verbose $(FILE_TEST)
else
	@echo "ERROR: FOLLOWING FILE DOES NOT EXIST: $(FILE_TEST)"
	@echo ""
endif
ifeq ($(shell test -e $(FILE_DOCTEST) && echo -n yes),yes)
	@uv run --no-project python -m pytest --verbose $(FILE_DOCTEST)
else
	@echo ""
	@echo "ERROR: FOLLOWING FILE DOES NOT EXIST: $(FILE_DOCTEST)"
endif

test-f: clear-console
	@uv run --no-project python ./src/utils/make_print_documentation.py test-f
	@echo "  - File Folder: $(FILE_FOLDER)"
	@echo "  - File Name: $(FILE_NAME)"
ifeq ($(shell test -e $(FILE_TEST) && echo -n yes),yes)
	@uv run --no-project python -m pytest --quiet $(FILE_TEST)
else
	@echo "ERROR: FOLLOWING FILE DOES NOT EXIST: $(FILE_TEST)"
	@echo ""
endif
ifeq ($(shell test -e $(FILE_DOCTEST) && echo -n yes),yes)
	@uv run --no-project python -m pytest --quiet $(FILE_DOCTEST)
else
	@echo ""
	@echo "ERROR: FOLLOWING FILE DOES NOT EXIST: $(FILE_DOCTEST)"
endif

all-f: mypy-f format-check-f lint-check-f docstring-check-f test-f

# COVERAGE -------------------------------------------------------------------------------------------------------------

# if you need to ignore a file, add to @pytest line to the end --ignore=tests/tests_xxx/test_yyy.py
cover-base:
	@uv run --no-project python ./src/utils/make_print_documentation.py cover-base
	@uv run --no-project pytest --cov-report html:coverage --cov=src tests/

cover: clear-console cover-base

cover-save:
	@uv run --no-project python ./src/utils/make_print_documentation.py cover-save
	@uv run --no-project python ./src/utils/cover_logger.py

cover-log: clear-console cover-base cover-save
