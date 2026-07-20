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
- Landed the P0+P1 backlog from the repository architecture & quality assessment
  (`specs/008_SP_asses_repository_architecture_and_quality`). `python_repo` is now the
  tracked, always-loaded config **base**; `config_loader.py` gained a `base_name` parameter
  that deep-merges a partial overlay (`python_personal`/`python_local`) over it and loads the
  merged result strictly (`typedload.load(..., basiccast=False, failonextra=True)`);
  `ApplicationConfig`'s `name` is now set authoritatively from `Envs().get_config()`, never
  read off the TOML — see [ADR 0006](adr/0006-config-tracked-base-and-overlays.md), now
  `accepted`. The build went uv-native: `pyproject.toml` moved `dev`/`windows` from
  optional-dependencies to PEP 735 `[dependency-groups]` under `[tool.uv] package = false,
  default-groups = ["dev", "windows"]`; every `uv run --no-project` in the `Makefile` became
  plain `uv run`; the five sync targets collapsed to `sync`/`lock`; `add-lib`/`remove-lib` now
  add onto those groups instead of pruning the dev toolchain; the `-linux` target pairs merged
  into single OS-detecting targets; `create-venv` now writes a minimal commented
  `python_personal.toml` overlay template instead of a full copy. CI's matrix became
  `{ubuntu-latest, windows-latest} × {3.13, 3.14}` (4 jobs): `actions/setup-python` is gone,
  `astral-sh/setup-uv` takes `python-version` directly (so the `3.14` leg actually runs 3.14),
  Windows jobs install `make` via chocolatey and run under `shell: bash`, and a new
  `test_running_interpreter_matches_ci_matrix` (skipped locally, gated on `EXPECTED_PYTHON`)
  asserts `sys.version_info` against the matrix leg. `Logger`/`cover_logger.py` dropped
  `import git` for a new stdlib-only `get_git_branch()` (parses `.git/HEAD`, `"unknown"` on any
  failure), which let `gitpython` drop out of `pyproject.toml` entirely; `Logger` gained
  `exception()` (delegates to `self._logger.exception`, real traceback) and `get()` is now
  typed `-> logging.Logger`; `ExceptionExecutioner.log_and_raise` is `-> NoReturn`, always logs
  via `Logger().exception(...)` (the `ENV_RUNNING_UNIT_TESTS` skip-branch is gone); `timer.py`
  dropped its `pandas` `DataFrame` return and replaced the deprecated `utcfromtimestamp` with
  `fromtimestamp`. `watchdog.py` gained pure `compute_backoff_delay`/`is_crash_loop` helpers
  driving a per-worker exponential backoff capped at `BACKOFF_CAP` (never permanently gives up),
  an atomic single-instance lock (`msvcrt`/`fcntl`), and a real graceful stop
  (`CREATE_NEW_PROCESS_GROUP` + `CTRL_BREAK_EVENT`/`SIGTERM`, with `SIGBREAK`/`SIGTERM` handlers
  added to both worker examples); `checker.py`'s `is_process_alive` is now fail-safe (any
  internal exception reads as *alive*, not dead); `test_checker.py`'s permanently-green
  `test_empty_file` got its real body back — see
  [ADR 0007](adr/0007-watchdog-supervision-semantics.md), now `accepted`.
  `datetime_one_hot_transformer.py` fixed the `min_inerval`→`min_interval` typo, moved
  configuration into `__init__(time_attributes, handle_unknown)` so `fit`/`predict`/
  `fit_predict` take only `dt_index` (aligned with the base signature), implemented a real
  `inverse()` via `self._encoder.inverse_transform`, and populates `_params` so
  `restore_from_params` rebuilds a working `OneHotEncoder` from saved categories without
  re-fitting — the in-repo reference for the persistence interface. Marimo went from an empty
  shell to a working second ecosystem: new `marimo/template/template_notebook.py` and
  `marimo/documentation/documentation_notebook.py` wire `Envs`→`Logger`→`ApplicationConfig`
  through a CWD-independent `sys.path` bootstrap; `.gitignore`'s Marimo section now matches the
  real folder names. Finally, `README.md`, `docs/tutorials/PERSISTENT_RUN.md`,
  `docs/tutorials/CHECKER_SCHEDULER_SET_UP.md`, and `CLAUDE.md` were swept for the residual
  `.conf`/HOCON wording, wrong `scripts_production` paths/filenames, `wmic`→CIM, and the stale
  `py311` claim; `docs/meta/TESTING_CHECKLIST.md` was deleted outright (1,889 lines) rather than
  merely marked historical.
