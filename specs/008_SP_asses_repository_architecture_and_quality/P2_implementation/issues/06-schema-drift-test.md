# Config schema drift-detection test

> **Status:** `ready-for-agent`

## Parent

[`../BRAINSTORM.md`](../BRAINSTORM.md) — P2. Report item 9. Decision I (**drift-detection
test**, not a generator).

## What to build

The JSON schemas in `configurations/schemas/*.schema.json` are hand-edited IDE aids
(PyCharm autocomplete) that are **not** loaded by the config loader (typedload validates at
runtime), so they silently drift from the NamedTuple trees. Add a test that fails when they
diverge — turning a manual chore into an invariant without adopting a generator.

1. New test `tests/tests_utils/test_config_schema_drift.py`:
   - Recursively collect the field names of the `ApplicationConfigData` NamedTuple tree
     (`src/utils/application_config_data.py`) and of the `WatchdogConfig` NamedTuple tree.
   - Parse `configurations/schemas/application_config.schema.json` and
     `configurations/schemas/watchdog_config.schema.json` with stdlib `json`.
   - Walk the schema `properties` (and nested `properties` under object types) and assert the
     property-key set matches the NamedTuple field-name set at each level.
   - On mismatch, fail with a message listing the missing/extra keys and the offending level
     (junior-friendly diagnostics, per the vision).
   - Parametrize over the two (NamedTuple-root, schema-file) pairs.
2. Compare **field names / structure** only — not JSON-Schema types (type fidelity is out of
   scope; the goal is catching "added a key, forgot the schema").

## Scope

- **OWNS:** `tests/tests_utils/test_config_schema_drift.py` (new).
- **Reads only:** `src/utils/application_config_data.py`, the `WatchdogConfig` NamedTuple,
  `configurations/schemas/*.schema.json`. Touches no source or schema file.

## Acceptance criteria

- [ ] The test passes against the current (in-sync) schemas.
- [ ] Adding a field to a NamedTuple without updating its schema (or vice versa) fails the
      test with a clear missing/extra-key message. (Verify by a temporary local edit.)
- [ ] `make all` green.

## Blocked by

- None — Wave 1.
