# Application Config delegates to the Config Loader

> **Status:** `ready-for-agent`

## Parent

[`specs/001_config_logger_decoupling/PRD.md`](../PRD.md) — *Decouple Config Loading from Logging & Anchor All Paths to Project Root*

## What to build

Stop `Config` (the **Application Config** singleton) from being a hand-maintained fork of the loading logic. It should delegate loading to the shared **Config Loader** (which resolves files via **Project Paths**) by composition, so it can no longer drift from **Component Config** loading. Remove the bespoke `_get_config_file_path` 4-candidate-path search and the `_is_profile` flag where it's no longer needed.

`Config` stays a **Singleton** and continues to select its profile ambiently via the **Env Selector** (`Envs`), defaulting to `python_personal` — profile choice stays environment-driven, not caller-passed. The everyday public surface is unchanged: `get_data()` still returns the `ConfigData` tree exactly as before, and `get_data_as_dict()` still works, so existing notebooks and tests don't churn.

At this stage the `.conf` files stay in their current locations with their existing internal paths — moving/rewriting them is a later slice — so this change must merge with `make all-secure` green.

## Acceptance criteria

- [ ] `Config().get_data()` returns the same `ConfigData` tree as before (existing consumers unaffected).
- [ ] `Config().get_data_as_dict()` behaves as before.
- [ ] `Config()` is idempotent (Singleton identity holds).
- [ ] Loading uses the shared **Config Loader**; the `_get_config_file_path` 4-path search is gone.
- [ ] `_is_profile` is removed where it's no longer needed; no bespoke path resolution remains in `Config`.
- [ ] Profile is selected via `Envs` (default `python_personal`), not passed by callers.
- [ ] Existing `Config` tests still pass (adjusted only where private internals were removed); `make all-secure` green on 3.11 / 3.12 / 3.13.

## Blocked by

- [`02-config-loader.md`](./02-config-loader.md)
