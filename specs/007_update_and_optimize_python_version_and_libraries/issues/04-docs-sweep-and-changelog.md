# Documentation truthfulness sweep + CHANGELOG for the 3.13–3.14 modernization

> **Status:** `ready-for-agent` · **AFK**

## Parent

[`specs/007_update_and_optimize_python_version_and_libraries/PRD.md`](../PRD.md) — *Update & optimize Python version and libraries*

## What to build

The documentation-truthfulness sweep for this spec (matching the standalone doc-sweep issue
in specs 002/003/004). Once the platform + dependency change has landed, the prose docs still
describe the old `3.11/3.12/3.13` baseline and the "Python 3.12" setup story; this slice
brings every hardcoded version reference and dependency note in line with the new state, and
records the change in the CHANGELOG.

End-to-end behaviour after this slice: a repo-wide read of `README.md`,
`docs/PROJECT_VISION.md`, and `CLAUDE.md` finds no stale `3.11`/`3.12` version reference or
"Python 3.12" setup text; the CI-matrix descriptions say `3.13 / 3.14`; the dependency notes
reflect that `marimo[recommended]` is kept and the transitive Jupyter pins were trimmed; and
`docs/CHANGELOG.md` carries an entry at the usual cadence.

Scope:

- **`README.md`** — update any hardcoded `3.11`/`3.12` mentions, the setup text that says
  Python 3.12, the CI-matrix description (→ `3.13 / 3.14`), and any dependency notes that
  reference the trimmed transitive packages or imply marimo is anything other than
  `[recommended]`.
- **`docs/PROJECT_VISION.md`** — align supported-Python and CI-matrix statements with the new
  `3.13–3.14` range.
- **`CLAUDE.md`** — update the "matrix: Python 3.11/3.12/3.13 on ubuntu" line to `3.13 / 3.14`,
  the `create-venv` "installs Python 3.12" description to 3.13, and any other version-pinned
  prose in the Tooling/Architecture sections.
- **`docs/CHANGELOG.md`** — add an entry summarising the modernization (3.13–3.14 range,
  local default 3.13, latest-floor dependency refresh, transitive trim, `marimo[recommended]`
  kept, pip-audit rebuild), referencing
  [ADR 0005](../../../docs/adr/0005-python-version-support-strategy.md).
- **Do not** recreate ADR 0005 (already written) and **do not** touch `CONTEXT.md` (no domain
  term is added or altered by this change).
- **Grep-audit** — confirm no `3.11`/`3.12` version reference survives in the swept docs.

## Acceptance criteria

- [ ] `README.md`, `docs/PROJECT_VISION.md`, and `CLAUDE.md` contain no stale `3.11`/`3.12` version reference or "Python 3.12" setup text; CI-matrix descriptions read `3.13 / 3.14`.
- [ ] Dependency notes in the docs reflect the kept `marimo[recommended]` suite and the trimmed transitive Jupyter pins.
- [ ] `docs/CHANGELOG.md` has a new entry for the modernization that references ADR 0005, matching the existing changelog cadence.
- [ ] `CONTEXT.md` is unchanged; ADR 0005 is not duplicated.
- [ ] A repo-wide search finds no `3.11`/`3.12` reference in the swept documentation files.
- [ ] `make all-secure` green in CI on **both Python 3.13 and 3.14**.

## Blocked by

- [`01-python-modernization-and-relock.md`](./01-python-modernization-and-relock.md)
