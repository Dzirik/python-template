# PRD: Rename the Config Classes to Match the Ubiquitous Language

> **Triage:** `ready-for-agent`
> **Source:** grill-me session (2026-07-10) refining the naming follow-on to spec 001.
> **Domain terms:** see [`CONTEXT.md`](../../CONTEXT.md) — *Application Config*, *Component Config*, *Config Loader*, *Env Selector*, *Logger*, *Project Paths*.
> **Decisions of record:** [ADR 0001](../../docs/adr/0001-foundational-config-layering.md) (foundational layering), [ADR 0002](../../docs/adr/0002-repo-root-path-anchoring.md) (repo-root path anchoring). This task changes **names only** and touches neither decision.
> **Builds on:** [spec 001](../001_config_logger_decoupling/PRD.md), which decoupled config loading from the Logger and established the shared **Config Loader**.

## Problem Statement

As someone building on this template — especially a junior reading the config
code for the first time — the two config classes have names that actively
mislead me about how they relate:

1. **`BaseConfig` implies an inheritance that does not exist.** The name reads
   like the base class that `Config` extends. It isn't: `Config` is a deliberate
   hand-written peer (spec 001 kept them separate by lifecycle — Singleton vs.
   multi-instance — sharing only the **Config Loader** by composition). So the
   very first thing the name tells me is false, and I go looking for a
   `class Config(BaseConfig)` that isn't there.
2. **`Config` is too generic for the most specific thing in the subsystem.** The
   bare name reads like "the root/base config type," when it is in fact the one
   process-wide **Application Config** singleton. The generic name hides its role
   and reinforces the wrong contrast with `BaseConfig` (that one is the "base"
   and `Config` the "derived").
3. **`ConfigData` is the odd tuple out.** The Component Config family already
   pairs `WatchdogConfig` with `WatchdogConfigData`. The Application Config side
   pairs `Config` with the generically-named `ConfigData`, so the two families
   don't read symmetrically and the tuple's owner isn't obvious at a glance.
4. **`WatchdogConfig` lies about its own identity at runtime.** It registers its
   `MetaClass` identity as `class_name="ColumnsGroupingPipelineConfig"` — a
   copy-paste leftover from an unrelated pipeline. That string feeds unified
   monitoring/logging (`get_class_name()`, `get_class_type_and_name()`), so the
   watchdog config mislabels itself in exactly the runtime output an operator
   would read. Its docstrings ("Pipelines configuration file.") are the same
   copy-paste.

The project already has a ratified ubiquitous language in
[`CONTEXT.md`](../../CONTEXT.md) — **Application Config**, **Component Config**,
**Config Loader** — but the class names in `src/` don't speak it. The glossary
even says, truthfully today but awkwardly, "Implemented today as the `Config`
singleton" and "via the `BaseConfig` base class."

## Solution

Rename the config classes, their modules, and the Application Config data tuple
so the code speaks the glossary's vocabulary, and fix the one runtime identity
string that lies. This is a **behavior-preserving rename** (plus one small
monitoring-identity correction): no logic, dependency direction, path
resolution, or public *behavior* changes — only names.

Concretely, from the reader's perspective:

- The application-wide singleton is named **`ApplicationConfig`** — specific, and
  clearly *not* a base class.
- The Component Config parent is named **`BaseComponentConfig`** — it keeps the
  house's `Base`-prefix-for-abstract-parent convention (parallel to
  `BaseTransformer`) but says *which* family it is the base of. `WatchdogConfig`
  now reads as "a watchdog config **is a** component config."
- The application data tuple is **`ApplicationConfigData`**, mirroring
  `WatchdogConfigData`, so both config families read identically:
  `<Owner>Config` + `<Owner>ConfigData`.
- `WatchdogConfig` reports its true identity (`WatchdogConfig`) in monitoring and
  logs.
- Every module filename matches its primary class (house rule: file ⇔ class), and
  the glossary/guidance docs are updated to name the new classes so nothing that
  a reader (or Claude) consults stays false.

There is **no back-compat alias**: `Config`, `BaseConfig`, and `ConfigData`
cease to exist. A template repo whose purpose is *teach-by-example* must speak
one vocabulary; an alias would leave two names per concept and juniors would copy
whichever they saw first.

## User Stories

### Reading & understanding the code

1. As a junior reading the config subsystem for the first time, I want the
   application-wide config class to be named `ApplicationConfig`, so that I know
   it's the one process-wide singleton and not a generic base.
2. As a junior, I want the Component Config parent to be named
   `BaseComponentConfig`, so that I understand it's the base of the *component*
   configs, not of `ApplicationConfig`.
3. As a junior, I want `WatchdogConfig(BaseComponentConfig[WatchdogConfigData])`
   to read as "a watchdog config is a component config," so that the inheritance
   relationship is self-evident from the names.
