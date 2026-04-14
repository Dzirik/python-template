# Technical Audit: Supervision System P1/P2 Implementations

**Date:** 2026-04-10
**Scope:** `src/scripts/checker.py`, `src/scripts/watchdog.py`, `src/scripts/watchdog_config_data.py`
**Auditor role:** Senior Python Backend Engineer & Systems Reliability Specialist

---

## 1. Executive Summary

This audit verifies the Priority 1 (stability, observability) and Priority 2 (architectural refinement) changes applied to the three-layer supervision hierarchy: **Windows Task Scheduler → `checker.py` → `watchdog.py` → Workers**. The system targets a 24/5 production environment managing "human-like" worker processes characterized by minute-level latencies and low-frequency daily actions.

**Overall verdict: CONDITIONALLY READY** — all P1/P2 changes are structurally correct, with two minor observations that should be tracked as follow-up items but do not block deployment.

---

## 2. Verification Matrix

| # | Requirement | Status | File(s) | Lines |
|---|-------------|--------|---------|-------|
| 2.1 | PID recycling mitigation via WMIC | ✅ PASS | `checker.py` | 91–154 |
| 2.2 | Recovery race condition delay (2.0s) | ✅ PASS | `checker.py` | 243–246 |
| 2.3 | Graceful worker shutdown escalation | ✅ PASS | `watchdog.py` | 242–267 |
| 2.4 | Centralized `Logger` singleton integration | ✅ PASS | both scripts | throughout |
| 2.5 | Per-config `RotatingFileHandler` supplement | ✅ PASS | both scripts | 31–55 / 44–68 |
| 2.6 | Startup grace period ordering | ✅ PASS | `watchdog.py` | 299–306 |
| 2.7 | `__file__`-based path resolution | ✅ PASS | `watchdog.py` | 22–23 |
| 2.8 | `NamedTuple` default values | ⚠️ PASS (note) | `watchdog_config_data.py` | 22, 31–32 |

---

## 3. Detailed Findings

### 3.1 PID Recycling Mitigation (P0 — previously implemented, verified here)

**Location:** `checker.py` lines 91–154

**Implementation review:**

The `_get_process_cmdline(pid)` function (lines 91–115) queries the Windows Management Instrumentation Command-line (`wmic process where ProcessId={pid} get CommandLine`) with a 10-second timeout. The output parsing correctly:
- Strips and splits WMIC's multi-line output.
- Skips the header line (`CommandLine`).
- Joins remaining lines to handle command lines that span multiple WMIC output rows.
- Returns `None` on any failure (non-zero return code, insufficient output, exceptions).

The `is_watchdog_process(pid, config_name)` function (lines 118–154) implements a layered verification:
1. **Existence check:** `is_process_alive(pid)` via `os.kill(pid, 0)` — fast short-circuit.
2. **Identity check:** `_get_process_cmdline(pid)` confirms the command line contains both `"watchdog.py"` and the expected `config_name`.
3. **Graceful degradation:** If WMIC fails (returns `None`), the function logs a warning and falls back to the basic alive check rather than triggering a false recovery. This is the correct defensive choice — a transient WMI service hiccup should not cause a restart cascade.

The `is_watchdog_healthy()` function (line 191) correctly delegates to `is_watchdog_process(pid, config_name)` instead of the raw `is_process_alive(pid)`, and `config_name` is threaded through from the `__main__` call site (line 273).

**Verdict:** ✅ PASS. The two-layer check (existence + identity) effectively prevents PID recycling false positives while maintaining availability through graceful degradation.

**Note:** WMIC is deprecated on modern Windows (post-2024) in favor of PowerShell's `Get-CimInstance`. The 10-second timeout mitigates any performance concern, but this should be monitored for compatibility in future Windows Server updates.

### 3.2 Recovery Stability — Race Condition Delay (P1)

**Location:** `checker.py` lines 243–246

**Implementation review:**

```
# Step 3: Wait for the OS to fully reclaim the killed process tree and
# release file handles before starting a new watchdog instance.
Logger().info("Waiting for process tree to be reclaimed...")
time.sleep(2.0)
```

The 2.0-second delay is inserted between Step 2 (orphaned worker cleanup via `taskkill /T /F`) and Step 4 (`subprocess.Popen` for the new watchdog). This placement is correct — it allows the Windows kernel to:
- Complete the asynchronous `TerminateProcess` calls initiated by `taskkill`.
- Release file handles on `.pid` and `.hb` files held by the dying processes.
- Reclaim the PID numbers so the new watchdog doesn't collide with zombie entries.

**Verdict:** ✅ PASS. The delay is appropriately placed and sized. For a 24/5 system with 30-second checker intervals, a 2-second delay is negligible but provides sufficient margin for process tree teardown.


### 3.3 Graceful Worker Shutdown (P1)

**Location:** `watchdog.py` lines 242–267

