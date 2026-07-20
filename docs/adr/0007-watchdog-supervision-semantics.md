---
status: accepted
---

# Watchdog supervision semantics: graceful-stop signal contract, crash-loop backoff, single-instance lock

This decision records the supervision-hardening outcome of
[`specs/SP_008_asses_repository_architecture_and_quality/implementation/BRAINSTORM.md`](../../specs/SP_008_asses_repository_architecture_and_quality/implementation/BRAINSTORM.md)
(issue 05). It relates to [`docs/PROJECT_VISION.md`](../PROJECT_VISION.md)'s Windows-first
guiding principle: the two deepest Windows-specific supervision claims (graceful stop and
crash recovery) were exactly where the shipped behaviour diverged from the documentation
(§3.6). The three choices below are the ones that are hard to reverse (workers now depend
on a signal contract), surprising without context, and genuine trade-offs; the mechanical
fixes from the same issue (fail-safe `is_process_alive`, `.hb` touch-on-restart) are
recorded in the issue and code comments, not here.

Before this decision the watchdog's "graceful" stop was illusory on Windows —
`process.terminate()` *is* `TerminateProcess`, a hard kill; the documented `CTRL_BREAK`
path was never wired because workers were not started in a new process group, so workers
never ran cleanup (data-corruption risk). A crash-looping worker was restarted every 30 s
forever with no backoff and no alert. And two independent respawners (Task Scheduler
restart-on-failure plus the checker's WMI respawn) could race to produce duplicate
watchdogs, with only a non-atomic PID file as any guard.

We decided:

1. **Graceful stop is a real signal contract.** Workers are started with
   `CREATE_NEW_PROCESS_GROUP`; on stop the watchdog sends `CTRL_BREAK_EVENT` to the group,
   waits the grace window, then falls back to `process.kill()`. The worker examples install
   a `SIGBREAK` (Windows) / `SIGTERM` (POSIX) handler that flushes and exits cleanly. Clean
   shutdown is thus a **contract every worker must honour**, demonstrated by the examples.
2. **Crash-loop policy is backoff-to-cap that never permanently gives up.** Per worker the
   restart delay is `min(base * 2**consecutive_failures, cap)`. A crash-loop (≥ N restarts
   within window W) raises a `CRITICAL` log and lets that worker's healthcheck ping lapse
   so healthchecks.io alerts — but the watchdog keeps retrying at the capped interval, so a
   transient cause (full disk, a locked file) self-heals when it clears. Other workers are
   unaffected.
3. **Single-instance is enforced by an atomic OS lock.** On startup the watchdog acquires an
   exclusive non-blocking lock on a per-config lockfile (`msvcrt.locking` on Windows,
   `fcntl.flock` on POSIX), held for the process lifetime; if the lock is already held,
   another instance is running and this one logs and exits.

## Considered options

- **Document honest hard-kill semantics instead of implementing graceful stop** — rejected:
  the template teaches production supervision, and "workers are always hard-killed" undersells
  it and leaves the data-corruption risk unaddressed. Honest docs are necessary but not
  sufficient; the false `CTRL_BREAK` claim is removed regardless.
- **Classic circuit-breaker (permanent give-up after N failures, supervisord-style)** —
  rejected as the default: permanently abandoning a worker maximises for avoiding resource
  thrash but minimises unattended uptime — a worker that hit a transient fault stays dead
  until a human restarts the watchdog. Backoff-to-cap-with-alert keeps the worker recoverable
  while still surfacing the problem loudly.
- **Single-instance via the checker's identity check only** (the status report's first-draft
  direction) — rejected as the primary guard: it reuses existing code and is cross-platform,
  but the check is not atomic, so two watchdogs starting near-simultaneously can both pass it
  and still duplicate — which is the exact bug being fixed. The atomic lock closes the race;
  the identity check remains available for friendlier diagnostics.

## Consequences

Every worker — including any migrated later — must install the stop-signal handler to shut
down cleanly; a worker that ignores it is hard-killed after the grace window, same as before.
The worker examples are the reference implementation of the contract.

The new tunables (backoff base, cap, crash-loop N and window W) ship as named module-level
constants alongside the existing `CHECK_INTERVAL` / `STARTUP_GRACE_PERIOD`. Moving *all*
supervision timings into the watchdog `.toml` is deliberately deferred (a later polish item)
to avoid a second schema churn; the constants are the seam.

The single-instance lock means a second watchdog for the same config exits quietly by design
— an operator who expects "run it again to get a fresh one" will instead see the new process
exit, which is the intended safety behaviour and is logged. The decision logic (backoff
schedule, crash-loop detection, single-instance check) is extracted into pure functions with
unit tests; broader end-to-end watchdog coverage remains follow-up work.
