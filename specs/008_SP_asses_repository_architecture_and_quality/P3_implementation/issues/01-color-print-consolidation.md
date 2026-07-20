# Color-print consolidation

## Parent

[`../PRD.md`](../PRD.md) — P3 implementation (polish), Item 1. Covers user stories 1, 2, 3.

## What to build

Make termcolor / `print_in_color` the single console-coloring mechanism in the repo.
`print_success.py` stays as the Makefile-facing `success`/`error` CLI — its argv dispatch and
its `print_success`/`print_error` public functions are unchanged in signature and in what a
user sees — but the two functions stop emitting raw ANSI escape codes and instead delegate to
`print_in_color` (from `helper_functions.py`): `print_success` prints green + bold,
`print_error` prints red + bold. termcolor is available because the Makefile recipes invoke the
script under `uv run`.

`print_in_color` itself is reused as-is (no behavior change). No `Makefile` recipe changes —
every recipe that shells out to `print_success.py success "..."` keeps working verbatim.

## Acceptance criteria

- [ ] `print_success` and `print_error` produce their coloring via `print_in_color` (termcolor); no raw ANSI escape sequences remain in `print_success.py`.
- [ ] The `success`/`error` argv CLI and both function signatures are unchanged; every existing `Makefile` invocation still works with no `Makefile` edit.
- [ ] `print_success` renders green+bold and `print_error` red+bold (visually equivalent to today).
- [ ] New `tests/tests_utils/test_print_success.py` asserts, via `capsys`, that each function prints the given message text (modelled on `test_helper_functions.py`'s `print_in_color` tests).
- [ ] `make all-secure` is green.

## Blocked by

None - can start immediately.
