# Migrate the Logger profiles to TOML and load them via `dictConfig`

> **Status:** `ready-for-agent`

## Parent

[`specs/004_check_logger_config_format/PRD.md`](../PRD.md) — *Migrate the Logger profiles from INI (`fileConfig`) to TOML (`dictConfig`)*

## What to build

The atomic core of the migration: switch `Logger`'s profile front-end from `logging.config.fileConfig` (INI) to `logging.config.dictConfig` (a `dict` parsed from TOML by stdlib `tomllib`), and convert all five profiles to TOML in the same change. These cannot be split, because `Logger._load_profile` loads whichever profile `ENV_LOGGER` names; the moment it parses TOML, every profile it can reach must already be TOML or logging (and the test suite) goes red. The test suite selects `logger_console` via `tests/conftest.py` and `logger_file_limit_console` via the CWD-independence subprocess test, so both — and every other shipped profile — must convert together.

End-to-end behaviour after this slice: constructing `Logger()` under any `ENV_LOGGER` value produces identical logging behaviour to today — same levels, formatter, handler set, rotation sizes/counts, `root`/named-logger structure, and branch-name init line — now sourced from `.toml` files through `dictConfig`. The format and mechanism change; observable logging does not.

Scope:

- **Profiles converted (all five)** — `logger_console`, `logger_file`, `logger_file_console`, `logger_file_limit`, `logger_file_limit_console` become self-contained `dictConfig` documents: `version = 1`, `disable_existing_loggers = false`, a `[formatters.full_formatter]` table, one or two `[handlers.*]` tables, and a `[root]` table. INI `args=` tuples become named keys — `StreamHandler` → `class = "logging.StreamHandler"`, `stream = "ext://sys.stdout"`; `FileHandler` → `class = "logging.FileHandler"`, `filename = "logs/<name>.log"`; `RotatingFileHandler` → `class = "logging.handlers.RotatingFileHandler"`, `filename`, `mode = "a"`, `maxBytes = 5_242_880`, `backupCount = 2`. Class names are fully qualified (no `fileConfig` implicit `logging`/`handlers` namespace). `#` comments (level cheat-sheet, usage notes, links) carry over. The old `.conf` versions are removed.
- **`disable_existing_loggers = false`** is set explicitly in every profile — `dictConfig` defaults the dict key to `true`, the opposite of the current `fileConfig(..., disable_existing_loggers=False)` call. Omitting it would silently disable already-created loggers.
- **`Logger._load_profile` rewrite** — open the resolved path binary, `tomllib.load()` it, inject the log path (see next), then call `logging.config.dictConfig(parsed)` in place of both `fileConfig` calls. `tomllib` is added to `logger.py`'s imports; `logger.py` must **not** import `src.utils.config_loader` or `src.utils.application_config` (ADR 0001 — the config-free import guard test must keep passing).
- **Path injection** — before `dictConfig`, walk the parsed `handlers` table and for any handler carrying a `filename`, replace it with `str(ProjectPaths().logs / Path(filename).name)` (keep the basename, force the directory). This reproduces the old redirect on plain data before instantiation; because `ProjectPaths.__init__` `mkdir`s the logs folder, the file opens in an existing directory.
- **Deletions** — remove the `try/except FileNotFoundError` retry-with-`mkdir` in `_load_profile`, and remove `_redirect_file_handlers_to_project_paths()` entirely (and its call site in `__init__`).
- **Preserved** — the `[root]` config + `getLogger(...replace("logger_", ""))` child that propagates to it; the `profile_file_path.exists()` guard, `_log_bad_file()`, and the `ValueError`; the branch-name init log line.
- **`config_file` default flip** — `Logger` calls `config_file(..., subfolder="loggers", extension=".toml")`. Since no caller then relies on the `.conf` default, flip `config_file`'s `extension` default from `".conf"` to `".toml"` and update its docstring (it currently documents `.conf` and names the Logger as the `.conf` consumer). `.conf` is thereby retired from the codebase.
- **Comment fix, not propagate** — both `*_limit*` profiles carry a false comment ("limits to 10 mega - 10485760") while `args` is `5 * 1024 * 1024` = 5,242,880 (5 MB). Preserve the behaviour (`maxBytes = 5_242_880`) and correct the comment to ~5 MB rather than copying the wrong text.
- **Regression tests** — add a test that `logger_file_limit_console` yields a `RotatingFileHandler` whose `baseFilename` is under `ProjectPaths().logs` and whose `maxBytes`/`backupCount` match the profile (proves the named-key translation landed). Keep `test_logger.py` otherwise unchanged — in particular `test_logger_module_imports_no_config_loader_or_config` and `test_logger_file_handler_lands_in_project_paths_logs` must both still pass against the new mechanism.

## Acceptance criteria

- [ ] All five logger profiles exist as `.toml` `dictConfig` documents; the `.conf` versions are removed. Levels, formatter, handler set, and rotation settings are preserved per profile.
- [ ] Every profile sets `version = 1` and `disable_existing_loggers = false`; handler args are named keys (`stream = "ext://sys.stdout"`, `filename`, `mode`, `maxBytes`, `backupCount`) with fully-qualified class names.
- [ ] `Logger._load_profile` parses with `tomllib` (binary open), injects `ProjectPaths().logs / <basename>` for each file handler, and calls `logging.config.dictConfig`; the `FileNotFoundError` retry and `_redirect_file_handlers_to_project_paths()` are gone.
- [ ] `logger.py` imports neither `src.utils.config_loader` nor `src.utils.application_config`; `test_logger_module_imports_no_config_loader_or_config` passes.
- [ ] `config_file`'s `extension` default is `.toml`; the Logger passes `.toml` explicitly; no `.conf` file remains in the repo.
- [ ] The missing-profile path still raises `ValueError` via the `exists()` guard and logs through `_log_bad_file()` (now resolving a `.toml` path).
- [ ] Constructing `Logger()` under each `ENV_LOGGER` profile behaves identically to the pre-migration INI load (levels, handlers, rotation, branch-name init line).
- [ ] The `*_limit*` profiles keep `maxBytes = 5_242_880`; their size comment is corrected (not the false "10 mega / 10485760").
- [ ] A regression test asserts `logger_file_limit_console` produces a `RotatingFileHandler` under `ProjectPaths().logs` with matching `maxBytes`/`backupCount`; `test_logger_file_handler_lands_in_project_paths_logs` still passes.
- [ ] `make all-secure` green on Python 3.11 / 3.12 / 3.13.

## Blocked by

- None - can start immediately.
