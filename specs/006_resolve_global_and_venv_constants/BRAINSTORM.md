---
status: brainstorm-complete
labels: [brainstorm]
supersedes: none
relates-to: docs/PROJECT_VISION.md
builds-on: none
---

# Brainstorm: Resolve global & venv constants

> **Context:** `src/constants/global_constants.py` is a catch-all that bundles five
> unrelated concerns, and the env-var / defaults layer (`src/utils/envs.py`,
> `.env.example`, `global_constants.py`) writes the same default profile names in three
> places. This brainstorm settles how to (B) reorganize the constants by domain and
> (C) give the env defaults a single source of truth — without touching config/logger
> loading semantics.

## Scope

The original request spanned three threads. The user narrowed to two:

| Thread | Title | In scope? |
|---|---|---|
| A | Secret / `.env` protection via git hooks or scanning | **Dropped** (user changed their mind) |
| B | Reorganize `global_constants.py` by concern | **Yes** |
| C | Rethink `Envs` / `.env` / defaults (single source of truth) | **Yes** |

B + C together match the branch name `006_resolve_global_and_venv_constants`.

## Current state (findings)

### `src/constants/global_constants.py` mixes five concerns

| Cluster | Contents | Real consumers |
|---|---|---|
| Env-var name keys | `ENV_CONFIG`, `ENV_LOGGER`, `ENV_RUNNING_UNIT_TESTS`, `ENV_PROJECT_ROOT` | `envs.py`, `test_config_loader.py`, `test_project_paths.py` |
| Magic logger filename | `SPECIAL_LOGGER_FILE_NAME = "logger_file_limit_console.log"` | `logger.py` only |
| Folder name | `FOLDER_CONFIGURATIONS = "configurations"` | `project_paths.py`, `test_config_loader.py` |
| Transformer method ids | `F`, `FP`, `P`, `INV` | `test_datetime_one_hot_transformer.py` only (imports `FP`, `P`) |
| Visualization palette | `COLORS` dict | `plotly_base.py` only |

### Defaults are written in two places (DRY risk)

The default logger profile name `logger_file_limit_console` appears in:

1. `.env.example` (documented default for `ENV_LOGGER`),
2. `envs.py` (`_DEFAULT_LOGGER`).

Change one, forget the other, and the fallback default silently diverges.

**Not a third copy:** `global_constants.py` also holds
`SPECIAL_LOGGER_FILE_NAME = "logger_file_limit_console.log"`, but this is a
*different concept* — the error-path fallback log filename used only by
`logger.py:_log_bad_file()` when the selected profile is missing. It only
*coincidentally* shares the `logger_file_limit_console` prefix; it does **not**
match any real profile's output (`logger_file_limit_console.toml` actually writes
to `python_log_file_limit_console.log`). The stale in-code comment claiming it
"should be the same as in config files for logger" is false today. It must stay an
independent literal — deriving it from `DEFAULT_LOGGER` would invent a false
coupling (changing the default profile would silently rename the fallback file).

### `Envs` is bypassed in two places

CLAUDE.md states `Envs` is the only place env vars are read/written, but:

- `src/scripts_production/watchdog.py:88` reads `os.getenv("HEALTHCHECK_PING_URL")` directly.
- `src/scripts_production/checker.py:34` reads `os.environ.get("SYSTEMROOT")` directly.

### `.env.example` is stale

The comments for `ENV_CONFIG` and `ENV_LOGGER` still say "without .conf extension",
left over from before the TOML migration (ADR 0003 / 0004). Profiles are `.toml` now.

### `F` and `INV` are dead

No reference to `F`, `FP`, `P`, `INV` exists anywhere in `src/`. Only one test imports
`FP` and `P`; `F` and `INV` are unused entirely.

## Decisions

| # | Decision | Choice made |
|---|---|---|
| C-1 | Single source of truth for defaults | Constants module holds the canonical defaults; `Envs` imports them; `.env.example` **documents them only**. |
| C-3 | `.env.example` fallback loading | **Remove** the `envs.py` else-branch that `load_dotenv(.env.example)` when `.env` is absent. `.env.example` must be pure documentation, never a live value source. Behaviour-neutral: `DEFAULT_*` mirror the `.env.example` values, and CI (no `.env`) resolves the same profile names via `DEFAULT_*`. |
| C-2 | `Envs` accessor style & reach | Keep explicit one-method-per-var house style. Add `get_healthcheck_ping_url()` so `watchdog.py` goes through `Envs`. Leave `SYSTEMROOT` (OS builtin, not app config) as-is with a clarifying comment. |
| B-1 | How to break up `global_constants.py` | Co-locate each cluster with the domain that owns it. |
| B-2 | `FOLDER_CONFIGURATIONS` placement | Move into `src/utils/project_paths.py` as a module constant (strict co-location; `project_paths` is its only real owner). |
| B-3 | "Dead" transformer ids | Keep all four (`F`, `FP`, `P`, `INV`) in a new production module as the canonical method-identifier vocabulary. **They are not dead** — a larger transformer suite (not yet migrated into this repo) uses all four heavily and needs one place to import them from. This template repo currently exercises only `FP`/`P` (test discriminators). Preserving them here reserves the import path so the incoming suite works unchanged. Do **not** prune `F`/`INV`. |

