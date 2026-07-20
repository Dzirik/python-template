# PRD — P3 implementation (polish)

- **Spec:** `008_SP_asses_repository_architecture_and_quality` / `P3_implementation`
- **Source:** [`../STATUS_REPORT.md`](../STATUS_REPORT.md) §6 **P3 — polish** (the seven items
  explicitly deferred out of P2; see the P2 BRAINSTORM "Out of scope").
- **State:** P0/P1 and P2 are landed. Every item below is scoped against the code as it
  stands at HEAD, since several P3 items reference code those earlier specs reshaped.
- **Label:** `ready-for-agent`

---

## Problem Statement

A developer who clones this template and reads its code as the reference for "how things
are done here" currently hits a tail of small inconsistencies that undercut the template's
one product — being *exemplary* teaching code:

- **Two ways to print in color.** `print_success.py` uses raw ANSI escape codes while the
  rest of the codebase colors console output through `print_in_color` (termcolor). A junior
  copying either one can't tell which is the house mechanism.
- **Teaching code that models non-idiomatic Python.** `date_time_functions` reinvents
  zero-padding by adding a power of ten and slicing the string, parses dates by hand-splitting
  on a literal `"-"` (ignoring its own `sep` parameter) instead of using `strptime`, and its
  docstrings claim a `yyyy-dd-yy` format that isn't what the code produces. This module has
  **no tests at all**, so the behavior isn't even pinned.
- **Supervision tunables are unreachable to operators.** The watchdog's timing constants
  (check interval, grace periods, crash-loop backoff) are hard-coded module globals; an
  operator running a real workload cannot tune them without editing source. The stop `.bat`
  tools make the operator hand-type a PID that the watchdog has already written to disk, the
  WMI respawn path appends to a log that grows without bound, and the checker's force-kill has
  no timeout.
- **Test-suite quality is bimodal in the small.** The logger level tests assert nothing
  ("should not raise"), and `test_exceptions.py` is thirteen near-identical copy-pasted
  functions where one parametrized test would read better and be the house pattern.
- **Housekeeping residue.** Author-personal entries (`ws.sh`, `a.sh`) and phantom paths
  (`archive_gen_01_ma`) linger in `.gitignore`; git hooks are copy-installed so edits to the
  tracked hook scripts silently don't take effect until re-install; `pip-audit` audits the
  installed venv rather than the committed lock, so local and (future) CI can audit different
  dependency closures.
- **Stale onboarding docs.** `TESTING_CHECKLIST.md` still references retired concepts
  ("Python 3.11+", "Minimal Template") and the README still routes new users to it.

Individually trivial; collectively they erode the "clone and immediately start real work at
high quality" promise the vision measures itself against.

## Solution

Ship the P3 polish tail as one focused sweep that leaves the codebase uniformly idiomatic and
the operator/onboarding surfaces honest:

- **One color mechanism.** `print_success.py` stays as the Makefile-facing `success`/`error`
  CLI, but its two functions delegate to `print_in_color` (termcolor). There is exactly one
  coloring implementation in the repo.
- **Idiomatic, tested date/time helpers.** `date_time_functions` uses f-string zero-padding
  and `strptime`, honors its `sep` parameter on both the format and parse sides, and its
  docstrings state the real `yyyy-mm-dd-hh-mm-ss` format. A new test file pins the behavior,
  including a format→parse round-trip.
- **Operator-tunable, self-service supervision.** The watchdog's supervision timings move
  into an **optional `[supervision]` table** in the watchdog Component Config TOML, defaulting
  to today's constants when omitted. The stop `.bat` tools read the watchdog PID from the
  heartbeat directory automatically, the WMI respawn log is capped, the checker's force-kill
  gets a timeout, and the task name is parametrized consistently.
- **Test quality raised to the house bar.** Logger level tests gain real assertions;
  `test_exceptions.py` becomes a single parametrized test; the new date/time and print_success
  tests fill the two remaining behavior gaps; a small unit test pins the WMI-log-cap helper.
- **Clean housekeeping.** `.gitignore` loses the author-personal and phantom entries, `.PHONY`
  is audited for completeness, git hooks install via `core.hooksPath` (auto-updating, no copy),
  and `pip-audit` runs against the exported lock.
- **Honest docs.** `TESTING_CHECKLIST.md` is refreshed (or clearly marked historical) and the
  README pointer updated; the logger-profile root-level divergence is either aligned or
  documented as intentional.

## User Stories

1. As a developer reading the template, I want exactly one console-coloring mechanism, so that
   I can copy the house pattern without guessing which of two is canonical.
