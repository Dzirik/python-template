# Delete `global_constants.py`; doc & comment cleanup

> **Status:** `ready-for-agent`

## Parent

[`specs/006_resolve_global_and_venv_constants/BRAINSTORM.md`](../BRAINSTORM.md) — *Resolve global & venv constants*

## What to build

The sealing slice. Once every cluster has moved to its owner (slices 01, 03, 04, 05, 06), `global_constants.py` is empty and can be deleted, and the remaining documentation drift is cleaned up so no reference to the old module survives.

End-to-end behaviour after this slice: `src/constants/global_constants.py` no longer exists; the `src/constants/` package survives holding only `env_constants.py` (plus `__init__.py`); a repo-wide search finds no `global_constants` reference in `src/` or `tests/`; the docs describe the new layout.

Scope:

- **Delete `src/constants/global_constants.py`.** Confirm it holds no remaining definitions before deleting (all clusters moved by the blocking slices). Keep `src/constants/__init__.py`.
- **`.env.example` cleanup** — fix the stale "without .conf extension" comments for both `ENV_CONFIG` and `ENV_LOGGER` → ".toml" (profiles are TOML now per ADR 0003/0004). Confirm the documented default values still match the `DEFAULT_*` constants in `env_constants.py`.
- **`README.md` file-tree section** (~L250-255) — drop the `global_constants.py` entry; add `env_constants.py` with an accurate one-liner (env-var name keys + canonical defaults); add entries for the new `src/visualisations/colors.py` and `src/transformations/transformer_methods.py` under their respective folders.
- **Notebook comments** — delete the `# from src.global_constants import *  # Remember to import only the constants in use` line in each of `notebooks/template/*.py`, `notebooks/documentation/*.py`, and `notebooks/raw/playground_notebook.py`. These already point at a dead path and have no single successor; delete rather than repoint.
- **Leave `docs/notebooks_freezes/*.html` untouched** — frozen historical output snapshots; knowingly stale.
- **Grep-audit** — verify no `global_constants` reference remains in `src/` or `tests/`.

## Acceptance criteria

- [ ] `src/constants/global_constants.py` is deleted; `src/constants/` contains only `env_constants.py` and `__init__.py`.
- [ ] A repo-wide search finds no `global_constants` reference in `src/` or `tests/`.
- [ ] `.env.example` comments for `ENV_CONFIG` and `ENV_LOGGER` say ".toml", not ".conf"; documented defaults match `env_constants.DEFAULT_*`.
- [ ] `README.md` file tree reflects the new layout: no `global_constants.py`; `env_constants.py`, `visualisations/colors.py`, and `transformations/transformer_methods.py` present and accurately described.
- [ ] The dead `# from src.global_constants import *` comment lines are removed from all five notebook `.py` files.
- [ ] `make all-secure` green on Python 3.11 / 3.12 / 3.13.

## Blocked by

- [`01-env-constants-single-source-of-truth.md`](./01-env-constants-single-source-of-truth.md)
- [`03-move-colors-to-visualisations.md`](./03-move-colors-to-visualisations.md)
- [`04-move-transformer-method-ids.md`](./04-move-transformer-method-ids.md)
- [`05-move-folder-configurations-to-project-paths.md`](./05-move-folder-configurations-to-project-paths.md)
- [`06-move-special-logger-file-name-to-logger.md`](./06-move-special-logger-file-name-to-logger.md)
