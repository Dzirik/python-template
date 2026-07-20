# Execution Playbook — P3 implementation (polish)

Map over the seven ready issues in [`issues/`](issues/). Consumes the blocked-by graph and
scope boundaries from those issues **as given** (all seven declare no blockers); layers an
execution map on top. Does not restate issue bodies — read each issue for its acceptance
criteria.

## Summary

- **Issues covered:** [01](issues/01-color-print-consolidation.md), [02](issues/02-date-time-functions-idioms.md),
  [03](issues/03-typo-docstring-sweep.md), [04](issues/04-watchdog-operator-ux.md),
  [05](issues/05-test-suite-quality.md), [06](issues/06-logger-profiles-and-onboarding-docs.md),
  [07](issues/07-dx-tooling.md).
- **Verdict:** parallel — **2 waves, max concurrency 6**. Six file-disjoint slices fan out in
  Wave 1; the repo-wide docstring sweep (03) runs alone in Wave 2 *after* Wave 1 merges, so it
  never races the slices whose files it must not touch.
- **Highest execution risk:** the typo/docstring sweep (03) is repo-wide by nature. Its
  **by-file must-not-touch boundary is load-bearing** — it must not edit docstrings in files
  owned by 01/02/04 even when it spots a stray typo there. Isolating it to Wave 2 removes the
  collision risk entirely; the boundary still governs which files it may open.

## Waves

### Wave 1 — gate: `make all-secure` (per branch, and on the merged tree)

Six isolated, parallel-safe subagents. Ownership is fully disjoint — verified no two agents
share a file or directory.

| Issue | Agent | Owns (files/dirs) | Must not touch | Depends on frozen interface |
|---|---|---|---|---|
| [01](issues/01-color-print-consolidation.md) | A | `src/utils/print_success.py`; **new** `tests/tests_utils/test_print_success.py` | `src/utils/helper_functions.py` (imports `print_in_color`, does not edit it) | none |
| [02](issues/02-date-time-functions-idioms.md) | B | `src/utils/date_time_functions.py` (incl. **all** its docstrings, the `yyyy-dd-yy` fix); **new** `tests/tests_utils/test_date_time_functions.py` | any file outside its two | none |
| [04](issues/04-watchdog-operator-ux.md) | D | `src/configurations/watchdog_config_data.py`, `watchdog_config.py`; `configurations/schemas/watchdog_config.schema.json`; `tests/tests_utils/test_config_schema_drift.py`; `src/scripts_production/{watchdog,checker}.py`, `stop_watchdog_cmd_02.bat`, `stop_watchdog_general.bat`; `tests/tests_scripts_production/test_checker.py` | any file outside its set; must not change ADR-0007 supervision *semantics* | none (owns `SupervisionTimingData` end-to-end itself) |
| [05](issues/05-test-suite-quality.md) | E | `tests/tests_utils/test_logger.py`, `tests/tests_exceptions/test_exceptions.py` | `src/utils/logger.py` (its docstrings belong to 03), any production code | none |
| [06](issues/06-logger-profiles-and-onboarding-docs.md) | F | `configurations/loggers/logger_*.toml` (all five); `TESTING_CHECKLIST.md`; the single README pointer line to it | `src/utils/logger.py`, test files, `Makefile` | none |
| [07](issues/07-dx-tooling.md) | G | `.gitignore`; `Makefile`; `scripts/install-hooks.ps1`, `install-hooks.sh`, `pre-commit`, `pre-push` | any file outside its set; no other slice edits the `Makefile` | none |

### Wave 2 — blocked by Wave 1 (all six merged + green) — gate: `make all-secure`

One serial subagent. Runs after Wave 1 so the files whose docstrings it must **not** own
(`date_time_functions.py`, `print_success.py`, watchdog/checker) already hold their final text.

| Issue | Agent | Owns (files/dirs) | Must not touch | Depends on frozen interface |
|---|---|---|---|---|
| [03](issues/03-typo-docstring-sweep.md) | C | *docstrings only* in `src/utils/helper_functions.py`, `logger.py`, `timer.py`, and `src/visualisations/*.py`; the two flagged missing private-method docstrings | `src/utils/date_time_functions.py` (02), `src/utils/print_success.py` (01), `src/scripts_production/watchdog.py` + `checker.py` (04) — even to fix a typo | none |

