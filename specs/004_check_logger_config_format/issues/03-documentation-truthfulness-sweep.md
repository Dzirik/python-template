# Documentation truthfulness sweep — remove Logger-as-INI/`.conf` claims

> **Status:** `ready-for-agent`

## Parent

[`specs/004_check_logger_config_format/PRD.md`](../PRD.md) — *Migrate the Logger profiles from INI (`fileConfig`) to TOML (`dictConfig`)*

## What to build

A focused documentation sweep so that, after the core migration, no doc still describes the Logger profiles as stdlib INI / `logging.config.fileConfig` / `.conf`, and every "`.conf` is reserved for the Logger" statement is corrected — because `.conf` is now retired from the repository entirely. This is the counterpart to spec 003's documentation-truthfulness sweep, applied to the claims that spec deliberately left standing about the (then out-of-scope) Logger.

Files to update:

- **`CLAUDE.md`** — the *Logging* section (Logger config is chosen by `ENV_LOGGER` naming a `logger_*.conf` in `logging.config.fileConfig` format → now `logger_*.toml` loaded via `dictConfig`), and the *Configuration* section line stating "`.conf` is reserved for the Logger's stdlib-INI profiles" (no longer true — `.conf` is gone). Correct any other `fileConfig`/`.conf` references.
- **`CONTEXT.md`** — any glossary/architecture entry pinning the Logger profile to `.conf`/INI/`fileConfig`.
- **`configurations/schemas/README.md`** — the *Optional: logger `.conf` file-type mapping* section, which tells contributors to map `loggers/*.conf` to the Properties/INI file type; the profiles are now `.toml` and auto-recognised, so this section is revised or removed.
- **`README.md`** — any reference describing logger configuration as `.conf`/INI.
- **`docs/CHANGELOG.md`** — a changelog entry recording the Logger `fileConfig`→`dictConfig` / TOML migration and the retirement of `.conf`.

The sweep changes documentation only; it must not alter code or profiles. It should reflect the reality shipped by the core migration issue, so it lands after it.

## Acceptance criteria

- [ ] No doc under the repo describes the Logger profiles as `.conf`, INI, or `logging.config.fileConfig`; all such references point to `.toml` / `logging.config.dictConfig`.
- [ ] `CLAUDE.md`'s "`.conf` is reserved for the Logger" statement is corrected to reflect that `.conf` is retired repo-wide.
- [ ] `configurations/schemas/README.md`'s optional logger `.conf` file-type-mapping guidance is revised/removed for the `.toml` reality.
- [ ] `docs/CHANGELOG.md` records the migration.
- [ ] `grep`-level check: no remaining `logger_*.conf` or Logger-`fileConfig` references in tracked docs.
- [ ] `make all-secure` stays green (docs-only change).

## Blocked by

- [`01-core-logger-toml-dictconfig-migration.md`](01-core-logger-toml-dictconfig-migration.md) — the docs describe the shipped reality (`.conf` retired, `dictConfig` in use), so the core migration lands first.