2. As a developer, I want `print_success`/`print_error` to produce the same green/red output as
   today, so that the Makefile's success banners are visually unchanged after the refactor.
3. As the maintainer, I want `print_success.py` to keep its `success`/`error` argv CLI, so that
   every existing `Makefile` recipe that shells out to it continues to work untouched.
4. As a developer, I want the date/time helpers to use f-string zero-padding, so that the code
   models the idiom a junior should reach for instead of an arithmetic-and-slice trick.
5. As a developer, I want `convert_string_date_to_datetime` to parse via `strptime`, so that the
   parse path is standard-library-idiomatic and symmetric with the formatting path.
6. As a developer, I want the date/time format and parse functions to honor the `sep` parameter
   on both sides, so that a non-default separator round-trips instead of silently breaking parse.
7. As a developer, I want the date/time docstrings to state the real `yyyy-mm-dd-hh-mm-ss`
   format, so that the documentation matches what the functions actually return.
8. As a developer, I want a test file for the date/time helpers, so that their behavior
   (padding, `sep`, round-trip) is pinned and can't silently regress.
9. As an operator running a real workload, I want to set the watchdog's supervision timings in
   the watchdog config TOML, so that I can tune check interval, grace periods, and crash-loop
   backoff without editing source.
10. As an operator, I want the supervision timings to be optional in the TOML with sensible
    defaults, so that my existing watchdog configs keep working with zero changes.
11. As the maintainer, I want the new supervision config fields covered by the existing schema
    drift-detection test, so that the JSON schema and the NamedTuple tree can't drift apart.
12. As an operator stopping a watchdog, I want the `.bat` tool to read the watchdog PID from the
    heartbeat directory automatically, so that I don't have to look it up and hand-type it.
13. As an operator, I want the stop `.bat` tools to use a consistent, parametrized task name, so
    that the general and per-config tools behave the same way.
14. As an operator relying on WMI respawn, I want the respawn log to be size-capped, so that a
    long-running or flapping watchdog can't fill the disk with an unbounded log.
15. As the maintainer, I want the checker's force-kill call to have a timeout, so that a hung
    `taskkill` can't block the ephemeral checker indefinitely.
16. As a developer, I want the logger level tests to assert observable output, so that they
    prove the level methods actually emit, not merely that they don't raise.
17. As a developer, I want the thirteen exception tests folded into one parametrized test, so
    that the suite matches the "parametrized pytest" house convention the docs claim.
18. As a contributor, I want `.gitignore` free of author-personal (`ws.sh`, `a.sh`) and phantom
    (`archive_gen_01_ma`) entries, so that the ignore file reflects only this project's reality.
19. As a contributor, I want `.PHONY` to list every phony target, so that a stray same-named
    file can never shadow a Make target.
20. As a contributor, I want git hooks installed via `core.hooksPath`, so that edits to the
    tracked hook scripts take effect immediately without a re-install step.
21. As the maintainer, I want `pip-audit` to run against the committed lock, so that local and
    (future) CI audits examine the identical dependency closure.
22. As a new user, I want `TESTING_CHECKLIST.md` to be current (or plainly marked historical),
    so that I'm not led through retired concepts like "Python 3.11+" or "Minimal Template".
23. As the maintainer, I want the logger-profile root levels either aligned or their divergence
    documented, so that the DEBUG/INFO differences across profiles are intentional, not
    accidental.
24. As the maintainer, I want the typo/docstring drift sweep completed ("branche", "does not
    exit", "timerer", "yyyy-dd-yy", "for trades", "Visualizer" stubs, missing private-method
    docstrings), so that the teaching surface reads cleanly.
25. As the maintainer, I want `make all-secure` green after every change, so that the polish
    sweep introduces no regressions in the quality gates.

## Implementation Decisions

### Item 1 — Consolidate color printing
- **Keep `print_success.py` as the Make-facing CLI.** Its `success`/`error` argv dispatch and
  `print_success`/`print_error` public functions remain; the Makefile is unchanged.
- **Delegate coloring to `print_in_color`.** `print_success` → green + bold; `print_error` →
  red + bold, both routed through `print_in_color` (termcolor). The raw ANSI escapes are
  removed. termcolor is available in the subprocess because the recipes run under `uv run`.
- This makes termcolor / `print_in_color` the single coloring mechanism, preserving the
  CLI-vs-library separation.

