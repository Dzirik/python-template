# Execution Playbook — Config Naming Refactor

> Map over the issues in [`issues/`](./issues/); consumes the blocked-by graph from `to-issues`, does not restate issue bodies.
> Parent PRD: [`PRD.md`](./PRD.md). Domain terms: [`CONTEXT.md`](../../CONTEXT.md). Decisions: [ADR 0001](../../docs/adr/0001-foundational-config-layering.md), [ADR 0002](../../docs/adr/0002-repo-root-path-anchoring.md) (both untouched by this work).

## Summary

- Issues covered: [01](./issues/01-rename-application-config-family.md), [02](./issues/02-rename-component-config-base-and-fix-watchdog-identity.md), [03](./issues/03-documentation-truthfulness-sweep.md).
- **Verdict: serial** — the blocked-by graph is a strict chain (01 → 02 → 03); no two issues can run concurrently. This is a single-branch, three-commit mechanical change; parallelism would be manufactured, not real.
- Highest execution risk: a **missed call site / reference** during a rename — mitigated by `make mypy` (`--strict`), which fails loudly on any un-updated import or annotation, so the per-step gate is a reliable net.

## Waves

All work lands on one branch: **`feature/config-naming`** (off `main`; the pre-commit hook blocks `main`/`master`/`develop`). One agent, three ordered steps.

### Wave 1 — gate: `make all`

| Issue | Agent | Owns (files/dirs) | Must not touch | Depends on frozen interface |
|---|---|---|---|---|
| 01 | A | `src/utils/config.py`→`application_config.py`, `src/utils/config_data.py`→`application_config_data.py`, their mirrored `tests/tests_utils/test_*` modules, every `Config()`/`ConfigData` call site in `src`/`tests`/`notebooks`, `make_config_template.mk` | `src/utils/base_config.py`, `src/configurations/`, `config_loader.py`, docs | Rename map (PRD) |

### Wave 2 — blocked by Wave 1 — gate: `make all`

| Issue | Agent | Owns (files/dirs) | Must not touch | Depends on frozen interface |
|---|---|---|---|---|
| 02 | A | `src/utils/base_config.py`→`base_component_config.py`, `src/configurations/watchdog_config.py`, `tests/tests_utils/test_base_config.py`→renamed, `tests/tests_configurations/test_watchdog_config.py` | `src/utils/application_config*.py` (from Wave 1), `config_loader.py`, `watchdog_config_data.py`, docs | Rename map (PRD) |

### Wave 3 — blocked by Wave 2 — gate: `make all-secure`

| Issue | Agent | Owns (files/dirs) | Must not touch | Depends on frozen interface |
|---|---|---|---|---|
| 03 | A | `CONTEXT.md`, `CLAUDE.md`, `docs/adr/0001-*.md`, `docs/adr/0002-*.md`, `docs/CHANGELOG.md`, the two in-code cross-ref docstrings | any `src/`/`tests/` logic (docstring text only) | Final class names from Waves 1–2 |

## Frozen interfaces

None to construct — this is a rename, not new development. The only contract parallel/serial work codes against is the **rename map**, already fixed in [`PRD.md`](./PRD.md):

- `Config` → `ApplicationConfig`; module `config.py` → `application_config.py`.
- `ConfigData` → `ApplicationConfigData`; module `config_data.py` → `application_config_data.py`.
- `BaseConfig` → `BaseComponentConfig`; module `base_config.py` → `base_component_config.py`.
- `WatchdogConfig` `class_name` → `"WatchdogConfig"`.
- Untouched: `config_loader.py` / `load_config`, `WatchdogConfig`/`WatchdogConfigData` names, all behavior.

## Per-agent dispatch specs

### Agent A — Wave 1 — issue 01

- Goal: rename the Application Config family end-to-end, no alias, staying green.
- Scope (OWNS): the two `src/utils` config/config_data modules + their test mirrors; all `Config()`/`ConfigData` references across `src`, `tests`, `notebooks`; `make_config_template.mk`.
- Inputs: rename map (PRD), issue 01.
- Outputs: `ApplicationConfig` / `ApplicationConfigData` in renamed modules; zero surviving `Config`/`ConfigData` symbols; Singleton + `get_data()`/`get_data_as_dict()` behavior unchanged.
- Constraints: must NOT touch `base_config.py`, `src/configurations/`, `config_loader.py`, or docs; must not change any behavior.
- Integration: commit on `feature/config-naming` — gate: `make all`.
- Dispatch: serial (Wave 1 of a linear chain).

### Agent A — Wave 2 — issue 02

- Goal: rename the Component Config base and fix `WatchdogConfig`'s runtime identity + docstrings.
- Scope (OWNS): `base_config.py`→renamed + test mirror; `watchdog_config.py` (base-class ref, `class_name`, docstrings); `test_watchdog_config.py` (new `get_class_name()` assertion).
- Inputs: rename map (PRD), issue 02; Wave 1 already merged.
- Outputs: `BaseComponentConfig`; `WatchdogConfig(name).get_class_name() == "WatchdogConfig"`; load behavior + `config_subfolder="watchdogs"` unchanged.
- Constraints: must NOT touch the Wave 1 `application_config*` modules, `config_loader.py`, or `watchdog_config_data.py`; must not change docs.
- Integration: commit on `feature/config-naming` — gate: `make all`.
- Dispatch: serial (Wave 2; blocked by Wave 1).

### Agent A — Wave 3 — issue 03

- Goal: sweep prose to the new names, history-aware.
- Scope (OWNS): `CONTEXT.md`, `CLAUDE.md`, ADR 0001/0002 (present-tense parentheticals only), `docs/CHANGELOG.md` (append), the two in-code cross-ref docstrings.
- Inputs: final class names from Waves 1–2, issue 03.
- Outputs: living docs name the new classes; ADR narratives byte-for-byte unchanged; one new changelog entry; no stale class-name reference in tracked docs.
- Constraints: must NOT alter any `src`/`tests` logic (docstring text only); must not rewrite ADR decision narrative or prior changelog entries.
- Integration: commit on `feature/config-naming` — gate: `make all-secure`.
- Dispatch: serial (Wave 3; blocked by Waves 1–2).

## Merge order & gates

- Order: **01 → 02 → 03**, one branch, three commits.
- Per-step gate between commits: **`make all`** (mypy + format + lint + docstring + test — the fast pre-push check).
- Final gate before opening the PR: **`make all-secure`** (`make all` + security; exactly what CI runs, matrix 3.11/3.12/3.13).
- Prefer three small commits (one per issue) over one squashed change, so each rename family reviews independently.

## Serial fallback

This *is* the serial plan; parallelism was considered and declined:

- **01 and 02 are technically file-disjoint** — the Application Config family (`config*.py` + its call sites) and the Component Config family (`base_config.py`, `watchdog_config.py`) share no files, so they *could* run as a single 2-agent parallel wave.
- Per the task decision they are **kept sequenced** (01 → 02). If that constraint is later relaxed, collapse Waves 1 and 2 into one parallel wave (max concurrency 2); 03 still trails both. No other change to the plan is needed.
- 03 has a genuine dependency on 01+02 (docs must name the final classes) and can never move earlier.
