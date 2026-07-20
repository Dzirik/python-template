# `date_time_functions` idioms + tests

## Parent

[`../PRD.md`](../PRD.md) — P3 implementation (polish), Item 4 (plus the `yyyy-dd-yy` docstring
fix from Item 3). Covers user stories 4, 5, 6, 7, 8.

## What to build

Rewrite `src/utils/date_time_functions.py` to model idiomatic standard-library Python, and pin
its behavior with a new test file (the module currently has no tests).

- **f-string zero-padding.** Replace the arithmetic-and-slice padding
  (`add_zeros_in_front_and_convert_to_string`, which adds a power of ten and slices off the lead
  digit) with f-string formatting (`f"{n:02d}"` for calendar/clock fields, `f"{micro:06d}"` for
  microseconds). The helper may be retired or kept as a thin shim, but the formatting/parsing
  callers use f-strings.
- **`strptime` parsing that honors `sep`.** `convert_string_date_to_datetime` parses via
  `datetime.strptime` with a format string built from the `sep` separator, symmetric with
  `convert_datetime_to_string_date`. It must round-trip any `sep` the formatter accepts — not
  just the default `"-"` (today it hard-splits on a literal `"-"` and ignores `sep`).
- **Truthful docstrings.** State the real produced format `yyyy-mm-dd-hh-mm-ss` (with optional
  `<-micro>`), replacing the wrong `yyyy-dd-yy` claim. Keep the house type-in-text docstring
  convention.

This slice **owns all docstrings in `date_time_functions.py`** (including the `yyyy-dd-yy` fix);
the typo/docstring-sweep slice deliberately does not touch this file.

## Acceptance criteria

- [ ] Zero-padding is done with f-strings; no power-of-ten-plus-slice padding remains in the format/parse paths.
- [ ] `convert_string_date_to_datetime` uses `datetime.strptime` and honors a non-default `sep` (parse succeeds for whatever `sep` the formatter emitted).
- [ ] A `sep` other than `"-"` round-trips: `convert_string_date_to_datetime(convert_datetime_to_string_date(dt, sep=X), sep=X) == dt` (to the second).
- [ ] Docstrings state `yyyy-mm-dd-hh-mm-ss` (`<-micro>`); no `yyyy-dd-yy` remains.
- [ ] New `tests/tests_utils/test_date_time_functions.py` (parametrized, house style) asserts: single-digit fields are zero-padded; microseconds are 6 digits; `sep` honored on both sides; a format→parse round-trip to the second (and to microsecond with `add_micro=True`); the `create_datetime_id`/`create_date_id` shapes.
- [ ] `make all-secure` is green.

## Blocked by

None - can start immediately.
