########################################################################################################################
# BEWARE OF TABS IN FRONT - PYCHARM CHANGE IT TO FOUR SPACES ###########################################################
# NEED TO REPLACE IT - FOR EXAMPLE NOTEPAD #############################################################################
########################################################################################################################

.PHONY: help hello clear-console install-hooks create-venv check-venv \
	add-lib add-lib-win remove-lib remove-lib-win lock sync \
	mypy-no-clear mypy format-check-no-clear format-check format-fix-no-clear format-fix \
	lint-check-no-clear lint-check lint-fix-no-clear lint-fix \
	docstring-check-no-clear docstring-check docstring-fix-no-clear docstring-fix \
	test-detailed-no-clear test-detailed test-no-clear test \
	security-check-no-clear security-check all all-secure \
	mypy-f format-check-f format-fix-f lint-check-f lint-fix-f \
	docstring-check-f docstring-fix-f test-f-detailed test-f all-f \
	jupyter marimo marimo-app marimo-new marimo-convert \
	cover-base cover cover-save cover-log

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

install-hooks: clear-console
	@python ./src/utils/make_print_documentation.py install-hooks
	@echo "Installing Git pre-push hooks..."
ifeq ($(OS),Windows_NT)
	@powershell -ExecutionPolicy Bypass -File scripts/install-hooks.ps1
else
	@bash scripts/install-hooks.sh
endif

create-venv: clear-console
	@python ./src/utils/make_print_documentation.py create-venv
	@echo "Setting up repository files..."
	@test -f make_config.mk && echo "make_config.mk already exists" || cp make_config_template.mk make_config.mk
	@test -f ./configurations/python_personal.toml && echo "python_personal.toml already exists" || python -c "from pathlib import Path; Path('configurations/python_personal.toml').write_text('# Personal config overlay - deep-merged over configurations/python_repo.toml (the tracked base).\n# Set only the keys you want to override; anything left commented out falls back to\n# python_repo.toml. Activate this profile by setting ENV_CONFIG=python_personal in your .env.\n#\n# name is set from the ENV_CONFIG selection, not read from this file - no need to set it here.\n\n# [path]\n# data = \"E:/DATA\"\n\n# [param_ntb_execution]\n# output_folder = \"reports\"\n')"
	@test -f .env && echo ".env already exists" || cp .env.example .env
	@test -f notebooks/raw/playground_notebook.py || cp notebooks/template/template_notebook_final.py notebooks/raw/playground_notebook.py
	@test -f marimo/raw/playground_marimo.py || cp marimo/template/template_notebook.py marimo/raw/playground_marimo.py
	@echo "Repository setup completed!"
	@echo ""
	@echo "Creating virtual environment with Python 3.13..."
	uv python install 3.13
	uv python pin 3.13
	test -d $(UV_ENV_DIR) || uv venv $(UV_ENV_DIR)
	uv sync
	@echo ""
	@echo "✅ Setup complete! Virtual environment created successfully."
ifeq ($(OS),Windows_NT)
	@echo "Next step: Activate the environment with: .venv\Scripts\activate"
else
	@echo "Next step: Activate the environment with: source .venv/bin/activate"
endif

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
	uv add $(library)
	@echo "Library $(library) added successfully!"
else
	@echo "Error: Please specify library name with library=<library>[==<version>]"
endif

add-lib-win: clear-console check-venv
ifdef library
	@python ./src/utils/make_print_documentation.py add-lib-win
	@echo "Adding Windows-only library: $(library)"
	uv add --group windows $(library)
	@echo "Windows library $(library) added successfully!"
else
	@echo "Error: Please specify library name with library=<library>"
endif

remove-lib: clear-console check-venv
ifdef library
	@python ./src/utils/make_print_documentation.py remove-lib
	@echo "Removing library: $(library)"
	uv remove $(library)
	@echo "Library $(library) removed successfully!"
else
	@echo "Error: Please specify library name with library=<library>"
endif