## Target design

### Part 1 — Module layout (Thread B)

`global_constants.py` is dismantled and **deleted**; each cluster moves to its owner:

| Constant(s) | New home | Consumers to update |
|---|---|---|
| `COLORS` | **new** `src/visualisations/colors.py` | `plotly_base.py` (import + docstring reference) |
| `F`, `FP`, `P`, `INV` | **new** `src/transformations/transformer_methods.py` (docstring: canonical method-id vocabulary for the transformer suite; `F`/`INV` reserved for the not-yet-migrated suite) | `test_datetime_one_hot_transformer.py` (imports `FP`, `P`) |
| `FOLDER_CONFIGURATIONS` | module constant in `src/utils/project_paths.py` | `project_paths.py`, `test_config_loader.py` |
| `SPECIAL_LOGGER_FILE_NAME` | derived constant in `src/utils/logger.py` | `logger.py` |
| `ENV_*` keys + `DEFAULT_*` | **renamed** `src/constants/env_constants.py` | `envs.py`, `test_config_loader.py`, `test_project_paths.py` |

The `src/constants/` package survives holding only `env_constants.py` — the env-var
name keys and canonical defaults. It is **deliberately kept out of `envs.py`** (its
notional domain owner, the Env Selector) because `envs.py` runs `load_dotenv` as an
**import-time side effect**. Keeping the keys/defaults in a pure, side-effect-free,
import-nothing data module lets foundational code (`project_paths.py`) and tests
reference key names without booting the env layer. This rationale must be written into
the `env_constants.py` module docstring so it is not "helpfully" folded back into
`envs.py` later.

### Part 2 — Envs / defaults single source of truth (Thread C)

`src/constants/env_constants.py` becomes the one place defaults are written:

```python
DEFAULT_CONFIG = "python_personal"
DEFAULT_LOGGER = "logger_file_limit_console"
DEFAULT_RUNNING_UNIT_TESTS = "False"
```

- `envs.py`: drop the local `_DEFAULT_*` strings; import `DEFAULT_*` from
  `env_constants`. Getter/setter API is unchanged. Also **remove the `.env.example`
  fallback** in the module-level `load_dotenv` block — load `.env` only if present;
  otherwise rely on the actual environment + `DEFAULT_*`. `.env.example` is docs-only.
- `logger.py`: `SPECIAL_LOGGER_FILE_NAME` moves here as an **independent literal**
  (unchanged value `"logger_file_limit_console.log"`), NOT derived from `DEFAULT_LOGGER`.
  Drop the false "should match config files" comment; add a one-line comment stating
  its real role as the error-path fallback destination. (Two-way dedup, not three-way.)
- Add `ENV_HEALTHCHECK_PING_URL = "HEALTHCHECK_PING_URL"` key to `env_constants.py`
  (**name ≠ value** — the live env var deliberately has no `ENV_` prefix; add an inline
  comment so nobody "fixes" it by renaming the variable). **Do not rename** the
  `HEALTHCHECK_PING_URL` env var, `.env.example`, or the watchdog warning strings.
  Add `Envs.get_healthcheck_ping_url() -> str | None` returning the **raw** string
  (or `None` when unset — no `DEFAULT_*`); `json.loads` + validation stay in
  `watchdog.resolve_ping_url` as domain logic.
- `watchdog.py`: replace `os.getenv("HEALTHCHECK_PING_URL")` with
  `Envs.get_healthcheck_ping_url()`.
- `checker.py`: `SYSTEMROOT` stays a direct `os.environ` read (OS builtin, not
  application config) with a one-line clarifying comment.

### Part 3 — `.env.example` cleanup

- Fix the stale "without .conf extension" comments → ".toml" for both `ENV_CONFIG` and
  `ENV_LOGGER`.
- Keep the documented defaults; confirm they match the new `DEFAULT_*` constants.

### Part 4 — Verification & doc consumers

- Full `make all` (mypy `--strict` + ruff format + lint + docstrings + pytest) — the
  per-file `-f` targets won't cover the cross-file moves.
- Grep-audit that no `global_constants` reference survives in `src/` or `tests/`.
- **`README.md` (file-tree section, ~L250-255):** in scope. Drop the
  `global_constants.py` entry, add `env_constants.py` (accurate one-liner), and add
  entries for the new `visualisations/colors.py` and `transformations/transformer_methods.py`.
- **Notebook comments** (`notebooks/template/*.py`, `notebooks/documentation/*.py`,
  `notebooks/raw/*.py`): the `# from src.global_constants import *` lines already point
  at a dead path (`src.global_constants` never existed post-package) and have no single
  successor. **Delete the commented line** in each — do not repoint.
- **`docs/notebooks_freezes/*.html`:** leave untouched — frozen historical output
  snapshots; knowingly stale, regenerate naturally.
- Add `plotly_base.py:48` docstring update (COLORS reference →
  `src/visualisations/colors.py`) — already noted in the Part 1 consumers table.

## Open items / notes

- No behavioural change intended — this is a structural refactor plus a defaults-DRY fix.
  Loading semantics (ADR 0001/0002/0003/0004) are untouched.
- `F` and `INV` are unused *within this repo* but are intentionally retained (see B-3):
  the incoming transformer suite depends on them. Not to be pruned.
