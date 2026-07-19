---
status: ready-for-agent
labels: [ready-for-agent]
supersedes: none
relates-to: docs/adr/0001-foundational-config-layering.md
builds-on: specs/002_config_naming_refactoring/PRD.md
---

# PRD: Migrate the HOCON config family to TOML

> **Builds on:** [spec 002](../002_config_naming_refactoring/PRD.md), the config-class
> rename, which shipped **after** this PRD was first drafted. This PRD has been
> reconciled with the post-002 names: the Application Config family is
> `ApplicationConfig` / `ApplicationConfigData` in `src/utils/application_config.py`
> and `src/utils/application_config_data.py`; the Component Config parent is
> `BaseComponentConfig` in `src/utils/base_component_config.py`. The Config Loader
> (`config_loader.py` / `load_config`) and `WatchdogConfig` / `WatchdogConfigData`
> keep their names. 002 (names) and this task (format + dependency) are behaviourally
> disjoint and compose cleanly.

## Problem Statement

As a developer working in (and adopting) this template, I hit friction with the
configuration profiles under `configurations/`. The application/component/watchdog
profiles (`python_*.conf`, `watchdogs/watchdog_*.conf`) are written in **HOCON** and
parsed by the third-party **`pyhocon`** library, and they carry the generic `.conf`
extension. Three things follow from that:

- **The extension is not self-describing.** `.conf` currently spans *three
  incompatible formats* in this repo — HOCON (the app/watchdog profiles), stdlib
  INI (`loggers/logger_*.conf`), and JSON (the runtime snapshots written by the
  saver/loader). Nothing about the extension tells a reader or an editor what is
  inside a given file; you have to know it from the folder.
- **My editor gives me nothing.** PyCharm (and other IDEs) do not recognise `.conf`
  as HOCON, so there is no syntax highlighting, no structural validation, and no
  autocomplete against the expected shape.
- **`pyhocon` is a niche dependency I carry for features I never use.** A scan of
  every tracked profile shows *zero* HOCON-specific features in use: no
  substitutions (`${...}`), no `include`, no duration/size units, no env-var
  interpolation. The files are effectively JSON-with-unquoted-keys plus `#`
  comments. `pyhocon` (and its `pyparsing` transitive dependency) is part of the
  `pip-audit` / `bandit` supply-chain surface that `make security-check` gates on,
  and it already needs a `DeprecationWarning` filter in `pyproject.toml`.

There is no active breakage — the current setup works. The problem is ongoing
ergonomic and dependency cost with no offsetting benefit.

## Solution

As a developer, I want the app/component/watchdog configuration profiles expressed
in **TOML** and parsed by the **standard-library `tomllib`**, so that I drop the
`pyhocon` dependency *without adding a replacement one*, get a standard,
IDE-recognised extension, keep inline comments, and keep the exact same typed
`NamedTuple` precision I have today.

The decisive insight that makes this cheap and safe: **the typed-`NamedTuple`
guarantee is provided by `typedload`, not by the file format.** The loader parses a
file into a plain mapping and then hands that mapping to `typedload` to validate it
into the target `NamedTuple` tree (`ApplicationConfigData`, the watchdog config
structure, etc.). `tomllib.load()` returns exactly the kind of plain `dict` that
`typedload` already consumes. So the entire typing layer, the
`ApplicationConfig`/`BaseComponentConfig` public
interface, `get_data()` returning a typed tree, and mypy-strict conformance all
survive untouched. Only the single parse call changes.

The **logger profiles stay exactly as they are** — stdlib INI consumed by
`logging.config.fileConfig`, with their live Python expressions in `args=`
(`5 * 1024 * 1024`, `sys.stdout`). They are dictated by the stdlib logging API, not
a free format choice, and are explicitly out of scope. A pleasant side effect of
this migration is that once the HOCON profiles become `.toml`, the `.conf`
extension is **de-overloaded** and comes to mean exactly one thing again: logger
INI files.

