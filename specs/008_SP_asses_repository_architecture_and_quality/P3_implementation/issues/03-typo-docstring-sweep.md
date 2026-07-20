# Typo & docstring drift sweep

## Parent

[`../PRD.md`](../PRD.md) — P3 implementation (polish), Item 3. Covers user story 24.

## What to build

A teaching-quality sweep of the enumerated typos and docstring-drift instances, keeping the
house type-in-text docstring convention (per D7). Fix at least:

- "branche" → "branch", "does not exit" → "does not exist", "timerer" → "timer" (in the
  `Logger`/`Timer` area).
- "for trades" leftover in the `helper_functions.py` module docstring (this module belongs to
  this slice for docstrings only — the color-print slice does not touch it).
- "Visualizer" stub docstrings in the `visualisations/` package.
- The two private methods that are missing docstrings.

Scope boundary: this slice does **not** touch `date_time_functions.py` (its docstrings,
including the `yyyy-dd-yy` fix, are owned by the `date_time_functions` slice), `print_success.py`
(color-print slice), or the watchdog/checker files (watchdog UX slice).

## Acceptance criteria

- [ ] "branche", "does not exit", "timerer", "for trades", and "Visualizer" stub wording are corrected wherever they appear in the owned files.
- [ ] The two private methods flagged as missing docstrings now have house-style docstrings.
- [ ] `make docstring-check` and `make all-secure` are green.
- [ ] No file owned by another P3 slice is modified.

## Blocked by

None - can start immediately.