4. As a maintainer, I want the class names to match the **Application Config** /
   **Component Config** terms already defined in `CONTEXT.md`, so that the code
   and the glossary speak one language.
5. As a maintainer, I want no class named `BaseConfig` to exist, so that nobody
   is misled into looking for a `Config(BaseConfig)` inheritance that never
   existed.
6. As a maintainer, I want the Application Config data tuple named
   `ApplicationConfigData`, so that it mirrors `WatchdogConfigData` and its owner
   is obvious.

### Module & test layout

7. As a maintainer, I want `src/utils/config.py` renamed to
   `application_config.py`, so that the filename matches its class per the house
   file⇔class rule (like `base_transformer.py` holds `BaseTransformer`).
8. As a maintainer, I want `src/utils/base_config.py` renamed to
   `base_component_config.py`, so that the filename matches its class.
9. As a maintainer, I want `src/utils/config_data.py` renamed to
   `application_config_data.py`, so that the filename matches its tuple.
10. As a maintainer, I want the mirrored test modules renamed to match
    (`test_application_config.py`, `test_base_component_config.py`,
    `test_application_config_data.py` if present), so that the test tree keeps
    mirroring `src/`.
11. As a maintainer, I want the single-file workflow config
    (`make_config_template.mk`, and any `FILE_NAME` documentation) updated for the
    renamed modules, so that `make mypy-f` / `test-f` still target the right
    files.

### Call sites & imports

12. As a maintainer, I want all ~11 imports of `from src.utils.config import
    Config` updated to import `ApplicationConfig` from `application_config`, so
    that the codebase compiles under the new names.
13. As a maintainer, I want all ~15 `Config()` call sites (in `src`, `tests`, and
    notebooks) updated to `ApplicationConfig()`, so that every caller uses the new
    name with no alias.
