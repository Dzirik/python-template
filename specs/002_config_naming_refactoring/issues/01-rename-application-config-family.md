# Rename the Application Config family

> **Status:** `ready-for-agent`

## Parent

[`specs/002_config_naming_refactoring/PRD.md`](../PRD.md) — *Rename the Config Classes to Match the Ubiquitous Language*

## What to build

A behavior-preserving rename of the **Application Config** family so the code speaks the `CONTEXT.md` glossary. The process-wide singleton `Config` becomes `ApplicationConfig`, and its own data tuple `ConfigData` becomes `ApplicationConfigData` — bundled, because the tuple is reachable only through the singleton and the singleton constructs it, so they must move together to stay green.

The rename is total: the modules move to match their primary symbols (house file⇔class rule), every import and call site adopts the new names, the mirrored test modules move, and the single-file workflow config is repointed if it names the old module. There is **no back-compat alias** — `Config` and `ConfigData` cease to exist.

Nothing about *behavior* changes: the Singleton semantics, the delegation to the shared **Config Loader** and **Project Paths** (from spec 001), the returned data tree, and its field names are all preserved. Only names change.

Renames in scope:

| Old | New |
|-----|-----|
| `Config` (class) | `ApplicationConfig` |
| `ConfigData` (NamedTuple) | `ApplicationConfigData` |
| `src/utils/config.py` | `src/utils/application_config.py` |
| `src/utils/config_data.py` | `src/utils/application_config_data.py` |
| `tests/tests_utils/test_config.py` | `tests/tests_utils/test_application_config.py` |
| (any `test_config_data.py`, if present) | `test_application_config_data.py` |

## Acceptance criteria

- [ ] No symbol named `Config` or `ConfigData` exists anywhere in `src`, `tests`, or `notebooks`; no back-compat alias is introduced.
- [ ] The two modules and their mirrored test modules are renamed as above; the module filename matches its primary class/tuple.
- [ ] All ~11 imports and ~15 `Config()` call sites (across `src`, `tests`, `notebooks`) use `ApplicationConfig`; all `ConfigData` references use `ApplicationConfigData`.
- [ ] `ApplicationConfig()` remains a Singleton (same instance every call); `ApplicationConfig().get_data()` returns the same data tree (now typed `ApplicationConfigData`) and `get_data_as_dict()` works unchanged.
- [ ] `make_config_template.mk` (and any `FILE_NAME` documentation) is updated if it referenced the old `config` module.
- [ ] The shared **Config Loader** (`config_loader.py` / `load_config`) is untouched; dependency direction (ADR 0001) and path anchoring (ADR 0002) are unchanged.
- [ ] Tests keep mirroring `src/` and follow the parametrized house style; the renamed test modules pass.
- [ ] `make all-secure` is green on Python 3.11 / 3.12 / 3.13 (mypy `--strict` over the renamed imports is the compile-time proof no site was missed).

## Blocked by

None - can start immediately.
