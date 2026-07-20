# Docs truth sweep

> **Status:** `ready-for-agent`

## Parent

[`../BRAINSTORM.md`](../BRAINSTORM.md) — P0+P1 implementation. Report items: P1 README sweep,
tutorial sweep, CLAUDE.md fixes (§3.9, §3.6, §4). Runs **last** — it describes the post-change
reality produced by issues 01–07.

## What to build

Bring the highest-traffic onboarding docs back in line with the code, and with the decisions
made in this spec. Three migrations (HOCON→TOML, INI→TOML logging, `scripts`→`scripts_production`)
plus this spec's changes left a residue trail; fix it so the docs stop mis-teaching.

1. **`README.md`**
   - Replace the ~19 `.conf`/HOCON references with the TOML reality; `create-venv` produces
     `python_personal.toml` (a minimal overlay template), not `.conf`.
   - Document the new config model: `python_repo` is the tracked default/base; `python_personal`
     is an opt-in partial overlay (link ADR 0006).
   - Fix the stale claims: `uv.lock` **is** committed; remove the `"../../data"` usage-example
     value (ADR 0002 banned it); drop the recommendation of `make all -i`.
   - Document the uv-native workflow (plain `uv run`, `make sync`/`lock`, dependency-groups,
     `add-lib`/`remove-lib` on groups) and the CI matrix (ubuntu+windows × 3.13/3.14).
   - Drop `set-up-repo` docs (target doesn't exist) or note its replacement; remove the phantom
     `LIBRARIES_LIST.md` references; dedupe the duplicated "Make Documentation" section and its
     raw `@HELP` placeholder.
   - Rewrite the Marimo sections to describe issue 07's real content (template + documentation
     notebooks, the bootstrap, `marimo-convert -o`); fix the corrupt `marimo-convert` recipe
     example.
2. **`docs/tutorials/PERSISTENT_RUN.md` + `docs/tutorials/CHECKER_SCHEDULER_SET_UP.md`**
   - Fix wrong paths (`src\scripts\watchdog.py` → `src\scripts_production\watchdog.py`), wrong
     worker filenames, the broken `docs/reports/AUDIT.md` link, and the `winotify` references
     (package not in the project).
   - `wmic` → `Get-CimInstance` (the code uses CIM; `wmic` is deprecated).
   - Update the stop semantics to ADR 0007: real graceful stop via `CTRL_BREAK` + the worker
     signal contract (remove any remaining false/again-outdated claims), and the new
     backoff/crash-loop/single-instance behavior.
3. **`CLAUDE.md`** — fix the contradictions with enforced invariants: `target-version = py311` →
   `py313`; remove the removed "candidate path search" sentence; drop the stale "specific CVEs are
   ignored" claim; correct the checker description (it is the sentinel, not "the monitored-worker
   example"); soften the doctest "run by pytest" overstatement. Add the new realities: uv-native
   workflow (plain `uv run`, dependency-groups, `make sync`/`lock`), the config base/overlay model
   (link ADR 0006), and the watchdog semantics (link ADR 0007).
4. **`docs/meta/TESTING_CHECKLIST.md`** — stop routing new users to it from the README; add a
   one-line "historical — Python 3.11+/Minimal-Template references are retired" banner (a full
   refresh is deferred to P3).

## Scope

- **OWNS:** `README.md`, `docs/tutorials/PERSISTENT_RUN.md`,
  `docs/tutorials/CHECKER_SCHEDULER_SET_UP.md`, `CLAUDE.md`,
  `docs/meta/TESTING_CHECKLIST.md` (banner + README routing only).

## Acceptance criteria

- [ ] No `.conf`/HOCON references remain in README/CLAUDE.md config sections; the config model
      described matches ADR 0006.
- [ ] `PERSISTENT_RUN.md` runs verbatim: correct `scripts_production` paths, worker filenames,
      CIM not wmic, no `winotify`, no broken AUDIT.md link; stop semantics match ADR 0007.
- [ ] `CLAUDE.md` states `py313`, no candidate-search/CVE-ignore/doctest overstatements, correct
      checker role, and documents the uv workflow + config/watchdog models.
- [ ] README documents the uv-native workflow, the CI matrix, and the real Marimo ecosystem;
      no `LIBRARIES_LIST.md`/`set-up-repo` phantoms; no duplicated Make section.
- [ ] `make all-secure` green (docs-only, but the repo must still gate clean).

## Blocked by

- **Issues 01–07** — the docs describe the post-change reality; this is the final wave.
