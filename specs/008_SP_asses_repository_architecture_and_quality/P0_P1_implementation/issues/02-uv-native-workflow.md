# uv-native workflow modernization

> **Status:** `ready-for-agent`

## Parent

[`../BRAINSTORM.md`](../BRAINSTORM.md) — P0+P1 implementation. Report items: P0#4 (add-lib
pruning), P1 D4 (uv-native modernization). Decision D in the BRAINSTORM.

## What to build

Move the build/dependency workflow fully uv-native so the stale-venv and false-green
failure classes disappear, and so `make add-lib` stops uninstalling the dev toolchain.

1. **`pyproject.toml`**
   - Add `[tool.uv]` with `package = false` and `default-groups = ["dev", "windows"]`.
   - Convert `[project.optional-dependencies].dev` and `.windows` into PEP-735
     `[dependency-groups]` (`dev`, `windows`); keep the `sys_platform == 'win32'` markers on
     the Windows deps. Runtime libs stay in `[project.dependencies]`.
   - **Drop `gitpython`** from `[project.dependencies]` (its only importers were removed in
     issue 04) and re-lock.
   - Delete the dead `[tool.mypy]` block (mypy reads `mypy.ini`).
2. **`mypy.ini`** — add `strict = True` so strictness lives in the config file, not only on
   the CLI (keeps direct/IDE runs as strong as the gate). Keep the global
   `ignore_missing_imports` (per-module overrides are deferred).
3. **`Makefile`**
   - Replace every `uv run --no-project` with plain `uv run` (auto-sync; safe under
     `package = false`).
   - Collapse the five sync targets (`sync`, `sync-deps`, `sync-install`, `sync-install-dev`,
     `lock`) to **`sync` (`uv sync`) + `lock` (`uv lock`)**.
   - Rewrite `add-lib`/`remove-lib`/`-win` onto groups: `uv add <lib>` (runtime),
     `uv add --group dev <lib>`, `uv add --group windows <lib>`; drop the pruning
     `uv sync --extra windows`.
   - Merge the two `-linux` pairs (`create-venv`/`create-venv-linux`,
     `install-hooks`/`install-hooks-linux`) into single OS-detecting targets
     (`ifeq ($(OS),Windows_NT)` for the activation-hint echo and the hook installer).
   - Fix `mypy-f`: run from the **repo root** (drop `cd src`) with the same invocation as the
     `mypy` gate, so `src.*` imports resolve instead of collapsing to `Any`.
   - **Integrate issue 01's interface:** in `create-venv`, generate the minimal commented
     `configurations/python_personal.toml` template (per ADR 0006) instead of copying
     `python_repo.toml`.
   - **Integrate issue 07's interface:** `create-venv` copies `marimo/template/…` →
     `marimo/raw/playground_marimo.py`; the `marimo-convert` recipe writes via
     `marimo convert IN -o OUT` (no stdout dump).
4. **`.PHONY`** — extend to the real target set (currently only `help`).

## Scope

- **OWNS:** `pyproject.toml`, `uv.lock`, `Makefile`, `mypy.ini`,
  `scripts/install-hooks.ps1`, `scripts/install-hooks.sh`.
- **Coordinates with:** issue 01 (personal-template content), issue 07 (playground copy,
  `marimo-convert -o`) — those issues specify the requirement; this issue implements it in the
  Makefile.

## Acceptance criteria

- [ ] `uv run <anything>` auto-syncs against `uv.lock`; no `--no-project` remains.
- [ ] `make add-lib library=<x>` adds the dep **without** uninstalling pytest/mypy/ruff/bandit.
- [ ] `dev` and `windows` are `[dependency-groups]`; plain `uv run` installs both (Windows deps
      no-op on Linux via marker).
- [ ] `make mypy-f` (with `make_config.mk` set) produces the same result as `make mypy` for the
      same file — no false green.
- [ ] `gitpython` is absent from `pyproject.toml` and `uv.lock`.
- [ ] The `-linux` target pairs are gone; one OS-detecting target each.
- [ ] `make all-secure` green.

## Blocked by

- **Issue 04** — GitPython imports must be removed before its dependency is dropped and the
  lock rebuilt.
