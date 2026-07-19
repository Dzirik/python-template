# Move `FOLDER_CONFIGURATIONS` → `project_paths.py`

> **Status:** `ready-for-agent`

## Parent

[`specs/006_resolve_global_and_venv_constants/BRAINSTORM.md`](../BRAINSTORM.md) — *Resolve global & venv constants*

## What to build

Co-locate the `configurations` folder name with its true owner. Per the project glossary, **Project Paths** exposes the canonical locations (`data`, `logs`, `reports`, `configurations`), and `project_paths.py` is already the only real consumer of `FOLDER_CONFIGURATIONS`. This slice moves the constant out of the catch-all into `project_paths.py` as a module constant.

End-to-end behaviour after this slice: `project_paths.py` defines and uses `FOLDER_CONFIGURATIONS` locally; `test_config_loader.py` imports it from `project_paths`; the `configurations` property resolves the same path as before.

Note on the side-effect trade-off (already decided): `FOLDER_CONFIGURATIONS` belongs with Project Paths by domain even though importing it from `project_paths.py` triggers that module's `Envs` import (and thus the import-time `load_dotenv`). It is deliberately **not** placed in the side-effect-free `env_constants.py` — that module is for env-var keys/defaults, not path vocabulary.

Scope:

- **`project_paths.py`** — define `FOLDER_CONFIGURATIONS = "configurations"` as a module constant (house-style comment), replacing the import from `global_constants`. The `configurations` property continues to use it.
- **`test_config_loader.py`** — repoint the `FOLDER_CONFIGURATIONS` import to `from src.utils.project_paths import FOLDER_CONFIGURATIONS`.
- **`global_constants.py`** — remove the `FOLDER_CONFIGURATIONS` line.

## Acceptance criteria

- [ ] `project_paths.py` defines `FOLDER_CONFIGURATIONS` locally and no longer imports it from `global_constants`; the `configurations` property is unchanged in behaviour.
- [ ] `test_config_loader.py` imports `FOLDER_CONFIGURATIONS` from `src.utils.project_paths`.
- [ ] `global_constants.py` no longer defines `FOLDER_CONFIGURATIONS`.
- [ ] No import of `FOLDER_CONFIGURATIONS` from `global_constants` remains anywhere.
- [ ] `make all-secure` green on Python 3.11 / 3.12 / 3.13.

## Blocked by

- None - can start immediately.
