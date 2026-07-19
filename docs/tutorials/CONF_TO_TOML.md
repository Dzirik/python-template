# Authoring Config Profiles in TOML

This guide teaches you to confidently read and edit this template's configuration
profiles — the application profiles (`configurations/python_repo.toml`,
`python_local.toml`, `python_personal.toml`) and the watchdog profiles
(`configurations/watchdogs/watchdog_cmd_01.toml`, `watchdog_cmd_02.toml`) — now that
they are written in **TOML** instead of HOCON. It is a practical authoring reference
for *this repo's* profiles, not a tour of the full TOML specification.

> **Why TOML?** See [`docs/adr/0003-toml-config-profiles.md`](../adr/0003-toml-config-profiles.md)
> for the decision record, and the
> ["How the profiles look — before and after"](../../specs/003_conf_files_form_resolution/PRD.md#how-the-profiles-look--before-hocon-and-after-toml)
> appendix in the PRD for the full before/after HOCON↔TOML comparison of every
> profile converted in this migration.

---

## Table of Contents

1. [Overview: How a Profile Becomes a Typed Object](#1-overview-how-a-profile-becomes-a-typed-object)
2. [Scalars — Strings, Integers, Floats, Booleans](#2-scalars--strings-integers-floats-booleans)
3. [Lists / Arrays](#3-lists--arrays)
4. [Tables — the Dictionary Equivalent](#4-tables--the-dictionary-equivalent)
5. [Nested Tables](#5-nested-tables)
6. [Lists of Objects](#6-lists-of-objects)
7. [Comments](#7-comments)
8. [HOCON → TOML Cheat-Sheet](#8-hocon--toml-cheat-sheet)
9. [Worked Example: A Full Profile, Section by Section](#9-worked-example-a-full-profile-section-by-section)

---

## 1. Overview: How a Profile Becomes a Typed Object

Every profile in `configurations/` is parsed the same way, by the shared Config
Loader (`src/utils/config_loader.py`):

1. `tomllib.load()` (Python's standard library — no third-party dependency) reads
   the `.toml` file into a plain nested `dict`.
2. `typedload.load(parsed, target)` validates and converts that `dict` into a typed
   `NamedTuple` tree — `ApplicationConfigData` for the application profiles,
   `WatchdogConfigData` for the watchdog profiles.

This means **every TOML construct you write maps directly onto a `NamedTuple`
field**, and the loader raises a diagnostic-rich exception (not a bare stack trace)
if a profile is missing, malformed, or the wrong shape — see the loader's
docstring for the three failure modes. Keep the target shape in mind as you read
this guide; each section below states which `NamedTuple` the example maps to.

The two shapes referenced throughout this guide:

```python
# src/utils/application_config_data.py
class Path(NamedTuple):
    data: str

class ParamNotebookExecution(NamedTuple):
    use_default: bool
    convert_to_html: bool
    ntb_path: str
    output_folder: str
    notebook_executioner_params: list[dict[str, float | str]]

class ApplicationConfigData(NamedTuple):
    name: str
    path: Path
    param_ntb_execution: ParamNotebookExecution
```

```python
# src/configurations/watchdog_config_data.py
class WorkerData(NamedTuple):
    name: str
    script: str
    args: list[str]
    timeout: float
    healthcheck_url_key: str = ""

class WatchdogConfigData(NamedTuple):
    name: str
    healthcheck_url_key: str = ""
    workers: list[WorkerData] = []
```

---

## 2. Scalars — Strings, Integers, Floats, Booleans

Scalars are `key = value` lines. From `configurations/python_repo.toml`:

```toml
name = "python_repo"
```

`name` is a **string** — always double-quoted in this repo's profiles. This maps
straight onto `ApplicationConfigData.name: str`.

From `configurations/python_local.toml`:

```toml
[path]
data = "E:/DATA"
```

Still a string — note the **forward slashes**, even on Windows. TOML's basic
(double-quoted) strings treat backslash as an escape character
(`"\n"`, `"\t"`, `"\\"`, …), so a raw Windows path like `E:\DATA` written between
double quotes would be misparsed. Forward slashes work fine on Windows and avoid the
issue entirely — that's why every path in this repo's profiles uses them. (If you
ever need a literal backslash, TOML also has single-quoted "literal" strings —
`'E:\DATA'` — which perform no escaping at all.)

From `configurations/watchdogs/watchdog_cmd_01.toml`, an **integer**, a **float**,
and a **negative integer**:

```toml
timeout = 240.0
```

```toml
# from the notebook_executioner_params array, configurations/python_repo.toml
{ n = 10, a = 1, b = 1, title = "Positive" }
{ n = 15, a = -1, b = -1, title = "Negative" }
```

`timeout` maps onto `WorkerData.timeout: float` — note `240.0`, not `240`; TOML
distinguishes integers (`1`, `-1`) from floats (`240.0`) by the presence of a
decimal point, and `typedload` enforces the annotated type. `n`, `a`, and `b` are
plain integers, landing in `notebook_executioner_params: list[dict[str, float | str]]`
as Python `int`/`float` values.

And a **boolean**, from `configurations/python_repo.toml`:

```toml
[param_ntb_execution]
use_default = true
convert_to_html = true
```

`true`/`false` are always **lower-case** in TOML — this is the one place HOCON and
TOML actually diverge syntactically for booleans (HOCON accepted Python-style
`True`/`False`; see the [cheat-sheet](#8-hocon--toml-cheat-sheet)). These map onto
`ParamNotebookExecution.use_default: bool` and `.convert_to_html: bool`.

---

## 3. Lists / Arrays

TOML arrays are homogeneous (same element type throughout) and map onto `list[...]`
fields. From `configurations/watchdogs/watchdog_cmd_01.toml`, a single-line array of
strings:

```toml
args = ["--delay", "3", "--hello", "Hi", "--minute", "5"]
```

This maps onto `WorkerData.args: list[str]`.

For longer arrays, TOML also allows a **multi-line form with a trailing comma**,
which is exactly how the object-list examples in this repo are formatted (see
[Section 6](#6-lists-of-objects) for the full inline-table version). Applied to a
plain string array, the equivalent multi-line form would read:

```toml
args = [
    "--delay",
    "3",
    "--hello",
    "Hi",
    "--minute",
    "5",
]
```

Both forms parse to the identical Python list — pick single-line for short arrays
(as every `args` value in this repo currently is) and multi-line once a list grows
long enough to hurt readability. The trailing comma after the last element is legal
in TOML (unlike JSON) and is kept even on the last line so that adding one more
element is a pure one-line diff.

---

## 4. Tables — the Dictionary Equivalent

A TOML **table** is the dictionary/mapping equivalent. It has two forms:

**The `[table]` header form** — everything until the next header (or end of file)
belongs to that table. From `configurations/python_repo.toml`:

```toml
[path]
data = "data"
```

This is exactly `ApplicationConfigData.path: Path`, where `Path` is a `NamedTuple`
with a single `data: str` field.

**The inline `{ key = value }` form** — a table written on one line, used when the
mapping is small and conceptually "one value" rather than "a section of the file".
From `configurations/python_repo.toml`, each entry of
`notebook_executioner_params` is an inline table:

```toml
{ n = 10, a = 1, b = 1, title = "Positive" }
```

**When to prefer which:** use the `[table]` header form for a profile's top-level
structural sections — the ones that correspond to a named `NamedTuple` field on the
outer config object (`[path]`, `[param_ntb_execution]`). Use the inline `{ }` form
for small, repeated, or nested-in-an-array mappings, where introducing a full
`[section]` header per entry would be noisy — exactly the
`notebook_executioner_params` case in [Section 6](#6-lists-of-objects).

---

## 5. Nested Tables

`[param_ntb_execution]` in `configurations/python_repo.toml` is itself a nested
table — one level below the profile's implicit root table:

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

Everything under `[param_ntb_execution]` becomes the fields of
`ParamNotebookExecution`, which is itself the `param_ntb_execution` field of the
outer `ApplicationConfigData`:

```
ApplicationConfigData
├── name                       ← top-level key, before any [table] header
├── path                       ← [path]
│   └── data
└── param_ntb_execution        ← [param_ntb_execution]
    ├── use_default
    ├── convert_to_html
    ├── ntb_path
    ├── output_folder
    └── notebook_executioner_params
```

Keys written *before* any `[table]` header belong to the file's implicit root
table — that's why `name = "python_repo"` at the top of the file lands directly on
`ApplicationConfigData.name`, with no header needed. Each `[section]` header then
opens a new table that stays active until the next header. There is no need for
this repo's profiles to go one level deeper (e.g. `[param_ntb_execution.sub]`) —
if you introduce a new nested `NamedTuple` field, follow the same pattern: one
`[header]` per nested `NamedTuple`.

---

## 6. Lists of Objects

Both forms below produce the exact same Python structure for `typedload` — a
`list` of `dict`/mapping objects — so the choice between them is purely about
which reads better for the shape of data you have.

### 6.1 `[[array-of-tables]]` form

Used for the watchdog `workers` list, where each entry is a substantial record
with several fields. From `configurations/watchdogs/watchdog_cmd_01.toml`:

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

[[workers]]
name = "cmd_02-01"
script = "run_cmd_status_print_02.py"
args = ["--delay", "1", "--pozdrav", "AHOOOOJ"]
timeout = 90.0
healthcheck_url_key = "cmd_02-01"
```

Each `[[workers]]` header opens a **new element** appended to the `workers` array;
every key until the next `[[workers]]` (or end of file) belongs to that element.
This maps onto `WatchdogConfigData.workers: list[WorkerData]` — three headers here
means a three-element list.

### 6.2 Inline-table-in-array form

Used for `notebook_executioner_params`, where each entry is a small, uniform
record. From `configurations/python_repo.toml`:

```toml
notebook_executioner_params = [
    { n = 10, a = 1, b = 1, title = "Positive" },
    { n = 15, a = -1, b = -1, title = "Negative" },
    { n = 20, a = 0, b = 2, title = "Zero" },
]
```

This is a single `key = [ ... ]` assignment whose value is an array of inline
tables — one line per element instead of a multi-line `[[header]]` block. It maps
onto `ParamNotebookExecution.notebook_executioner_params: list[dict[str, float | str]]`.

### 6.3 Same shape, either way

Both examples above parse to the same kind of Python value before `typedload` ever
sees it — a `list` of mappings:

```python
# [[workers]] form, three [[workers]] headers →
[
    {"name": "cmd_01-01", "script": "run_cmd_status_print_01.py",
     "args": ["--delay", "3", "--hello", "Hi", "--minute", "5"],
     "timeout": 240.0, "healthcheck_url_key": "cmd_01-01"},
    {"name": "cmd_01-02", ...},
    {"name": "cmd_02-01", ...},
]

# inline-table-in-array form, one array literal →
[
    {"n": 10, "a": 1, "b": 1, "title": "Positive"},
    {"n": 15, "a": -1, "b": -1, "title": "Negative"},
    {"n": 20, "a": 0, "b": 2, "title": "Zero"},
]
```

**Rule of thumb for your own profiles:** reach for `[[array-of-tables]]` when each
element is "record-shaped" and long enough that a multi-line block per entry aids
readability (the watchdog `workers`, one worker per screenful). Reach for the
inline-table-in-array form when each element is short and the whole list reads
better as one compact block (`notebook_executioner_params`, three short parameter
sets).

---

## 7. Comments

TOML comments start with `#` and run to the end of the line — exactly like HOCON's
`#` comments, so nothing changes here during migration. `configurations/python_local.toml`
preserves the guidance comment that told a template adopter where to point their
local data directory:

```toml
[path]
# Customize this path for your local data directory
# Example: "E:/DATA" or "/home/user/data" or "C:/Users/YourName/Documents/data"
data = "E:/DATA"
```

Comments can precede a key (as above), follow a value on the same line
(`data = "E:/DATA"  # local override`), or stand alone on their own line anywhere
in the file. Use them the same way you would have in the HOCON profiles — to
explain *why* a value is what it is, not to restate the key name.

---

## 8. HOCON → TOML Cheat-Sheet

A side-by-side translation of every structure this repo's profiles actually use,
from the [PRD's before/after appendix](../../specs/003_conf_files_form_resolution/PRD.md#how-the-profiles-look--before-hocon-and-after-toml):

| Structure | HOCON (before) | TOML (after) |
|---|---|---|
| Top-level string | `name: "python_repo"` | `name = "python_repo"` |
| Object / table | `path: { data: "data" }` | `[path]`<br>`data = "data"` |
| Nested object | `param_ntb_execution: { use_default: True, ... }` | `[param_ntb_execution]`<br>`use_default = true` |
| Boolean | `True` / `False` (Python-style, capitalised) | `true` / `false` (lower-case only) |
| Integer | `10`, `-1` | `10`, `-1` (unchanged) |
| Float | `240.0` | `240.0` (unchanged) |
| String array | `["--delay", "3", "--hello", "Hi"]` | `["--delay", "3", "--hello", "Hi"]` (unchanged) |
| List of objects | `[ {"n": 10, "a": 1, ...}, {"n": 15, ...} ]` | `[[workers]]` blocks **or** `[ { n = 10, a = 1, ... }, ... ]` inline-table array |
| Comment | `# a comment` | `# a comment` (unchanged) |
| Key quoting | Keys are usually unquoted (`name:`); quoting is optional | Keys are unquoted the same way (`name =`); quote a key only if it contains characters outside `A-Za-z0-9_-` |

**Gotchas when migrating your own custom profile:**

- **`True`/`False` → `true`/`false`.** This is the one value-level syntax change
  you must make by hand — TOML has no tolerance for the capitalised, Python-style
  spelling that HOCON accepted.
- **Unquoted keys are stricter in TOML.** HOCON is lenient about what counts as a
  bare key. TOML bare keys are limited to `A-Z`, `a-z`, `0-9`, `_`, and `-`; a key
  with a space, dot, or other punctuation must be quoted (`"my key" = 1`). None of
  this repo's profiles need a quoted key today, but keep it in mind if you add one.
  Table headers follow the same key rules (`[my_table]` bare, `["my table"]` quoted).
- **No substitutions, no includes.** HOCON supports `${...}` variable substitution
  and `include` file composition; TOML has neither. This repo's profiles never used
  either feature (confirmed during the migration audit — see the ADR), so nothing
  is lost, but if you were relying on either in a custom HOCON profile, you must
  inline the value or duplicate the shared section instead.
- **Choosing `[[array-of-tables]]` vs. an inline-table array.** Both parse to an
  identical list-of-mappings for `typedload` (see [6.3](#63-same-shape-either-way)).
  Prefer `[[header]]` for record-shaped, multi-field entries you want to read one
  per block (`workers`); prefer the inline `{ }` array for short, uniform entries
  you want to read as one compact list (`notebook_executioner_params`). There is no
  functional difference — pick whichever is more readable for the data at hand.
- **No duration/size unit literals.** HOCON can parse strings like `"30s"` or
  `"10 MB"` into durations/sizes for HOCON-aware consumers; TOML has no such
  literal — this repo never used the feature (all its timeouts are already plain
  floats of seconds, e.g. `timeout = 240.0`), so there is nothing to convert.

---

## 9. Worked Example: A Full Profile, Section by Section

Putting every construct above together, here is the complete
`configurations/python_local.toml` — the profile a template adopter is most likely
to hand-edit first, since it is the one meant to carry personal, local-machine
guidance:

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

Reading it top to bottom against [Section 1](#1-overview-how-a-profile-becomes-a-typed-object)'s
`ApplicationConfigData` shape:

- `name = "python_local"` — a top-level **scalar** ([Section 2](#2-scalars--strings-integers-floats-booleans)) → `ApplicationConfigData.name`.
- `[path]` — a **table header** ([Section 4](#4-tables--the-dictionary-equivalent)) → `ApplicationConfigData.path`, itself carrying a **comment** ([Section 7](#7-comments)) above its one field.
- `[param_ntb_execution]` — a **nested table** ([Section 5](#5-nested-tables)) → `ApplicationConfigData.param_ntb_execution`.
- `notebook_executioner_params = [ ... ]` — an **inline-table-in-array** ([Section 6.2](#62-inline-table-in-array-form)) → `ParamNotebookExecution.notebook_executioner_params`.

If you are adding a new watchdog config instead, use
`configurations/watchdogs/watchdog_cmd_01.toml` from [Section 6.1](#61-array-of-tables-form)
as your template: a top-level `name` and `healthcheck_url_key` scalar pair, followed
by one `[[workers]]` block per worker process.