The solution also includes first-class **PyCharm ecosystem support** so the new
profiles are recognised, validated, and autocompleted in the IDE (see
Implementation Decisions → *PyCharm ecosystem support*).

## User Stories

1. As a template adopter, I want configuration profiles in a widely-recognised
   format (TOML), so that I do not have to learn a niche syntax before editing them.
2. As a developer, I want the `pyhocon` dependency removed, so that my
   supply-chain / security-audit surface shrinks and I no longer need a
   `DeprecationWarning` filter for it.
3. As a developer, I want configuration parsed by the standard library
   (`tomllib`), so that I add *no* new runtime dependency in exchange for removing
   `pyhocon`.
4. As a developer, I want the exact same typed `NamedTuple` result from loading a
   profile, so that all downstream code and mypy-strict checks keep working
   unchanged.
5. As a developer, I want `ApplicationConfig().get_data()`,
   `BaseComponentConfig.get_data()`, and `get_data_as_dict()` to behave identically
   after the migration, so that no caller has to change.
6. As a developer, I want the application profiles (`python_repo`, `python_personal`,
   `python_local`) converted to TOML, so that the three shipped profiles keep
   selecting correctly via `ENV_CONFIG`.
7. As an operator of the production supervision system, I want the watchdog profiles
   (`watchdog_cmd_01`, `watchdog_cmd_02`) converted to TOML, so that `watchdog.py`
   and `checker.py` load their worker definitions exactly as before.
8. As a developer, I want comments preserved in the profiles, so that guidance like
   "customise this path for your local data directory" in the local profile survives
   the migration.
9. As a developer, I want the profile-selection env vars (`ENV_CONFIG`) and the
   bare-name convention (name without extension) to keep working, so that nothing in
   the `.env` / `Envs` layer changes for users.
10. As a developer, I want the logger profiles left untouched, so that logging
    behaviour, rotation, and console/file handlers are unaffected.
11. As a developer, I want the `.conf` extension to end up meaning exactly one thing
    (logger INI), so that the extension becomes self-describing again.
12. As a PyCharm user, I want `.toml` profiles auto-recognised by the IDE, so that I
    get syntax highlighting, a structure view, and formatting for free.
13. As a PyCharm user, I want a JSON Schema mapped to the profile files, so that I
    get autocomplete and inline validation that reflects the `ApplicationConfigData`
    shape while I edit.
14. As a PyCharm user, I want the schema mapping shared through version control, so
    that every contributor gets the same IDE assistance without manual setup.
15. As a developer, I want the runtime config-snapshot save/load pair (in the
    saver/loader) to stop depending on `pyhocon`, so that removing the dependency is
    complete and nothing still imports it.
15a. As a developer, I want the runtime config-snapshot files to carry the `.json`
    extension rather than `.conf`, so that JSON content is no longer written into a
    `.conf` file and the `.conf` extension can genuinely collapse to logger INI only
    (the de-overloading promised in User Story 11 and the Problem Statement's third
    `.conf` meaning).
16. As a developer running `make all-secure`, I want the full quality gate (mypy,
    ruff format/lint/docstring, pytest, bandit, pip-audit) to pass after the
    migration, so that CI stays green on the 3.11/3.12/3.13 matrix.
17. As a maintainer, I want the decision and its rejected alternatives recorded in an
    ADR, so that a future contributor understands *why* TOML was chosen over YAML,
    JSON, and keeping HOCON.
18. As a documentation reader, I want CLAUDE.md, PROJECT_VISION, and tutorial
    references updated from "HOCON" to "TOML", so that the docs match the code.
18a. As a reader of `CONTEXT.md`, I want the glossary's config terms to stop being
    pinned to a specific file extension — its *Config Profile / Logger Profile*,
    *Application Config*, *Component Config*, and *Config Loader* entries currently say
    "`.conf` file", which this migration makes false for config profiles — so that the
    glossary stays truthful and, per its own rule, free of implementation detail.
