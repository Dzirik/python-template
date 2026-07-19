# Add PyCharm JSON-Schema validation and shared IDE mapping for the TOML profiles

> **Status:** `ready-for-agent`

## Parent

[`specs/003_conf_files_form_resolution/PRD.md`](../PRD.md) — *Migrate the HOCON config family to TOML*

## What to build

First-class PyCharm ecosystem support so the new `.toml` profiles are recognised, validated, and autocompleted while editing — restoring, in the IDE and *while typing*, the same "must match the shape" guarantee `typedload` enforces at load time.

- **Schema-driven validation & autocomplete** — commit a JSON Schema describing the application-profile shape (mirroring `ApplicationConfigData`) and one for the watchdog-profile shape, under the configurations area. Add a version-controlled JSON-Schema mapping (in the project's shared IDE settings, e.g. `.idea`) so every contributor's PyCharm validates and autocompletes the profiles against those shapes with no manual setup.
- **Logger `.conf` guidance** — document the optional PyCharm File-Types mapping of `loggers/*.conf` to the Properties/INI file type for basic highlighting. No format change; guidance only.
- Note in the repo that the schemas mirror the `NamedTuple` fields by hand and keeping them in sync is a documented maintenance step (auto-generation is out of scope).

`.toml` auto-recognition (highlighting, structure view, formatting) needs no configuration — it follows from the extension alone; only the schema mapping is committed.

## Acceptance criteria

- [ ] A committed JSON Schema for the application profile mirrors the `ApplicationConfigData` fields; a committed JSON Schema mirrors the watchdog profile shape.
- [ ] A version-controlled JSON-Schema mapping (shared IDE settings) associates the schemas with the corresponding `.toml` profiles so PyCharm validates and autocompletes them without per-user setup.
- [ ] The logger `.conf`→Properties/INI File-Types mapping is documented as an optional step.
- [ ] The hand-maintenance / sync expectation for the schemas is documented.
- [ ] `make all-secure` stays green (committed schema/IDE files do not affect the Python quality gate).

## Blocked by

- [`01-core-toml-migration.md`](./01-core-toml-migration.md)
