# Rename the Component Config base + fix WatchdogConfig's runtime identity

> **Status:** `ready-for-agent`

## Parent

[`specs/002_config_naming_refactoring/PRD.md`](../PRD.md) — *Rename the Config Classes to Match the Ubiquitous Language*

## What to build

Rename the **Component Config** base and, in the same file it forces you to touch, correct the one runtime identity string that lies.

The base class `BaseConfig` becomes `BaseComponentConfig` — keeping the house `Base`-prefix convention for an abstract parent (parallel to `BaseTransformer`) but qualifying it with the family, so it no longer claims to be the base of *all* configs. `WatchdogConfig(BaseComponentConfig[WatchdogConfigData])` then reads as "a watchdog config **is a** component config." No back-compat alias.

Bundled into the same slice because it edits the same file (`WatchdogConfig`): fix the copy-paste `MetaClass` identity. `WatchdogConfig` currently registers `class_name="ColumnsGroupingPipelineConfig"` — a leftover from an unrelated pipeline that mislabels the watchdog config in all unified monitoring/logging output. Change it to `"WatchdogConfig"`, and replace its copy-paste docstrings ("Pipelines configuration file.") with ones describing a watchdog config.

Behavior is otherwise preserved: `BaseComponentConfig` keeps its `Generic[_T]` typing, `parse_config()`, and `get_data()` / `get_data_as_dict()` surface; `WatchdogConfig` keeps `config_subfolder="watchdogs"` and its load behavior.

Renames in scope:

| Old | New |
|-----|-----|
| `BaseConfig` (class) | `BaseComponentConfig` |
| `src/utils/base_config.py` | `src/utils/base_component_config.py` |
| `tests/tests_utils/test_base_config.py` | `tests/tests_utils/test_base_component_config.py` |

## Acceptance criteria

- [ ] No symbol named `BaseConfig` exists anywhere in `src` or `tests`; no alias is introduced.
- [ ] The module and its mirrored test module are renamed as above; `WatchdogConfig`'s base-class declaration and super-call reference `BaseComponentConfig`.
- [ ] `WatchdogConfig`'s `class_name` is `"WatchdogConfig"` (not `"ColumnsGroupingPipelineConfig"`); its class and `__init__` docstrings describe a watchdog config.
- [ ] A test asserts `WatchdogConfig(name).get_class_name() == "WatchdogConfig"` at the public `MetaClass` seam (natural home: `tests/tests_configurations/test_watchdog_config.py`).
- [ ] `WatchdogConfig(name).get_data()` still returns `WatchdogConfigData` from `configurations/watchdogs/`; `WatchdogConfig` / `WatchdogConfigData` names are unchanged.
- [ ] The shared **Config Loader** is untouched; dependency direction (ADR 0001) and path anchoring (ADR 0002) are unchanged.
- [ ] `make all-secure` is green on Python 3.11 / 3.12 / 3.13.

## Blocked by

- [`01-rename-application-config-family.md`](./01-rename-application-config-family.md) (sequenced per task decision; the two rename families are technically independent).