14. As a maintainer, I want all references to `BaseConfig` (including
    `WatchdogConfig`'s base-class declaration and `__init__` super-call) updated
    to `BaseComponentConfig`, so that the component family compiles.
15. As a maintainer, I want all references to `ConfigData` (return-type
    annotations, the loader call in `ApplicationConfig`, imports) updated to
    `ApplicationConfigData`, so that the typed tree keeps type-checking.

### Runtime identity correction

16. As a watchdog operator, I want `WatchdogConfig` to report its `MetaClass`
    identity as `"WatchdogConfig"` (not `"ColumnsGroupingPipelineConfig"`), so
    that monitoring and logs label the watchdog config truthfully.
17. As a maintainer, I want `WatchdogConfig(name).get_class_name()` to return
    `"WatchdogConfig"`, so that the corrected identity is verifiable at the
    public `MetaClass` seam.
18. As a reader, I want `WatchdogConfig`'s docstrings to describe a watchdog
    config (not "Pipelines configuration file."), so that the copy-paste artifact
    is gone.

### Preserved behavior (compatibility)

19. As a template user, I want `ApplicationConfig().get_data()` to return the same
    data tree that `Config().get_data()` returned, so that only the name changed,
    not the result.
20. As a template user, I want `ApplicationConfig()` to remain a **Singleton**
    (same instance every call), so that process-wide config semantics are
    unchanged.
21. As a template user, I want `ApplicationConfig().get_data_as_dict()` to keep
    working, so that dict-based consumers are unaffected.
22. As a watchdog operator, I want `WatchdogConfig(name).get_data()` to keep
    returning `WatchdogConfigData` from `configurations/watchdogs/`, so that
    supervision code and config locations are unchanged.
23. As a maintainer, I want the **Config Loader** (`config_loader.py` /
    `load_config`) left untouched, so that the shared foundational mechanism —
    already correctly named per the glossary — stays stable.
24. As a maintainer, I want the dependency direction, path resolution, and
    Singleton composition from spec 001 unchanged, so that this rename touches
    neither ADR 0001 nor ADR 0002.

### Documentation truthfulness

25. As a reader of `CONTEXT.md`, I want its "Implemented today as the `Config`
    singleton" / "via the `BaseConfig` base class" lines updated to the new class
    names, so that the living glossary stays authoritative.
26. As a user of Claude on this repo, I want `CLAUDE.md`'s architecture section to
    name `ApplicationConfig` / `BaseComponentConfig`, so that per-session guidance
    doesn't point at classes that no longer exist.
27. As a maintainer, I want the in-code cross-references (the "Methods should the
    same as in `src/utils/base_config.py`" and "Only `src/utils/config` is
    different" docstrings) updated to the new module names, so that the
    hand-written breadcrumbs don't rot.
28. As a maintainer, I want the ADRs updated only in their *present-tense
    "implemented as" parentheticals* (not their historical decision narrative),
    so that the record of what was decided when is preserved while stale class
    names are corrected.
29. As a maintainer, I want a new `docs/CHANGELOG.md` entry describing the rename
    (rather than a rewrite of past entries), so that changelog history stays
    append-only.

### Quality gate

30. As a maintainer, I want `make all-secure` green after the rename on Python
    3.11–3.13, so that the mechanical change ships safely.
31. As a maintainer, I want the renamed code to pass mypy `--strict`, ruff
    format/lint, and the ruff docstring rules, so that it stays indistinguishable
    from surrounding `src/` code.

## Implementation Decisions

### The rename map

| Kind | Old | New |
|------|-----|-----|
| Class | `Config` | `ApplicationConfig` |
| Class | `BaseConfig` | `BaseComponentConfig` |
| NamedTuple | `ConfigData` | `ApplicationConfigData` |
| Module | `src/utils/config.py` | `src/utils/application_config.py` |
| Module | `src/utils/base_config.py` | `src/utils/base_component_config.py` |
| Module | `src/utils/config_data.py` | `src/utils/application_config_data.py` |
| Test module | `tests/tests_utils/test_config.py` | `test_application_config.py` |
| Test module | `tests/tests_utils/test_base_config.py` | `test_base_component_config.py` |

### Naming rationale (of record)

- **`ApplicationConfig`, not `Config`.** The class is the concrete, process-wide
  singleton — the *most specific* config, not a base. Dropping the "Base"-adjacent
  genericness removes the false contrast that made `BaseConfig` look like its
  parent. Mirrors how concrete subclasses in this codebase get specific names
  (`PlotlyHistogram`, `DatetimeOneHotEncoderTransformer`).
- **`BaseComponentConfig`, not `ComponentConfig` or `BaseConfig`.** Keeps the
  single house convention for an abstract parent — the `Base` prefix, exactly as
  `BaseTransformer` — because the class genuinely *is* subclassed; but qualifies
  it with the family (**Component**) so it no longer claims to be the base of
  *all* configs. The `Base` prefix is honest here in a way it never was for the
  whole-subsystem `BaseConfig`.
- **`ApplicationConfigData`, not `ConfigData`.** Restores `<Owner>Config` +
  `<Owner>ConfigData` symmetry with the already-correct
  `WatchdogConfig` / `WatchdogConfigData` pair.
- **No alias.** Hard rename; `Config` / `BaseConfig` / `ConfigData` are deleted.
  An alias would re-introduce the two-names-per-concept ambiguity this task
  exists to remove — the same class of "leaky low-value surface" spec 001 chose
  to shed rather than add.

### Modules modified

- **`ApplicationConfig` (was `Config`).** Class and module renamed. Its internal
  delegation to the **Config Loader** and **Project Paths** (from spec 001) is
  unchanged; only the class name, the module name, and its reference to
  `ApplicationConfigData` change. The `__main__` self-test block updates to the
  new names.
- **`BaseComponentConfig` (was `BaseConfig`).** Class and module renamed. Its
  `Generic[_T]` typing, `parse_config()`, `get_data()` / `get_data_as_dict()`
  surface, and its `MetaClass.__init__(class_type=CONFIG_TYPE_NAME, ...)` call are
  unchanged.
- **`ApplicationConfigData` (was `ConfigData`).** The whole nested NamedTuple tree
  keeps its structure and field names; only the top-level type name and its module
  filename change. All annotation sites that named `ConfigData` update.
- **`WatchdogConfig`.** Base class reference updates to
  `BaseComponentConfig[WatchdogConfigData]`; the `class_name` argument changes
  from `"ColumnsGroupingPipelineConfig"` to `"WatchdogConfig"`; the class/`__init__`
  docstrings change from "Pipelines configuration file." to describe a watchdog
  config. No change to `config_subfolder="watchdogs"` or load behavior.
- **Call sites (`src`, `tests`, `notebooks`).** ~11 imports and ~15 `Config()`
  usages updated to `ApplicationConfig`; all `BaseConfig` / `ConfigData` names
  updated. Because imports are absolute from `src.`, these are find-and-replace
  over known sites.
- **`make_config_template.mk`** (and any doc referencing `FILE_NAME`) updated so
  the single-file workflow points at the renamed modules.

### Explicitly unchanged

- **`config_loader.py` / `load_config`** — the glossary's **Config Loader**, its
  name already accurate and shared by both families. Not touched.
- **`WatchdogConfig` / `WatchdogConfigData`** names — already correct.
- **`Envs`, `ProjectPaths`, `Logger`** — untouched.
- All **behavior**: dependency direction (ADR 0001), path anchoring (ADR 0002),
  Singleton-by-composition, HOCON/`pyhocon`/`typedload`/`NamedTuple` stack,
  `.conf` file locations and contents.

### Documentation propagation (history-aware)

- **Update as living docs:** the two in-code cross-reference docstrings;
  `CLAUDE.md` architecture section; `CONTEXT.md`'s "Implemented today as…" lines.
- **Update parentheticals only:** ADR 0001 / 0002 present-tense "implemented as"
  mentions — never their historical narrative.
- **Append, don't rewrite:** a new `docs/CHANGELOG.md` entry.

## Testing Decisions

**What makes a good test here:** because this is a behavior-preserving rename,
the strongest signal is that the **existing** behavioral tests still pass once
they import the new names from the new modules — driving the same public seams
(`ApplicationConfig().get_data()`, `WatchdogConfig(name).get_data()`) and
asserting the same results. Tests assert *external behavior*, never the rename
mechanics. No new seams are introduced; the rename reuses the highest existing
ones. The compiler and the full suite are themselves a seam: a missed import or
call site fails `make mypy` / `make test` loudly.

**The one genuinely new assertion** — the Q6 identity fix — rides an existing
public seam on `MetaClass`:

- `WatchdogConfig(name).get_class_name() == "WatchdogConfig"` (was
  `"ColumnsGroupingPipelineConfig"`). This locks the corrected monitoring
  identity at the highest available seam rather than asserting on the source
  string.

**Prior art in the codebase** (mirror these):

- `tests/tests_configurations/test_watchdog_config.py` — parametrized
  `WatchdogConfig(name).get_data()` behavior tests; the natural home for the new
  `get_class_name()` assertion.
- `tests/tests_utils/test_config.py` → `test_application_config.py` — Application
  Config `get_data()` / Singleton behavior, renamed and re-imported.
- `tests/tests_utils/test_base_config.py` → `test_base_component_config.py` —
  Component Config base behavior, renamed and re-imported.
- `tests/conftest.py` — session-autouse fixture forcing `ENV_LOGGER=logger_console`
  and `ENV_RUNNING_UNIT_TESTS=True`; Singleton caching means env must be set via
  `Envs` before first instantiation. Unchanged by this task, but keep in mind when
  moving Application Config tests.

**Modules to test (all existing seams):**

- **Application Config:** `ApplicationConfig().get_data()` returns the expected
  `ApplicationConfigData`; Singleton identity holds; `get_data_as_dict()` works.
- **Component Config:** `WatchdogConfig(name).get_data()` returns
  `WatchdogConfigData` from `configurations/watchdogs/`; and the new
  `get_class_name() == "WatchdogConfig"` assertion.
- **Compile-time seam:** `make mypy` (strict) over `src` + `tests` proves every
  import and annotation followed the rename.

**Coverage gate:** `fail_under = 25` in `pyproject.toml` must stay satisfied
(unchanged — no new logic to cover).

## Out of Scope

- Any **behavioral** change to config loading, path resolution, the Logger, or
  the watchdog supervision logic — this is names only (plus the one monitoring
  identity string).
- Renaming or restructuring the **Config Loader** (`config_loader.py` /
  `load_config`) — already correctly named.
- Renaming `WatchdogConfig` / `WatchdogConfigData` — already correct.
- A **back-compat alias** for `Config` / `BaseConfig` / `ConfigData` — explicitly
  rejected (hard rename, one vocabulary).
- Revisiting ADR 0001 / ADR 0002 decisions — this task changes neither.
- Rewriting notebook *contents* beyond updating the `Config()` → `ApplicationConfig()`
  call sites (and the notebook that `application_config.py`'s docstring points at,
  `notebooks/documentation/low_level_tools_documentation.py`, if it demonstrates
  the class by name).
- Broadening the rename to other subsystems' class names.

## Further Notes

- **Publishing:** consistent with spec 001, no issue tracker is configured in this
  environment (no connected Linear/Jira/`gh` tracker), so this PRD lives as a file
  beside future spec-002 artifacts. Intended triage state is **`ready-for-agent`**
  (noted at the top). When a tracker is connected, port this file into an issue
  and carry the label over.
- **Delivery:** land on a **new branch off `main`** (e.g. `feature/config-naming`),
  separate from `feature/config-logger-decoupling`, so the mechanical rename
  reviews cleanly on its own. The pre-commit hook blocks direct commits to
  `main`/`master`/`develop`.
- **Blast radius (measured):** `Config()` — 15 call sites across 8 files; `Config`
  imports — 11; `BaseConfig` — 5 references. Small and mechanical.
- **Sequencing hint:** rename modules and classes first (let `make mypy` surface
  every missed site), then fix the `WatchdogConfig` identity + docstrings, then the
  docs sweep, then `make all-secure`.
- **Next step:** break into tracer-bullet slices via `to-issues` if a staged
  series is wanted; otherwise this is a single-PR mechanical change.
