# Notebook executioner merge

> **Status:** `ready-for-agent`

## Parent

[`../BRAINSTORM.md`](../BRAINSTORM.md) — P2. Report item 2 (merge the two executioners) +
item 5 (the 1 pylint pragma in `notebooks_executioner.py`). Decision B. The
`jupyter_server_config.py` automation is **issue 09** (Makefile).

## What to build

There are two executioner classes with duplicated, *divergent* logic; the spawn /
`imap_unordered` ("Linux") variant is strictly better and works on Windows (spawn is the
Windows default). Collapse to one.

1. **Fold** the spawn / `imap_unordered` batch-execution logic and output-naming from
   `NotebookExecutionerLinux` **up into `NotebookExecutioner`** (`notebooks_executioner.py`),
   keeping the canonical class name `NotebookExecutioner`. Resolve the divergences (batching
   strategy, static-name strings, output-naming) in favor of the Linux implementation.
2. **Delete** `src/utils/notebooks_executioner_linux.py`.
3. **`src/scripts/param_notebook_execution.py`**: drop the `platform.system()` branch and the
   `NotebookExecutionerLinux` import; always use the merged `NotebookExecutioner`.
4. Remove the 1 `# pylint:` pragma in `notebooks_executioner.py`.
5. **Verify on Windows**: run `param_notebook_execution` (or its `__main__` demo) so the
   spawn/`imap_unordered` path is confirmed working on the Windows-first target — this is the
   one behavioral change (Windows previously used the other class).
6. **Tests**: add/adjust `tests/tests_utils/test_notebooks_executioner.py` — at minimum
   construct the merged class and exercise the output-name resolution and command building
   (pure-ish helpers), since these were the divergent bits. (Heavy papermill execution can
   stay out of the unit suite.)

## Scope

- **OWNS:** `src/utils/notebooks_executioner.py`,
  `src/utils/notebooks_executioner_linux.py` (deleted),
  `src/scripts/param_notebook_execution.py`,
  `tests/tests_utils/test_notebooks_executioner.py`.
- **Does NOT touch:** `Makefile` (`make jupyter` guard is issue 09), notebook templates
  (issue 05).

## Acceptance criteria

- [ ] One executioner class (`NotebookExecutioner`); `_linux` module deleted; no
      `platform.system()` branch in `param_notebook_execution.py`.
- [ ] The merged path is verified to run on Windows.
- [ ] The executioner's pylint pragma is gone; new/updated tests pass; `make all` green.

## Blocked by

- None — Wave 1.
