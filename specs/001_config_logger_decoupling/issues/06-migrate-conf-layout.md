# Migrate .conf layout and remove all `../../` paths

> **Status:** `ready-for-agent`

## Parent

[`specs/001_config_logger_decoupling/PRD.md`](../PRD.md) — *Decouple Config Loading from Logging & Anchor All Paths to Project Root*

## What to build

With every module now resolving through **Project Paths**, migrate the `.conf` tree to the target layout and eliminate CWD-relative paths entirely. Organize everything under one central `configurations/` tree by kind:

- **Application Config** (`python_*`) stays at the `configurations/` top level.
- **Logger** profiles move under `configurations/loggers/`.
- Each **Component Config** kind gets its own subfolder — watchdog files move to `configurations/watchdogs/`.

Repoint the modules at the new subfolders (Logger looks under `loggers/`; `WatchdogConfig` loads from `watchdogs/`; `python_*` unchanged at top level). Remove **every** `../../` path from **all** `.conf` files (config profiles and logger profiles alike): paths *inside* the profiles (`data`, notebook paths, `output_folder`, etc.) become root-relative values that **Project Paths** resolves — not `../../`-prefixed CWD-relative strings — so `Config().get_data().path.data` points at the real `data/` folder. Fix `SPECIAL_LOGGER_FILE_NAME` (the fallback bad-config log path) to resolve via Project Paths instead of a hard-coded `../../`.

The three Config Profiles (`python_repo`, `python_personal`, `python_local`) and the five Logger Profiles keep their names and selection semantics. This is the coordinated move that makes the file locations match the domain model; it must merge with `make all-secure` green.

## Acceptance criteria

- [ ] **Zero** `../../` occurrences remain in any `.conf` file (grep-verifiable) — config and logger profiles alike.
- [ ] `logger_*` profiles live under `configurations/loggers/`; the Logger resolves them there.
- [ ] Watchdog profiles live under `configurations/watchdogs/`; `WatchdogConfig(name)` loads them there.
- [ ] `python_*` profiles remain at the `configurations/` top level.
- [ ] Internal profile paths (`data`, notebook, `output_folder`) resolve to the correct absolute locations via Project Paths; `Config().get_data().path.data` points at the real `data/` folder.
- [ ] `SPECIAL_LOGGER_FILE_NAME` resolves via Project Paths, not a hard-coded `../../` path.
- [ ] The three Config Profile names and five Logger Profile names / selection semantics are unchanged.
- [ ] `make all-secure` green on 3.11 / 3.12 / 3.13.

## Blocked by

- [`03-config-delegates-to-loader.md`](./03-config-delegates-to-loader.md)
- [`04-baseconfig-drops-logger.md`](./04-baseconfig-drops-logger.md)
- [`05-logger-independent-path-injection.md`](./05-logger-independent-path-injection.md)
