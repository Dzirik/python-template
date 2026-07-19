---
status: ready-for-agent
labels: [ready-for-agent]
supersedes: none
relates-to: docs/adr/0003-toml-config-profiles.md
builds-on: specs/003_conf_files_form_resolution/PRD.md
---

# PRD: Migrate the Logger profiles from INI (`fileConfig`) to TOML (`dictConfig`)

> **Builds on:** [spec 003](../003_conf_files_form_resolution/PRD.md), which migrated
> the application/component/watchdog config family from HOCON `.conf` to TOML parsed
> by stdlib `tomllib`, and **explicitly deferred the Logger profiles** as "out of
> scope ... because `logging.config.fileConfig` dictates their format" (see
> [ADR 0003](../../docs/adr/0003-toml-config-profiles.md), *Consequences*). This PRD
> picks up exactly that deferred thread. It leaves ADR 0001's "config loading stays
> Logger-free" guarantee untouched — in fact it depends on it (see the import
> constraint in *Implementation Decisions*).

## Problem Statement

As a developer working in (and adopting) this template, the five Logger profiles
under `configurations/loggers/` (`logger_console`, `logger_file`, `logger_file_console`,
`logger_file_limit`, `logger_file_limit_console`) are written in stdlib **INI**
format and loaded through `logging.config.fileConfig`. After spec 003 migrated every
*other* config family to TOML, this is the last `.conf`/INI island in the template,
and it carries three specific costs:

- **`fileConfig` `eval()`s handler arguments.** The profiles pass handler
  constructor arguments as literal Python source in `args=` strings —
  `args=(sys.stdout,)`, `args=("logs/python_log.log",)`, and
  `args=("logs/...log", "a", 5 * 1024 * 1024, 2,)`. `fileConfig` evaluates these as
  Python expressions. It is opaque (the reader must know it is eval'd source, not
  data), positional (argument meaning is by tuple position, not name), and a small
  but real `eval`-on-config-text smell in a repo whose `make security-check` gates on
  `bandit`/`pip-audit`.
- **The CWD-relative paths force a two-part runtime hack.** The `args=` file paths are
  relative to the process CWD (`"logs/python_log.log"`), which need not exist for an
  arbitrary CWD, and `logging.FileHandler` opens its target eagerly. `Logger` works
  around this with (a) a `try/except FileNotFoundError` in `_load_profile` that
  `mkdir`s the missing directory and *retries the whole load*, and (b) a separate
  `_redirect_file_handlers_to_project_paths()` pass that, after loading, closes and
  reopens every file handler onto the real `ProjectPaths().logs` directory. This is
  fragile mechanism that exists only because `fileConfig` gives no seam to inject a
  computed path before the handler is instantiated.
- **`.conf`/INI is the last non-TOML config format.** After spec 003, the whole
  template speaks TOML except here. The extension is not self-describing relative to
  the rest of the tree, and the format gives weaker IDE support than TOML's native
  PyCharm recognition.

There is no active breakage — logging works today. The problem is ongoing mechanism
cost (the eval, the retry, the reopen) and a lone format outlier, with no offsetting
benefit now that spec 003 has established TOML + stdlib parsing as the template's
config standard.

## Solution

As a developer, I want the Logger profiles expressed in **TOML** and loaded through
**`logging.config.dictConfig`** (parsed by stdlib `tomllib`), so that I remove the
`eval`'d `args=` strings, delete the load-retry and handler-reopen hacks, keep inline
comments, gain native IDE recognition, and unify the template on a single config
syntax — **all with no new dependency and no change to logging behaviour**.

The decisive insight that makes this cheap and safe: **the stdlib offers two config
front-ends over the same logging machinery.** `fileConfig` consumes INI; `dictConfig`
consumes a plain `dict`. `tomllib.load()` produces exactly the kind of plain `dict`
that `dictConfig` accepts, and a `dictConfig` document expresses every construct these
profiles use (formatters, `StreamHandler`, `FileHandler`, `RotatingFileHandler`, and a
configured `root` logger) natively — with named keys instead of positional eval'd
tuples. So the migration is a **single parse-and-load change** in `Logger`, not a
rewrite of the logging model.

Because `dictConfig` takes a `dict`, the log path can be **computed in Python and
injected into the dict before any handler is instantiated**. This is what lets both
hacks disappear: there is no CWD-relative path to fail on (so the retry goes), and no
post-hoc handler to reopen (so `_redirect_file_handlers_to_project_paths()` goes). The
current contract — *the directory in the profile is advisory; logs always land under
`ProjectPaths().logs`* — is preserved exactly by keeping each file handler's
**basename** and forcing it under `ProjectPaths().logs`.

