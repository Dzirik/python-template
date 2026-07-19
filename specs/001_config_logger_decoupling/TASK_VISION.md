# Task Vision

## Why this task exists

Config loading and logging are tangled in a way that was judged a wrong
architectural decision. The tangle is not a literal circular import between
`Config` and `Logger` — those two classes do not import each other. The real
problems are:

1. **Config loading depends on the logger.** `BaseConfig.parse_config()` calls
   `Logger().debug(...)`, so every **Component Config** (e.g. the watchdog) drags
   in the logger just to read a file. This is the wrong dependency direction:
   config is foundational, logging is a higher-level concern.
2. **The main `Config` is a hand-maintained fork.** To dodge the
   `BaseConfig → Logger` dependency, the **Application Config** reimplements
   parsing and path resolution by hand, duplicating `BaseConfig` — with a
   *different* path-search strategy (4 candidate paths vs. `BaseConfig`'s single
   `../../` vs. `Logger`'s 2 paths). Divergent duplicated logic is the source of
   the "`.conf` file debugging" pain.
3. **All paths are resolved against the current working directory.** Both the
   *location* of `.conf` files (candidate-path search hacks) and the paths
   *inside* them (`../../logs`, `../../data`, `../../reports`) depend on CWD,
   which differs between `make`, notebooks, direct file runs, and CI. Every
   path hack in the codebase is a patch for "we don't know the CWD." This is why
   pointing at the `logs/` folder is unreliable.

The goal is to make config and logging **independent and independently usable**,
resolve all paths deterministically, and remove the duplication — following
[`docs/PROJECT_VISION.md`](../../docs/PROJECT_VISION.md). Terminology used here is
defined in [`CONTEXT.md`](../../CONTEXT.md).

## Scope

Refactor `src/utils/config.py`, `src/utils/base_config.py`, and
`src/utils/logger.py` (plus the constants and `.conf` files they depend on),
delivered as **one coherent task, phased internally**:

1. **Foundation.** Introduce a **Project Paths** service that computes the
   project root once (walking up from `__file__` to a marker such as
   `pyproject.toml`/`.git`) and exposes the canonical I/O locations (`data`,
   `logs`, `reports`, `configurations`), with an env override (via **Env
   Selector**) for out-of-repo deployments. Extract a single shared **Config
   Loader** (locate → parse HOCON → `typedload` into a NamedTuple) used by
   Application Config, Component Config, and the Logger.
2. **Decouple.** Remove all logger usage from config loading. `BaseConfig` no
   longer touches `Logger`. Config parsing is **silent on success** and reports
   failures via well-crafted exceptions (which is what actually helps `.conf`
   debugging). With the logger gone from the shared loader, the circular-
   dependency excuse disappears and `Config` stops being a fork.
3. **Migrate paths & layout.** Eliminate `../../` from every `.conf` file
   (including the stdlib logger profiles, whose log paths are resolved via
   Project Paths and injected into `fileConfig` at init) and from
   `SPECIAL_LOGGER_FILE_NAME`. Keep **all** `.conf` files under one central
   `configurations/` folder, organized by kind: **Application Config**
   (`python_*`) directly at the top level; **Logger** profiles under
   `configurations/loggers/`; each **Component Config** kind in its own subfolder
   (e.g. `configurations/watchdogs/`). Everything resolves through Project Paths
   against the project root — no co-location in `src/`, no `__file__`-relative
   split.

The everyday public API stays call-compatible (`Config().get_data()`,
`Logger().info/debug/warning/error/critical`, the timer methods), so notebooks
and tests do not churn; low-value or leaky surface (e.g. `Logger().get() -> Any`,
the `_is_profile`/`_is_logger` flags) may be cleaned up surgically.

### Out of scope / kept fixed

- The config stack: **HOCON + `pyhocon` + `typedload` + `NamedTuple`**.
- The **Singleton** pattern for Application Config and Logger.
- The stdlib **`logging.config.fileConfig`** format for logger profiles (only its
  hard-coded paths change).
- **`Envs`** as the sole environment-variable gateway (it gains ownership of the
  path override).
- The exception system, notebook contents, and the watchdog's supervision logic
  (only its config *location* moves).

## Inputs and outputs

- **Input:** the current implementation — `config.py` (forked singleton),
  `base_config.py` (logger-coupled, CWD-relative), `logger.py` (own path search),
  and `.conf` files full of `../../` paths.
- **Output:** a Project Paths service + a single Config Loader; a `Config` and a
  `BaseConfig` that share loading but stay separate by lifecycle; a `Logger`
  independent of config loading; and `.conf` files with no CWD-relative paths.

## Workflow

The three phases above (Foundation → Decouple → Migrate), shippable as one PR or
a short staged series, each phase leaving `make all-secure` green.

## Primary users

- **The repository itself** — nearly every component is built around Config and
  Logger (notebooks, transformers, watchdog, exceptions).
- **Users of the repository**, especially juniors, who configure a project and
  read its logs. Their `.conf` files must resolve identically regardless of
  where the code is launched from.

## What pain it removes

- Debugging `.conf` resolution ("works from repo root, breaks from a notebook").
- The maintenance burden and drift of duplicated, divergent loading logic.
- The inability to point reliably at `logs/` (and `data/`, `reports/`).
- Config that cannot be loaded or tested without dragging in the logger.

## What success looks like

- **Config and logger are independently usable.** Application Config and
  Component Config load with no dependency on the Logger; the Logger initializes
  with no dependency on config loading.
- **One Config Loader and one path-resolution rule.** No per-class path search;
  the 4-path/2-path/1-path divergence is gone.
- **`.conf` files resolve from anywhere** — repo root, notebook, direct file run,
  CI, or an out-of-repo deployment via the env override — with **zero** CWD
  dependence and no `../../` in any `.conf`.
- **Log and data files land in the intended folders** every time.
- `make all-secure` passes on Python 3.11–3.13; existing call sites keep working.

## Guiding principles

1. **Dependency direction is one-way.** The Config Loader and Project Paths are
   foundational and must never import the project `Logger`. Any breadcrumb they
   need uses stdlib `logging.getLogger(__name__)`, never the singleton. See
   [ADR 0001](../../docs/adr/0001-foundational-config-layering.md).
2. **Never resolve paths against CWD.** All paths anchor to a computed project
   root (or an explicit override), never the working directory; all `.conf` files
   live under one central `configurations/` tree organized by kind. See
   [ADR 0002](../../docs/adr/0002-repo-root-path-anchoring.md).
3. **Share the mechanism, not the identity.** Config and Logger reuse one loader
   by composition; they remain separate classes because their lifecycles differ
   (singleton vs. multi-instance; see
   [ADR 0001](../../docs/adr/0001-foundational-config-layering.md)).
4. **Fail loudly, succeed quietly.** Config parsing is silent on success and
   raises diagnostic-rich exceptions on failure.
5. Inherit all of `docs/PROJECT_VISION.md`: Windows-first, `make all-secure`
   quality gate, house style, teach-by-example.

## Constraints

- Windows-first, cross-platform via `pathlib`; passes on Python 3.11–3.13 (CI).
- Keep HOCON/`pyhocon`/`typedload`/`NamedTuple`, Singletons, `fileConfig`, and
  `Envs` (see *Out of scope / kept fixed*).
- The common public API stays call-compatible so notebooks and tests don't churn.
- `make all-secure` gates every phase.

## What we refuse to optimize for

- Turning config into a **pip-installable, general-purpose config library** — it
  stays clone-and-build-in, anchored to a repo root.
- Supporting **arbitrary config formats or parsers** beyond HOCON.
- **Runtime CWD independence via `os.chdir`** or ever-longer candidate-path
  searches — both are rejected as hacks.
- Preserving **every** legacy interface detail; leaky low-value surface may go.

## Long-term direction

- The Project Paths service is the natural seam for future **containerization /
  out-of-repo deployment** (the env override already anticipates it).
- The foundational-layering rule (nothing foundational imports the Logger) should
  guide future low-level components.

## Current stage

Current implementation at `src/utils/config.py`, `src/utils/base_config.py`, and
`src/utils/logger.py`, with `.conf` files under `configurations/` and the
CWD-relative path hacks described above.
