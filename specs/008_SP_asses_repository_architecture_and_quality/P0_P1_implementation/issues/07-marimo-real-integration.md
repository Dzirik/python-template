# Marimo real integration

> **Status:** `ready-for-agent`

## Parent

[`../BRAINSTORM.md`](../BRAINSTORM.md) — P0+P1 implementation. Report item: P1 D1 (Marimo real
integration). Decision K. Answers vision open-question #4 "both ecosystems, for real."

## What to build

Turn the empty Marimo shell (5 folders, only `__init__.py`; can't reach `src/`) into a working
second notebook ecosystem that wires Config/Logger/Envs, matching the Jupyter ecosystem's
py-as-source discipline.

1. **`marimo/template/` template notebook** — the integration reference:
   - A self-contained first cell that walks up from `__file__` to the `pyproject.toml`/`.git`
     marker and inserts the repo root into `sys.path` (CWD- and launcher-independent — works via
     `make marimo`, the marimo UI, or `uv run marimo`). Strictly better than the Jupyter
     template's CWD hack.
   - Then the house wiring: `Envs` → `Logger` → `ApplicationConfig`, and a minimal reactive
     example (a cell whose output updates from a UI element) to demonstrate marimo's model.
2. **`marimo/documentation/` documentation notebook** — explains marimo reactivity, the
   `src/`-import bootstrap pattern, and how the workflow differs from the jupytext-paired Jupyter
   flow (pure `.py`, no pairing).
3. **`.gitignore`** — fix the Marimo section: `apps` → `app`; drop the phantom `temporal`
   entries; list `__marimo__` cache dirs for the real folders (`app`, `documentation`, `final`,
   `raw`, `template`); keep `marimo/raw/playground_marimo.py` ignored.

**Interfaces handed to issue 02 (Makefile owner):**
- `create-venv` copies `marimo/template/<template>.py` → `marimo/raw/playground_marimo.py`
  (mirroring the Jupyter playground), git-ignored.
- The `marimo-convert` recipe writes output via `marimo convert IN -o OUT` (the current recipe
  dumps to stdout; the README example corrupts the file by piping `make` output into it).

Do **not** edit the Makefile here.

## Scope

- **OWNS:** `marimo/template/*.py` (new), `marimo/documentation/*.py` (new), `.gitignore`
  (Marimo section only).
- **Coordinates with:** issue 02 (create-venv copy, `marimo-convert -o`), issue 08 (README
  Marimo sections describe this real content).

## Acceptance criteria

- [ ] The template notebook imports and uses `ApplicationConfig`/`Logger`/`Envs` from `src/` via
      the `__file__` marker-walk bootstrap, runnable from the marimo UI without `make`.
- [ ] A documentation notebook exists explaining reactivity + the integration pattern.
- [ ] `.gitignore` Marimo section matches the real folder names; no `apps`/`temporal` phantoms.
- [ ] `make all` green (the new notebooks are `.py` under `marimo/`, outside the `src tests` gate,
      but must at least import-parse cleanly).

## Blocked by

- None — Wave 1.
