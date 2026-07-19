# Single source of truth for env defaults: `env_constants.py` + `Envs` rewire

> **Status:** `ready-for-agent`

## Parent

[`specs/006_resolve_global_and_venv_constants/BRAINSTORM.md`](../BRAINSTORM.md) — *Resolve global & venv constants*

## What to build

The foundation of the refactor and Thread C's single-source-of-truth. Today the default profile names live in two places (`.env.example` and `envs.py`'s `_DEFAULT_*`), the env-var name keys sit in the catch-all `global_constants.py`, and `envs.py` silently loads `.env.example` as a live fallback when `.env` is absent — which makes `.env.example` a value source rather than pure documentation.

After this slice there is exactly one code-level source for the env-var name keys and the canonical defaults, `Envs` imports them, and `.env.example` is documentation only.

Create a new **side-effect-free** module `src/constants/env_constants.py` holding the env-var name keys (`ENV_CONFIG`, `ENV_LOGGER`, `ENV_RUNNING_UNIT_TESTS`, `ENV_PROJECT_ROOT`) and the canonical defaults (`DEFAULT_CONFIG = "python_personal"`, `DEFAULT_LOGGER = "logger_file_limit_console"`, `DEFAULT_RUNNING_UNIT_TESTS = "False"`). Its module docstring must state **why it is deliberately kept out of `envs.py`**: `envs.py` runs `load_dotenv` as an import-time side effect, so keeping these as pure data lets foundational code (`project_paths.py`) and tests import the key names without booting the env layer. This prevents a future maintainer from "helpfully" folding it into `envs.py`.

Rewire `Envs`: import `ENV_*` and `DEFAULT_*` from `env_constants`, delete the local `_DEFAULT_*` strings, and **remove the `.env.example` fallback** in the module-level `load_dotenv` block — load `.env` only if present; otherwise rely on the real environment plus `DEFAULT_*`. The getter/setter API is otherwise unchanged.

This is behaviour-neutral: the `DEFAULT_*` mirror the `.env.example` values, and CI (which never creates a `.env`) resolves the same profile names via `DEFAULT_*` that it previously got from the `.env.example` fallback.

Scope:

- **New `src/constants/env_constants.py`** — the four `ENV_*` keys + three `DEFAULT_*`, house-style docstrings, no imports, no side effects.
- **`envs.py`** — import `ENV_*`/`DEFAULT_*` from `env_constants`; delete `_DEFAULT_CONFIG`/`_DEFAULT_LOGGER`/`_DEFAULT_RUNNING_UNIT_TESTS`; drop the `else: load_dotenv(.env.example)` branch so only a present `.env` is loaded.
- **Consumers** — repoint the `ENV_*` imports in `tests/tests_utils/test_config_loader.py` and `tests/tests_utils/test_project_paths.py` from `global_constants` to `env_constants`. (`test_config_loader.py` also imports `FOLDER_CONFIGURATIONS` — leave that import on `global_constants` for now; it moves in a later slice.)
- **`global_constants.py`** — remove the four `ENV_*` lines only. The remaining clusters stay until their own slices.

## Acceptance criteria

- [ ] `src/constants/env_constants.py` exists, is import-side-effect-free (imports nothing that runs `load_dotenv`), and its docstring explains why it is kept separate from `envs.py`.
- [ ] `DEFAULT_CONFIG`, `DEFAULT_LOGGER`, `DEFAULT_RUNNING_UNIT_TESTS` are defined once in `env_constants.py` and match the values documented in `.env.example`.
- [ ] `envs.py` imports `ENV_*` and `DEFAULT_*` from `env_constants`, has no `_DEFAULT_*` locals, and no longer loads `.env.example` as a fallback.
- [ ] `Envs` getter/setter signatures and return semantics are unchanged; the fallback for an unset var is the corresponding `DEFAULT_*`.
- [ ] `test_config_loader.py` and `test_project_paths.py` import `ENV_*` from `env_constants`; no `ENV_*` import from `global_constants` remains.
- [ ] `global_constants.py` no longer defines the `ENV_*` keys.
- [ ] `make all-secure` green on Python 3.11 / 3.12 / 3.13.

## Blocked by

- None - can start immediately.