remove-lib-win: clear-console check-venv
ifdef library
	@python ./src/utils/make_print_documentation.py remove-lib-win
	@echo "Removing Windows-only library: $(library)"
	uv remove --group windows $(library)
	@echo "Windows library $(library) removed successfully!"
else
	@echo "Error: Please specify library name with library=<library>"
endif

lock: clear-console
	@python ./src/utils/make_print_documentation.py lock
	@echo "Locking dependencies from pyproject.toml..."
	uv lock
	@echo ""
	@echo "✅ Lock file updated successfully!"

sync: clear-console
	@python ./src/utils/make_print_documentation.py sync
	@echo "Syncing dependencies from uv.lock..."
	uv sync
	@echo ""
	@echo "✅ Dependencies synced successfully!"

# SOURCE CODE QUALITY --------------------------------------------------------------------------------------------------

mypy-no-clear:
	@uv run python ./src/utils/make_print_documentation.py mypy-no-clear
	@uv run mypy --strict src tests --config-file mypy.ini

mypy: clear-console mypy-no-clear

format-check-no-clear:
	@uv run python ./src/utils/make_print_documentation.py format-check-no-clear
	@uv run ruff format --check src tests
	@echo ""
	@uv run python ./src/utils/print_success.py success "Success: code is already formatted"

format-check: clear-console format-check-no-clear

format-fix-no-clear:
	@uv run python ./src/utils/make_print_documentation.py format-fix-no-clear
	@uv run ruff format src tests
	@echo ""
	@uv run python ./src/utils/print_success.py success "Success: code formatted successfully"

format-fix: clear-console format-fix-no-clear

lint-check-no-clear:
	@uv run python ./src/utils/make_print_documentation.py lint-check-no-clear
	@uv run ruff check --extend-ignore D src tests
	@echo ""
	@uv run python ./src/utils/print_success.py success "Success: no linting issues found"

lint-check: clear-console lint-check-no-clear

lint-fix-no-clear:
	@uv run python ./src/utils/make_print_documentation.py lint-fix-no-clear
	@uv run ruff check --extend-ignore D --fix src tests
	@echo ""
	@uv run python ./src/utils/print_success.py success "Success: linting issues fixed"

lint-fix: clear-console lint-fix-no-clear

docstring-check-no-clear:
	@uv run python ./src/utils/make_print_documentation.py docstring-check-no-clear
	@uv run ruff check --select D --ignore D104 --ignore D200 --ignore D205 --ignore D400 --ignore D401 src tests
	@echo ""
	@uv run python ./src/utils/print_success.py success "Success: no docstring issues found"

docstring-check: clear-console docstring-check-no-clear

docstring-fix-no-clear:
	@uv run python ./src/utils/make_print_documentation.py docstring-fix-no-clear
	@uv run ruff check --select D --ignore D104 --ignore D200 --ignore D205 --ignore D400 --ignore D401 --fix src tests
	@echo ""
	@uv run python ./src/utils/print_success.py success "Success: docstring issues fixed"

docstring-fix: clear-console docstring-fix-no-clear

test-detailed-no-clear:
	@uv run python ./src/utils/make_print_documentation.py test-detailed-no-clear
	@uv run python -m pytest --verbose

test-detailed: clear-console test-detailed-no-clear

test-no-clear:
	@uv run python ./src/utils/make_print_documentation.py test-no-clear
	@uv run python -m pytest --quiet

test: clear-console test-no-clear

security-check-no-clear:
	@uv run python ./src/utils/make_print_documentation.py security-check-no-clear
	@uv run bandit -r src -c pyproject.toml
	@echo ""
	@tmp_reqs=$$(mktemp) && \
		uv export --frozen --no-hashes -q -o "$$tmp_reqs" && \
		uv run pip-audit -r "$$tmp_reqs"; \
		status=$$?; rm -f "$$tmp_reqs"; exit $$status
	@echo ""
	@uv run python ./src/utils/print_success.py success "Success: no security issues found"

security-check: clear-console security-check-no-clear