19. As a developer, I want the per-kind subfolder convention (`loggers/`,
    `watchdogs/`) preserved, so that resolution logic and mental model are unchanged.
20. As a developer, I want a malformed TOML profile to raise a diagnostic-rich
    exception (not a bare stack trace), so that config problems stay as debuggable as
    they are today under HOCON.
21. As a developer, I want a shape mismatch against the target `NamedTuple` to keep
    raising the existing distinct "does not match the shape of ..." exception, so
    that the three failure modes (missing file / malformed syntax / wrong shape) stay
    individually identifiable.
22. As a developer, I want the loader to remain silent on success and Logger-free, so
    that ADR 0001 (config loading must not depend on the Logger) still holds.
23. As a developer, I want the git-ignored generated profile (`python_personal`) and
    its template to move to `.toml` too, so that `make create-venv` still generates a
    working personal profile.
24. As a template adopter unfamiliar with TOML, I want a hands-on tutorial
    (`docs/tutorials/CONF_TO_TOML.md`) that shows how to express the standard
    structures I need — scalars, lists, dictionaries/tables, nested tables, lists of
    objects, inline vs. multi-line forms, and comments — so that I can confidently
    author and edit configuration profiles in the new style without reading the full
    TOML spec.
25. As a template adopter, I want the tutorial to map each old HOCON structure to its
    TOML equivalent side by side and call out the common gotchas (`True`→`true`,
    quoting rules, when to use `[[array-of-tables]]` vs. inline tables), so that I can
    migrate my own custom profiles by analogy.

## Implementation Decisions

- **Target format: TOML, parsed by stdlib `tomllib`.** `requires-python` is
  `>=3.11,<3.14`, so `tomllib` is present on every supported interpreter. This
  removes `pyhocon` while adding **no** replacement runtime dependency. TOML keeps
  comments (unlike JSON) and adds no third-party parser (unlike YAML/PyYAML).
- **Single parse-point change.** The shared config loader is the only module that
  parses HOCON for profiles. Its parse step changes from the `pyhocon` factory to
  `tomllib.load` (opening the file in binary mode as `tomllib` requires). The
  subsequent `typedload.load(parsed, target)` call is unchanged, preserving the typed
  `NamedTuple` output. The three distinct failure modes are preserved: missing file,
  malformed-syntax (now catching the TOML decode error instead of the HOCON parse
  error), and shape-mismatch.
- **Typed layer untouched.** `ApplicationConfigData` and the watchdog config
  `NamedTuple` structures, `ApplicationConfig`, `BaseComponentConfig`, `get_data()`,
  `get_data_as_dict()`, and all callers are unchanged. This is the core reason the
  migration is low-risk.
- **Extension resolution must become per-family.** The project-paths helper that
  builds a profile's path currently appends a hard-coded `.conf`, and it is shared by
  *both* the profile loader and the logger loader. It will gain an explicit extension
  parameter (defaulting to the current `.conf`) so that the HOCON-family callers
  resolve `.toml` while the logger caller keeps `.conf`. This avoids breaking the
  out-of-scope logger path.
- **Runtime snapshot round-trip decoupled from the profile format.** The
  saver/loader pair that dumps a config `NamedTuple` and reads it back currently
  *writes* JSON but *reads* via `pyhocon`, and both sides use a `.conf` extension. It
  will be made symmetric on stdlib `json` (write and read), which both removes the
  last `pyhocon` import and sidesteps the fact that `tomllib` is read-only. **The
  snapshot extension also changes from `.conf` to `.json`** (both `save_config_data`
  and `load_config_data`), so the file's name matches its content and the third `.conf`
  meaning identified in the Problem Statement disappears — without this the
  "`.conf` means exactly one thing" claim would be false. These snapshots are machine
  round-trips, never hand-edited, so JSON is the right fit and no human-facing format
  is lost.
