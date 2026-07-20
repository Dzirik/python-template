# Notebook template defect fixes

> **Status:** `ready-for-agent`

## Parent

[`../BRAINSTORM.md`](../BRAINSTORM.md) — P2. Report item 10 (**defects only — no lint
gate**, Decision J) + item 5 (the 1 pylint pragma in `notebook_support_functions.py`).

## What to build

Fix the defects in the committed *teaching* notebooks + their support module. Do **not** add
a lint gate; `make all` still runs on `src tests` only.

1. **`src/utils/notebook_support_functions.py`**: `create_button()` injects jQuery, which is
   dead in Notebook 7 (the environment the module claims to support). **Delete it** (and any
   now-unused jQuery/HTML helpers), or reimplement using an `ipywidgets` button if a real
   consumer needs it — deletion preferred unless a template actually calls it. Remove the 1
   `# pylint:` pragma in this file.
2. **Broken navigation anchors**: replace `<a name="...">` anchors (declared broken in
   Notebook 7 by `docs/meta/JUPYTER_ECOSYSTEM.md`) with heading-based Markdown anchors in the
   committed templates (`notebooks/template/*.py`).
3. **Anaconda-era error log**: remove the stale Anaconda-era error-handling/log block from the
   templates.
4. **Dedupe `template_notebook_repo.py`**: remove the duplicated imports and the double
   `start_timer()` call; fix the bare `except:` to a specific exception.
5. Sanity-check the other committed templates (`template_notebook_final.py`,
   `template_parameterized_execution_notebook.py`) for the same anchor/`except:`/dup issues
   and fix in place.

Note: the git-ignored `notebooks/raw/playground_*.py` are generated copies — do not edit
them; fixing the templates is enough.

## Scope

- **OWNS:** `notebooks/template/*.py`, `src/utils/notebook_support_functions.py`.
- **Does NOT touch:** the executioners (issue 07), `make jupyter` / `pyproject`
  (issue 09), documentation notebooks under `notebooks/documentation/` unless they call a
  deleted helper (then update the call).

## Acceptance criteria

- [ ] No `<a name=` anchors or bare `except:` remain in `notebooks/template/*.py`.
- [ ] `create_button()`'s dead jQuery is removed (or replaced with a working widget); the
      file's pylint pragma is gone.
- [ ] `template_notebook_repo.py` has no duplicated imports / double `start_timer()`.
- [ ] `make all` green (notebooks remain outside the gate; nothing new fails).

## Blocked by

- None — Wave 1.