all: clear-console mypy-no-clear format-check-no-clear lint-check-no-clear docstring-check-no-clear test-no-clear

all-secure: clear-console mypy-no-clear format-check-no-clear lint-check-no-clear docstring-check-no-clear test-no-clear security-check-no-clear

# ONE FILE QUALITY -----------------------------------------------------------------------------------------------------

mypy-f: clear-console
	@uv run python ./src/utils/make_print_documentation.py mypy-f
	@echo "  - File Name: $(FILE_CODE)"
	@echo ""
	@uv run mypy --strict $(FILE_CODE) --config-file mypy.ini
ifeq ($(shell test -e $(FILE_TEST) && echo -n yes),yes)
	@uv run python ./src/utils/make_print_documentation.py mypy-f
	@echo "  - File Name: $(FILE_TEST)"
	@echo ""
	@uv run mypy --explicit-package-bases --strict $(FILE_TEST) --config-file mypy.ini
else
	@echo ""
	@echo "⚠ Warning: Test file not found, skipping mypy check: $(FILE_TEST)"
endif
	@echo ""
	@uv run python ./src/utils/print_success.py success "Success: no type issues found"

format-check-f: clear-console
	@uv run python ./src/utils/make_print_documentation.py format-check-f
	@echo "  - File Name: $(FILE_CODE)"
	@echo ""
	@uv run ruff format --check $(FILE_CODE)
ifeq ($(shell test -e $(FILE_TEST) && echo -n yes),yes)
	@uv run python ./src/utils/make_print_documentation.py format-check-f
	@echo "  - File Name: $(FILE_TEST)"
	@echo ""
	@uv run ruff format --check $(FILE_TEST)
else
	@echo ""
	@echo "⚠ Warning: Test file not found, skipping format check: $(FILE_TEST)"
endif
	@echo ""
	@uv run python ./src/utils/print_success.py success "Success: code is already formatted"

format-fix-f: clear-console
	@uv run python ./src/utils/make_print_documentation.py format-fix-f
	@echo "  - File Name: $(FILE_CODE)"
	@echo ""
	@uv run ruff format $(FILE_CODE)
ifeq ($(shell test -e $(FILE_TEST) && echo -n yes),yes)
	@uv run python ./src/utils/make_print_documentation.py format-fix-f
	@echo "  - File Name: $(FILE_TEST)"
	@echo ""
	@uv run ruff format $(FILE_TEST)
else
	@echo ""
	@echo "⚠ Warning: Test file not found, skipping format fix: $(FILE_TEST)"
endif

lint-check-f: clear-console
	@uv run python ./src/utils/make_print_documentation.py lint-check-f
	@echo "  - File Name: $(FILE_CODE)"
	@echo ""
	@uv run ruff check --extend-ignore D $(FILE_CODE)
ifeq ($(shell test -e $(FILE_TEST) && echo -n yes),yes)
	@uv run python ./src/utils/make_print_documentation.py lint-check-f
	@echo "  - File Name: $(FILE_TEST)"
	@echo ""
	@uv run ruff check --extend-ignore D $(FILE_TEST)
else
	@echo ""
	@echo "⚠ Warning: Test file not found, skipping lint check: $(FILE_TEST)"
endif
	@echo ""
	@uv run python ./src/utils/print_success.py success "Success: no linting issues found"

lint-fix-f: clear-console
	@uv run python ./src/utils/make_print_documentation.py lint-fix-f
	@echo "  - File Name: $(FILE_CODE)"
	@echo ""
	@uv run ruff check --extend-ignore D --fix $(FILE_CODE)
ifeq ($(shell test -e $(FILE_TEST) && echo -n yes),yes)
	@uv run python ./src/utils/make_print_documentation.py lint-fix-f
	@echo "  - File Name: $(FILE_TEST)"
	@echo ""
	@uv run ruff check --extend-ignore D --fix $(FILE_TEST)
else
	@echo ""
	@echo "⚠ Warning: Test file not found, skipping lint fix: $(FILE_TEST)"