## Frozen interfaces

- **None across agents.** No slice consumes another slice's output, so there is no cross-agent
  contract to freeze — this is *why* single-wave parallelism is safe for Wave 1.
- `SupervisionTimingData` (the eight-field NamedTuple + its JSON-schema table + the drift-test
  parity) is **internal to Agent D**, which owns the NamedTuple, the schema, and the drift test
  together per the PRD sequencing note. It is not a shared interface.

## Per-agent dispatch specs

### Agent A — Wave 1 — issue [01](issues/01-color-print-consolidation.md)
- Goal: make `print_in_color` (termcolor) the single console-coloring mechanism; `print_success`/`print_error` delegate to it (green+bold / red+bold), dropping raw ANSI.
- Scope (OWNS): `src/utils/print_success.py`; **new** `tests/tests_utils/test_print_success.py`.
- Inputs: issue #01; `print_in_color` reused as-is; `test_helper_functions.py` as the `capsys` test model.
- Outputs: refactored CLI (argv + both signatures unchanged); new `capsys` test.
- Constraints: must NOT touch `helper_functions.py` or any `Makefile` recipe.
- Integration: merge to integration branch — gate: `make all-secure`.
- Dispatch: isolated subagent (parallel-safe).

### Agent B — Wave 1 — issue [02](issues/02-date-time-functions-idioms.md)
- Goal: idiomatic f-string zero-padding + `strptime` parsing that honors `sep`; truthful `yyyy-mm-dd-hh-mm-ss` docstrings; pin behavior with a new test.
- Scope (OWNS): `src/utils/date_time_functions.py` (incl. **all** its docstrings); **new** `tests/tests_utils/test_date_time_functions.py`.
- Inputs: issue #02; house docstring convention (D7).
- Outputs: rewritten module; parametrized round-trip test.
- Constraints: owns the `yyyy-dd-yy` fix (03 will not); touch nothing else.
- Integration: merge — gate: `make all-secure`.
- Dispatch: isolated subagent (parallel-safe).

### Agent D — Wave 1 — issue [04](issues/04-watchdog-operator-ux.md)
- Goal: operator-tunable supervision via optional `[supervision]` TOML table; `.bat` PID auto-read; capped WMI respawn log (extracted helper); `timeout=` on checker force-kill.
- Scope (OWNS): the watchdog config trio (`watchdog_config_data.py`, `watchdog_config.schema.json`, `test_config_schema_drift.py`) **together**, plus `watchdog_config.py`, `scripts_production/{watchdog,checker}.py`, both `stop_watchdog_*.bat`, `test_checker.py`.
- Inputs: issue #04 (exact 8-field table shape); ADR 0007 (semantics unchanged); P2 drift test as extension point.
- Outputs: `SupervisionTimingData` NamedTuple w/ defaults = today's constants; schema + drift-test parity; omit-→-defaults and set-→-override tests; log-cap helper unit test.
- Constraints: preserve strict typedload (`failonextra=True`); do not change graceful-stop kill contract; touch nothing outside the set.
- Integration: merge — gate: `make all-secure`.
- Dispatch: isolated subagent (parallel-safe).

### Agent E — Wave 1 — issue [05](issues/05-test-suite-quality.md)
- Goal: real level assertions in `test_logger.py`; fold 13 exception-description tests into one parametrized test (keep the distinct `ExceptionExecutioner` behavior tests).
- Scope (OWNS): `tests/tests_utils/test_logger.py`, `tests/tests_exceptions/test_exceptions.py`.
- Inputs: issue #05; session-autouse `conftest.py` (`ENV_LOGGER=logger_console`, root `DEBUG`).
- Outputs: `capsys`/`caplog` level assertions; parametrized exception test with equivalent coverage.
- Constraints: no production code; do not touch `logger.py`. **Assumes `logger_console` root stays `DEBUG`** (see the 05↔06 coordination note under Merge order).
- Integration: merge — gate: `make all-secure`.
- Dispatch: isolated subagent (parallel-safe).

