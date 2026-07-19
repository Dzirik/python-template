# Execution Playbook — Migrate the HOCON config family to TOML

> Execution map over the ready issues in
> [`specs/003_conf_files_form_resolution/issues/`](./issues/). It layers a
> parallelization plan on top of the issues; it does not restate or modify them.
> Read each issue for its full scope and acceptance criteria.

## Summary

- **Issues covered:** [#01](./issues/01-core-toml-migration.md),
  [#02](./issues/02-snapshot-json-round-trip.md),
  [#03](./issues/03-remove-pyhocon-dependency.md),
  [#04](./issues/04-pycharm-schema-and-ide-mapping.md),
  [#05](./issues/05-adr-toml-decision.md),
  [#06](./issues/06-conf-to-toml-tutorial.md),
  [#07](./issues/07-documentation-truthfulness-sweep.md).
- **Verdict:** parallel — **2 waves, max concurrency 4**. Ownership is genuinely
  disjoint within each wave; all seven issues are AFK, so no wave contains a human
  decision.
- **Highest execution risk:** issue #01 is the atomic core — the shared
  `load_config` cannot straddle HOCON and TOML, so the loader swap and *every*
  profile + fixture conversion must land together and pass `make all-secure` as one
  unit. Everything in Wave 2 reads the profile shapes #01 freezes, so #01 must be
  merged (not just written) before Wave 2 fans out.

## Waves

### Wave 1 — gate: `make all-secure` (green on 3.11 / 3.12 / 3.13)

| Issue | Agent | Owns (files/dirs) | Must not touch | Depends on frozen interface |
|---|---|---|---|---|
| [#01](./issues/01-core-toml-migration.md) | A | `src/utils/config_loader.py`, `src/utils/project_paths.py`, `configurations/python_*.toml`, `configurations/watchdogs/*.toml`, `Makefile` (create-venv recipes), `tests/tests_utils/test_{config_loader,application_config,base_component_config,project_paths}.py`, `tests/tests_configurations/test_watchdog_config.py` | `src/data/saver_and_loader.py`, `pyproject.toml`, `uv.lock`, `docs/**` | — (defines the interfaces) |
| [#02](./issues/02-snapshot-json-round-trip.md) | B | `src/data/saver_and_loader.py`, new `tests/tests_data/test_saver_and_loader.py` | `src/utils/**`, `configurations/**`, `pyproject.toml` | — (independent of profile format) |
| [#05](./issues/05-adr-toml-decision.md) | C | `docs/adr/0003-*.md` (new) | all code, all other docs | — (records the already-made decision) |

### Wave 2 — blocked by Wave 1 — gate: `make all-secure` (green on 3.11 / 3.12 / 3.13)

| Issue | Agent | Owns (files/dirs) | Must not touch | Depends on frozen interface |
|---|---|---|---|---|
| [#03](./issues/03-remove-pyhocon-dependency.md) | D | `pyproject.toml`, `uv.lock` | all `src/**`, all `docs/**`, `configurations/**` | *No `pyhocon` import* (from #01+#02) |
| [#04](./issues/04-pycharm-schema-and-ide-mapping.md) | E | `configurations/schemas/*.json` (new), `.idea/` schema mapping (new) | `configurations/*.toml`, `configurations/watchdogs/**`, `src/**` | `ApplicationConfigData` / watchdog shape + `.toml` profile shape (from #01) |
| [#06](./issues/06-conf-to-toml-tutorial.md) | F | `docs/tutorials/CONF_TO_TOML.md` (new) | all other tutorials, all code | `.toml` profile shape (from #01) |
| [#07](./issues/07-documentation-truthfulness-sweep.md) | G | `CLAUDE.md`, `docs/PROJECT_VISION.md`, `CONTEXT.md`, `docs/tutorials/PERSISTENT_RUN.md`, `docs/tutorials/CHECKER_SCHEDULER_SET_UP.md` | `docs/tutorials/CONF_TO_TOML.md`, `docs/adr/**`, all code | Migration end-state (TOML/`tomllib`, `.conf`=logger-only) from #01; links #05 + #06 by path |

## Frozen interfaces

- **Converted TOML profile shape** — the concrete structure of `python_repo.toml`,
  `python_local.toml`, and `watchdog_cmd_0{1,2}.toml`. Owned by **#01**, frozen
  before Wave 2. Agents E (schema) and F (tutorial) mirror/document it; they read it,
  never edit it.
- **`ApplicationConfigData` / watchdog config `NamedTuple` field tree** — unchanged
  by this migration (guaranteed by #01). It is the shape agent E's JSON Schemas
  mirror. Pointer: `src/utils/application_config_data.py`,
  `src/configurations/watchdog_config_data.py`.
- **`config_file(name, subfolder=None, extension=".conf")` signature** — owned by
  **#01**; the per-family extension seam (Config Loader passes `.toml`, Logger keeps
  `.conf`). Internal to #01's scope; listed so no later agent re-opens it.
- **"No module imports `pyhocon`" state** — established jointly by **#01** (loader)
  and **#02** (saver/loader); precondition for agent D to remove the dependency and
  pass `pip-audit`.

## Per-agent dispatch specs

### Agent A — Wave 1 — issue [#01](./issues/01-core-toml-migration.md)

- **Goal:** swap the profile parse-point to `tomllib` and convert every profile the
  shared loader touches to TOML, atomically, keeping typed output identical.
- **Scope (OWNS):** `src/utils/config_loader.py`, `src/utils/project_paths.py`,
  the `configurations/python_*` and `configurations/watchdogs/*` profiles (as
  `.toml`), the create-venv recipes in `Makefile`, and the five config/loader/paths
  test modules listed above.
- **Inputs:** issue #01; the existing `ApplicationConfigData` / watchdog `NamedTuple`
  shapes (to preserve).
- **Outputs:** `tomllib`-based `load_config`; `config_file` extension param; five
  `.toml` profiles + generated personal profile; converted fixtures + malformed-TOML
  fixture. Freezes the TOML profile shape and the `config_file` signature.
- **Constraints:** must NOT touch `src/data/saver_and_loader.py`, `pyproject.toml`,
  `uv.lock`, or any `docs/**`; must NOT change the `ApplicationConfigData` / watchdog
  `NamedTuple` field trees; leave the Logger `.conf` path resolving as `.conf`.
- **Integration:** merge to the feature branch — gate: `make all-secure`.
- **Dispatch:** isolated subagent (parallel-safe).

### Agent B — Wave 1 — issue [#02](./issues/02-snapshot-json-round-trip.md)

- **Goal:** make the config-snapshot round-trip symmetric on stdlib `json` with a
  `.json` extension, dropping the last `pyhocon` import.
- **Scope (OWNS):** `src/data/saver_and_loader.py`; new
  `tests/tests_data/test_saver_and_loader.py`.
- **Inputs:** issue #02.
- **Outputs:** `save_config_data` / `load_config_data` symmetric on `json`, `.json`
  extension, no `pyhocon` import; round-trip equality test asserting the `.json` file.
- **Constraints:** must NOT touch `src/utils/**`, `configurations/**`, or
  `pyproject.toml`; independent of the profile format.
- **Integration:** merge to the feature branch — gate: `make all-secure`.
- **Dispatch:** isolated subagent (parallel-safe).

### Agent C — Wave 1 — issue [#05](./issues/05-adr-toml-decision.md)

- **Goal:** record ADR 0003 — the TOML-over-HOCON decision and its rejected
  alternatives.
- **Scope (OWNS):** `docs/adr/0003-*.md` (new).
- **Inputs:** issue #05; the PRD; ADRs 0001 / 0002 (for house style).
- **Outputs:** ADR following the 0001/0002 format with the four-way comparison,
  `typedload`-orthogonality insight, shared-extension wrinkle, dismissed
  custom-extension argument, and reversal condition.
- **Constraints:** must NOT touch any code or any other doc.
- **Integration:** merge to the feature branch — gate: `make all-secure` (trivially
  green; docs-only).
- **Dispatch:** isolated subagent (parallel-safe).

### Agent D — Wave 2 — issue [#03](./issues/03-remove-pyhocon-dependency.md)

- **Goal:** remove `pyhocon` and its deprecation-warning filters now that nothing
  imports it.
- **Scope (OWNS):** `pyproject.toml`, `uv.lock`.
- **Inputs:** issue #03; the frozen "no `pyhocon` import" state from #01 + #02.
- **Outputs:** `pyhocon` removed via `make remove-lib`; the two
  `pyhocon`/`pyparsing` `filterwarnings` entries deleted.
- **Constraints:** must NOT touch any `src/**`, `docs/**`, or `configurations/**`;
  never hand-edit `uv.lock`.
- **Integration:** merge to the feature branch — gate: `make all-secure` (incl.
  `pip-audit`, `bandit`).
- **Dispatch:** isolated subagent (parallel-safe).

### Agent E — Wave 2 — issue [#04](./issues/04-pycharm-schema-and-ide-mapping.md)

- **Goal:** add JSON Schemas + a shared PyCharm mapping so `.toml` profiles validate
  and autocomplete in-IDE.
- **Scope (OWNS):** `configurations/schemas/*.json` (new); the `.idea/` JSON-Schema
  mapping (new).
- **Inputs:** issue #04; the frozen `ApplicationConfigData` / watchdog shape and the
  `.toml` profile shape from #01.
- **Outputs:** application + watchdog schemas mirroring the `NamedTuple` shapes; a
  version-controlled schema mapping; logger-`.conf`→INI guidance; the sync-maintenance
  note.
- **Constraints:** must NOT touch the `.toml` profiles themselves or any `src/**`.
- **Integration:** merge to the feature branch — gate: `make all-secure` (committed
  schema/IDE files do not affect the Python gate).
- **Dispatch:** isolated subagent (parallel-safe).

### Agent F — Wave 2 — issue [#06](./issues/06-conf-to-toml-tutorial.md)

- **Goal:** write the `CONF_TO_TOML.md` authoring tutorial in house tutorial style.
- **Scope (OWNS):** `docs/tutorials/CONF_TO_TOML.md` (new).
- **Inputs:** issue #06; the frozen `.toml` profile shapes from #01; the PRD's
  before/after appendix.
- **Outputs:** tutorial covering scalars, arrays, tables/inline tables, nested tables,
  `[[array-of-tables]]` + inline-table-in-array, comments, and the HOCON→TOML
  cheat-sheet.
- **Constraints:** must NOT touch the other tutorials or any code; snippets must match
  #01's actual converted profiles.
- **Integration:** merge to the feature branch — gate: `make all-secure` (docs-only).
- **Dispatch:** isolated subagent (parallel-safe).

### Agent G — Wave 2 — issue [#07](./issues/07-documentation-truthfulness-sweep.md)

- **Goal:** sweep the prose docs from HOCON to TOML and de-pin `.conf` from the
  config-profile glossary terms.
- **Scope (OWNS):** `CLAUDE.md`, `docs/PROJECT_VISION.md`, `CONTEXT.md`,
  `docs/tutorials/PERSISTENT_RUN.md`, `docs/tutorials/CHECKER_SCHEDULER_SET_UP.md`.
- **Inputs:** issue #07; the migration end-state from #01; ADR 0003 (#05) and
  `CONF_TO_TOML.md` (#06) as link targets by stable path.
- **Outputs:** no stale HOCON/`pyhocon` references (except deliberate history);
  four glossary entries de-pinned from `.conf`; pointers to ADR 0003 and the tutorial.
- **Constraints:** must NOT edit `docs/tutorials/CONF_TO_TOML.md` (owned by F) or
  `docs/adr/**` (owned by C) — reference them by path only; must NOT touch code.
- **Integration:** merge to the feature branch — gate: `make all-secure` (docs-only).
- **Dispatch:** isolated subagent (parallel-safe).

## Merge order & gates

1. **Wave 1** — fan out A, B, C in parallel. Merge each behind `make all-secure`;
   prefer three small merges over one batch. Wave 1 is complete only when #01 and #02
   are both merged (this establishes the frozen TOML shape and the no-`pyhocon`-import
   state).
2. **Gate checkpoint** — run `make all-secure` on the integrated branch before Wave 2
   fans out.
3. **Wave 2** — fan out D, E, F, G in parallel. Merge each behind `make all-secure`.
   D's `pip-audit` pass is the proof that the `pyhocon` removal is complete.
4. **Final integration gate** — `make all-secure` green on the full Python
   3.11 / 3.12 / 3.13 matrix (exactly what CI runs).

## Serial fallback

Not required — the two waves have disjoint ownership and a single clean freeze point
(#01's TOML profile shape). If isolated worktrees are unavailable and agents must share
one tree, the safe serial order is: **#01 → #02 → #05 → #03 → #04 → #06 → #07** (core
first, then its independent Wave-1 peers, then the pyhocon removal once both importers
are gone, then the three #01-dependent deliverables in any order).
