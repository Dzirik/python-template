# Documentation truthfulness sweep

> **Status:** `ready-for-agent`

## Parent

[`specs/002_config_naming_refactoring/PRD.md`](../PRD.md) — *Rename the Config Classes to Match the Ubiquitous Language*

## What to build

Update every piece of prose that names the renamed classes so nothing a reader — or Claude — consults stays false after slices 01 and 02. The renames are enforced by the compiler in code, but docstrings and docs are not, so they must be swept by hand. The sweep is **history-aware**: living docs get corrected in place, historical records do not get rewritten.

- **Update as living docs:**
  - `CONTEXT.md` — the "Implemented today as the `Config` singleton" and "via the `BaseConfig` base class" lines, updated to `ApplicationConfig` / `BaseComponentConfig`, so the glossary stays authoritative.
  - `CLAUDE.md` — the architecture section, so per-session guidance names classes that exist.
  - The two in-code cross-reference docstrings (the "Methods should the same as in `src/utils/base_config.py`" and "Only `src/utils/config` is different" breadcrumbs), updated to the new module names.
- **Update present-tense parentheticals only** (never the historical decision narrative):
  - ADR 0001 and ADR 0002 — only the "implemented as `Config`/`BaseConfig`" mentions.
- **Append, don't rewrite:**
  - `docs/CHANGELOG.md` — a new entry describing the rename; existing entries are left intact.

This slice changes no code and introduces no runtime behavior.

## Acceptance criteria

- [ ] `CONTEXT.md` names `ApplicationConfig` and `BaseComponentConfig` in the "Implemented today as…" lines; the glossary terms themselves (Application Config / Component Config) are unchanged.
- [ ] `CLAUDE.md`'s architecture section names the new classes; no reference to `Config`/`BaseConfig` as class names remains.
- [ ] The two in-code cross-reference docstrings point at the renamed modules.
- [ ] ADR 0001 / 0002 have only their present-tense "implemented as" parentheticals updated; their decision narratives are byte-for-byte unchanged.
- [ ] A new `docs/CHANGELOG.md` entry describes the rename; no prior entry is modified.
- [ ] No stale `Config` / `BaseConfig` / `ConfigData` class-name reference remains in tracked docs (a repo-wide search is clean, excluding historical narrative and this spec's own before/after tables).
- [ ] `make all-secure` is green (docs-only change; the gate confirms nothing was accidentally broken).

## Blocked by

- [`01-rename-application-config-family.md`](./01-rename-application-config-family.md)
- [`02-rename-component-config-base-and-fix-watchdog-identity.md`](./02-rename-component-config-base-and-fix-watchdog-identity.md)