- **Dependency removal.** `pyhocon` is removed from `pyproject.toml` (via the
  `uv`/Makefile dependency workflow, never by hand-editing `uv.lock`), along with the
  now-unneeded `pyhocon` `DeprecationWarning` filter in the pytest config. `typedload`
  stays.
- **Profiles converted:** the three application profiles and the two watchdog
  profiles, plus the git-ignored personal profile and its generated template. Values,
  nesting, and comments are carried over verbatim; HOCON's Python-style `True`
  becomes TOML `true`. No HOCON-only feature has to be unwound because none is used.
- **PyCharm ecosystem support (new deliverable):**
  - **Auto-recognition:** naming the profiles `.toml` is sufficient for PyCharm's
    bundled TOML support to provide highlighting, structure view, and formatting — no
    per-user configuration.
  - **Schema-driven validation & autocomplete:** a JSON Schema describing the
    application-profile shape (and one for the watchdog shape) is committed under the
    configurations area, and a JSON-Schema mapping is shared through the project's
    version-controlled IDE settings so PyCharm validates and autocompletes the
    profiles against the `ApplicationConfigData` / watchdog shapes as they are edited.
    The schema mirrors the `NamedTuple` fields; keeping it in sync is a documented maintenance
    step.
  - **Logger `.conf` files:** documented as an optional PyCharm File-Types mapping of
    `loggers/*.conf` to the Properties/INI file type for basic highlighting. No format
    change; guidance only.
- **Hands-on TOML tutorial (new deliverable):** a `docs/tutorials/CONF_TO_TOML.md`
  guide, following the existing tutorial house style (a title, a short overview, a
  numbered Table of Contents, then numbered sections with copy-pasteable fenced
  examples — as in `PERSISTENT_RUN.md` / `CHECKER_SCHEDULER_SET_UP.md`). It is a
  practical authoring reference for the config profiles, not a TOML language spec. It
  must cover, each with a runnable snippet:
  - **Scalars** — strings (and quoting rules), integers, floats, booleans
    (`true`/`false`, lower-case), and how they land in the typed `NamedTuple`.
  - **Lists / arrays** — homogeneous arrays (`args = ["--delay", "3"]`), and both the
    single-line and multi-line (trailing-comma) forms.
  - **Dictionaries / tables** — the `[table]` header form and the inline
    `{ key = value }` form, and when to prefer each.
  - **Nested tables** — dotted headers (`[param_ntb_execution]`, nested keys) mapped
    to the nested `NamedTuple` tree.
  - **Lists of objects** — the `[[array-of-tables]]` form (as used by the watchdog
    `workers`) *and* the compact inline-table-in-array form (as used by
    `notebook_executioner_params`), showing both produce the same list-of-mappings.
  - **Comments** — `#` line comments, mirroring the guidance comments preserved in
    `python_local`.
  - **HOCON→TOML cheat-sheet** — a side-by-side table translating each structure this
    repo actually uses, plus the gotchas: `True`→`true`, unquoted-key differences,
    no HOCON substitutions/includes, and choosing `[[...]]` vs inline tables.
  The tutorial cross-links the profile examples in this PRD and the "how the profiles
  look" appendix, and is referenced from the docs-update user story (CLAUDE.md /
  PROJECT_VISION pointers).
- **ADR:** a new ADR (`docs/adr/0003-*`) records the decision, the four-way
  comparison (keep HOCON / TOML / YAML / JSON), the `typedload`-orthogonality
  insight, the shared-extension wrinkle, and the "custom extension won't collide with
  future types" argument as weighed-and-dismissed (it defends a non-cost; the real
  cost is self-description, which a standard extension fixes).
- **Condition that would reverse the decision (recorded, not triggered):** if the
  template deliberately adopts *config composition* — layered overrides, `include`-d
  fragments, or `${?ENV_VAR}` inline fallbacks — HOCON's unused features would earn
  their keep. That is a future architecture change from today's "select one whole
  profile via `ENV_CONFIG`" model and is out of scope here.

