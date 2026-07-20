# Manifest & docs sweep

> **Status:** `ready-for-agent`

## Parent

[`../BRAINSTORM.md`](../BRAINSTORM.md) — P2. Report items 6 (doctest collection), 7 (drop
`fail_under` + `cover_logger` rework), 5 (CLAUDE.md pylint guidance + residual pragmas),
2 (`make jupyter` guard). Decisions F, G, E. **Wave 3** — single owner of the manifest /
Makefile / CLAUDE.md, run after all code waves so it describes post-change reality.

## What to build

1. **Doctest collection** (`pyproject.toml`): add `--doctest-glob="*.txt"` to `addopts` so
   `make test` / CI collect `tests/tests_transformations/test_datetime_one_hot_transformer.txt`
   (currently only `make test-f` runs it). Do **not** add `--doctest-modules`. Confirm the
   doctest passes under the merged run.
2. **Drop the coverage gate** (`pyproject.toml`): remove `fail_under = 25` (D8). `make cover`
   stays as an on-demand report. (The dead CI coverage-artifact step was already removed by
   issue 03 — nothing to do there.)
3. **`cover_logger.py` rework** (`src/utils/cover_logger.py`): replace the BeautifulSoup HTML
   scrape with `coverage json` + stdlib `json` parsing; **remove the `input()` prompt and the
   comment feature entirely** so `make cover` runs non-interactively start to finish. Then
   **drop the `bs4` / `beautifulsoup4` dependency** from `pyproject.toml` and re-lock
   (`make lock`). (`bs4` is used only by this file — verify with a grep before removing.)
4. **`make jupyter` guard** (`Makefile`): before launching Jupyter, idempotently ensure
   `.venv/etc/jupyter/jupyter_server_config.py` exists with
   `c.ServerApp.contents_manager_class = "jupytext.TextFileContentsManager"` (mkdir -p +
   write if absent). OS-detecting like the other targets; survives any `.venv` rebuild.
5. **Residual pylint pragmas**: remove the 2 `# pylint:` pragmas in
   `src/utils/helper_functions.py` (no other issue owns this file).
6. **CLAUDE.md sweep**:
   - Remove the pylint-pragma guidance (pylint never runs; mypy + ruff are the gates).
   - Fix the doctest claim to match reality now that `--doctest-glob` is set (the `.txt` is
     run by `make test`/CI).
   - Update `MetaClass` → `MonitoredBase` / `meta_class.py` → `monitored_base.py` references
     (rename landed in issue 01).
   - Update the executioner description if it names the `_linux` variant (merged in issue 07).

## Scope

- **OWNS:** `pyproject.toml`, `uv.lock`, `Makefile`, `src/utils/cover_logger.py`,
  `src/utils/helper_functions.py`, `CLAUDE.md`.
- **Does NOT touch:** any other `src/` file, `.github/workflows/ci.yml`.

## Acceptance criteria

- [ ] `make test` collects and passes the `.txt` doctest; `fail_under` gone from pyproject.
- [ ] `make cover` runs non-interactively via `coverage json` (no `input()`, no `bs4`);
      `beautifulsoup4` removed from deps and `uv.lock` re-locked.
- [ ] `make jupyter` recreates `jupyter_server_config.py` when missing.
- [ ] No `# pylint:` pragma remains anywhere in `src/`; CLAUDE.md pylint/doctest/`MonitoredBase`
      references are accurate.
- [ ] `make all-secure` green.

## Blocked by

- **All code waves** (01–08): the sweep describes/removes their post-change reality
  (`MonitoredBase` rename, executioner merge, doctest now collected, `bs4` no longer used).