### Agent F — Wave 1 — issue [06](issues/06-logger-profiles-and-onboarding-docs.md)
- Goal: make logger-profile root levels intentional (align or document divergence); refresh/retire `TESTING_CHECKLIST.md` and its README pointer.
- Scope (OWNS): five `configurations/loggers/logger_*.toml`; `TESTING_CHECKLIST.md`; the single README pointer line.
- Inputs: issue #06; current root levels (all five are `DEBUG` at root today).
- Outputs: aligned-or-commented root levels (decision recorded in issue #06); refreshed checklist; updated README pointer.
- Constraints: **must keep `logger_console.toml` root at `DEBUG`** — Agent E's strengthened level tests assert `debug` emission under `logger_console`. Do not touch `logger.py`, test files, or the `Makefile`.
- Integration: merge — gate: `make all-secure`.
- Dispatch: isolated subagent (parallel-safe).

### Agent G — Wave 1 — issue [07](issues/07-dx-tooling.md)
- Goal: `.gitignore` cleanup; `.PHONY` completeness pass; hooks via `core.hooksPath`; `pip-audit` against the exported lock.
- Scope (OWNS): `.gitignore`; `Makefile`; `scripts/install-hooks.{ps1,sh}`; `scripts/pre-commit`, `scripts/pre-push`.
- Inputs: issue #07.
- Outputs: cleaned ignore file; complete `.PHONY`; OS-detecting `core.hooksPath` install (onboarding message preserved); `security-check` audits the `uv.lock` closure.
- Constraints: sole editor of the `Makefile`; preserve pre-commit branch-block + pre-push security behavior.
- Integration: merge — gate: `make all-secure`.
- Dispatch: isolated subagent (parallel-safe).

### Agent C — Wave 2 — issue [03](issues/03-typo-docstring-sweep.md)
- Goal: teaching-quality typo/docstring-drift sweep ("branche", "does not exit", "timerer", "for trades", "Visualizer" stubs) + two missing private-method docstrings, house convention.
- Scope (OWNS): docstrings only in `helper_functions.py`, `logger.py`, `timer.py`, `visualisations/*.py`; the two flagged private methods.
- Inputs: issue #03; house docstring convention (D7); Wave 1 already merged (target files at final state).
- Outputs: corrected docstrings; `make docstring-check` green.
- Constraints: must NOT touch `date_time_functions.py` (02), `print_success.py` (01), or `watchdog.py`/`checker.py` (04) — even to fix a spotted typo. By-file boundary is absolute.
- Integration: merge onto the Wave-1-integrated tree — gate: `make all-secure`.
- Dispatch: serial (runs alone, after Wave 1).

## Merge order & gates

1. **Wave 1** — Agents A, B, D, E, F, G run concurrently on isolated branches. Each must be
   green on `make all-secure` before its branch merges. Prefer six small merges as each finishes
   over one big integration event; ownership is disjoint so merges should not textually conflict.
2. **Wave 1 integration gate** — run `make all-secure` on the merged tree. This is where the
   **05↔06 coordination** is verified: Agent E's level assertions must pass against Agent F's
   final `logger_console.toml` (kept at root `DEBUG`). If it fails here, the fix is a one-line
   root-level correction in `logger_console.toml`.
3. **Wave 2** — Agent C (issue 03) runs alone against the integrated tree, then merges.
4. **Final integration gate** — `make all-secure` green on the fully merged tree (exactly what
   CI runs: `{ubuntu, windows} × {py3.13, 3.14}`).

## Serial fallback

Not needed for Wave 1 — ownership is provably disjoint. The one partial serialization already
applied is issue 03 → Wave 2, chosen to keep the repo-wide docstring sweep from ever racing the
slices whose files it must not touch. If any Wave-1 branch turns out to need a change in a file
another slice owns (unexpected, given the boundaries), stop and serialize that pair rather than
widening an agent's ownership mid-wave.