## Testing Decisions

- **Good tests exercise external behaviour, not parsing internals.** A good test
  loads a profile through the public loading path and asserts on the resulting typed
  values (e.g. the profile `name`, a nested path value, a list of worker/notebook
  parameter objects) — never on how the bytes were parsed. The format swap must be
  invisible to these tests once the fixtures are converted.
- **Reuse existing seams — no new ones.** The highest existing seams already cover
  this surface:
  - the shared **config loader** entry point (prior art: `test_config_loader.py`),
    including its three failure modes — missing file, malformed syntax, shape
    mismatch;
  - **`ApplicationConfig`** and its `get_data()` / `get_data_as_dict()` (prior art:
    `test_application_config.py`);
  - **`BaseComponentConfig`** as the multi-instance parent used by the watchdog config
    (prior art: `test_base_component_config.py`);
  - **`Logger`** loading, as a regression guard that the untouched logger path still
    works (prior art: `test_logger.py`).
- **Modules tested:** the config loader, `ApplicationConfig`, `BaseComponentConfig`, the watchdog config,
  and (regression only) `Logger`. The saver/loader round-trip gets a test that a
  dumped config `NamedTuple` reloads equal to the original via the new JSON-symmetric
  path, asserting the snapshot is written to a `.json` file (not `.conf`).
- **Fixtures:** convert the profile fixtures/samples the tests rely on from HOCON to
  TOML; keep assertions identical. Add a malformed-TOML fixture to prove the
  "malformed syntax" exception path still fires with a diagnostic-rich message.
- **Failure-mode parity:** assert that a missing profile, a syntactically broken
  TOML profile, and a well-formed-but-wrong-shape profile each raise their existing
  distinct exception types.
- **Gate:** `make all-secure` must pass on the 3.11/3.12/3.13 matrix, including
  `pip-audit` now that `pyhocon` is gone.

## Out of Scope

- **The logger profiles** (`loggers/logger_*.conf`) and any change to
  `logging.config.fileConfig`. They remain stdlib INI. (A separate, higher-cost, and
  lower-value decision — explicitly excluded.)
- **Any config-composition capability** (substitutions, includes, env-var
  interpolation, profile merging/layering). Today's model is "select one whole
  profile via `ENV_CONFIG`", and that is retained.
- **Changing the `Envs` / `.env` layer or the profile-selection mechanism.**
- **YAML and JSON** as the target format (evaluated and rejected: YAML adds a
  dependency, contradicting the drop-`pyhocon` goal and adding footguns; JSON loses
  comments).
- **Auto-generating the JSON Schema from the `NamedTuple` at build time.** The schema
  is committed and maintained by hand for now; automatic generation can be a later
  enhancement.
- **VS Code / other IDE support.** Only PyCharm ecosystem support is in scope per the
  request (though `.toml` recognition is broadly automatic elsewhere too).

## Further Notes

### How the profiles look — before (HOCON) and after (TOML)

**Application profile — before (`python_repo.conf`, HOCON):**

```hocon
{
    name: "python_repo",
    path: {
        data: "data"
    },
    param_ntb_execution: {
        use_default: True,
        convert_to_html: True,
        ntb_path: "notebooks/template/template_parameterized_execution_notebook.ipynb",
        output_folder: "reports",
        notebook_executioner_params: [
            {"n": 10, "a": 1, "b": 1, "title": "Positive"},
            {"n": 15, "a": -1, "b": -1, "title": "Negative"},
            {"n": 20, "a": 0, "b": 2, "title": "Zero"}
        ]
    }
}
```

**Application profile — after (`python_repo.toml`, TOML):**

```toml
name = "python_repo"

[path]
data = "data"

[param_ntb_execution]
use_default = true
convert_to_html = true
ntb_path = "notebooks/template/template_parameterized_execution_notebook.ipynb"
output_folder = "reports"
notebook_executioner_params = [
    { n = 10, a = 1, b = 1, title = "Positive" },
    { n = 15, a = -1, b = -1, title = "Negative" },
    { n = 20, a = 0, b = 2, title = "Zero" },
]
```