endif

docstring-check-f: clear-console
	@uv run python ./src/utils/make_print_documentation.py docstring-check-f
	@echo "  - File Name: $(FILE_CODE)"
	@echo ""
	@uv run ruff check --select D --ignore D104 --ignore D200 --ignore D205 --ignore D400 --ignore D401 $(FILE_CODE)
ifeq ($(shell test -e $(FILE_TEST) && echo -n yes),yes)
	@uv run python ./src/utils/make_print_documentation.py docstring-check-f
	@echo "  - File Name: $(FILE_TEST)"
	@echo ""
	@uv run ruff check --select D --ignore D104 --ignore D200 --ignore D205 --ignore D400 --ignore D401 $(FILE_TEST)
else
	@echo ""
	@echo "⚠ Warning: Test file not found, skipping docstring check: $(FILE_TEST)"
endif
	@echo ""
	@uv run python ./src/utils/print_success.py success "Success: no docstring issues found"

docstring-fix-f: clear-console
	@uv run python ./src/utils/make_print_documentation.py docstring-fix-f
	@echo "  - File Name: $(FILE_CODE)"
	@echo ""
	@uv run ruff check --select D --ignore D104 --ignore D200 --ignore D205 --ignore D400 --ignore D401 --fix $(FILE_CODE)
ifeq ($(shell test -e $(FILE_TEST) && echo -n yes),yes)
	@uv run python ./src/utils/make_print_documentation.py docstring-fix-f
	@echo "  - File Name: $(FILE_TEST)"
	@echo ""
	@uv run ruff check --select D --ignore D104 --ignore D200 --ignore D205 --ignore D400 --ignore D401 --fix $(FILE_TEST)
else
	@echo ""
	@echo "⚠ Warning: Test file not found, skipping docstring fix: $(FILE_TEST)"
endif

test-f-detailed: clear-console
	@uv run python ./src/utils/make_print_documentation.py test-f-detailed
	@echo "  - File Folder: $(FILE_FOLDER)"
	@echo "  - File Name: $(FILE_NAME)"
ifeq ($(shell test -e $(FILE_TEST) && echo -n yes),yes)
	@uv run python -m pytest --verbose $(FILE_TEST)
else
	@echo "ERROR: FOLLOWING FILE DOES NOT EXIST: $(FILE_TEST)"
	@echo ""
endif
ifeq ($(shell test -e $(FILE_DOCTEST) && echo -n yes),yes)
	@uv run python -m pytest --verbose $(FILE_DOCTEST)
else
	@echo ""
	@echo "ERROR: FOLLOWING FILE DOES NOT EXIST: $(FILE_DOCTEST)"
endif

test-f: clear-console
	@uv run python ./src/utils/make_print_documentation.py test-f
	@echo "  - File Folder: $(FILE_FOLDER)"
	@echo "  - File Name: $(FILE_NAME)"
ifeq ($(shell test -e $(FILE_TEST) && echo -n yes),yes)
	@uv run python -m pytest --quiet $(FILE_TEST)
else
	@echo "⚠ Warning: Test file not found, skipping: $(FILE_TEST)"
	@echo ""
endif
ifeq ($(shell test -e $(FILE_DOCTEST) && echo -n yes),yes)
	@uv run python -m pytest --quiet $(FILE_DOCTEST)
else
	@echo "⚠ Warning: Doctest file not found, skipping: $(FILE_DOCTEST)"
	@echo ""
endif

all-f: mypy-f format-check-f lint-check-f docstring-check-f test-f

# JUPYTER NOTEBOOK -----------------------------------------------------------------------------------------------------

jupyter: clear-console
	@uv run python ./src/utils/make_print_documentation.py jupyter
	@mkdir -p .venv/etc/jupyter
	@test -f .venv/etc/jupyter/jupyter_server_config.py || echo 'c.ServerApp.contents_manager_class = "jupytext.TextFileContentsManager"' > .venv/etc/jupyter/jupyter_server_config.py
	@echo "Starting Jupyter Notebook 7 (JupyterLab-based)..."
	@echo "The notebook server will open in your default browser"
	@echo "Press Ctrl+C to stop the server"
	@echo ""
	@uv run python -m notebook

