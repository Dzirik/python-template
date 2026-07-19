# CWD-independence acceptance test

> **Status:** `ready-for-agent`

## Parent

[`specs/001_config_logger_decoupling/PRD.md`](../PRD.md) — *Decouple Config Loading from Logging & Anchor All Paths to Project Root*

## What to build

The capstone acceptance test for the whole feature: prove the headline property — **launch method is irrelevant** — by exercising the public APIs from a *different* working directory and asserting identical resolution. After `chdir`-ing to a temp dir (and/or a subfolder), `Config()`, `Logger()`, and `WatchdogConfig()` must each resolve their `.conf` files and their I/O paths (`data`, `logs`, `reports`, `configurations`) to the same absolute locations they resolve to from the repo root.

Drive external behavior through the highest available seam — the existing public APIs — not private path-search internals. The test must not itself depend on the caller's CWD, and must account for the fact that `Config` and `Logger` are Singletons (env vars set via `Envs` **before** first instantiation; singleton caching considered when varying CWD). Mirror the prior art in `tests/tests_utils/test_logger.py` and the session-autouse fixture in `tests/conftest.py`. Keep the `fail_under = 25` coverage gate satisfied.

## Acceptance criteria

- [ ] A test `chdir`s to a temp dir and asserts `Config().get_data()` resolves identically to the repo-root run.
- [ ] Same for `Logger()` (log file lands in the same absolute `logs/`) and `WatchdogConfig(name).get_data()`.
- [ ] I/O locations (`data`, `logs`, `reports`, `configurations`) resolve to the same absolute paths regardless of CWD.
- [ ] The test does not depend on the caller's CWD and correctly handles Singleton caching.
- [ ] Coverage stays at or above `fail_under = 25`.
- [ ] `make all-secure` green on 3.11 / 3.12 / 3.13 (the acceptance gate for the whole feature).

## Blocked by

- [`06-migrate-conf-layout.md`](./06-migrate-conf-layout.md)
