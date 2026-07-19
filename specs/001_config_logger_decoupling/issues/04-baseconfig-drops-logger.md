# Component Config drops the Logger dependency

> **Status:** `ready-for-agent`

## Parent

[`specs/001_config_logger_decoupling/PRD.md`](../PRD.md) — *Decouple Config Loading from Logging & Anchor All Paths to Project Root*

## What to build

Break the wrong-way dependency in **Component Config**: `BaseConfig.parse_config()` currently calls `Logger().debug(...)`, so loading *any* component config (e.g. the watchdog) drags in the whole logging stack just to read a file. Remove that call and delegate loading to the shared **Config Loader** (via **Project Paths**), enforcing the foundational dependency direction of ADR 0001 structurally rather than by convention.

`BaseConfig` keeps its generic `BaseConfig[_T]` typing and its `get_data()` / `get_data_as_dict()` surface. `WatchdogConfig(name).get_data()` continues to return `WatchdogConfigData` unchanged — supervision code is untouched.

At this stage the watchdog `.conf` files stay in their current location (their move to `configurations/watchdogs/` is a later slice); `BaseConfig` resolves them via Project Paths from where they currently live, so this change merges with `make all-secure` green.

## Acceptance criteria

- [ ] `BaseConfig.parse_config()` no longer references `Logger` in any form.
- [ ] Loading a Component Config pulls in **no** logging stack (asserted, e.g. import-graph / no-Logger-import test).
- [ ] `BaseConfig` delegates to the shared **Config Loader** and keeps its `BaseConfig[_T]` generic typing.
- [ ] `WatchdogConfig(name).get_data()` still returns `WatchdogConfigData` with the same shape.
- [ ] Existing component-config / watchdog-config tests pass; `make all-secure` green on 3.11 / 3.12 / 3.13.

## Blocked by

- [`02-config-loader.md`](./02-config-loader.md)