**Implementation review:**

The `stop_worker()` function implements a proper two-phase shutdown:

1. **Early exit guard** (lines 255–257): If the process is already dead (`process.poll() is not None`), it logs the exit code and returns. This prevents calling `terminate()` on a dead handle.
2. **Graceful phase** (lines 259–263): `process.terminate()` sends `CTRL_BREAK_EVENT` on Windows (equivalent to `SIGTERM` on POSIX), followed by `process.wait(timeout=5)`.
3. **Escalation phase** (lines 264–267): On `subprocess.TimeoutExpired`, logs a warning and calls `process.kill()` (`TerminateProcess` on Windows — non-catchable), then `process.wait()` to collect the exit status and prevent zombie handles.

This pattern is critical for workers like `cmd_status_print_01.py`, which use `finally` blocks (line 81) to call `hc_heartbeat.stop()`. The 5-second graceful window gives workers time to execute their cleanup logic and send a final healthcheck ping before the hard kill.

**Verdict:** ✅ PASS. The escalation pattern is correctly implemented. The 5-second timeout is appropriate for the "human-like" worker profile — worker cleanup logic (stopping a heartbeat thread, flushing buffers) should complete well within this window.

### 3.4 Logging Integration (P1)

**Location:** `checker.py` lines 24–55, `watchdog.py` lines 28, 44–68

**Implementation review:**

Both scripts follow the same integration pattern:

**Centralized Logger singleton:**
- Both scripts import `from src.utils.logger import Logger` and use `Logger()` for all log calls.
- The `Logger` class (singleton via `Singleton` metaclass) initializes from the `ENV_LOGGER` environment variable, defaulting to `logger_file_limit_console` which provides both rotating file output (`logs/python_log_file_limit_console.log`, 5 MB, 2 backups) and console output via `StreamHandler(sys.stdout)`.
- No `setup_logging()` functions remain in either script. No `logging.getLogger()` calls remain.

**Supplemental per-config RotatingFileHandler:**
- Each script defines `_add_script_file_handler(config_name)`, which:
  - Creates the `logs/` directory if missing (`mkdir(parents=True, exist_ok=True)`).
  - Constructs a `RotatingFileHandler` targeting `logs/checker_{config_name}.log` or `logs/watchdog_{config_name}.log`.
  - Configures it with `maxBytes=5_242_880` (5 MB), `backupCount=3`, and UTF-8 encoding.
  - Uses the project-standard format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`.
  - Attaches it to the underlying stdlib logger via `Logger().get().addHandler(file_handler)`.
- This handler is added once at startup in the `__main__` block, before any business logic executes.

**Call site patterns:**
- Standard calls use `Logger().info(f"...")`, `Logger().warning(f"...")`, `Logger().error(f"...")` with pre-formatted f-strings. This is required because the `Logger` wrapper methods accept only `message: str` — they do not forward `*args` or `**kwargs` to the underlying stdlib logger.
- Exception-handling calls that require stack traces use `Logger().get().error(f"...", exc_info=True)` to access the underlying stdlib `logging.Logger` directly. This pattern appears in three locations in `watchdog.py` (lines 303, 318, 337) — all within `except` blocks in the monitoring loop and startup sequence.

**Verdict:** ✅ PASS. The dual-handler approach (centralized Logger singleton + per-script supplemental handler) is correct and maintainable. Log output flows to three destinations simultaneously: the console (via Logger's default `StreamHandler`), the project-wide rotating log (via Logger's default `RotatingFileHandler`), and the per-script rotating log (via the supplemental handler).

**Observation:** The supplemental handler's format string matches the project convention in `logger_file_limit_console.conf`, ensuring consistent formatting across all log destinations. Supervision log messages are duplicated in `logs/python_log_file_limit_console.log` — acceptable for a 24/5 environment (more observability is better) but could be optimized if log volume becomes a concern.


### 3.5 Architectural Fixes (P2)

#### 3.5.1 Startup Grace Period Inversion Fix

**Location:** `watchdog.py` lines 297–306

The `watchdog()` function now executes in the correct order:
1. `write_pid("watchdog", heartbeat_dir)` — line 297.
2. Worker startup loop (`for config in workers: ... start_worker(...)`) — lines 299–303.
3. Grace period log + sleep — lines 305–306.
4. `while True:` monitoring loop — line 308.

Previously, the sleep was between steps 1 and 2, which caused the monitoring loop to poll before workers had time to create their `.hb` files, triggering immediate "frozen" false positives.

**Verdict:** ✅ PASS. Workers are spawned first, then the grace period gives them `STARTUP_GRACE_PERIOD` (5.0s) to initialize before monitoring begins.

#### 3.5.2 `__file__`-Based Path Resolution

**Location:** `watchdog.py` lines 22–23

```
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path += [str(_SCRIPT_DIR / ".."), str(_SCRIPT_DIR / "../..")]
```

This replaces the previous `Path.cwd()` approach, which would break when the script was invoked from a working directory other than `src/scripts/` (e.g., from Windows Task Scheduler, which defaults CWD to `C:\WINDOWS\system32`). `Path(__file__).resolve().parent` is deterministic regardless of CWD. `checker.py` already used this pattern (line 19), so both scripts are now consistent.

**Verdict:** ✅ PASS.

#### 3.5.3 `NamedTuple` Default Values

**Location:** `watchdog_config_data.py` lines 8–32

```python
class WorkerData(NamedTuple):
    name: str
    script: str
    args: list[str]
    timeout: float
    healthcheck_url_key: str = ""

