# PRD: Decouple Config Loading from Logging & Anchor All Paths to Project Root

> **Triage:** `ready-for-agent`
> **Source:** [`TASK_VISION.md`](./TASK_VISION.md)
> **Domain terms:** see [`CONTEXT.md`](../../CONTEXT.md) — *Application Config*, *Component Config*, *Config Loader*, *Env Selector*, *Logger*, *Project Paths*, *Config Profile / Logger Profile*.
> **Decisions of record:** [ADR 0001](../../docs/adr/0001-foundational-config-layering.md) (foundational layering), [ADR 0002](../../docs/adr/0002-repo-root-path-anchoring.md) (repo-root path anchoring).

## Problem Statement

As someone building on this template — and especially as a junior configuring a
project and reading its logs — my `.conf` files resolve differently depending on
where I launch the code from. A profile that loads cleanly from the repo root
breaks from a notebook, from a direct file run, or in CI, and I can't reliably
point the project at its `logs/` (or `data/`, `reports/`) folder. When something
goes wrong, I end up debugging `.conf` path resolution instead of my actual work.

Underneath that experience are three structural faults:

1. **Config loading depends on the Logger.** `BaseConfig.parse_config()` calls
   `Logger().debug(...)`, so loading *any* Component Config (e.g. the watchdog)
   drags in the whole logging stack just to read a file. The dependency points
   the wrong way: config is foundational; logging is a higher-level concern that
   may itself need config.