**Local profile with a user-guidance comment — after (`python_local.toml`):**

```toml
name = "python_local"

[path]
# Customize this path for your local data directory
# Example: "E:/DATA" or "/home/user/data" or "C:/Users/YourName/Documents/data"
data = "E:/DATA"

[param_ntb_execution]
use_default = true
convert_to_html = true
ntb_path = "notebooks/template/template_parameterized_execution_notebook.ipynb"
output_folder = "reports"
notebook_executioner_params = [
    { n = 10, a = 1, b = 1, title = "Positive" },
    { n = 15, a = -1, b = -1, title = "Negative" },
    { n = 20, a = 0, b = 2, title = "Zero" },
]
```

**Watchdog profile — before (`watchdog_cmd_01.conf`, HOCON):**

```hocon
{
    name: "watchdog_cmd_01",
    healthcheck_url_key: "watchdog_cmd_01",
    workers: [
        {
            name: "cmd_01-01",
            script: "run_cmd_status_print_01.py",
            args: ["--delay", "3", "--hello", "Hi", "--minute", "5"],
            timeout: 240.0,
            healthcheck_url_key: "cmd_01-01"
        },
        ...
    ]
}
```

**Watchdog profile — after (`watchdog_cmd_01.toml`, TOML, array-of-tables):**

```toml
name = "watchdog_cmd_01"
healthcheck_url_key = "watchdog_cmd_01"

[[workers]]
name = "cmd_01-01"
script = "run_cmd_status_print_01.py"
args = ["--delay", "3", "--hello", "Hi", "--minute", "5"]
timeout = 240.0
healthcheck_url_key = "cmd_01-01"

[[workers]]
name = "cmd_01-02"
script = "run_cmd_status_print_01.py"
args = ["--delay", "5", "--hello", "Hello", "--minute", "15"]
timeout = 360.0
healthcheck_url_key = "cmd_01-02"
```

Notes on the mapping: HOCON's Python-style `True` becomes TOML `true`; `240.0` stays
a float; string/int/bool/list/table all have native TOML representations, so no value
is lost. Object-lists can use compact inline tables (application profile) or the
`[[table]]` array-of-tables form (watchdog profile) — both parse to the same list of
mappings for `typedload`.

### PyCharm ecosystem support

- **Zero-config recognition:** once files carry the `.toml` extension, PyCharm's
  bundled TOML support provides highlighting, a structure view, and formatting with
  no setup.
- **Schema validation + autocomplete:** a committed JSON Schema for the application
  profile (and one for the watchdog profile), plus a version-controlled JSON-Schema
  mapping, gives inline validation and completion that reflects the
  `ApplicationConfigData` / watchdog shapes as the file is edited. This restores — in
  the IDE — the same
  "must match the shape" guarantee that `typedload` enforces at load time, but *while
  typing*.
- **Logger `.conf`:** optionally mapped to the Properties/INI file type in PyCharm's
  File Types settings for basic highlighting; no format change.

### Estimated cost

Roughly half a day to a day, low risk: 5 profile files converted mechanically, ~5
code touch-points (loader parse call, path-helper extension parameter, saver/loader
JSON symmetry, dependency removal, docstring/doc updates), test fixtures converted,
schema + IDE mapping added, the `docs/tutorials/CONF_TO_TOML.md` authoring guide, plus
the ADR. `make all-secure` is the acceptance gate.

### Provenance

This PRD is the outcome of a design-review session: the HOCON files were scanned and
confirmed to use no HOCON-specific features; the `typedload`-vs-format
orthogonality was verified against the loader; and TOML was selected over keeping
HOCON, YAML, and JSON against the developer's stated motivations (familiarity/
ecosystem, dropping `pyhocon`, standard extension/tooling) with no active pain
forcing the change.
