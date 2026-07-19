# Remove the `pyhocon` dependency and its deprecation-warning filter

> **Status:** `ready-for-agent`

## Parent

[`specs/003_conf_files_form_resolution/PRD.md`](../PRD.md) — *Migrate the HOCON config family to TOML*

## What to build

With nothing left importing `pyhocon` (the Config Loader now uses `tomllib`, the saver/loader now uses stdlib `json`), remove the dependency entirely and clean up the workarounds it required. This completes the "drop `pyhocon` without adding a replacement" goal and shrinks the supply-chain surface that `make security-check` gates on.

- Remove `pyhocon` through the `uv` / Makefile dependency workflow (`make remove-lib library=pyhocon`), never by hand-editing `uv.lock`.
- Remove the now-unneeded `pyhocon` / `pyparsing` `DeprecationWarning` filters from the pytest `filterwarnings` config in `pyproject.toml`.
- `typedload` stays.

## Acceptance criteria

- [ ] `pyhocon` is gone from `pyproject.toml` and `uv.lock` (removed via `make remove-lib`, not by hand-editing the lock).
- [ ] No source, test, or notebook file imports `pyhocon` or `pyparsing` (grep-verifiable).
- [ ] The `ignore::DeprecationWarning:pyhocon.*` and `ignore::pyparsing.exceptions.PyparsingDeprecationWarning` `filterwarnings` entries are removed from `pyproject.toml`.
- [ ] `make all-secure` green on Python 3.11 / 3.12 / 3.13, including `pip-audit` and `bandit` with `pyhocon`/`pyparsing` no longer in the tree.

## Blocked by

- [`01-core-toml-migration.md`](./01-core-toml-migration.md)
- [`02-snapshot-json-round-trip.md`](./02-snapshot-json-round-trip.md)
