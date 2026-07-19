# Execution Playbook — Consolidate colored console echo into the `Logger`

## Summary

- Issues covered: [#01](issues/01-remove-log-and-print-slim-helper-functions.md) (remove `log_and_print`, slim `helper_functions.py`, test `print_in_color`), [#02](issues/02-add-colored-console-echo-to-logger.md) (add colored console echo to the `Logger` level methods).
- Verdict: **serial, single branch** — strict dependency chain (#02 blocked by #01), max concurrency 1. Parallelism would not help even though the two file sets are disjoint, because the ordering is forced by a runtime import cycle, not by file collision.
- Highest execution risk: the `helper_functions → Logger` import must be gone (#01) **before** `logger.py` imports `print_in_color` (#02); reversing the order produces a circular import that breaks every test.

## Waves

Because the work is serial, each "wave" is a single issue. Each is fully validated and merged before the next starts.

### Wave 1 — gate: `make all-secure`

| Issue | Agent | Owns (files/dirs) | Must not touch | Depends on frozen interface |
|---|---|---|---|---|
| [#01](issues/01-remove-log-and-print-slim-helper-functions.md) | A | `src/utils/helper_functions.py`; `tests/tests_utils/test_helper_functions.py` (new); the `# log_and_print` comment lines in `src/scripts_production/run_cmd_status_print_01.py` and `run_cmd_status_print_02.py` | `src/utils/logger.py`; `tests/tests_utils/test_logger.py`; the `print()` call bodies in the two `run_cmd_status_print_*.py` scripts | — (defines and freezes `print_in_color`) |

### Wave 2 — blocked by Wave 1 — gate: `make all-secure`

| Issue | Agent | Owns (files/dirs) | Must not touch | Depends on frozen interface |
|---|---|---|---|---|
| [#02](issues/02-add-colored-console-echo-to-logger.md) | B | `src/utils/logger.py`; `tests/tests_utils/test_logger.py` | `src/utils/helper_functions.py` (esp. the `print_in_color` signature) | frozen `print_in_color` (from #01) |

## Frozen interfaces

- `print_in_color(message, color=None, on_color=None, attrs=None) -> None` — owned by issue [#01](issues/01-remove-log-and-print-slim-helper-functions.md), frozen before Wave 2. This is the existing signature; "freeze" means #01 must leave it unchanged (only `log_and_print` is removed and docstrings corrected), so the Logger's `_echo` in #02 codes against a stable contract, including its tolerant fallback (bad color → plain print, no raise).

## Per-agent dispatch specs

### Agent A — Wave 1 — issue [#01](issues/01-remove-log-and-print-slim-helper-functions.md)

- Goal: remove the dead `log_and_print`, slim `helper_functions.py` to depend only on `termcolor`, correct the stale docstrings, clean the dangling script comments, and add tests for the surviving `print_in_color`. This clears the `helper_functions → Logger` import so Wave 2 is cycle-safe.
- Scope (OWNS): `src/utils/helper_functions.py`; new `tests/tests_utils/test_helper_functions.py`; the `# log_and_print` comment lines only, in `src/scripts_production/run_cmd_status_print_01.py` and `run_cmd_status_print_02.py`.
- Inputs: issue #01; the existing `print_in_color` implementation.
- Outputs: `log_and_print` gone (no references anywhere); `helper_functions.py` importing only `termcolor` (no `Logger`, no `datetime`); corrected docstrings (no `color_console_print.py` reference); `print_in_color` unchanged in signature/behaviour; `test_helper_functions.py` covering print / bad-color fallback / `color is None`.
- Constraints: must NOT touch `src/utils/logger.py` or `tests/tests_utils/test_logger.py`; must NOT change the `print_in_color` signature or its tolerant behaviour; must leave the `print()` call bodies in the two scripts functionally unchanged.
- Integration: merge to the feature branch — gate: `make all-secure` (Python 3.11 / 3.12 / 3.13).
- Dispatch: serial (Wave 1 of a serial chain).

### Agent B — Wave 2 — issue [#02](issues/02-add-colored-console-echo-to-logger.md)

- Goal: add optional `color`/`on_color`/`attrs` params + a private `_echo` helper to all five `Logger` level methods, reusing `print_in_color` for the colored, timestamp-prefixed console echo; add echo tests and the `__main__` demo line.
- Scope (OWNS): `src/utils/logger.py`; `tests/tests_utils/test_logger.py`.
- Inputs: issue #02; frozen `print_in_color` (from #01); the session-autouse `conftest.py` (`ENV_LOGGER=logger_console`) as the test fixture.
- Outputs: five level methods with backward-compatible optional params; `_echo` echoing only when `color is not None`, timestamp-prefixed, delegating to `print_in_color`; `datetime` + `print_in_color` imported into `logger.py` (still no `config_loader` / `application_config`); a colored-echo line in `__main__`; echo tests added to `test_logger.py` with all pre-existing tests still passing.
- Constraints: must NOT touch `src/utils/helper_functions.py`; must NOT change the `print_in_color` signature; must NOT alter the timer methods or any current logging behaviour; must keep `test_logger_module_imports_no_config_loader_or_config` passing.
- Integration: merge to the feature branch after Wave 1's gate is green — gate: `make all-secure` (Python 3.11 / 3.12 / 3.13).
- Dispatch: serial (blocked by Wave 1).

## Merge order & gates

1. **Wave 1 (#01)** → `make all-secure` green → merge.
2. **Wave 2 (#02)** starts only after #01 is merged (the import cycle must already be cleared) → `make all-secure` green → merge.
3. Final integration gate: `make all-secure` on the combined branch, 3.11 / 3.12 / 3.13.

Two small sequential merges, one issue each — no large integration event.

## Serial fallback

This *is* the serial plan. Parallel execution is unsafe here: although Agent A and Agent B own disjoint files, #02 introduces a `logger.py → helper_functions.py` import that is only cycle-free once #01 has removed the `helper_functions → Logger` import. Running them concurrently risks a window where both imports coexist and every test fails on a circular import. Implement #01, gate, then #02.
