# Migrate the config loader and all profiles from HOCON to TOML

> **Status:** `ready-for-agent`

## Parent

[`specs/003_conf_files_form_resolution/PRD.md`](../PRD.md) — *Migrate the HOCON config family to TOML*

## What to build

The atomic core of the migration: switch the single profile parse-point from `pyhocon` to the standard-library `tomllib`, and convert every profile the shared **Config Loader** touches to TOML in the same change. These cannot be split, because `ApplicationConfig` and every `WatchdogConfig` both load through `load_config`; the moment the loader parses TOML, every profile it reaches must already be TOML or the quality gate goes red.

End-to-end behaviour after this slice: `ApplicationConfig().get_data()`, `get_data_as_dict()`, and `WatchdogConfig(name)` return the exact same typed `NamedTuple` values as before, now sourced from `.toml` files. The typed layer (`ApplicationConfigData`, the watchdog config `NamedTuple`s, `typedload.load(...)`) and every caller are untouched — only the parse call and the file format change.

Scope:

- **Loader parse swap** — the profile parse changes from the `pyhocon` factory to `tomllib.load`, opening the file in binary mode as `tomllib` requires. The `typedload.load(parsed, target)` step is unchanged. The malformed-syntax failure mode now catches `tomllib.TOMLDecodeError` instead of the HOCON/`pyparsing` parse errors. The other two failure modes (missing file, shape mismatch) are preserved with their existing distinct exception types.
- **Per-family extension resolution** — the Project Paths helper that builds a profile path (`config_file`) gains an explicit extension parameter defaulting to `.conf`. The Config Loader passes `.toml`; the **Logger** caller keeps the default `.conf` so the out-of-scope logger path is unaffected.
- **Profiles converted** — the three application profiles (`python_repo`, `python_local`, and the git-ignored `python_personal`) and the two watchdog profiles (`watchdog_cmd_01`, `watchdog_cmd_02`), plus the personal-profile generation used by `make create-venv` / `create-venv-linux` (the copy source and the `name:` string-replace in the `Makefile`). Values, nesting, and comments carry over verbatim; HOCON `True` becomes TOML `true`; floats like `240.0` stay floats. No HOCON-only feature has to be unwound (none is used).
- **Test fixtures converted** — the profile fixtures the tests write/read (`test_config_loader`, `test_application_config`, `test_base_component_config`, `test_watchdog_config`, and the `.conf` assertions in `test_project_paths`) become TOML, with assertions unchanged. Add a malformed-TOML fixture proving the "malformed syntax" path raises the diagnostic-rich exception.

`pyhocon` is still imported by the saver/loader after this slice; its removal from the dependency set is a later issue.

## Acceptance criteria

- [ ] `load_config` parses profiles with `tomllib.load` (binary-mode open); no profile parse goes through `pyhocon`.
- [ ] `config_file` takes an extension parameter defaulting to `.conf`; the Config Loader resolves `.toml`; the Logger still resolves its profile as `.conf`.
- [ ] The three application profiles and two watchdog profiles exist as `.toml`, values/nesting/comments preserved (`True`→`true`); the old `.conf` versions are removed.
- [ ] `make create-venv` (and `-linux`) generates a working `python_personal.toml` with `name = "python_personal"`.
- [ ] `ApplicationConfig().get_data()`, `get_data_as_dict()`, and `WatchdogConfig(name)` return identical typed values to the pre-migration HOCON load; no caller changes.
- [ ] Three failure modes remain individually identifiable: missing file, malformed TOML (via `TOMLDecodeError`), and shape mismatch against the target `NamedTuple` (existing "do not match the shape of ..." exception).
- [ ] The Config Loader stays silent on success and imports no project `Logger` (ADR 0001 preserved).
- [ ] Test fixtures are TOML; a malformed-TOML fixture proves the malformed-syntax exception path fires with a diagnostic message; assertions are otherwise unchanged.
- [ ] `make all-secure` green on Python 3.11 / 3.12 / 3.13.

## Blocked by

- None - can start immediately.