### Item 2 — Housekeeping (`.gitignore`, `.PHONY`, hooks)
- **`.gitignore`:** remove author-personal entries (`ws.sh`, `a.sh`) and phantom
  `archive_gen_01_ma` paths. Leave the (already-correct) marimo `app` and attributes entries.
- **`.PHONY`:** audit the declaration against the actual target list and add any missing phony
  targets (it is already broadly populated; this is a completeness pass, not a rewrite).
- **Hooks via `core.hooksPath`:** move the tracked `pre-commit`/`pre-push` into a dedicated
  hooks directory and point `git config core.hooksPath` at it, so hook edits auto-apply with no
  copy step. `install-hooks.ps1`/`.sh` collapse to setting the config value; the Makefile's
  OS-detecting `install-hooks` entry stays. Preserve the current onboarding messaging (the
  blocked-commit output that teaches the feature-branch workflow).

### Item 3 — Typos & docstring drift sweep
- Fix the enumerated instances: "branche", "does not exit", "timerer", "yyyy-dd-yy", "for
  trades" (the `helper_functions.py` module docstring leftover), "Visualizer" stub docstrings,
  and the two private methods missing docstrings. Keep the house type-in-text docstring
  convention (per D7). Ruff `D` + `make docstring-check` gate the result.

### Item 4 — `date_time_functions` idioms
- Replace `add_zeros_in_front_and_convert_to_string` usage with f-string zero-padding
  (`f"{n:02d}"`, `f"{micro:06d}"`). The helper may be retired or kept as a thin shim; callers
  move to f-strings regardless.
- `convert_string_date_to_datetime` parses with `datetime.strptime` and **honors `sep`** by
  building the format string from the separator, symmetric with `convert_datetime_to_string_date`.
- Correct the docstrings to the real `yyyy-mm-dd-hh-mm-ss` (`<-micro>`) format.

### Item 5 — Watchdog operator UX
- **Supervision timings → optional `[supervision]` TOML table.** A new `SupervisionTimingData`
  NamedTuple carries the eight tunables, each defaulting to today's module constant.
  `WatchdogConfigData` gains `supervision: SupervisionTimingData = SupervisionTimingData()`, so
  a config that omits the table gets defaults. The watchdog reads timings from config instead of
  module globals. The hand-authored JSON schema gains the new table, and the P2 schema
  drift-detection test extends to cover it automatically. Strict typedload (`failonextra=True`)
  is preserved. The exact table shape (decided in the grill):

  ```toml
  [supervision]              # optional; omitted -> defaults below
  check_interval = 30.0
  startup_grace_period = 5.0
  stop_grace_period = 5.0
  watchdog_healthcheck_interval = 30.0
  backoff_base = 2.0
  backoff_cap = 300.0
  crash_loop_count = 5
  crash_loop_window = 300.0
  ```

- **`.bat` PID auto-read.** The stop tools read `heartbeats_{config_name}/watchdog.pid` and use
  it for the `taskkill`, falling back to a prompt only if the file is missing. The task name is
  parametrized consistently across the general and per-config `.bat` tools.
- **Cap the WMI respawn log.** Before spawning, cap/rotate `watchdog_{config}_wmi.log` so the
  appended redirect can't grow unbounded. Extract the cap logic into a small, unit-testable
  helper.
- **Timeout on the checker force-kill.** Add a `timeout=` to the `taskkill` `subprocess.run` in
  the checker's kill path so a hung kill can't block the ephemeral checker.

### Item 6 — pip-audit against the lock
- Change the audit to run against the exported lock (`uv export ... | pip-audit -r -` or
  equivalent) so the audited closure matches the committed `uv.lock`, aligning local and future
  CI audits. Wired through `make security-check`.

### Item 7 — Test-suite quality + logger profiles + checklist
- **Logger level tests:** add real assertions (capsys/caplog) proving each level method emits.
- **`test_exceptions.py`:** fold the thirteen near-identical description tests into one
  parametrized test over (exception class, error code, description fragment); keep the
  distinct `ExceptionExecutioner` behavior tests as-is.
- **Logger profile root levels:** align the root levels across the five logger profiles, or, if
  the divergence is intentional, document it in the profile comments (decision recorded in the
  issue when the profiles are compared).
