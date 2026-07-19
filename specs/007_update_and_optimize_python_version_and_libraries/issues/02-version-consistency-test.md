# Add a version-consistency test that forbids 3.11/3.12 and keeps the version files in sync

> **Status:** `ready-for-agent` · **AFK**

## Parent

[`specs/007_update_and_optimize_python_version_and_libraries/PRD.md`](../PRD.md) — *Update & optimize Python version and libraries*

## What to build

A durable regression guard that encodes the "no 3.11/3.12 anywhere" exclusion and the
mutual consistency of the version-bearing files as a test, so future edits cannot silently
reintroduce a dropped interpreter or let the files drift apart. CI proving green on both
interpreters shows the deps *work*, but does not by itself prove that 3.11/3.12 are *absent*
or that the declared floor, interpreter pin, and CI matrix still agree — this test closes
that gap.

End-to-end behaviour after this slice: a new pytest reads the version-bearing project files
and fails the build if `3.11` or `3.12` reappears in any of them, or if their version
settings diverge from the agreed target. It runs as part of `make test` / `make all` like
every other test and follows the house docstring, typing, and parametrized-pytest style.

Scope:

- **New test module under `tests/`**, mirroring the `src`/`tests_` layout convention (a
  project-metadata invariant test — place it alongside the existing meta/invariant tests,
  e.g. under `tests/tests_utils/`). Locate the repo root the way the codebase already does
  (`ProjectPaths().root`, as `tests/tests_utils/test_project_paths.py` does).
- **Parse and assert** across `pyproject.toml` (via stdlib `tomllib`), `.python-version`,
  and `.github/workflows/ci.yml`:
  - `3.11` and `3.12` appear **nowhere** in these files (the hard exclusion).
  - `requires-python` is `">=3.13,<3.15"`; trove classifiers are exactly `{3.13, 3.14}`.
  - `[tool.mypy] python_version == "3.13"` and `[tool.ruff] target-version == "py313"`.
  - `.python-version` is `3.13`.
  - the CI matrix `python-version` is exactly `["3.13", "3.14"]`.
- **Prior art to follow:** `test_logger_module_imports_no_config_loader_or_config`
  (`tests/tests_utils/test_logger.py`) — an architectural-invariant test that reads a source
  artifact and asserts a property — is the direct model. Keep the assertions about *external
  contract* (which interpreters the template supports), not internal wiring, and do **not**
  invoke `uv lock`/`uv sync` (slow, network-bound; that behaviour is owned by CI).

## Acceptance criteria

- [ ] A new pytest reads `pyproject.toml` (via `tomllib`), `.python-version`, and `ci.yml` and asserts `3.11`/`3.12` are absent from all three.
- [ ] The test asserts `requires-python == ">=3.13,<3.15"`, classifiers `== {3.13, 3.14}`, mypy `python_version == "3.13"`, ruff `target-version == "py313"`, `.python-version == 3.13`, and CI matrix `== ["3.13", "3.14"]`.
- [ ] The test locates project files via `ProjectPaths().root` (no CWD assumptions) and does not run `uv`.
- [ ] The test follows the house docstring (reST/Sphinx), full typing (mypy `--strict`), and parametrized-pytest conventions, and passes `make all`.
- [ ] Deliberately reintroducing a `3.12` reference in any of the three files makes the test fail.
- [ ] `make all-secure` green in CI on **both Python 3.13 and 3.14**.

## Blocked by

- [`01-python-modernization-and-relock.md`](./01-python-modernization-and-relock.md)