class WatchdogConfigData(NamedTuple):
    name: str
    healthcheck_url_key: str = ""
    workers: list[WorkerData] = []
```

Fields with defaults are correctly placed after fields without defaults, satisfying Python's `NamedTuple` ordering constraint. The defaults are safe:
- `WorkerData.healthcheck_url_key = ""` — downstream in `build_command()`, this passes `""` as `--healthcheck-url-key`, and `resolve_ping_url("")` returns `None`, disabling healthcheck pings. This is correct behavior.
- `WatchdogConfigData.healthcheck_url_key = ""` — same pattern for the watchdog-level healthcheck.
- `WatchdogConfigData.workers = []` — an empty worker list causes the monitoring loop to no-op. The watchdog runs as a harmless heartbeat emitter. No crash.

Both existing config files (`watchdog_cmd_01.conf`, `watchdog_cmd_02.conf`) provide explicit values for all fields, so the defaults serve purely as resilience against future configs that omit optional fields.

**Verdict:** ⚠️ PASS with note. The `workers: list[WorkerData] = []` default uses Python's `NamedTuple` mechanism, which does **not** suffer from the shared-mutable-default-argument bug (each instance gets its own copy). However, `typedload`'s handling of `NamedTuple` defaults during deserialization should be verified with a unit test using a minimal `.conf` that omits `healthcheck_url_key`.

#### 3.5.4 Polling Interval Optimization

**Location:** `watchdog.py` line 36

`CHECK_INTERVAL` was changed from `5.0` to `30.0` seconds. Given worker timeouts range from `90.0s` to `360.0s`, a 30-second poll means:
- A crashed worker is detected within 30s (worst case) — well within the 90s minimum timeout.
- A frozen worker is detected within `timeout + 30s` worst case.
- The ratio `CHECK_INTERVAL / min(timeout)` = `30 / 90` ≈ 0.33, ensuring at least 3 poll cycles per timeout window.

**Verdict:** ✅ PASS.


---

## 4. Production Readiness Assessment

### 4.1 Strengths

1. **Defense in depth:** The three-layer supervision stack (Scheduler → checker → watchdog → workers) has no single point of failure. The ephemeral checker pattern avoids the "who watches the watchman" problem.
2. **PID recycling protection:** The WMIC-based command line verification is a robust mitigation absent in most Python supervision systems.
3. **Graceful degradation:** WMIC failures fall back safely; `terminate()` failures escalate to `kill()`; missing config fields use safe defaults.
4. **Observable logging:** Every state transition (start, crash, freeze, restart, recovery) is logged through the centralized `Logger` singleton with per-script rotating files.
5. **Correct startup sequencing:** Workers are spawned before the grace period sleep, eliminating false-positive freeze detection on boot.

### 4.2 Follow-Up Items (Non-Blocking)

| # | Item | Severity | Description |
|---|------|----------|-------------|
| F1 | WMIC deprecation | Low | `wmic.exe` is deprecated on Windows 11/Server 2025+. Plan migration to `Get-CimInstance` via PowerShell before the OS drops WMIC support. |
| F2 | `typedload` + defaults | Low | Verify that `typedload.load()` correctly populates `NamedTuple` fields that have defaults when the source `.conf` omits them. Write a unit test with a minimal conf that omits `healthcheck_url_key`. |
| F3 | Log duplication | Info | Supervision messages appear in both `logs/python_log_file_limit_console.log` (via Logger's default handler) and `logs/watchdog_{config}.log` (via supplemental handler). Acceptable for observability but could be optimized if log volume grows. |
| F4 | Stale `.pid`/`.hb` cleanup | Low | `recover_watchdog()` does not delete old `.pid`/`.hb` files before spawning the new watchdog. The new watchdog overwrites them on startup, but there is a brief window where stale files could mislead a concurrent checker invocation. |

### 4.3 Final Verdict

**The supervision system is CONDITIONALLY READY for 24/5 production deployment.** All P1 and P2 requirements have been correctly implemented and verified. The follow-up items (F1–F4) are low-severity enhancements that should be tracked in the backlog but do not represent deployment blockers.

---

*End of audit.*
