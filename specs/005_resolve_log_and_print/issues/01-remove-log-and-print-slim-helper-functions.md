# Remove `log_and_print`, slim `helper_functions.py`, and test `print_in_color`

> **Status:** `ready-for-agent`

## Parent

[`specs/005_resolve_log_and_print/PRD.md`](../PRD.md) — *Consolidate colored console echo into the `Logger`*

## What to build

The dependency-inversion half of the consolidation, shipped first because it clears an import cycle that would otherwise block the Logger change. Today `src/utils/helper_functions.py` imports `Logger` purely to implement `log_and_print`; the moment `logger.py` starts importing `print_in_color` from `helper_functions.py` (the next slice), that becomes a circular import. This slice removes the offending import by deleting the dead `log_and_print` function, leaving `helper_functions.py` depending only on `termcolor`.

End-to-end behaviour after this slice: `log_and_print` no longer exists anywhere; nothing references it (it was already dead — only `# log_and_print` comments above bare `print()` calls in the two `run_cmd_status_print_*.py` scripts mentioned it). `print_in_color` survives unchanged as a standalone, log-free public utility and is now covered by tests. `helper_functions.py` no longer imports `Logger` or `datetime`. `make all-secure` stays green.

Scope:

- **Delete `log_and_print`** from `helper_functions.py`, including its `log_only` parameter (the "log only" case moves to "omit the color" on the Logger in the next slice — there is nothing to migrate here).
- **Slim the imports** — remove `from src.utils.logger import Logger` and `from datetime import datetime` (both were used only by `log_and_print`). Keep `from termcolor import colored`, used by `print_in_color`.
- **Fix stale docstrings** — the module docstring and `print_in_color`'s docstring reference a non-existent `src/utils/color_console_print.py`. Correct these to point at `termcolor` / this module, consistent with spec 004's documentation truthfulness sweep. `print_in_color`'s behaviour and signature are otherwise unchanged.
- **Clean the dangling comments** — in `src/scripts_production/run_cmd_status_print_01.py` and `run_cmd_status_print_02.py`, the `# log_and_print` comments now reference a deleted function; remove or correct them. The bare `print()` calls beneath them are left as-is (rewiring those scripts is explicitly out of scope in the PRD).
- **New test file `tests/tests_utils/test_helper_functions.py`** — unit-test `print_in_color` via pytest's `capsys`: it prints the message; it falls back to a plain (uncolored) print when handed a bad/unsupported color rather than raising; and it plain-prints when `color is None`. Follow the house test style and the `tests/tests_utils/` layout mirroring `src/utils/`.

## Acceptance criteria

- [ ] `log_and_print` is removed from `helper_functions.py`; no reference to it remains anywhere in the repo (including the `run_cmd_status_print_*.py` comments).
- [ ] `helper_functions.py` no longer imports `Logger` or `datetime`; it imports only `termcolor` (plus stdlib as needed). No import cycle exists.
- [ ] `print_in_color` is unchanged in signature and behaviour; its docstring and the module docstring no longer reference the non-existent `color_console_print.py`.
- [ ] `tests/tests_utils/test_helper_functions.py` exists and covers `print_in_color`: message is printed; bad color degrades to plain print without raising; `color is None` plain-prints.
- [ ] The bare `print()` calls in `run_cmd_status_print_*.py` are left functionally unchanged (only the stale comment is cleaned up).
- [ ] `make all-secure` green on Python 3.11 / 3.12 / 3.13.

## Blocked by

- None - can start immediately.