A pleasant side effect, completing what spec 003 started: once the Logger profiles
become `.toml`, the `.conf` extension is **retired from the repository entirely**.

## User Stories

1. As a developer, I want the Logger profiles in TOML, so that the whole template
   speaks one config syntax and the last INI/`.conf` outlier is gone.
2. As a developer, I want the profiles loaded via `logging.config.dictConfig`, so that
   handler arguments are named data (`filename`, `maxBytes`, `stream = "ext://sys.stdout"`)
   instead of positional Python source that `fileConfig` `eval()`s.
3. As a developer, I want the `_load_profile` `FileNotFoundError` retry-with-`mkdir`
   deleted, so that loading no longer depends on catching an eager-open failure.
4. As a developer, I want `_redirect_file_handlers_to_project_paths()` deleted, so that
   handlers are never closed-and-reopened after the fact.
5. As a developer, I want the absolute log path computed from `ProjectPaths().logs` and
   injected into the config dict before handler instantiation, so that file handlers
   open a path that always exists (the logs folder is `mkdir`'d in `ProjectPaths.__init__`).
6. As a developer, I want the current "logs always land under `ProjectPaths().logs`,
   only the basename from the profile is honoured" behaviour preserved exactly, so that
   the change is behaviourally invisible.
7. As a developer, I want all five profiles (`logger_console`, `logger_file`,
   `logger_file_console`, `logger_file_limit`, `logger_file_limit_console`) converted,
   keeping their exact levels, handlers, formatter, and rotation settings, so that each
   keeps selecting and behaving identically via `ENV_LOGGER`.
8. As a developer, I want the `root` logger configured (as today) with the named child
   logger (`getLogger("console")`, etc.) still propagating to it, so that
   `Logger.get()` and every log call behave identically.
9. As a developer, I want `disable_existing_loggers = false` set in the TOML, so that
   `dictConfig` (which defaults it to `true`, unlike the current
   `fileConfig(..., disable_existing_loggers=False)`) does not silently disable
   already-created loggers.
10. As a developer, I want `#` comments preserved in the profiles, so that the level
    cheat-sheet (`DEBUG=10 INFO=20 ...`), the rotation-size note, and the reference
    links survive the migration.
11. As a developer, I want `Logger` to keep parsing its profile with **stdlib
    `tomllib` directly** and **not** import `config_loader` / `application_config`, so
    that ADR 0001 (Logger stays config-free) and its regression guard
    (`test_logger_module_imports_no_config_loader_or_config`) keep passing.
12. As a developer, I want the missing-profile error path (`_log_bad_file` + the
    `exists()` check that raises `ValueError`) preserved, so that selecting a
    nonexistent profile still fails loudly the same way.
13. As a developer, I want `ProjectPaths.config_file` called with `extension=".toml"`
    for the Logger, and — since no caller then uses the `.conf` default — its default
    flipped to `.toml`, so that `.conf` disappears from the codebase and the helper's
    default reflects reality.
14. As a developer, I want the profile-selection env var (`ENV_LOGGER`) and the
    bare-name convention (name without extension) unchanged, so that nothing in `.env`
    / `Envs` changes for users. (`Envs._DEFAULT_LOGGER = "logger_file_limit_console"`
    stays a bare name and keeps working.)
15. As a PyCharm user, I want the `.toml` profiles auto-recognised, so that I get
    highlighting, a structure view, and formatting for free (no JSON Schema is in scope
    — see *Out of Scope*).
16. As a developer, I want `test_logger.py` to keep passing unchanged where it is
    behavioural, and its `test_logger_file_handler_lands_in_project_paths_logs`
    subprocess regression to still prove logs land under `ProjectPaths().logs`, so that
    the CWD-independence guarantee is verified against the new mechanism.
17. As a maintainer, I want the decision and its rejected alternatives recorded in a new
    ADR, so that a future contributor understands why `dictConfig`/TOML was chosen over
    keeping `fileConfig`/INI, a Python-dict-in-code approach, JSON, and YAML.
18. As a documentation reader, I want `CLAUDE.md`, `CONTEXT.md`,
    `configurations/schemas/README.md`, `README.md`, and `docs/CHANGELOG.md` updated so
    that no doc still describes the Logger as INI/`fileConfig`/`.conf` and the
    "`.conf` is reserved for the Logger" statements are corrected.
19. As a developer running `make all-secure`, I want the full quality gate (mypy strict,
    ruff format/lint/docstring, pytest, bandit, pip-audit) to pass on the
    3.11/3.12/3.13 matrix after the migration, so that CI stays green.

## Implementation Decisions

- **Target: TOML `dictConfig` documents, parsed by stdlib `tomllib`.** No new runtime
  dependency (`tomllib` ships on every supported interpreter; spec 003 already relies
  on it). Each profile is a self-contained `dictConfig` document with `version = 1`,
  `disable_existing_loggers = false`, a `[formatters.full_formatter]` table, one or two
  `[handlers.*]` tables, and a `[root]` table.
- **Handler-argument translation (INI `args=` → named dict keys):**
  - `StreamHandler` `args=(sys.stdout,)` → `class = "logging.StreamHandler"`,
    `stream = "ext://sys.stdout"`.
  - `FileHandler` `args=("logs/python_log.log",)` → `class = "logging.FileHandler"`,
    `filename = "logs/python_log.log"`.
  - `RotatingFileHandler`
    `args=("logs/...log", "a", 5 * 1024 * 1024, 2,)` → `class = "logging.handlers.RotatingFileHandler"`,
    `filename = "logs/...log"`, `mode = "a"`, `maxBytes = 5_242_880`, `backupCount = 2`.
  Class names become fully-qualified (`logging.StreamHandler`,
  `logging.handlers.RotatingFileHandler`) because `dictConfig` does not carry
  `fileConfig`'s implicit `logging`/`handlers` namespace.
- **Single load-point change in `Logger._load_profile`.** New body: open the resolved
  path in binary mode, `tomllib.load()` it into a `dict`, **inject the absolute log
  path** (see below), then `logging.config.dictConfig(parsed)`. `dictConfig` is called
  in place of both `fileConfig` calls.
- **Path injection preserves the current contract.** Before calling `dictConfig`, walk
  the parsed `handlers` table; for any handler carrying a `filename`, replace it with
  `str(ProjectPaths().logs / Path(filename).name)` — i.e. keep the basename, force the
  directory to `ProjectPaths().logs`. This reproduces exactly what
  `_redirect_file_handlers_to_project_paths()` did, but on plain data before
  instantiation. Because `ProjectPaths.__init__` `mkdir`s the logs folder, the handler
  opens an existing directory and the `FileNotFoundError` retry is unnecessary.
- **Deletions.** Remove the `try/except FileNotFoundError` retry in `_load_profile` and
  remove the `_redirect_file_handlers_to_project_paths()` static method entirely
  (and its call site in `__init__`).
- **`root` vs named logger unchanged.** The TOML configures `[root]` (as the INI
  configured `[logger_root]`); `__init__` keeps
  `logging.getLogger(self._env.get_logger().replace("logger_", ""))`, which returns a
  child that propagates to `root`. Behaviour is identical.
- **`disable_existing_loggers = false` is mandatory in every profile.** This is the one
  behavioural trap in the `fileConfig`→`dictConfig` switch: `fileConfig` was called with
  `disable_existing_loggers=False`, but `dictConfig` defaults the *dict key* to `true`.
  It must be set explicitly in each TOML file (equivalently, defaulted in code — the
  PRD specifies the file, so the profile is self-describing).
- **Logger stays config-free (hard constraint).**
  `test_logger_module_imports_no_config_loader_or_config` forbids `Logger` from
  importing `src.utils.config_loader` or `src.utils.application_config`. Therefore the
  Logger does **not** reuse `load_config`; it calls `tomllib` directly (already how it
  is free to use stdlib `logging.config`). `tomllib` is added to `logger.py`'s imports.
- **Path helper default flip.** `Logger` calls
  `ProjectPaths().config_file(self._env.get_logger(), subfolder="loggers", extension=".toml")`.
  After this, no caller relies on the `.conf` default, so `config_file`'s `extension`
  default changes from `".conf"` to `".toml"` and its docstring is updated (it currently
  documents the `.conf` default and references the Logger as the `.conf` consumer).
- **Missing-profile path preserved.** The `profile_file_path.exists()` guard, the
  `_log_bad_file()` helper, and the `ValueError` remain; only the extension of the
  resolved path changes.
- **ADR.** A new ADR (`docs/adr/0004-*`) records the decision, the four-way comparison
  (keep `fileConfig`/INI / TOML+`dictConfig` / Python-dict-in-code / JSON / YAML), the
  `dictConfig`-takes-a-dict insight that enables path injection, the two hacks it
  retires, and the `disable_existing_loggers` gotcha. It closes the loop opened by ADR
  0003's *Consequences* paragraph.
- **Condition that would reverse the decision (recorded, not triggered):** if profiles
  ever needed genuinely dynamic, code-computed handler wiring beyond a single injected
  path (e.g. handlers chosen at runtime from application state), a Python-dict-in-code
  approach would start earning its keep over static TOML files. No such need exists.

## Testing Decisions

- **Good tests exercise logging behaviour, not parse internals.** Tests drive `Logger`
  through its public surface (construction under a given `ENV_LOGGER`, the level
  methods, timer integration, `get()`) and assert on observable effects — never on how
  the TOML was parsed. The format swap must be invisible to them.
- **Reuse existing seams — no new ones.** `tests/tests_utils/test_logger.py` is the
  existing seam and already covers: the singleton, initialisation, every level method,
  timer integration, `get()`, the **config-free import guard**
  (`test_logger_module_imports_no_config_loader_or_config` — must still pass, proving no
  `config_loader`/`application_config` import crept in), and the **CWD-independence
  regression** (`test_logger_file_handler_lands_in_project_paths_logs`, a subprocess
  that selects `logger_file_limit_console` from a foreign CWD and asserts a `*.log`
  lands under `ProjectPaths().logs` — this is the key guard that path injection
  replicates the old redirect).
- **Fixtures:** the tests select real shipped profiles by name via `ENV_LOGGER`
  (`logger_console` in `conftest.py`, `logger_file_limit_console` in the subprocess
  test), so converting the five profile files to `.toml` *is* the fixture change; no
  separate sample fixtures exist to convert.
- **Regression additions (small):** a test that a file-backed profile
  (`logger_file_limit_console`) produces a `RotatingFileHandler` whose `baseFilename`
  is under `ProjectPaths().logs` and whose `maxBytes`/`backupCount` match the profile
  (proving the named-key translation landed), and a guard that a `.toml` profile loads
  without raising (the console profile already covers this via `conftest`).
- **Gate:** `make all-secure` must pass on the 3.11/3.12/3.13 matrix. `bandit` should be
  quieter, not louder, since eval'd config source is gone.

## Out of Scope

- **A JSON Schema for the Logger TOML and its `.idea/jsonSchemas.xml` mapping.**
  Deferred by decision: `.toml` recognition already gives highlighting/structure/format
  for free, and the `dictConfig` shape is larger than the `NamedTuple`-mirroring schemas
  spec 003 added. Recorded as a possible follow-up issue, not built here.
- **Honouring an arbitrary directory from the profile.** The "force `ProjectPaths().logs`,
  keep basename" contract is retained deliberately; per-profile log directories are not
  introduced.
- **A Python-dict-in-code configuration** (dropping the profile files). Evaluated and
  rejected: it would lose the file-based, non-programmer-editable config the template
  provides, for no benefit given a single injected path.
- **JSON or YAML** as the target format. JSON loses the `#` comments the profiles rely
  on; YAML would add a third-party parser, contradicting the stdlib-only stance spec
  003 established.
- **Changing logging behaviour** — levels, formatter string, rotation sizes/counts,
  handler set per profile, the `root`/named-logger structure, or the branch-name init
  log line — all preserved verbatim.
- **Changing the `Envs` / `.env` layer, `ENV_LOGGER`, or the bare-name selection
  mechanism.**
- **The `SPECIAL_LOGGER_FILE_NAME` error-logger path** beyond the extension change —
  `_log_bad_file` keeps building its handler directly in stdlib code.

## Further Notes

### How the profiles look — before (INI) and after (TOML)

**`logger_file_limit_console` — before (`.conf`, INI consumed by `fileConfig`):**

```ini
# The main usage of this logger is in notebooks ...
# Note: limits to 10 mega - 10485760.
# NOTSET=0. DEBUG=10. INFO=20. WARN=30. ERROR=40. CRITICAL=50.

[loggers]
keys=root

[logger_root]
level=INFO
handlers=file_handler, console_handler

[formatters]
keys=full_formatter

[formatter_full_formatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s

[handlers]
keys=file_handler, console_handler

[handler_file_handler]
class=handlers.RotatingFileHandler
level=DEBUG
formatter=full_formatter
args=("logs/python_log_file_limit_console.log", "a", 5 * 1024 * 1024, 2,) # 2 backups

[handler_console_handler]
class=StreamHandler
level=DEBUG
formatter=full_formatter
args=(sys.stdout,)
```

**`logger_file_limit_console` — after (`.toml`, dict consumed by `dictConfig`):**

```toml
# The main usage of this logger is in notebooks, where console output is needed but
# the file must be size-limited due to unbounded growth on automatic runs.
# Note: limits to ~5 MB per file, 2 backups.
# Levels: NOTSET=0 DEBUG=10 INFO=20 WARN=30 ERROR=40 CRITICAL=50
version = 1
disable_existing_loggers = false

[formatters.full_formatter]
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

[handlers.file_handler]
class = "logging.handlers.RotatingFileHandler"
level = "DEBUG"
formatter = "full_formatter"
filename = "logs/python_log_file_limit_console.log"  # dir is advisory; forced to ProjectPaths().logs
mode = "a"
maxBytes = 5_242_880   # 5 * 1024 * 1024
backupCount = 2

[handlers.console_handler]
class = "logging.StreamHandler"
level = "DEBUG"
formatter = "full_formatter"
stream = "ext://sys.stdout"

[root]
level = "INFO"
handlers = ["file_handler", "console_handler"]
```

**`logger_console` — after (console-only, the profile tests run under):**

```toml
# Console-only logging.
# Levels: NOTSET=0 DEBUG=10 INFO=20 WARN=30 ERROR=40 CRITICAL=50
version = 1
disable_existing_loggers = false

[formatters.full_formatter]
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

[handlers.console_handler]
class = "logging.StreamHandler"
level = "DEBUG"
formatter = "full_formatter"
stream = "ext://sys.stdout"

[root]
level = "DEBUG"
handlers = ["console_handler"]
```

Notes on the mapping: `fileConfig`'s `[loggers]`/`[handlers]`/`[formatters]` `keys=`
registries and the `logger_`/`handler_`/`formatter_` section-name prefixes collapse
into `dictConfig`'s nested `[handlers.*]` / `[formatters.*]` / `[root]` tables; the
eval'd `args=` tuples become named keys; `sys.stdout` becomes the `ext://sys.stdout`
access string; and the arithmetic size literal becomes the pre-computed integer
`5_242_880`. No level, handler, or formatter behaviour changes.

### The two hacks this retires

*Before* (`logger.py`): `_load_profile` calls `fileConfig`, catches
`FileNotFoundError`, `mkdir`s the missing parent, and retries the whole load; then
`_redirect_file_handlers_to_project_paths()` iterates the root logger's handlers,
closes each `FileHandler`, rewrites `baseFilename` to `ProjectPaths().logs / <name>`,
and reopens the stream.

*After*: `_load_profile` `tomllib.load`s the dict, rewrites each handler's `filename`
to `ProjectPaths().logs / <basename>` on the plain dict, and calls `dictConfig`. The
directory already exists (created in `ProjectPaths.__init__`), so there is nothing to
catch and nothing to reopen. Both the retry and the redirect method are deleted.

### Pre-existing comment/value discrepancy to fix, not propagate

Both `*_limit*` profiles (`logger_file_limit`, `logger_file_limit_console`) carry a
comment "limits to 10 mega - 10485760" while their actual `args` size is
`5 * 1024 * 1024` = **5,242,880 (5 MB)** — the comment is already wrong in the shipped
INI. The migration preserves *behaviour* (`maxBytes = 5_242_880`) and corrects the
comment to match (~5 MB), rather than copying the false "10 mega / 10485760" text into
the new TOML. This is the one place the "preserve comments verbatim" intent is
deliberately overridden, because the existing comment misdescribes the code.

### Estimated cost

Roughly half a day, low risk: 5 profile files converted (INI→TOML `dictConfig`), one
focused rewrite of `Logger._load_profile` plus two deletions, a one-line
default-extension flip in `project_paths.py`, a couple of small regression tests, the
doc sweep (`CLAUDE.md`, `CONTEXT.md`, `schemas/README.md`, `README.md`, `CHANGELOG.md`),
and the ADR. `make all-secure` is the acceptance gate.

### Provenance

This PRD is the outcome of a design-review session: the five INI profiles were scanned
and confirmed to use only constructs `dictConfig` expresses natively; the
`fileConfig`→`dictConfig` behavioural deltas (`disable_existing_loggers` default,
fully-qualified class names, `ext://` stream syntax) were identified; the Logger's
config-free import constraint was verified against its regression test; and
TOML+`dictConfig` was selected over keeping `fileConfig`/INI, a Python-dict-in-code
approach, JSON, and YAML against the developer's stated motivations (IDE/readability,
killing the eval/path hacks, and an honest comparison) with no active pain forcing the
change.
