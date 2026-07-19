# Change Log

## Week 13.-19.07.2026

- Consolidated colored console echo into the `Logger`: the five level methods
  (`debug`/`info`/`warning`/`error`/`critical`) now take optional `color`/`on_color`/`attrs`
  params, so passing a `color` logs as usual *and* prints a timestamp-prefixed colored copy to
  the console (via a new private `_echo` helper delegating to `print_in_color`); omitting it
  stays log-only. Removed the now-redundant `log_and_print` from `src/utils/helper_functions.py`,
  which no longer imports `Logger` (it depends only on `termcolor`); `print_in_color` stays as a
  standalone colored-print utility and is now covered by `tests/tests_utils/test_helper_functions.py`.
- Migrated the five Logger profiles (`configurations/loggers/*.conf` → `*.toml`) from stdlib
  INI parsed by `logging.config.fileConfig` to TOML parsed by `tomllib` and loaded via
  `logging.config.dictConfig`; `Logger._load_profile` now rewrites handler `filename` entries
  onto `ProjectPaths().logs` before calling `dictConfig`, and `disable_existing_loggers = false`
  is set explicitly in every profile (`dictConfig` defaults this key to `true`, unlike the
  previous `fileConfig(..., disable_existing_loggers=False)` call).
- `src/utils/project_paths.py`'s `config_file()` now defaults its `extension` parameter to
  `.toml` instead of `.conf`; `.conf` is thereby retired from the repository entirely. See
  [ADR 0004](adr/0004-logger-profiles-toml-dictconfig.md) for the decision record.
- Swept `CLAUDE.md`, `CONTEXT.md`, `README.md`, and `configurations/schemas/README.md` to
  remove the now-stale claims that the Logger profiles are `.conf`/INI/`fileConfig` and that
  `.conf` is reserved for the Logger.
- Retired the catch-all `src/constants/global_constants.py`, moving each cluster to its true
  owner: the env-var name keys and canonical defaults now live in a new side-effect-free
  `src/constants/env_constants.py` (`Envs` imports from it; the `.env.example` live-fallback in
  `envs.py` is gone, so `.env.example` is documentation only); `COLORS` moved to
  `src/visualisations/colors.py`; the transformer method-id vocabulary (`F`/`FP`/`P`/`INV`,
  with `F`/`INV` reserved for an incoming transformer suite) moved to
  `src/transformations/transformer_methods.py`; `FOLDER_CONFIGURATIONS` became a module
  constant on `src/utils/project_paths.py`; `SPECIAL_LOGGER_FILE_NAME` became an independent
  literal on `src/utils/logger.py`, correcting its false "should match the logger config file"
  comment. Also routed `watchdog.py`'s `HEALTHCHECK_PING_URL` read through a new
  `Envs.get_healthcheck_ping_url()` instead of a direct `os.getenv`, so all application
  environment access goes through `Envs`; `checker.py`'s `SYSTEMROOT` read stays a direct OS
  read with a comment explaining why. `global_constants.py` is now deleted; `README.md`'s file
  tree and the notebook templates' dead `from src.global_constants import *` comments were
  updated to match.
- Raised the Python support range to `3.13`–`3.14`: `requires-python` is now
  `">=3.13,<3.15"` (dropping `3.11` and `3.12` entirely), the CI matrix (`ci.yml`) narrowed
  to `["3.13", "3.14"]`, and mypy's `python_version` / ruff's `target-version` moved to the
  new floor (`3.13` / `py313`). Local development keeps defaulting to `.python-version`
  `3.13` (not the newest admitted `3.14`) so the daily-driver interpreter stays the
  proven one while CI continuously proves `3.14`; see
  [ADR 0005](adr/0005-python-version-support-strategy.md) for the full rationale. Regenerated
  `uv.lock` in a single pass, bumping every dependency floor to its current latest;
  `marimo[recommended]` is kept as-is, `openpyxl`, `termcolor`, and `types-requests` gained
  explicit floors, and 17 hand-pinned transitive Jupyter packages (`traitlets`, `parso`,
  `jedi`, `pyzmq`, `tornado`, `mistune`, `pandocfilters`, `send2trash`, `nest-asyncio`,
  `decorator`, `qtconsole`, `qtpy`, `jupyter-core`, `jupyterlab-pygments`, `terminado`,
  `prompt-toolkit`, `pygments`) were removed from the explicit `pyproject.toml` dependency
  list — they remain pinned transitively via `uv.lock` — while `notebook` and `jupyterlab`
  stay top-level for their anchor-fix rationale. The `pip-audit` ignore-list rebuild for the
  refreshed dependency set is tracked separately.
