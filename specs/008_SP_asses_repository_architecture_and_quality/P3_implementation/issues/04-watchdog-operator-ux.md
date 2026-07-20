# Watchdog operator UX

## Parent

[`../PRD.md`](../PRD.md) — P3 implementation (polish), Item 5. Covers user stories 9, 10, 11,
12, 13, 14, 15.

## What to build

Make the watchdog operable and tunable without editing source, and close three operational
rough edges. Four coordinated changes, all owned by this slice (it owns the watchdog config
trio together — the NamedTuple, the JSON schema, and the drift test):

- **Supervision timings → optional `[supervision]` TOML table.** A new `SupervisionTimingData`
  NamedTuple carries the eight tunables, each defaulting to today's `watchdog.py` module
  constant. `WatchdogConfigData` gains `supervision: SupervisionTimingData = SupervisionTimingData()`,
  so a config that omits the table gets the current defaults (zero change for existing configs).
  The watchdog reads timings from config instead of module globals. The hand-authored JSON
  schema gains the table, and the P2 schema drift-detection test extends to it. Strict typedload
  (`failonextra=True`) is preserved. Exact shape (from the grill):

  ```toml
  [supervision]              # optional; omitted -> defaults below
  check_interval = 30.0
  startup_grace_period = 5.0
  stop_grace_period = 5.0
  watchdog_healthcheck_interval = 30.0
  backoff_base = 2.0
  backoff_cap = 300.0
  crash_loop_count = 5
  crash_loop_window = 300.0
  ```

- **`.bat` PID auto-read.** The stop `.bat` tools read the watchdog PID from
  `heartbeats_{config_name}/watchdog.pid` and use it for `taskkill`, prompting only if the file
  is missing. The task name is parametrized consistently across the general and per-config tools.
- **Cap the WMI respawn log.** Before the checker spawns the watchdog via WMI, cap/rotate
  `watchdog_{config}_wmi.log` so the appended redirect can't grow unbounded. Extract the cap
  logic into a small, unit-testable helper.
- **Timeout on the checker force-kill.** Add a `timeout=` to the `taskkill` `subprocess.run` in
  the checker's kill path so a hung kill can't block the ephemeral checker.

Supervision *semantics* (ADR 0007) are unchanged — the defaults reproduce today's behavior
exactly. This slice does not revisit the graceful-stop kill contract (that landed in P0/P1).

## Acceptance criteria

- [ ] `SupervisionTimingData` exists with the eight fields above, each defaulting to today's constant; `WatchdogConfigData.supervision` defaults to `SupervisionTimingData()`.
- [ ] A watchdog TOML that omits `[supervision]` loads the documented defaults; one that sets a value overrides only that value; the watchdog uses config values, not module globals.
- [ ] The JSON schema includes `[supervision]`, and the schema drift-detection test passes over the new fields (schema ↔ NamedTuple parity).
- [ ] A test asserts both the omit-→-defaults and the set-→-override behaviors for `[supervision]`.
- [ ] The stop `.bat` tools read the PID from `heartbeats_{config_name}/watchdog.pid` (prompt only on missing file) and use a consistent parametrized task name.
- [ ] The WMI respawn log is size-capped via an extracted helper; `test_checker.py` unit-tests it (over-cap truncates/rotates, under-cap untouched, missing file is a no-op).
- [ ] The checker's `taskkill` `subprocess.run` passes a `timeout=`.
- [ ] `make all-secure` is green.

## Blocked by

None - can start immediately.
