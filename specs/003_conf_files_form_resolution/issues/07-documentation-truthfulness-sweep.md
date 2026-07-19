# Sweep the documentation from HOCON to TOML

> **Status:** `ready-for-agent`

## Parent

[`specs/003_conf_files_form_resolution/PRD.md`](../PRD.md) — *Migrate the HOCON config family to TOML*

## What to build

Bring the prose documentation into line with the migrated code, and finish de-overloading the `.conf` extension in the docs so `.conf` reads as "logger INI only".

- **`CLAUDE.md`** — update the configuration-layer description and any HOCON references to TOML / `tomllib`; `.conf` now means logger INI files, config profiles are `.toml`.
- **`docs/PROJECT_VISION.md`** — update HOCON references to TOML; add pointers to the new ADR 0003 and the `CONF_TO_TOML.md` tutorial.
- **`CONTEXT.md` glossary** — the *Config Profile / Logger Profile*, *Application Config*, *Component Config*, and *Config Loader* entries currently say "`.conf` file", which is now false for config profiles. De-pin these entries from a specific extension so the glossary stays truthful and free of implementation detail (per its own stated rule).
- **Tutorials** (`PERSISTENT_RUN.md`, `CHECKER_SCHEDULER_SET_UP.md`) — update any watchdog/config profile references that name HOCON or `.conf`; cross-link `CONF_TO_TOML.md` where relevant.

This completes User Story 11 ("`.conf` means exactly one thing") at the documentation level.

## Acceptance criteria

- [ ] No stale "HOCON" or "`pyhocon`" reference remains in `CLAUDE.md`, `docs/PROJECT_VISION.md`, `CONTEXT.md`, or the tutorials (grep-verifiable) except where deliberately describing the *former* state / the ADR history.
- [ ] The four named `CONTEXT.md` glossary entries no longer pin config profiles to a `.conf` extension.
- [ ] `CLAUDE.md` and `PROJECT_VISION.md` describe config profiles as TOML parsed by `tomllib`, and reference ADR 0003 and the `CONF_TO_TOML.md` tutorial.
- [ ] Docs consistently reflect `.conf` as logger-INI-only.
- [ ] `make all-secure` stays green (docs-only change).

## Blocked by

- [`01-core-toml-migration.md`](./01-core-toml-migration.md)