- Swept `README.md`, `docs/PROJECT_VISION.md`, and `CLAUDE.md` for the retired `3.11`/`3.12`
  baseline: hardcoded version mentions, the "Python 3.12" `create-venv` setup text, and the
  CI-matrix descriptions now all read `3.13` / `3.14`.

## Week 06.-12.07.2026

- Added `CLAUDE.md` documenting commands, architecture, and code-style rules for Claude Code.
- Added `docs/PROJECT_VISION.md` capturing the template's purpose, scope, principles, constraints, and roadmap.
- Updated `README.md` to reframe the template from "minimal" to a batteries-included data-science template.
- Added `src/utils/project_paths.py`: a foundational `ProjectPaths` service that resolves `root`/`data`/`logs`/`reports`/`configurations` from a marker (`pyproject.toml`/`.git`), independent of the current working directory, with an environment override via `Envs`.
- Added `src/utils/config_loader.py`: a shared `load_config()` mechanism (HOCON via `pyhocon` + `typedload`) reused by `Config` and `BaseConfig`, raising diagnostic exceptions on missing/malformed/mismatched config instead of logging.
- Updated `Config` (`src/utils/config.py`) and `BaseConfig` (`src/utils/base_config.py`) to delegate to `ConfigLoader`/`ProjectPaths` instead of hand-rolled candidate-path searches; removed the `Config → Logger` dependency so loading a config never drags in the logging stack.
- Updated `Logger` (`src/utils/logger.py`) to resolve its profile and log output directory via `ProjectPaths`, independent of config loading; log files now always land under the real `logs/` folder regardless of launch CWD.
- Migrated `.conf` layout: `logger_*.conf` moved to `configurations/loggers/`, `watchdog_*.conf` moved to `configurations/watchdogs/`; removed every `../../`-relative path from `.conf` files and `SPECIAL_LOGGER_FILE_NAME`.
- Added `tests/tests_utils/test_cwd_independence.py` proving `Config`, `Logger`, `WatchdogConfig`, and `ProjectPaths` all resolve identically regardless of the process's working directory.
- Renamed the Application Config family end-to-end: `Config` → `ApplicationConfig` (`src/utils/config.py` → `src/utils/application_config.py`), `ConfigData` → `ApplicationConfigData` (`src/utils/config_data.py` → `src/utils/application_config_data.py`), with no back-compat alias.
- Updated every `Config()`/`ConfigData` import and call site across `src`, `tests`, and `notebooks` to the new names; renamed `tests/tests_utils/test_config.py` → `tests/tests_utils/test_application_config.py` to match.
- Singleton semantics, the delegation to `ConfigLoader`/`ProjectPaths`, and the returned data tree are unchanged - only names.
- Renamed `BaseConfig` → `BaseComponentConfig` (`src/utils/base_config.py` → `src/utils/base_component_config.py`), with no back-compat alias; `WatchdogConfig` now declares `BaseComponentConfig[WatchdogConfigData]`.
- Fixed `WatchdogConfig`'s `MetaClass` identity, which mislabelled itself as `"ColumnsGroupingPipelineConfig"` (a copy-paste leftover) in unified monitoring/logging; it now reports `"WatchdogConfig"`, and its copy-pasted "Pipelines configuration file." docstrings now describe a watchdog config.
- Updated `CONTEXT.md`, `CLAUDE.md`, `README.md`, ADR 0001/0002's present-tense mentions, and the in-code cross-reference docstrings to reference the renamed `ApplicationConfig`/`ApplicationConfigData`/`BaseComponentConfig` classes and modules.