# MARIMO NOTEBOOKS -----------------------------------------------------------------------------------------------------

marimo: clear-console
	@uv run python ./src/utils/make_print_documentation.py marimo
	@echo "Starting Marimo editor in marimo folder..."
	@echo "The editor will open in your default browser"
	@echo "Press Ctrl+C to stop the server"
	@echo ""
	@cd marimo && uv run marimo edit

marimo-app: clear-console
ifdef notebook
	@uv run python ./src/utils/make_print_documentation.py marimo-app
	@if [ -f "marimo/$(notebook)" ]; then \
		echo "Running Marimo app: marimo/$(notebook)"; \
		echo "The app will open in your default browser"; \
		echo "Press Ctrl+C to stop the server"; \
		echo ""; \
		cd marimo && uv run marimo run $(notebook); \
	else \
		echo "Error: File 'marimo/$(notebook)' not found."; \
		echo ""; \
		echo "Available notebooks in marimo folder:"; \
		find marimo -name "*.py" -type f | grep -v "__init__.py" | sed 's|marimo/||'; \
		exit 1; \
	fi
else
	@echo "Error: Please specify notebook name with notebook=<filename.py>"
	@echo ""
	@echo "Usage: make marimo-app notebook=<filename.py>"
	@echo "Example: make marimo-app notebook=raw/my_notebook.py"
	@echo ""
	@echo "Available notebooks in marimo folder:"
	@find marimo -name "*.py" -type f | grep -v "__init__.py" | sed 's|marimo/||'
endif

marimo-new: clear-console
ifdef notebook
	@uv run python ./src/utils/make_print_documentation.py marimo-new
	@if [ -f "marimo/$(notebook)" ]; then \
		echo "Error: File 'marimo/$(notebook)' already exists."; \
		exit 1; \
	else \
		echo "Creating new Marimo notebook: marimo/$(notebook)"; \
		echo "The editor will open in your default browser"; \
		echo "Press Ctrl+C to stop the server"; \
		echo ""; \
		cd marimo && uv run marimo edit $(notebook); \
	fi
else
	@echo "Error: Please specify notebook name with notebook=<filename.py>"
	@echo ""
	@echo "Usage: make marimo-new notebook=<filename.py>"
	@echo "Example: make marimo-new notebook=raw/my_new_notebook.py"
endif

marimo-convert: clear-console
ifdef notebook
	@uv run python ./src/utils/make_print_documentation.py marimo-convert
	@if [ -f "$(notebook)" ]; then \
		output="$(notebook)"; \
		output="$${output%.ipynb}.py"; \
		echo "Converting Jupyter notebook to Marimo: $(notebook)"; \
		echo "Writing Marimo notebook to: $$output"; \
		uv run marimo convert $(notebook) -o "$$output"; \
	else \
		echo "Error: File '$(notebook)' not found."; \
		exit 1; \
	fi
else
	@echo "Error: Please specify notebook path with notebook=<path/to/notebook.ipynb>"
	@echo ""
	@echo "Usage: make marimo-convert notebook=<path/to/notebook.ipynb>"
	@echo "Example: make marimo-convert notebook=notebooks/raw/my_notebook.ipynb"
endif

# COVERAGE -------------------------------------------------------------------------------------------------------------

# if you need to ignore a file, add to @pytest line to the end --ignore=tests/tests_xxx/test_yyy.py
cover-base:
	@uv run python ./src/utils/make_print_documentation.py cover-base
	@uv run pytest --cov-report html:coverage --cov=src tests/

cover: clear-console cover-base

cover-save:
	@uv run python ./src/utils/make_print_documentation.py cover-save
	@uv run python ./src/utils/cover_logger.py

cover-log: clear-console cover-base cover-save
