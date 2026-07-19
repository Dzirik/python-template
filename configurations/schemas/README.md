# Configuration schemas

This folder holds JSON Schemas that give PyCharm (and any other JSON-Schema-aware editor)
validation and autocomplete while editing the `.toml` configuration profiles. They are the
IDE-time counterpart to the load-time shape check `typedload` already performs in
`src/utils/config_loader.py`.

## Files

- `application_config.schema.json` - mirrors `ApplicationConfigData`
  (`src/utils/application_config_data.py`). Matches the application profiles:
  `configurations/python_repo.toml`, `configurations/python_local.toml`,
  `configurations/python_personal.toml`.
- `watchdog_config.schema.json` - mirrors `WatchdogConfigData`
  (`src/configurations/watchdog_config_data.py`). Matches the watchdog profiles under
  `configurations/watchdogs/*.toml`.

The mapping from schema file to `.toml` glob is registered project-wide in
`.idea/jsonSchemas.xml` (version-controlled - see the exception carved out for it in
`.gitignore`), so every contributor gets validation/autocomplete in PyCharm with no
per-machine setup.

## Maintenance - these schemas are hand-written, not generated

Auto-generating the schemas from the `NamedTuple` definitions is out of scope for now.
Whenever a field is added, renamed, removed, or its type/optionality changes on
`ApplicationConfigData`, `WatchdogConfigData`, or any nested `NamedTuple`
(`Path`, `ParamNotebookExecution`, `WorkerData`), update the matching schema file by hand in
the same change. A drift between the schema and the `NamedTuple` shape will not fail
`make all-secure` (no Python is involved) - it will only silently stop being useful in the
IDE, so treat "touched a config `NamedTuple`" as "touch its schema too".

Note: the logger profiles (`configurations/loggers/*.toml`) are also `.toml`, so PyCharm
already recognises and highlights them out of the box - no extra File-Types mapping is
needed for them (see [ADR 0004](../../docs/adr/0004-logger-profiles-toml-dictconfig.md) for
their `fileConfig`-to-`dictConfig` migration). They are not covered by a JSON Schema here,
same as before.