2. **The Application Config is a hand-maintained fork.** To dodge the
   `BaseConfig → Logger` dependency, `Config` reimplements parsing and path
   resolution by hand, duplicating `BaseConfig` — and drifting from it, with a
   *different* path-search strategy (4 candidate paths vs. `BaseConfig`'s single
   `../../` vs. `Logger`'s 2 paths). Divergent duplicated logic is the direct
   source of the "`.conf` debugging" pain.
3. **Every path is resolved against the current working directory.** Both the
   *location* of `.conf` files (candidate-path-search hacks) and the paths
   *inside* them (`../../logs`, `../../data`, `../../reports`) depend on CWD,
   which differs between `make`, notebooks, direct runs, and CI. Every path hack
   in the codebase is a patch for "we don't know the CWD."

## Solution

Make config and logging **independent and independently usable**, resolve all
paths **deterministically against a computed project root**, and remove the
duplicated loading logic — while keeping the everyday public API call-compatible
so notebooks and tests don't churn.

Concretely, from the user's perspective:

- I can load an **Application Config** or a **Component Config** without the
  **Logger** ever being imported or initialized.
- The **Logger** starts up without depending on config *loading*.
- My `.conf` files and my `logs/`, `data/`, and `reports/` folders resolve to the
  **same absolute locations** whether I run from the repo root, a notebook, a
  direct file run, or CI — with an environment override for out-of-repo
  deployments.
- No `.conf` file contains a `../../` path any more.
- When a config is malformed or missing, I get a **diagnostic-rich exception**
  telling me exactly what was looked for and where — instead of a silent
  misload or a cryptic failure.

Delivered as **one coherent task, phased internally** (Foundation → Decouple →
Migrate), each phase leaving `make all-secure` green.

## User Stories

### Path resolution & Project Paths

1. As a template user, I want the project root to be computed once by walking up
   from the source file to a marker (`pyproject.toml`/`.git`), so that resolution
   never depends on my current working directory.
2. As a template user, I want a single **Project Paths** service that exposes the
   canonical I/O locations (`data`, `logs`, `reports`, `configurations`), so that
   every part of the code asks one place where things live.
3. As a notebook user, I want `Config().get_data().path.data` to point at the
   real `data/` folder when I run a cell, so that I don't have to `cd` first or
   patch paths.
4. As a CI maintainer, I want config and log paths to resolve identically on the
   3.11/3.12/3.13 ubuntu matrix as they do on my Windows machine, so that CI
   reflects local behavior.
5. As someone running a script directly (`uv run --no-project python src/...`), I
   want the same paths to resolve as when I run via `make`, so that launch method
   is irrelevant.
6. As a deployer, I want to override the project base directory via an environment
   variable (through the **Env Selector**), so that I can run the code from
   outside the repo tree (e.g. a container) without editing `.conf` files.
7. As a template user, I want the resolved `logs/` directory to be created if it
   doesn't exist, so that logging never fails on a fresh checkout.
8. As a maintainer, I want exactly one path-resolution rule, so that the
   4-path / 2-path / 1-path divergence between `Config`, `Logger`, and
   `BaseConfig` is gone.

### Config Loader (shared mechanism)

9. As a maintainer, I want a single **Config Loader** that locates a `.conf`,
   parses it with `pyhocon`, and loads it into a `NamedTuple` via `typedload`, so
   that Application Config, Component Config, and the Logger all reuse one
   implementation.
10. As a maintainer, I want the **Config Loader** to never import the project
    **Logger**, so that the foundational dependency direction (ADR 0001) is
    enforced structurally, not just by convention.
11. As a template user, I want config parsing to be **silent on success**, so that
    loading a config produces no log noise.
12. As a template user loading a **missing** config, I want an exception naming the
    profile, the folder searched, and the resolved absolute path, so that I can
    fix it immediately.
13. As a template user loading a **malformed** config (bad HOCON, or a shape that
    doesn't match the target `NamedTuple`), I want a diagnostic exception that
    surfaces the parse/type failure, so that I know whether the problem is syntax
    or schema.
14. As a maintainer, I want the Config Loader parameterized by the target
    `NamedTuple` type, so that each config kind gets its own typed, immutable
    result.

### Application Config (the `Config` singleton)

15. As a template user, I want `Config().get_data()` to keep returning the
    `ConfigData` tree exactly as before, so that my existing code doesn't change.
16. As a template user, I want `Config()` to remain a **Singleton** (same instance
    every call), so that process-wide config semantics are preserved.
17. As a template user, I want `Config().get_data_as_dict()` to keep working, so
    that dict-based consumers are unaffected.
18. As a maintainer, I want `Config` to stop being a hand-maintained fork and
    instead delegate loading to the shared **Config Loader**, so that it can't
    drift from Component Config loading again.
19. As a template user, I want `Config` to select its profile ambiently via the
    **Env Selector** (default `python_personal`), so that profile choice stays
    environment-driven, not caller-passed.

### Component Config (`BaseConfig` / `WatchdogConfig`)

20. As a watchdog operator, I want `WatchdogConfig(name).get_data()` to keep
    returning `WatchdogConfigData`, so that supervision code is unchanged.
21. As a maintainer, I want `BaseConfig.parse_config()` to no longer call
    `Logger()`, so that loading a Component Config pulls in no logging stack.
22. As a maintainer, I want `BaseConfig` to delegate to the shared **Config
    Loader**, so that it shares the one path-resolution rule.
23. As a watchdog operator, I want watchdog `.conf` files to live under
    `configurations/watchdogs/`, so that Component Config files are organized by
    kind rather than scattered.
24. As a template author adding a new Component Config kind, I want a clear
    convention (its own `configurations/<kind>/` subfolder), so that I know where
    to put new profiles.

### Logger (independence + path injection)

25. As a template user, I want `Logger().info/debug/warning/error/critical(...)`
    and the timer methods (`start_timer`, `set_meantime`, `end_timer`) to keep
    working unchanged, so that all existing logging call sites are unaffected.
26. As a template user, I want `Logger()` to remain a **Singleton**, so that
    process-wide logging semantics are preserved.
27. As a maintainer, I want the **Logger** to initialize without depending on
    config *loading* (no Config Loader / Application Config dependency for its own
    startup), so that the two subsystems are independently usable.
28. As a template user, I want the logger's profile chosen by the **Env Selector**
    (`ENV_LOGGER` → a `logger_*.conf`), so that logger selection stays
    environment-driven.
29. As a template user, I want the log file to be written to the **Project
    Paths**-resolved `logs/` directory, so that logs always land in the intended
    folder regardless of CWD.
30. As a maintainer, I want the resolved absolute log path injected into
    `logging.config.fileConfig` at init (since stdlib profiles can't compute paths
    themselves), so that the `logger_*.conf` files carry no `../../` paths.
31. As a template user, I want the Logger to keep logging the active git branch and
    host on init, so that that breadcrumb is preserved.

### `.conf` file migration & layout

32. As a maintainer, I want **zero** `../../` paths in any `.conf` file (config
    profiles and logger profiles alike), so that no config is CWD-relative.
33. As a maintainer, I want all `.conf` files under one central `configurations/`
    tree organized by kind — Application Config (`python_*`) at the top level,
    **Logger** profiles under `configurations/loggers/`, each **Component Config**
    kind in its own subfolder — so that the layout mirrors the domain model.
34. As a maintainer, I want `SPECIAL_LOGGER_FILE_NAME` (the fallback bad-config log
    path) to be resolved via **Project Paths** rather than a hard-coded `../../`
    path, so that even the failure-path log lands correctly.
35. As a template author, I want the three Config Profiles (`python_repo`,
    `python_personal`, `python_local`) and the five Logger Profiles to keep their
    names and selection semantics, so that documented profile names still work.

### Quality & compatibility

36. As a maintainer, I want each internal phase (Foundation → Decouple → Migrate)
    to leave `make all-secure` green, so that the work can ship as one PR or a
    short staged series safely.
37. As a maintainer, I want new code to pass mypy `--strict`, ruff format/lint, the
    ruff docstring rules, and the house style, so that it's indistinguishable from
    existing `src/` code.
38. As a maintainer, I want leaky low-value surface (`Logger().get() -> Any`, the
    `_is_profile` / `_is_logger` flags) cleaned up surgically where it doesn't
    break the common public API, so that the interfaces get tighter without
    churning callers.

## Implementation Decisions

### Modules built / modified

- **New: Project Paths service** (a foundational module under `src/utils/`).
  Computes the project root once by walking up from `__file__` to a marker
  (`pyproject.toml` or `.git`). Exposes the canonical locations: `root`,
  `data`, `logs`, `reports`, `configurations`, plus resolution of a named
  `.conf` file to an absolute path. Honors an environment base-directory
  override supplied through the **Env Selector**. **Must not import the project
  `Logger`.** Creates the `logs/` directory if absent.
- **New: Config Loader** (a foundational module under `src/utils/`). One function
  or small class: given a config file name (resolved via Project Paths) and a
  target `NamedTuple` type, it parses HOCON with `pyhocon` and loads into the
  `NamedTuple` with `typedload`, returning the typed immutable result. Raises
  diagnostic-rich exceptions on missing file, HOCON parse error, and typedload
  shape mismatch. **Must not import the project `Logger`.**
- **Modified: `Config` (Application Config).** Stops reimplementing parsing/path
  search; delegates to the **Config Loader** (which uses **Project Paths**).
  Remains a Singleton selecting its profile via **Env Selector**. Removes the
  bespoke `_get_config_file_path` 4-path search and the `_is_profile` flag where
  no longer needed. Public surface `get_data()` / `get_data_as_dict()` unchanged.
- **Modified: `BaseConfig` (Component Config).** `parse_config()` no longer calls
  `Logger()`. Delegates to the **Config Loader**. Keeps its generic
  `BaseConfig[_T]` typing and `get_data()` / `get_data_as_dict()` surface.
- **Modified: `Logger`.** Initializes independently of config *loading*. Resolves
  its profile file and its log-output directory via **Project Paths**, and
  injects the resolved absolute log path into `logging.config.fileConfig` at
  init. Drops its own 2-path candidate search. Common public API
  (`info/debug/warning/error/critical`, timer methods) unchanged; `get()` and the
  `_is_logger` flag may be cleaned up surgically.
- **Modified: constants.** `SPECIAL_LOGGER_FILE_NAME` no longer hard-codes
  `../../`; the fallback log location resolves via **Project Paths**.
- **Modified: `.conf` files.** All `../../` removed. `python_*` stay at
  `configurations/` top level; `logger_*` move under `configurations/loggers/`;
  `watchdog_*` move under `configurations/watchdogs/`. Paths *inside* config
  profiles (`data`, notebook paths, `output_folder`) become root-relative values
  that Project Paths resolves, not `../../`-prefixed CWD-relative strings.

### Architectural decisions

- **Dependency direction is one-way (ADR 0001).** Project Paths and Config Loader
  are foundational and must never import the project `Logger`. Any breadcrumb they
  genuinely need uses stdlib `logging.getLogger(__name__)`, never the singleton.
- **Share the mechanism, not the identity (ADR 0001).** `Config` and `BaseConfig`
  reuse the one Config Loader by **composition**; they stay separate classes
  because their lifecycles differ (singleton vs. multi-instance). `Config` is no
  longer a fork.
- **Never resolve against CWD (ADR 0002).** All paths anchor to the computed
  project root (or the explicit env override). Rejected alternatives, recorded in
  ADR 0002: unified CWD candidate-path search, `os.chdir` at startup, per-module
  co-location of component configs.
- **Fail loudly, succeed quietly.** Config parsing emits nothing on success and
  raises diagnostic exceptions on failure — the exceptions are what actually help
  `.conf` debugging.
- **Env override owned by the Env Selector.** The Project Paths base-directory
  override is read/written only through `Envs`; nothing touches `os.environ`
  directly.

### Kept fixed (constraints, not choices to revisit)

- Config stack: **HOCON + `pyhocon` + `typedload` + `NamedTuple`**.
- **Singleton** for Application Config and Logger.
- stdlib **`logging.config.fileConfig`** format for logger profiles (only the
  hard-coded paths change; the resolved path is injected at init).
- **`Envs`** as the sole environment-variable gateway.
- The exception system, notebook contents, and the watchdog supervision logic
  (only its config *location* moves).
- The common public API stays call-compatible.

### Interfaces (behavioral contracts, not signatures to freeze)

- `Config().get_data() -> ConfigData` and `Config().get_data_as_dict() -> dict`
  behave as today; `Config()` is idempotent (Singleton).
- `WatchdogConfig(name).get_data() -> WatchdogConfigData` behaves as today; loads
  from `configurations/watchdogs/`.
- `Logger()` is idempotent (Singleton); `info/debug/warning/error/critical(str)`
  and `start_timer/set_meantime/end_timer` behave as today; log output lands in
  the Project-Paths `logs/`.
- Project Paths exposes read accessors for `root`, `data`, `logs`, `reports`,
  `configurations`, and a resolver from a config file name to an absolute path;
  respects the Env Selector override.
- Config Loader: `(config_name, target_namedtuple_type) -> instance of that type`;
  raises a diagnostic exception on any failure.

## Testing Decisions

**What makes a good test here:** exercise **external behavior through the highest
available seam**, not implementation details. Prefer driving the existing public
APIs (`Config().get_data()`, `Logger()`, `WatchdogConfig(...)`) over asserting on
private path-search internals. The headline property — CWD independence — is best
proven by running those public APIs *from a different working directory* and
asserting identical resolution, rather than by unit-testing path strings. Tests
must not depend on the caller's CWD themselves.

**Prior art in the codebase** (mirror these):

- `tests/tests_utils/test_logger.py` — singleton assertion, "does not raise"
  smoke tests for each log level, timer-integration flow. Parametrized-pytest
  house style, one behavior per test.
- `tests/conftest.py` — session-autouse fixture sets `ENV_LOGGER=logger_console`
  and `ENV_RUNNING_UNIT_TESTS=True`. Note: because Config and Logger are
  Singletons, env vars must be set (via `Envs`) **before** first instantiation;
  new tests that vary the environment/CWD must account for singleton caching.
- Test tree mirrors `src/` with a `tests_` prefix; ruff lint/docstring rules
  apply to `tests` too.

**Modules to test:**

- **Project Paths (new seam):** root resolves to the marker regardless of CWD;
  `data`/`logs`/`reports`/`configurations` resolve under root; the Env Selector
  override repoints the base; `logs/` is created if missing.
- **Config Loader (new seam):** a valid profile + `NamedTuple` yields the typed
  result; a missing file raises a diagnostic exception naming what/where; a
  malformed HOCON and a shape mismatch each raise a diagnostic exception;
  success path is silent (no logging side effect); the module imports no
  `Logger`.
- **Application Config (existing seam):** `Config().get_data()` returns the
  expected `ConfigData`; Singleton identity holds; loads without importing the
  Logger.
- **Component Config (existing seam):** `WatchdogConfig(name).get_data()` returns
  `WatchdogConfigData` and loads with no Logger dependency, from
  `configurations/watchdogs/`.
- **Logger (existing seam):** initializes independently of config loading; log
  file lands in the Project-Paths `logs/`; existing `test_logger.py` behaviors
  still pass (adjusted only if `get()` is removed).
- **CWD-independence acceptance (existing seam, varied CWD):** after `chdir` to a
  temp dir / a subfolder, `Config()`, `Logger()`, and `WatchdogConfig()` all
  resolve their `.conf` files and I/O paths identically. This is the acceptance
  test for the whole feature.

**Coverage gate:** `fail_under = 25` in `pyproject.toml` must stay satisfied.

## Out of Scope

- Turning config into a **pip-installable, general-purpose config library** — it
  stays clone-and-build-in, anchored to a repo root.
- Supporting **arbitrary config formats or parsers** beyond HOCON.
- **Runtime CWD independence via `os.chdir`** or ever-longer candidate-path
  searches — both rejected as hacks (ADR 0002).
- Changing the **watchdog supervision logic**, `heartbeat.py`, or `checker.py`
  behavior — only the *location* of watchdog `.conf` files moves.
- Rewriting **notebook contents** or the exception system.
- Preserving **every** legacy interface detail — leaky low-value surface
  (`Logger().get()`, `_is_profile` / `_is_logger`) may be removed surgically.
- Introducing dependency injection of a logger into the loader (explicitly
  rejected in ADR 0001).

## Further Notes

- **Publishing:** no issue tracker is configured in this environment (no git
  remote, no `gh`, no connected Linear/Jira MCP), so this PRD lives as a file
  beside `TASK_VISION.md`. The intended triage state is **`ready-for-agent`**
  (noted at the top). When a tracker is connected, port this file into an issue
  and carry the label over.
- **Phasing:** the three phases (Foundation → Decouple → Migrate) can ship as one
  PR or a short staged series; each must leave `make all-secure` green on Python
  3.11–3.13.
- **Windows-first:** all path work uses `pathlib`; verify on Windows and the
  Linux CI matrix.
- **Long-term:** the Project Paths env override is the deliberate seam for future
  containerization / out-of-repo deployment; the foundational-layering rule
  (nothing foundational imports the Logger) should guide future low-level
  components.
- **Next step:** this PRD can be broken into tracer-bullet vertical slices via the
  `to-issues` skill once a tracker is available.