- **`TESTING_CHECKLIST.md`:** refresh to current reality (drop "Python 3.11+", "Minimal
  Template") or mark it clearly historical; update the README pointer accordingly.

## Testing Decisions

**What makes a good test here:** exercise the public seam and assert observable behavior
(printed output via `capsys`, returned/parsed values, raised exceptions, config values after
load) — never reach into private implementation detail. Follow the established `tests/` layout
that mirrors `src/` with a `tests_` prefix, and prefer parametrization (the house convention).

**New / strengthened tests (the confirmed "full set"):**

- **`tests/tests_utils/test_date_time_functions.py` (new).** The richest new seam. Assert:
  zero-padding of single-digit month/day/hour/minute/second and 6-digit microseconds; `sep`
  honored in both `convert_datetime_to_string_date` and `convert_string_date_to_datetime`; a
  **format→parse round-trip** returns the original datetime to second (and to microsecond with
  `add_micro=True`); the `create_datetime_id`/`create_date_id` shapes. Seam: the public module
  functions.
- **`tests/tests_utils/test_print_success.py` (new).** Via `capsys`: `print_success` and
  `print_error` each print the given message (color codes may be present or stripped depending
  on TTY, so assert on the message text, mirroring `test_helper_functions.py`'s `print_in_color`
  tests). Seam: the public `print_success`/`print_error` functions.
- **`tests/tests_scripts_production/test_checker.py` (extend).** Unit-test the extracted
  WMI-log-cap helper: a file over the cap is truncated/rotated; a file under the cap is left
  alone; a missing file is a no-op. Pure filesystem behavior, no subprocess.
- **`tests/tests_utils/test_logger.py` (strengthen).** Replace the assertion-free level smoke
  tests with `capsys`/`caplog` assertions that each level method emits at the expected level.
- **`tests/tests_exceptions/test_exceptions.py` (refactor).** Parametrized description test
  replacing the thirteen copies; behavior preserved.
- **Watchdog supervision config:** covered by the existing config-load path and the P2 schema
  drift-detection test (extended to the new `[supervision]` fields); add a focused assertion
  that a TOML omitting `[supervision]` loads the documented defaults and one that sets a value
  overrides it.

**Prior art to follow:**
- `tests/tests_utils/test_helper_functions.py` — `capsys` output assertions for `print_in_color`
  (direct model for the new `print_success` tests).
- The P2 schema drift-detection test (config NamedTuple ↔ JSON-schema parity).
- `tests/tests_scripts_production/test_checker.py` — existing checker unit tests / regression
  scenarios (PID recycling) as the style model for the log-cap helper test.
- ADR-enforcement / parametrized tests already in the suite as the model for the parametrized
  `test_exceptions.py`.

**Pure DX/docs items (no unit tests; verified by `make all-secure` + manual):** `.gitignore`
cleanup, `.PHONY` completeness, `core.hooksPath` install, `pip-audit`-against-lock,
`TESTING_CHECKLIST.md` refresh, and the typo/docstring sweep (gated by ruff `D`).

## Out of Scope

- **D3 phase-2 monitoring wire-up** (`Logger` consumes `ClassInfo`, error codes surfaced,
  `MLModelDescription`'s fate) — remains deferred to the DS/ML migration spec (009+), per the
  P2 BRAINSTORM. P3 does not touch it.
- **Generating** JSON schemas from the NamedTuple tree — P3 extends the drift *test* to the new
  supervision fields; it does not add a generator.
- **A notebook lint gate** — declined in P2 and not revisited here.
- **Rewriting the graceful-stop kill semantics** — the watchdog hardening (backoff, single
  instance, CTRL_BREAK/hard-kill honesty) landed in P0/P1; P3's item-5 work is operator UX
  (timings config, `.bat` PID read, log cap, kill timeout), not the supervision contract.
- **Any behavioral change to `print_in_color`** — it is reused as-is; only `print_success.py`
  is refactored to delegate to it.

## Further Notes

- **Publishing target.** This repo has no git remote (`git remote -v` is empty, confirmed in the
  STATUS_REPORT), so the `specs/` tree is the tracker of record. This PRD is published there as
  `P3_implementation/PRD.md`, matching the 005/007 convention.
- **Grill decisions captured (2026-07-17):** (1) color CLI delegates to `print_in_color`;
  (2) watchdog timings use an optional `[supervision]` NamedTuple table; (3) the full test-seam
  set. These are recorded here so the downstream issues/execution playbook inherit them without
  re-litigating.
- **No new ADR.** None of the P3 decisions changes an architectural invariant. The supervision
  timings move from constants to optional config, but the supervision *semantics* (ADR 0007) are
  unchanged — the defaults reproduce today's behavior exactly.
- **Sequencing note for the execution playbook.** Item 5's `[supervision]` fields touch
  `WatchdogConfigData` + the JSON schema + the drift test; that issue should own those three
  files together. All other P3 items have disjoint file ownership and can run in parallel.
