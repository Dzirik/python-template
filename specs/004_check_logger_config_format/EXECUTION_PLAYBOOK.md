# Execution Playbook — Migrate the Logger profiles to TOML (`dictConfig`)

> Execution map over the ready issues in
> [`specs/004_check_logger_config_format/issues/`](./issues/). It layers a
> parallelization plan on top of the issues; it does not restate or modify them.
> Read each issue for its full scope and acceptance criteria.

## Summary

- **Issues covered:** [#01](./issues/01-core-logger-toml-dictconfig-migration.md),
  [#02](./issues/02-adr-logger-dictconfig-decision.md),
  [#03](./issues/03-documentation-truthfulness-sweep.md).
- **Verdict:** parallel — **2 waves, max concurrency 2**. Ownership is genuinely
  disjoint within each wave; all three issues are AFK, so no wave contains a human
  decision. The parallelism is modest by design — Wave 1 is code-vs-a-single-new-ADR-file.
- **Highest execution risk:** issue #01 is the atomic core — `Logger._load_profile`
  cannot straddle `fileConfig`/INI and `dictConfig`/TOML, so the loader rewrite and
  *all five* profile conversions (plus the `config_file` default flip and its two
  test assertions) must land together and pass `make all-secure` as one unit. Wave 2's
  doc sweep asserts `.conf` is gone repo-wide, so #01 must be **merged** (not just
  written) before Wave 2 fans out.

## Waves

### Wave 1 — gate: `make all-secure` (green on 3.11 / 3.12 / 3.13)

| Issue | Agent | Owns (files/dirs) | Must not touch | Depends on frozen interface |
|---|---|---|---|---|
| [#01](./issues/01-core-logger-toml-dictconfig-migration.md) | A | `src/utils/logger.py`, `src/utils/project_paths.py`, `configurations/loggers/*.toml` (converted; removes the `*.conf`), `tests/tests_utils/test_logger.py`, `tests/tests_utils/test_project_paths.py` | `docs/**`, `CLAUDE.md`, `CONTEXT.md`, `README.md`, `configurations/schemas/**` | — (defines the interfaces) |
| [#02](./issues/02-adr-logger-dictconfig-decision.md) | B | `docs/adr/0004-*.md` (new) | all code, all other docs, `configurations/**` | — (records the already-made decision) |

### Wave 2 — blocked by Wave 1 — gate: `make all-secure` (green on 3.11 / 3.12 / 3.13)

| Issue | Agent | Owns (files/dirs) | Must not touch | Depends on frozen interface |
|---|---|---|---|---|
| [#03](./issues/03-documentation-truthfulness-sweep.md) | C | `CLAUDE.md`, `CONTEXT.md`, `configurations/schemas/README.md`, `README.md`, `docs/CHANGELOG.md` | all code, `configurations/loggers/**`, `docs/adr/**` | Migration end-state (`.conf` retired, TOML/`dictConfig` in use) from #01; links #02 by path |

## Frozen interfaces

- **TOML `dictConfig` profile shape** — the concrete structure of the five
  `configurations/loggers/*.toml` files (`version`, `disable_existing_loggers`,
  `[formatters.*]` / `[handlers.*]` / `[root]` tables, `ext://sys.stdout`, named handler
  keys). Owned by **#01**, frozen by the PRD before Wave 1. Agent C documents the
  end-state; it reads the shape, never edits the profiles.
- **`config_file(name, subfolder=None, extension=".toml")` signature** — the
  default-extension flip from `.conf` to `.toml`. Owned by **#01**; internal to its
  scope (also touches `test_project_paths.py`'s two default-extension assertions).
  Listed so no later agent re-opens it.
- **Migration end-state** — "`.conf` retired repo-wide, Logger loads via
  `logging.config.dictConfig`". Established by **#01**; the precondition Agent C's
  documentation sweep asserts against.

## Per-agent dispatch specs

### Agent A — Wave 1 — issue [#01](./issues/01-core-logger-toml-dictconfig-migration.md)

- **Goal:** switch `Logger`'s profile front-end from `fileConfig`/INI to
  `dictConfig`/TOML and convert all five profiles, atomically, keeping observable
  logging behaviour identical.
- **Scope (OWNS):** `src/utils/logger.py` (rewrite `_load_profile`; delete the
  `FileNotFoundError` retry and `_redirect_file_handlers_to_project_paths()`),
  `src/utils/project_paths.py` (flip `config_file` default to `.toml`, update
  docstring), the five `configurations/loggers/*.toml` profiles (as `dictConfig`
  documents; remove the `.conf` versions), `tests/tests_utils/test_logger.py`
  (regression additions), and `tests/tests_utils/test_project_paths.py` (update the two
  `.conf`→`.toml` default-extension assertions at the `arbitrary_profile` and
  `logger_console` cases).
- **Inputs:** issue #01; the PRD's before/after profile appendix; the existing logging
  behaviour to preserve.
- **Outputs:** `tomllib`-based `_load_profile` with `ProjectPaths().logs` basename
  injection + `dictConfig`; five `.toml` profiles; `config_file` default `.toml`;
  regression test for the rotating handler. Freezes the TOML profile shape and the
  `config_file` signature.
- **Constraints:** must NOT touch `docs/**`, `CLAUDE.md`, `CONTEXT.md`, `README.md`, or
  `configurations/schemas/**`; must NOT import `src.utils.config_loader` or
  `src.utils.application_config` in `logger.py` (ADR 0001 — the config-free import guard
  must stay green); must NOT change logging behaviour (levels, formatter, rotation,
  `root`/named-logger structure, branch-name init line).
- **Integration:** merge to the feature branch — gate: `make all-secure`.
- **Dispatch:** isolated subagent (parallel-safe).

### Agent B — Wave 1 — issue [#02](./issues/02-adr-logger-dictconfig-decision.md)

- **Goal:** record ADR 0004 — the TOML/`dictConfig`-over-INI/`fileConfig` decision and
  its rejected alternatives; close ADR 0003's deferred *Consequences* thread.
- **Scope (OWNS):** `docs/adr/0004-*.md` (new).
- **Inputs:** issue #02; the PRD; ADRs 0001 / 0002 / 0003 (for house style and the
  thread being closed).
- **Outputs:** ADR following the 0001–0003 format with the option comparison, the
  two-front-ends insight, the two retired hacks, the `disable_existing_loggers` gotcha,
  the `.conf`-retirement / ADR-0001 note, and the reversal condition.
- **Constraints:** must NOT touch any code, any other doc, or `configurations/**`;
  codes against the PRD-frozen decision, not Agent A's output, so it is safe in parallel
  with #01.
- **Integration:** merge to the feature branch — gate: `make all-secure` (trivially
  green; docs-only).
- **Dispatch:** isolated subagent (parallel-safe).

### Agent C — Wave 2 — issue [#03](./issues/03-documentation-truthfulness-sweep.md)

- **Goal:** sweep the prose docs so nothing describes the Logger as INI / `fileConfig` /
  `.conf`, and correct the "`.conf` reserved for the Logger" statements now that `.conf`
  is retired repo-wide.
- **Scope (OWNS):** `CLAUDE.md`, `CONTEXT.md`, `configurations/schemas/README.md`,
  `README.md`, `docs/CHANGELOG.md`.
- **Inputs:** issue #03; the migration end-state from #01; ADR 0004 (#02) as a link
  target by stable path.
- **Outputs:** no stale `logger_*.conf` / Logger-`fileConfig` references in tracked
  docs; the schemas-README optional logger-`.conf` file-type guidance revised/removed;
  a CHANGELOG entry recording the migration.
- **Constraints:** must NOT touch any code, `configurations/loggers/**`, or
  `docs/adr/**` (reference ADR 0004 by path only).
- **Integration:** merge to the feature branch — gate: `make all-secure` (docs-only).
- **Dispatch:** isolated subagent (parallel-safe within the wave; sole occupant here).

## Merge order & gates

1. **Wave 1** — fan out A and B in parallel. Merge each behind `make all-secure`;
   prefer two small merges over one batch. Wave 1 is complete only when #01 is merged
   (this establishes the frozen TOML profile shape and the `.conf`-retired end-state).
2. **Gate checkpoint** — run `make all-secure` on the integrated branch before Wave 2
   fans out.
3. **Wave 2** — run C. Merge behind `make all-secure`. C's `grep`-level check (no
   remaining `logger_*.conf` / Logger-`fileConfig` doc references) is the proof the
   sweep is complete.
4. **Final integration gate** — `make all-secure` green on the full Python
   3.11 / 3.12 / 3.13 matrix (exactly what CI runs).

## Serial fallback

Not required — the two waves have disjoint ownership and a single clean freeze point
(#01's TOML profile shape + `.conf`-retired end-state). If isolated worktrees are
unavailable and agents must share one tree, the safe serial order is:
**#01 → #02 → #03** (atomic core first, then the ADR and the doc sweep — both of which
describe the shipped reality — in that order).