- Landed the P2 backlog from the same assessment. `src/utils/meta_class.py` was renamed to
  `src/utils/monitored_base.py` and `MetaClass` to `MonitoredBase` (it was an `ABC`, never a
  metaclass) — pure rename, `ClassInfo` and its consumer wiring stay deferred to a future spec.
  Plotly's `dashboard` parameter stopped being a no-op: `PlotlyBase._plot_single_figure` now
  returns a `go.Figure` when `dashboard=True` and calls `fig.show()`/returns `None` when
  `False`; the repeated background-layout block was hoisted into
  `PlotlyBase._create_background_layout()`; `get_colors_for_level` gained the missing
  `"vertical_line"` key (fixing a latent `KeyError`); `ATTR_HIGH` changed `"HIGHT"` → `"HIGH"`;
  `tuple[float]` became `tuple[float, float]` where a 2-tuple was required; every `# pylint:`
  pragma was stripped from `src/visualisations/`. `src/data/attributes.py` now anchors its CSV
  path via `Path(__file__).resolve().parent` instead of a CWD-relative string (the Windows-only
  `chdir` test workaround is gone) and actually `raise`s its previously-constructed-but-unraised
  `NoProperOptionInIf`; `SaverAndLoader` now raises `IncorrectDataStructure` on undersized files
  instead of silently returning empty data. `Singleton` gained a test-only `reset()` classmethod,
  and `Envs.set_config`/`set_logger` now raise `NotValidOperation` if `ApplicationConfig`/`Logger`
  is already instantiated, closing the silent-no-op ordering trap. The teaching notebooks lost
  their dead jQuery `create_button()` helper, their broken `<a name=...>` anchors (replaced with
  heading anchors), and `template_notebook_repo.py`'s duplicated imports/`start_timer()` call. A
  new `tests/tests_utils/test_config_schema_drift.py` fails when the hand-edited JSON schemas
  diverge from the `ApplicationConfigData`/`WatchdogConfigData` NamedTuple trees. The two
  divergent notebook executioners were merged: `notebooks_executioner_linux.py` is deleted, its
  spawn-context/`imap_unordered` logic now lives in the single `NotebookExecutioner`, and
  `param_notebook_execution.py` dropped its `platform.system()` branch (verified end-to-end on
  Windows). New tests cover previously 0%-covered risk: `test_heartbeat.py` (mocked session),
  watchdog helper gaps (`build_command`, `heartbeat_age_seconds`, `process_alive`,
  `resolve_ping_url`, `heartbeat_path`/`write_pid`), and a 17-file
  `tests/tests_visualisations/` smoke-test package asserting every plot module returns a
  `go.Figure` under `dashboard=True` (including a `vertical_lines_positions` case guarding the
  `vertical_line` fix). Finally, `pyproject.toml` added `--doctest-glob="*.txt"` (so `make
  test`/CI now collect the datetime-encoder doctest) and dropped the decorative
  `fail_under = 25` coverage gate; `cover_logger.py` was reworked onto `coverage`'s own
  `json_report()` + stdlib `json` (no more BeautifulSoup scrape or blocking `input()` prompt),
  letting `beautifulsoup4` drop out of the dependency groups; `make jupyter` now idempotently
  regenerates `jupyter_server_config.py`; the last 2 `# pylint:` pragmas in
  `helper_functions.py` were removed; and `CLAUDE.md` was swept for the `MonitoredBase` rename,
  the merged executioner, and the now-true doctest-collection claim.
- Landed the P3 polish backlog from the same assessment. `print_success.py`'s `print_success`/
  `print_error` stopped emitting raw ANSI escapes and now delegate to `print_in_color`
  (green+bold / red+bold respectively), making `termcolor` the repo's single console-coloring
  mechanism. `date_time_functions.py` was rewritten onto stdlib idioms: f-string zero-padding
  replaced the arithmetic-and-slice `add_zeros_in_front_and_convert_to_string` (deleted), and
  `convert_string_date_to_datetime` now parses via `datetime.strptime` honoring a `sep` other
  than `"-"`; docstrings were corrected from the wrong `yyyy-dd-yy` claim to the real
  `yyyy-mm-dd-hh-mm-ss<-micro>` format. A teaching-quality sweep fixed the `"for trades"`
  leftover in `helper_functions.py`'s module docstring and replaced the `"Visualizer"` stub
  docstrings across 8 `src/visualisations/` modules with real descriptions. The watchdog config
  gained an optional `[supervision]` TOML table backed by a new `SupervisionTimingData`
  NamedTuple (`check_interval`, `startup_grace_period`, `stop_grace_period`,
  `watchdog_healthcheck_interval`, `backoff_base`, `backoff_cap`, `crash_loop_count`,
  `crash_loop_window`; each defaulting to today's former module constant, so an omitting config
  is unaffected) — `watchdog.py` now reads these from config instead of module globals, the JSON
  schema and drift test were extended to match, the stop `.bat` tools read the watchdog PID from
  `heartbeats_<config>/watchdog.pid` instead of prompting, the checker's WMI respawn log is now
  size-capped/rotated via an extracted helper, and its `taskkill` call gained a `timeout=`. The
  five assertion-free `Logger` level smoke tests now assert real `caplog` records at the
  expected level, and `test_exceptions.py`'s 13 near-identical tests folded into one
  parametrized, table-driven test. Each of the five logger TOML profiles gained a leading
  comment explaining its root-level policy (the two byte-capped `RotatingFileHandler` profiles
  stay at `INFO` to protect their rotation budget; the three unconstrained profiles stay at
  `DEBUG`), turning the existing split into a documented decision; `README.md`'s references to
  the already-deleted `TESTING_CHECKLIST.md` were updated to state plainly that it was removed.
  `.gitignore` dropped author-personal (`ws.sh`, `a.sh`) and phantom (`archive_gen_01_ma`)
  entries; the tracked hooks moved to `scripts/hooks/` with `install-hooks.ps1`/`.sh` collapsed
  to setting `git config core.hooksPath` (edits to a tracked hook now take effect with no
  re-install step); and `make security-check` now runs `pip-audit` against an exported
  `uv.lock` (`uv export | pip-audit -r -`) instead of the installed venv, so local and CI audit
  the same closure.

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
