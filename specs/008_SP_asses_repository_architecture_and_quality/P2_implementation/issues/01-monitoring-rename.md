# Monitoring rename: `MetaClass` → `MonitoredBase`

> **Status:** `ready-for-agent`

## Parent

[`../BRAINSTORM.md`](../BRAINSTORM.md) — P2. Report item 1 (reduced to the rename only;
Decision A). The consumer-dependent D3 wire-up is **deferred to spec 009** — do NOT build
any Logger/error-code/`MLModelDescription` consumer here.

## What to build

Rename the misleadingly-named `MetaClass` (it is an `ABC`, not a metaclass — actively
confuses the junior audience) to `MonitoredBase`, and rename its module. Pure hygiene, no
behavior change.

1. `src/utils/meta_class.py` → **`src/utils/monitored_base.py`**; class `MetaClass` →
   **`MonitoredBase`**. Update the module/class docstrings to say "common ABC base giving
   every class a `ClassInfo` for unified monitoring/logging" (drop the "Metaclass" wording).
   Leave `ClassInfo`, `TransformerDescription`, `MLModelDescription`, the `*_TYPE_NAME`
   constants, and all methods exactly as-is (their real consumers arrive with spec 009).
2. Update every importer:
   - `src/transformations/base_transformer.py`
   - `src/utils/base_component_config.py`
   - `tests/tests_configurations/test_watchdog_config.py`
   - `tests/tests_utils/test_meta_class.py` → rename file to
     **`tests/tests_utils/test_monitored_base.py`**; update imports/class refs.
3. Grep the repo for any remaining `MetaClass` / `meta_class` references in **code/tests**
   and update them. References in `CLAUDE.md` are **owned by issue 09** — do not edit docs
   here; issue 09's sweep updates them.

## Scope

- **OWNS:** `src/utils/monitored_base.py` (renamed from `meta_class.py`),
  `src/transformations/base_transformer.py`, `src/utils/base_component_config.py`,
  `tests/tests_utils/test_monitored_base.py` (renamed from `test_meta_class.py`),
  `tests/tests_configurations/test_watchdog_config.py`.
- **Does NOT touch:** `CLAUDE.md` (issue 09), any consumer wire-up.

## Acceptance criteria

- [ ] No `MetaClass` / `meta_class` symbol or path remains in `src/` or `tests/`.
- [ ] `MonitoredBase` lives in `src/utils/monitored_base.py`; `ClassInfo` et al. unchanged.
- [ ] `make all` green.

## Blocked by

- None — Wave 1.
