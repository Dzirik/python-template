# Tests for the untested riskiest code

> **Status:** `ready-for-agent`

## Parent

[`../BRAINSTORM.md`](../BRAINSTORM.md) — P2. Report item 3. Decision C. **Wave 2** — depends
on issue 02 (viz smoke tests call `dashboard=True` to get a `go.Figure` back).

## What to build

The watchdog *decision* logic is already unit-tested (P0/P1 issue 05). Fill the remaining
0%-coverage gaps that carry real risk, highest value per effort (D8 dropped the coverage
gate, so there is no number to hit — target risk, not a percentage).

1. **`heartbeat.py`** — `tests/tests_scripts_production/test_heartbeat.py` (new): mock the
   `requests`/session object; assert a successful ping calls the URL with the 5 s timeout;
   assert a network exception is swallowed and logged (does not propagate); assert the
   monotonic-clock / session-reuse behavior. No real network.
2. **`visualisations/` smoke tests** — `tests/tests_visualisations/test_*.py` (new, one per
   plot module, ~16): construct each plot class with minimal valid input, call its plot API
   with **`dashboard=True`**, assert the return is a `go.Figure` and the expected trace count
   / basic layout. This also guards the `HIGH` rename and the `vertical_line` key fix from
   issue 02 (include a case exercising `vertical_lines_positions`).
3. **Watchdog helper gaps** — extend `tests/tests_scripts_production/test_watchdog.py`:
   `build_command`, `heartbeat_age_seconds`, `process_alive`, `resolve_ping_url`,
   `heartbeat_path` / `write_pid` (pure-ish, filesystem via `tmp_path`). Do not re-test the
   already-covered `compute_backoff_delay` / `is_crash_loop` / lock functions.

## Scope

- **OWNS:** `tests/tests_scripts_production/test_heartbeat.py` (new),
  `tests/tests_visualisations/` (new package + tests),
  additions to `tests/tests_scripts_production/test_watchdog.py`.
- **Does NOT touch:** any `src/` file (tests only), `test_checker.py`.

## Acceptance criteria

- [ ] `heartbeat.py` has tests with a mocked session (ping success, swallowed failure).
- [ ] Every `visualisations/` plot module has a smoke test asserting `go.Figure` + traces;
      a `vertical_lines_positions` case passes without `KeyError`.
- [ ] The remaining watchdog helpers are unit-tested; `make all` green.

## Blocked by

- **Issue 02** (real `dashboard` return). Wave 2.
