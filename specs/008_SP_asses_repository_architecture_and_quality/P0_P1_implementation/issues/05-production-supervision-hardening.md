# Production supervision hardening

> **Status:** `ready-for-agent`

## Parent

[`../BRAINSTORM.md`](../BRAINSTORM.md) — P0+P1 implementation. Realises **ADR 0007**
([`docs/adr/0007-watchdog-supervision-semantics.md`](../../../../docs/adr/0007-watchdog-supervision-semantics.md)).
Report items: P0#6 (`test_checker` empty test), P1 watchdog hardening (§3.6). Decision I.

## What to build

Close the four trust gaps between "works for demos" and "trust with real workers," and fix the
permanently-green no-op test. Write the new decision logic as **pure functions** with unit
tests (the production centerpiece currently has zero tests).

1. **Restart backoff + crash-loop (per-worker), `watchdog.py`**
   - Pure `compute_backoff_delay(consecutive_failures, base, cap) -> float` =
     `min(base * 2**consecutive_failures, cap)`.
   - Pure `is_crash_loop(restart_times: list[float], now: float, n: int, window: float) -> bool`.
   - Track per-worker consecutive failures + restart timestamps; apply the backoff before each
     restart. On crash-loop: `Logger().critical(...)` and stop pinging that worker's healthcheck
     (so healthchecks.io alerts) but **keep retrying at the capped interval** — never permanently
     give up. Other workers unaffected.
   - New tunables as named module constants beside `CHECK_INTERVAL` (e.g. `BACKOFF_BASE`,
     `BACKOFF_CAP`, `CRASH_LOOP_COUNT`, `CRASH_LOOP_WINDOW`). Moving these to the watchdog TOML
     is deferred.
2. **Single-instance lock, `watchdog.py`**
   - `acquire_single_instance_lock(config_name) -> handle`: exclusive non-blocking lock on a
     per-config lockfile (`msvcrt.locking(LK_NBLCK)` on Windows, `fcntl.flock(LOCK_EX|LOCK_NB)`
     on POSIX), held for process lifetime. If already held → log + `sys.exit(0)`. Acquire in
     `__main__` before starting workers.
3. **Real graceful stop, `watchdog.py` + worker examples**
   - Start workers with `creationflags=CREATE_NEW_PROCESS_GROUP` on Windows.
   - `stop_worker`: send `CTRL_BREAK_EVENT` to the group (`os.kill(pid, signal.CTRL_BREAK_EVENT)`
     on Windows / `SIGTERM` on POSIX), wait the grace window, then `process.kill()` fallback.
   - `run_cmd_status_print_01.py` and `run_cmd_status_print_02.py`: install a
     `SIGBREAK` (Windows) / `SIGTERM` (POSIX) handler that flushes/checkpoints and exits cleanly
     — the reference implementation of the stop contract.
4. **Fail-safe `is_process_alive`, `checker.py`** — any exception (incl. a tasklist timeout) is
   treated as **alive**, not dead, so the checker never `taskkill /F`s a healthy watchdog tree on
   a transient error.
5. **`.hb` on restart, `watchdog.py`** — when restarting a frozen worker, delete (or touch to
   now) its `.hb` so a slow-starting restart is not instantly re-flagged frozen.
6. **`test_checker.py`** — give `test_empty_file` its body (empty `.pid` → `read_pid` returns
   `None`); remove the misplaced assertions currently stranded at the end of
   `test_permission_error_scenario`. Add a fail-safe `is_process_alive` test.
7. **`test_watchdog.py` (new)** — unit tests for `compute_backoff_delay`, `is_crash_loop`, and
   the single-instance lock (second acquire fails).
8. **Code-local staleness** — fix the `.conf` references in `watchdog.py --help` text and
   `WatchdogConfig` docstrings while here (the prose docs are issue 08). Flip **ADR 0007** to
   `accepted` when green.

Uses `Logger().get()` / `Logger().critical()` — compatible with issue 04's changes in either
order; no hard dependency.

## Scope

- **OWNS:** `src/scripts_production/watchdog.py`, `src/scripts_production/checker.py`,
  `src/scripts_production/run_cmd_status_print_01.py`,
  `src/scripts_production/run_cmd_status_print_02.py`,
  `src/configurations/watchdog_config.py` (docstring only),
  `tests/tests_scripts_production/test_checker.py`,
  `tests/tests_scripts_production/test_watchdog.py` (new),
  `docs/adr/0007-watchdog-supervision-semantics.md`.
- **Does NOT touch:** the prose tutorials (issue 08).

## Acceptance criteria

- [ ] A crash-looping worker is restarted on an exponential backoff capped at `BACKOFF_CAP`,
      never abandoned, with a `CRITICAL` log + healthcheck lapse on crash-loop detection.
- [ ] A second watchdog for the same config exits via the atomic lock (verified by test).
- [ ] Workers are started in a new process group and stopped via `CTRL_BREAK`/`SIGTERM` with a
      `kill()` fallback; the worker examples handle the stop signal cleanly.
- [ ] `checker.is_process_alive` returns `True` on any internal exception (fail-safe).
- [ ] `test_empty_file` has a real body and asserts; no assertions remain stranded in
      `test_permission_error_scenario`.
- [ ] `compute_backoff_delay`, `is_crash_loop`, single-instance lock have unit tests.
- [ ] `ADR 0007` is `accepted`; `make all` green.

## Blocked by

- None — Wave 1.
