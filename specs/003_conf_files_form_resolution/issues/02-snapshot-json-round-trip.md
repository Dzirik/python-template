# Make the config-snapshot round-trip symmetric on stdlib JSON with a `.json` extension

> **Status:** `ready-for-agent`

## Parent

[`specs/003_conf_files_form_resolution/PRD.md`](../PRD.md) — *Migrate the HOCON config family to TOML*

## What to build

Decouple the runtime config-snapshot round-trip in the saver/loader from the profile format and from `pyhocon`. Today `save_config_data` *writes* JSON but `load_config_data` *reads* it back through `pyhocon`, and both use a `.conf` extension — so JSON content lives in a `.conf` file and the saver/loader is the last `pyhocon` importer.

Make the pair symmetric on the standard-library `json` module (write *and* read) and change the snapshot extension from `.conf` to `.json`, so the file name matches its content and the third overloaded meaning of `.conf` disappears. These snapshots are machine round-trips, never hand-edited, so JSON is the right fit and no human-facing format is lost. This slice is independent of the profile format and can proceed in parallel with the core migration.

## Acceptance criteria

- [ ] `save_config_data` writes the dumped `NamedTuple` as JSON to a `.json` file.
- [ ] `load_config_data` reads the snapshot back with stdlib `json` (no `pyhocon`) from a `.json` file and validates it into the target `NamedTuple` via `typedload`.
- [ ] The saver/loader module no longer imports `pyhocon`.
- [ ] A round-trip test dumps a config `NamedTuple`, reloads it, asserts equality with the original, and asserts the snapshot file carries the `.json` extension (not `.conf`).
- [ ] Missing-file behaviour still raises the existing diagnostic exception.
- [ ] `make all-secure` green on Python 3.11 / 3.12 / 3.13.

## Blocked by

- None - can start immediately (parallel with [`01-core-toml-migration.md`](./01-core-toml-migration.md)).
