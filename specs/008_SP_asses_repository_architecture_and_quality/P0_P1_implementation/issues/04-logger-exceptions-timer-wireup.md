# Logger / exceptions / timer wire-up + drop GitPython

> **Status:** `ready-for-agent`

## Parent

[`../BRAINSTORM.md`](../BRAINSTORM.md) — P0+P1 implementation. Report items: P0#5 (timer fix),
P1 logger/exceptions wire-up phase 1. Decisions G and H.

## What to build

Fix the lossy, heavy, deprecated bits of the shared logging/exception path so the mandated
error pathway is trustworthy before it is widely consumed, and shrink the import chain
(`exception import → Logger → Timer → pandas`/GitPython).

1. **`timer.py`**
   - `_as_date` → `datetime.fromtimestamp(timestamp)` (**local** wall-clock; removes the
     deprecated `utcfromtimestamp` and unmixes the Timer-UTC / logger-echo-local mismatch).
   - **Drop the `DataFrame`** from `get_data()`: return the three lists only; remove
     `from pandas import DataFrame`. Update the `__main__` demo.
2. **`helper_functions.py`** — add `get_git_branch() -> str`: read the active branch from
   `.git/HEAD` using stdlib only (parse `ref: refs/heads/<branch>`; detached HEAD or any error
   → `"unknown"`). No `git` import, no subprocess, no git binary.
3. **`logger.py`**
   - Replace the `git.Repo(...)` branch read with `get_git_branch()`; drop `import git`. The
     init line logs the real branch or `"unknown"` (no more literal `"ERROR"`).
   - Add `exception(self, message, ...) -> None` mirroring `error()` but logging with
     `exc_info=True` (delegates to `self._logger.exception`), plus the same optional colored
     echo.
   - Type the logger: `_logger: logging.Logger` and `get(self) -> logging.Logger`.
   - Fix the local typos: `"branche"` → `"branch"`, `"does not exit"` → `"does not exist"`,
     `"timerer"` → `"timer"`.
4. **`cover_logger.py`** — replace its `git.Repo(...)` read with `get_git_branch()`; drop
   `import git`. (This is what lets issue 02 remove the `gitpython` dependency.)
5. **`exception_executioner.py`**
   - `log_and_raise(...) -> NoReturn`.
   - Log with a real traceback: `raise` the exception inside a `try`, catch it, call
     `Logger().exception(exc.get_description())`, then re-raise — so the log carries a
     traceback.
   - **Remove** the `ENV_RUNNING_UNIT_TESTS` branch (test-harness awareness in production
     code); the conftest already forces the console logger, so logging during tests is safe.
   - Keep the `# type: ignore[call-arg]` only if still required after signature review.
6. **Tests** — `test_timer.py` (drop DataFrame assertions, assert local-time formatting is
   non-deprecated); `test_logger.py` (assert `get()` returns a `logging.Logger`; exercise
   `exception()`); add direct tests for `ExceptionExecutioner.log_and_raise` (raises the right
   type, is `NoReturn`, logs with traceback) — the mandated pathway currently has zero tests;
   a `get_git_branch()` test (mock a `.git/HEAD`, assert branch + `"unknown"` fallback).

Do **not** edit `pyproject.toml`/`uv.lock` here — issue 02 drops the now-unused `gitpython`
dependency and re-locks.

## Scope

- **OWNS:** `src/utils/timer.py`, `src/utils/logger.py`, `src/utils/cover_logger.py`,
  `src/utils/helper_functions.py`, `src/exceptions/exception_executioner.py`,
  `tests/tests_utils/test_timer.py`, `tests/tests_utils/test_logger.py`,
  `tests/tests_exceptions/test_exceptions.py` (+ new ExceptionExecutioner tests).

## Acceptance criteria

- [ ] No `import git` anywhere in `src/`; branch is read from `.git/HEAD` with an `"unknown"`
      fallback.
- [ ] `timer.py` imports no pandas; `get_data()` returns three lists; timestamps use local time
      with no deprecation warning.
- [ ] `Logger.exception()` exists and logs a traceback; `get()` is typed `-> logging.Logger`.
- [ ] `ExceptionExecutioner.log_and_raise` is `-> NoReturn`, logs with a traceback via
      `exception()`, has no `ENV_RUNNING_UNIT_TESTS` branch, and has direct tests.
- [ ] `make all` green (note: `gitpython` still declared until issue 02 removes it — that is
      expected at this issue's boundary).

## Blocked by

- None — Wave 1. (Issue 02 depends on this.)
