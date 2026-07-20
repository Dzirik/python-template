# Repository Status Report — Architecture & Quality Assessment

- **Date:** 2026-07-15
- **Branch:** `008_asses_repository_architecture_and_quality`
- **Scope:** full sweep — config/env layer, logging & exceptions, notebook ecosystems, tooling & Makefile DX, CI, production supervision, DS-facing code, tests, documentation
- **Lens:** judged against both [`docs/PROJECT_VISION.md`](../../docs/PROJECT_VISION.md) and modern Python ecosystem practice; every core design decision was challengeable
- **Status of findings:** all `file:line` claims were taken from direct code reads; the clean-checkout test failure was reproduced in a clean worktree; the absence of CI runs was verified (`git remote -v` is empty)

---

## 1. Executive summary

The **architectural bones of the template are good and worth keeping.** The config layering (ADRs 0001–0003), the stdlib-first TOML posture, the three-layer supervision architecture, and — the standout pattern in the repo — **ADRs backed by enforcement tests** (AST guards that config never imports Logger; 12 parametrized tests pinning the Python-version policy) all hold up under a challenge-everything review.

The recurring weaknesses are not the architecture. They are:

1. **Documentation that has drifted from the code it teaches.** The README still describes the retired HOCON/`.conf` world in ~19 places; the flagship production tutorial contains wrong file paths that fail verbatim; `CLAUDE.md` contradicts enforced invariants. For a template whose stated product is *docs as onboarding capital*, this directly attacks the vision's single success measure ("clone and immediately start real work").
2. **Quality gates that look strict but don't bite.** CI is not yet live (development is local by intent; a remote comes later) and could not pass as written when it does go live; the 3.14 matrix leg would silently test 3.13; the coverage gate never runs in any automated path; the single doctest file isn't collected; `mypy-f` gives false greens; 2,100+ lines of notebooks sit outside all gates; 32 `pylint` pragmas exist for a linter that isn't installed.
3. **Ceremony built for consumers that were never built — or not yet migrated.** `ExceptionExecutioner`, exception error codes, `MetaClass`/`ClassInfo` descriptions, and the `dashboard` parameter threaded through 10 plot APIs await a monitoring consumer that doesn't exist yet; `BaseTransformer`'s persistence API has real consumers (transformers pending migration into the template) but no in-repo example demonstrates it. (Direction decision: **wire it up**, not strip it — see §5.)

**Headline numbers:** 216 tests, all green in ~23 s on Windows/3.13 · real coverage 34.91 % (branch) · watchdog/heartbeat/visualisations at 0 % coverage · CI not yet live (local development phase; remote planned) · ~19 stale `.conf`/HOCON references in README · Marimo ecosystem: 0 notebooks in 5 folders.

---

## 2. Method

Seven parallel audit passes, one per area, each reading the actual code and docs (not summaries), judging against two yardsticks simultaneously: the project vision (junior onboarding, Windows-first, clone-and-go, one house style) and current Python ecosystem practice (uv-native workflows, sklearn conventions, stdlib logging idioms, supervisor table stakes). Every finding was classified **WELL-DESIGNED / INCONVENIENT / RECONSIDER** and required `file:line` evidence. Load-bearing claims were re-verified: the test suite was run (216/216 pass), coverage measured (34.91 %), the clean-worktree failure reproduced, and the missing git remote confirmed first-hand.

Findings were then discussed with the maintainer; eight direction decisions were made and are recorded in §5. The backlog in §6 reflects those decisions.

---

## 3. Area-by-area assessment

### 3.1 Configuration & environment layer — **sound core, fixable traps**

**Well-designed (keep):**
- `config_loader.py` — one ~40-line tomllib+typedload mechanism serving app/component/logger configs, with distinct, path-rich exceptions for missing file / bad TOML / shape mismatch (`src/utils/config_loader.py:43-65`). Exactly the junior-friendly diagnostics the vision demands.
- Root anchoring per ADR 0002 (`project_paths.py:22-36`: marker-walk from `__file__` + `ENV_PROJECT_ROOT` override), backed by real subprocess CWD-independence tests (`tests/tests_utils/test_cwd_independence.py:57-83`).
- ADR 0001 layering (config never imports Logger), enforced by AST tests (`tests/tests_utils/test_application_config.py:47-62`).
- The typed NamedTuple tree — genuine mypy-strict access (`data.path.data` autocompletes), immutable, dependency-light. A pydantic-settings rewrite was considered and **explicitly rejected**: the pain points are all fixable in place.
- The `envs.py` / `env_constants.py` split with its documented rationale (`src/constants/env_constants.py:1-10`); `.env.example` is self-documenting.

**Problems:**

| Sev | Finding | Evidence |
|---|---|---|
| HIGH | Clean checkout cannot pass the test suite: default profile `python_personal` is git-ignored and only generated by `make create-venv`; reproduced in a clean worktree (3 failures in `test_application_config.py`) | `env_constants.py:22`, `.gitignore:17`, `Makefile:45-50` |
| HIGH | Adding one config key costs 5–7 touch points (three TOMLs, NamedTuple, hand-edited JSON schema, `_replace` pyramid for paths, usage site) and silently breaks every teammate's git-ignored personal profile — no migration story | `schemas/README.md:26-31`, `application_config.py:53-59` |
| MED | typedload runs lax: misspelled/extra keys silently ignored; `"yes"` coerces to `True` (`basiccast=True`, `failonextra=False` defaults) — the exact error class the typed tree exists to catch | `config_loader.py:60` |
| MED | Singleton ordering trap: `Envs.set_config()` after first instantiation is silently ignored; even in-repo code walks the tightrope; no reset seam, forcing tests into subprocesses | `singleton_meta.py:23-26`, `notebooks_executioner.py:72-75` |
| LOW | Paths are stringly (`str`, not `Path`); which fields get root-resolved is hard-coded per field; `getattr(...path, where)` dispatch defeats the typing | `application_config_data.py:13`, `saver_and_loader.py:30` |
| LOW | `ProjectPaths.__init__` mkdirs `logs/` as a side effect; duplicate `_NamedTupleLike` protocol; builtin vs custom exception mix in `base_component_config.py:41` | `project_paths.py:56` |

### 3.2 Logging & exceptions — **good profiles, weak wrapper, unwired ceremony**

**Well-designed (keep):**
- The TOML → `dictConfig` migration (ADR 0004) — stdlib-only, retires the `eval`'d INI args; the log-path rewrite seam (`logger.py:74-77`) makes logs CWD-independent. ADR 0004 itself is a model decision record.
- The architectural decoupling test (`test_logger.py:182-199`) — Logger provably never imports config machinery, enforced in the suite.
- Direct level methods (`Logger().info("x")`) — lower friction than `getLogger` boilerplate for the target audience; five distinct, commented logger profiles is appropriate richness, not bloat.
- Subprocess-isolated Singleton tests with honest docstrings explaining why (`test_logger.py:202-276`).

**Problems:**

| Sev | Finding | Evidence |
|---|---|---|
| HIGH | `datetime.utcfromtimestamp` — deprecated on the supported 3.12+ range — inside the Timer used by every Logger; also mixes UTC (Timer) with local time (echo) | `timer.py:177`, `logger.py:210` |
| HIGH | The wrapper is lossy vs stdlib: no `exception()`/`exc_info`, so the "unified" error path logs **without tracebacks**; production code escapes through `Logger().get()` exactly where logging matters most | `watchdog.py:325,340,359`, `exception_executioner.py:32` |
| HIGH | Heavy import chain: any exception import → Logger → Timer → **pandas** (plus GitPython) — a trivial script raising `NoData` pays a pandas import and requires a git binary | `development_exception.py:6`, `timer.py:8`, `logger.py:15,21` |
| MED | `ExceptionExecutioner`: one call site in all of `src`, zero tests, needs `# type: ignore[call-arg]` to exist, typed `-> None` not `NoReturn`, and contains an `ENV_RUNNING_UNIT_TESTS` branch (test-harness awareness in production code) | `exception_executioner.py:24-32`, `datetime_one_hot_transformer.py:139` |
| MED | Error codes (101–305) are never matched, branched on, or reported anywhere; `CustomException.__init__` never calls `Exception.__init__`, so `exc.args` is empty | `custom_exception.py:18-36` |
| MED | One global logger name — `%(name)s` prints the profile, not the emitting module; `heartbeat.py:12` already breaks the house convention with `logging.getLogger(__name__)` | `logger.py:50` |
| MED | `cover_logger.py` scrapes coverage HTML with BeautifulSoup (a runtime dep for one file; `coverage json` exists) and blocks on interactive `input()` at the end of `make cover` | `cover_logger.py:66,79-80`, `Makefile:508` |
| LOW | `_logger: Any` / `get() -> Any` discards the `logging.Logger` type under the repo's own strict gate; branch-capture failure logs the literal string `"ERROR"`; typos ("branche", "does not exit", "timerer") | `logger.py:35,46,55-56,92,213` |

### 3.3 Notebook ecosystems — **Jupyter functional, Marimo an empty shell**

**Well-designed (keep):**
- py-as-source-of-truth discipline: `jupytext.toml` pairing + per-folder `.ipynb` gitignore + `_ensure_ipynb_from_py()` regeneration (`notebooks_executioner.py:94-113`).
- Config-driven **parallel papermill batch execution** — a real differentiator (`param_ntb_execution` in `python_repo.toml`, HTML export, timing benchmarks).
- `template_notebook_final.py` teaches the house integration (Envs → Logger → ApplicationConfig, papermill `parameters` tag).
- `docs/meta/JUPYTER_ECOSYSTEM.md` — honest migration record with known limitations and workarounds.
- Marimo make-target ergonomics (existence checks, usage text, notebook listing; `Makefile:426-494`).

**Problems:**

| Sev | Finding | Evidence |
|---|---|---|
| HIGH | Marimo is documentation without implementation: all 5 folders contain only `__init__.py`; README claims `marimo/template/` is "pre-configured with common imports" — it contains nothing; one commit ever | `marimo/*/`, `README.md:1944-1961` |
| HIGH | Marimo can't reach `src/`: `make marimo` does `cd marimo && marimo edit`; no template demonstrates the path setup — Config/Logger/Envs are unreachable from Marimo as shipped | `Makefile:432,442,471` |
| MED | Two executioner classes with duplicated, *divergent* logic (output-naming reimplemented, static-name strings differ, batching strategy differs); the "Linux" variant is simply better and would work on Windows (spawn is the Windows default) | `notebooks_executioner_linux.py:47-68` vs `notebooks_executioner.py:125-144` |
| MED | `create_button()` injects jQuery — dead in Notebook 7, the very environment the module claims to support | `notebook_support_functions.py:44-57` |
| MED | Notebooks sit outside all quality gates (ruff/mypy run on `src tests` only); templates contain bare `except:`, duplicated imports, a double `start_timer()` | `Makefile:191,215,231`, `template_notebook_repo.py:53-56` |
| MED | Templates use `<a name>` anchors that the project's own docs declare broken in Notebook 7; `jupyter_server_config.py` lives in git-ignored `.venv/` and no automation recreates it on fresh clones | `template_notebook_final.py:19+`, `JUPYTER_ECOSYSTEM.md:150,184-191` |
| LOW | `.gitignore` mismatches (`/marimo/apps/__marimo__` vs actual `app/`; phantom `archive_gen_01_ma` entries); README's `marimo-convert` recipe pipes `make` output into the `.py` file (corrupt result); "HTML freezes auto-updated" claim has no automation; zero tests for any notebook-support code | `.gitignore:29-47`, `README.md:2035,1799` |

### 3.4 Tooling & Makefile DX — **works, ~40 % duplication, several sharp edges**

**Well-designed (keep):**
- **`make all-secure` == CI, exactly** — perfect local/CI parity is the single best property of the build system (`Makefile:261`, `ci.yml:42`).
- The `-no-clear` pattern (two lines per target, composes into `all`, CI-safe) — the *right* amount of Makefile cleverness.
- Idempotent working-file generation in `create-venv` (`Makefile:44-52`).
- Committed `uv.lock` + `.python-version` — real reproducibility.
- Hook messaging as onboarding capital — the blocked-commit output literally teaches the feature-branch workflow (`scripts/pre-commit:28-49`).
- Ruff configuration quality — broad modern rule families (incl. PD/NPY), every ignore justified inline (`pyproject.toml:93-134`).

**Problems:**

| Sev | Finding | Evidence |
|---|---|---|
| HIGH | `make add-lib` **uninstalls the dev toolchain**: `uv sync --extra windows` is exact and prunes pytest/mypy/ruff/bandit installed by `create-venv`'s `--all-extras` | `Makefile:101,113,126,139` vs `:59` |
| HIGH | `mypy-f` gives false greens: `cd src` + global `ignore_missing_imports = True` turns all `src.*` imports into `Any` — the documented inner loop is weaker than the gate | `Makefile:269`, `mypy.ini:7` |
| MED | `uv run --no-project` never syncs — stale venvs are used silently after lockfile changes; five overlapping sync targets compensate | `Makefile:145-179` |
| MED | ~40 % duplication: `create-venv`/`-linux` differ only in the final echo; six `*-f` targets repeat the same conditional block; docstring-rule flags copy-pasted into 6 recipes | `Makefile:41-85,223-372` |
| MED | `make help` drift: documents nonexistent `make set-up-repo`; wrong override vars for `*-f` targets; bootstrap targets require a system `python` before any venv exists (MS-Store alias trap on fresh Windows) | `README.md:799,909-915`, `Makefile:19,22,42` |
| MED | Dead/duplicated tool config: `[tool.mypy]` in pyproject is never read (Makefile passes `mypy.ini`); strictness lives on the CLI, so direct/IDE mypy runs are weaker than `make mypy`; addopts `--verbose` fights `make test --quiet` | `pyproject.toml:84-87,151`, `Makefile:185` |
| LOW | Hooks installed by copy — never auto-update; `.PHONY` declares only `help`; pip-audit audits the installed venv, not the lock, so local and CI audit different closures; author-personal residue in `.gitignore` (`ws.sh`, `~$attributes.xlsm`, phantom paths) | `install-hooks.ps1:26-30`, `Makefile:6,253`, `.gitignore:20-62` |

*(Note: at HEAD the pip-audit `--ignore-vuln` list is empty — commit `6299150` cleaned it. `CLAUDE.md`'s "specific CVEs are ignored" claim is now stale.)*

### 3.5 CI — **not yet live (by design), but could not pass as written**

Context: development is currently local by intent; the repo will be pushed to a git remote later, at which point CI starts executing. The finding is therefore not that CI hasn't run — that's expected — but that **when it goes live it will fail or mislead unless three defects are fixed first**:

1. **The 3.14 matrix leg would test 3.13.** The committed `.python-version` (pinning 3.13) outranks setup-python's interpreter for `uv sync`; neither `UV_PYTHON` nor setup-uv's `python-version` is set (`ci.yml:26-38`). The version-consistency test checks file *contents*, not the running interpreter, so it cannot catch this. The vision's "must pass on both" constraint is unverified.
2. **A clean checkout fails the suite** (§3.1) — CI runs `uv sync` + `make all-secure` with no config-profile generation step.
3. **No Windows runner** despite Windows-first being guiding principle #1 — the platform the vision calls a hard requirement is the one CI never exercises. The coverage-artifact upload step is dead (nothing produces `coverage/`).

### 3.6 Production supervision — **right architecture, missing supervisor table stakes**

**Well-designed (keep):**
- The three-layer design (ephemeral Task-Scheduler-launched checker → watchdog → workers) genuinely solves "who watches the watchman" (`checker.py:1-9`).
- The **WMI `Win32_Process.Create` escape from the Task Scheduler Job Object**, with a docstring explaining why `CREATE_BREAKAWAY_FROM_JOB` doesn't work (`checker.py:259-288`) — hard-won Windows knowledge captured exactly as the vision demands.
- PID-recycling defense in depth: Popen-handle `poll()` in the watchdog, tasklist + CIM cmdline identity check in the checker, with the regression scenario pinned by a test (`test_checker.py:264-276`).
- **One config system** — `WatchdogConfig` rides the same loader/NamedTuple/schema machinery, not a parallel system.
- `heartbeat.py` — monotonic clock, session reuse, 5 s timeouts, exceptions swallowed and logged; tidy and failure-tolerant.
- Tutorial pedagogy (Session 0 pitfall, 3-day task limit, AC-power condition, `PT1M` XML trick) — real onboarding capital.

**Problems:**

| Sev | Finding | Evidence |
|---|---|---|
| HIGH | Graceful shutdown is illusory on Windows: `Popen.terminate()` *is* `TerminateProcess`; the doc's CTRL_BREAK claim is false (workers aren't started with `CREATE_NEW_PROCESS_GROUP`); the SIGTERM handler never fires on Windows. Workers never run cleanup — data-corruption risk | `watchdog.py:264-289,390`, `PERSISTENT_RUN.md:326-329` |
| HIGH | No restart backoff / crash-loop breaker: a worker that dies instantly is restarted every 30 s forever, silently | `watchdog.py:330-362` |
| HIGH | No single-instance enforcement: Task Scheduler restart-on-failure + checker WMI respawn = two independent respawners for the same config; a race yields duplicate watchdogs and workers | `PERSISTENT_RUN.md:184-185`, `checker.py:259-335`, `watchdog.py:319` |
| HIGH | The flagship tutorial fails verbatim: wrong paths (`src\scripts\watchdog.py` — actual is `scripts_production`), wrong worker filenames, broken link to nonexistent `docs/reports/AUDIT.md`, `winotify` references to a package not in the project | `PERSISTENT_RUN.md:8,34-36,98-99,170-171,260,91,117` |
| MED | `is_process_alive` treats *any* exception (incl. a tasklist timeout) as "dead" → checker `taskkill /F`s a healthy watchdog tree; fail-unsafe in the destructive direction | `checker.py:128-130` |
| MED | Zero tests for `watchdog.py` (149 stmts) and `heartbeat.py` (61 stmts) — the riskiest code in the repo; checker recovery path also untested | coverage data |
| MED | `test_empty_file` has a docstring and **no body** (permanently green); its intended assertions were pasted onto the end of an unrelated test | `test_checker.py:147-149,277-279` |
| MED | Restarted frozen workers inherit their stale `.hb` file → restart churn for slow starters; WMI respawn appends to an unbounded log; supervision timings are hard-coded constants, not config | `watchdog.py:327-356,40-42`, `checker.py:296-303` |
| LOW | Stale `.conf`/HOCON strings in `--help` text and `WatchdogConfig` docstrings; `CLAUDE.md` misidentifies `checker.py` as "the monitored-worker example" (it is the sentinel); worker examples use a CWD-dependent `sys.path` hack and import helpers from `watchdog.py` (side effects on import) | `watchdog.py:124`, `watchdog_config.py:11,16`, `run_cmd_status_print_01.py:14,17` |

### 3.7 DS-facing code — **flagship example superbly tested; base interface has real defects**

**Well-designed (keep):**
- The datetime-encoder test suite: independent one-hot ground truth over two years, 62 fit/predict configuration sweeps, `handle_unknown` and min-interval edge coverage, plus a doctest companion. Exemplary.
- Plotly wrappers add real value: unified palette, rangeselector defaults, anomaly/event/candle overlays, seaborn-matched heatmap, input validation with clear errors in the newer classes.
- `transformer_methods.py` documents its own speculative constants explicitly — the right way to keep forward-looking code.
- Healthy module sizes, clean dependency DAG (no circular-import risk), strict typing throughout.

**Problems** (direction decision: the house `fit`/`predict` interface **stays**; these are the defects to fix within it — see §5):

| Sev | Finding | Evidence |
|---|---|---|
| HIGH | `get_params`/`restore_from_params` is a shared persistence interface consumed by transformers **not yet migrated into this repo** — it must be preserved — but nothing in-repo populates `self._params`: the worked example never demonstrates it, so a junior's save/restore round-trip silently restores nothing and there is no in-repo reference for how migrated transformers should use it | `base_transformer.py:53-66` |
| HIGH | The flagship example violates its own base signature: `fit(data)` → `fit(dt_index, add_hours, …)` with 7 positional args, masked by pylint disables; every migrated transformer will copy this | `datetime_one_hot_transformer.py:164-176` |
| HIGH | `src/data/attributes.py`: module-level CSV read at import time via CWD-relative path, a Windows-only CWD hack "because of the test", and an exception constructed but never raised | `attributes.py:14,82,122-124,169` |
| MED | 32 `# pylint: disable` pragmas across `src` — pylint is absent from pyproject, uv.lock, and the Makefile; `CLAUDE.md` codifies pragmas for a linter that never runs | e.g. `datetime_one_hot_transformer.py:164-166` |
| MED | `dashboard` parameter is a no-op threaded through 10 public plot APIs; all their docstrings misstate the return contract | `plotly_base.py:78-81` |
| MED | `get_colors_for_level` omits the `"vertical_line"` key → runtime `KeyError` when combined with `vertical_lines_positions`; `ATTR_HIGH = "HIGHT"` forces a misspelled column name on users | `visualisation_functions.py:50-58`, `plotly_time_series_base.py:28` |
| MED | Zero tests for the entire `visualisations/` package (~1,300 lines); `inverse` returns `None` and the test enshrines the stub | `datetime_one_hot_transformer.py:234-238` |
| MED | `SaverAndLoader` silently returns empty data when a file exists but is under `min_size` — masks corrupt/truncated files | `saver_and_loader.py:91-95,155-160` |
| LOW | Public typos (`min_inerval` NamedTuple field, `numberical`, "yyyy-dd-yy"); `tuple[float]` where 2-tuples are required; `date_time_functions` reinvents `f"{n:02d}"`/`strptime`; "for trades" docstring leftover; docstring drift in ≥5 places incl. two private methods with no docstring at all | `datetime_one_hot_transformer.py:38,98`, `plotly_histogram.py:37`, `helper_functions.py:2`, `plotly_base.py:60,83` |

### 3.8 Tests — **bimodal: new tests exemplary, old ones assertion-free; big coverage holes**

**Well-designed (keep):**
- ADR-enforcement tests (version policy pinned by 12 parametrized tests; AST architecture guards) — decision-as-executable-guard is the best pattern in the repo.
- Subprocess-based Singleton testing with rationale-rich docstrings (`test_cwd_independence.py:1-17`) — honest, documented, Windows-safe.
- `test_checker.py` encodes a real production incident (infinite restart loop, PID recycling) as regression tests.
- The suite is fast (216 tests / ~23 s) and green on Windows.
- The `conftest.py` session-autouse env mechanism works (with the caveat that it writes `os.environ` directly, bypassing the house `Envs` rule).

**Problems:**

| Sev | Finding | Evidence |
|---|---|---|
| HIGH | Coverage holes at the riskiest spots: `watchdog.py`, `heartbeat.py`, both worker examples, `param_notebook_execution.py`, `attributes.py`, both notebook executioners, and all 16 `visualisations/` modules have no tests at all | coverage run: 34.91 % total |
| MED | The coverage gate (`fail_under=25`) fires only in `make cover`, which nothing runs automatically — decorative. (Direction decision: **drop the gate**, keep `make cover` on-demand — §5) | `pyproject.toml:167`, `Makefile:500-502` |
| MED | The single doctest file runs only via `make test-f` with the right `make_config.mk`; `make test`/CI never collect it — silent-rot risk; `CLAUDE.md` overstates ("run by pytest") | no `--doctest-glob` in pyproject |
| MED | Assertion-free smoke tests (5 logger-level tests: "if we got here, the test passed"); `test_exceptions.py` is 13 near-identical unparametrized functions; `ExceptionExecutioner` — the mandated raising pathway — has zero direct tests | `test_logger.py:40-82` |
| LOW | Parametrization in only 5 of 19 test files despite `CLAUDE.md` calling the tests "parametrized pytest"; stale ".conf" wording in a test docstring | `test_cwd_independence.py:126` |

### 3.9 Documentation — **excellent practice, badly drifted content**

**Well-designed (keep):**
- The ADR practice (0001–0005): consistent front-matter, options-considered-with-rejection-reasons, consequences; ADR 0004 explicitly closes the loop ADR 0003 opened; ADR 0005 is enforced by tests.
- `PROJECT_VISION.md` — a model vision doc (scope, refusals, open questions). `CONTEXT.md` — crisp 54-line glossary with a conflict-resolution rule. `CHANGELOG` entries dated and ADR-cross-linked. No contradictions among these three.
- `CONF_TO_TOML.md` — accurate, maps every TOML construct to the actual NamedTuple shapes.
- Tutorial hand-holding depth (exact Task Scheduler field values, troubleshooting, verification steps) — real onboarding capital *where accurate*.

**Problems:**

| Sev | Finding | Evidence |
|---|---|---|
| HIGH | README config/setup sections describe the retired HOCON world: ~19 `.conf`/HOCON references; claims `create-venv` produces `python_personal.conf` (actual: `.toml`); usage example prints a `"../../data"` value that ADR 0002 banned; says `uv.lock` is "not included" (it is committed); recommends `make all -i` (ignore-errors mode) to juniors | `README.md:48,115-126,170-187,386-392,930-950,1453,111` |
| HIGH | `PERSISTENT_RUN.md` wrong paths/filenames/mechanisms (§3.6) — aimed at non-developers copying exact values | see §3.6 |
| MED | `CLAUDE.md` contradicts enforced invariants: `target-version = py311` (actual py313, pinned by test), the config "candidate path search" claim (removed by ADR 0002), the stale CVE-ignore claim, the checker misdescription, the doctest overstatement | `CLAUDE.md:67` vs `pyproject.toml:91` |
| MED | `TESTING_CHECKLIST.md` (1,884 lines): "Python 3.11+", "Minimal Template" — both retired; README still routes new users to it | `TESTING_CHECKLIST.md:3,14`, `README.md:479` |
| MED | Both scheduler tutorials describe `wmic` while the code uses `Get-CimInstance` and calls wmic deprecated | `PERSISTENT_RUN.md:314`, `checker.py:133-146` |
| LOW | Phantom `docs/LIBRARIES_LIST.md` referenced twice; duplicated "Make Documentation" README section with a raw `@HELP` placeholder; Marimo sections describe phantom content (§3.3) | `README.md:67,371,852-920` |

---

## 4. Cross-cutting themes

1. **Doc drift is systematic, not incidental.** Three migrations (HOCON→TOML, INI→TOML logging, `scripts`→`scripts_production`) each left a residue trail across README, tutorials, docstrings, `--help` text, and `CLAUDE.md`. The repo has no mechanism that makes doc claims fail when code changes — except where it does (ADR 0005's version test), and there the docs stayed true. **Lesson: the enforcement-test pattern works; extend it** (e.g. tests that assert README's documented commands/paths exist).
2. **Gates must actually run to gate.** Local `make all-secure` is real and green; everything downstream of it (CI — dormant until the planned remote exists, coverage, doctests, single-file mypy, notebook lint, pylint pragmas) is partially or wholly unwired. The fix is less about adding rigor than about wiring existing rigor to execution paths — ideally before the remote goes live.
3. **Speculative infrastructure needs a consumer or a deadline.** `ExceptionExecutioner`, error codes, `ClassInfo`, `dashboard` — each adds a concept juniors must learn without removing any work. (`_params` is the exception: its consumers exist as transformers pending migration; what it lacks is an in-repo demonstration.) The maintainer's decision (§5) is to build the consumer (monitoring wired into Logger) alongside the DS/ML migration, which converts this from ceremony into roadmap.
4. **Duplication pairs signal a missing abstraction.** Two notebook executioners, two color-print mechanisms, `-linux` Makefile target pairs, three config profiles with one behavioral difference — each pair diverged after copying. Merge where one implementation demonstrably serves both cases.
5. **Windows-first needs Windows enforcement.** The two deepest Windows-specific claims (graceful stop semantics, CI verification) are exactly where reality diverges from docs. A Windows CI job + honest documentation of kill semantics closes the gap.

---

## 5. Direction decisions (made 2026-07-15, maintainer)

These are recorded so future specs (009+) inherit them without re-litigating:

| # | Decision | Direction |
|---|---|---|
| D1 | Marimo ecosystem | **Commit — build real integration**: a template notebook solving `src/` imports + Config/Logger wiring, a documentation notebook, fixed `.gitignore`. Vision open question #4 is answered "both, for real" — not by deletion. |
| D2 | `BaseTransformer` interface | **Keep the house interface** (`fit`/`predict`/`fit_predict`/`inverse`); fix defects only (example's signature violation, stub `inverse`). `get_params`/`restore_from_params` is a shared interface used by transformers pending migration — **preserve it as-is** and add an in-repo demonstration. sklearn compatibility is a **documented non-goal**. |
| D3 | Monitoring/ceremony layer | **Keep and wire it up**: `ClassInfo` consumed by the Logger, error codes used in reporting, `ExceptionExecutioner` fixed (`NoReturn`, traceback via `exception()`, tests). The consumer arrives with the DS/ML migration. |
| D4 | uv/Make workflow | **Modernize uv-native**: `[tool.uv] package = false`, PEP-735 dependency-groups, plain `uv run` (auto-sync) everywhere, collapse the five sync targets, merge `-linux` pairs. |
| D5 | CI | **Full fix + Windows runner**: correct interpreter selection, clean-checkout pass, add a `windows-latest` job. CI is treated as real, not aspirational. |
| D6 | Config default profile | **Tracked default + overlay**: `DEFAULT_CONFIG` becomes the tracked `python_repo`; `python_personal` becomes an optional git-ignored override layered over it (missing keys fall back). |
| D7 | Docstring convention | **Keep the type-in-text convention** as deliberate house style; fix the drifted instances. |
| D8 | Coverage gate | **Drop `fail_under`**; keep `make cover` as an on-demand report. Coverage improves through targeted tests (watchdog, visualisations), not a threshold. |

---

## 6. Prioritized improvement backlog

Each item is sized S/M/L and is a candidate seed for a future spec folder (009+). Grouping is by priority, not by area.

### P0 — gate integrity & correctness (small, do first)

| Item | Why | Effort |
|---|---|---|
| **Fix CI interpreter selection** (setup-uv `python-version: ${{ matrix.python-version }}` or `UV_PYTHON`; drop setup-python) + add a CI-only assertion that `sys.version_info` matches the matrix | The 3.14 leg currently would test 3.13 — the version constraint is unverified | S |
| **Make clean checkouts pass**: flip `DEFAULT_CONFIG` to tracked `python_repo` (D6, first half) | Fresh clone + CI currently fail 3 tests before any user change | S |
| **Strict typedload**: `basiccast=False, failonextra=True` in `config_loader.py:60` | One line; catches typo'd keys and wrong-typed values loudly | S |
| **Fix `add-lib`/`remove-lib` pruning** (`--all-extras` or move to dependency-groups per D4) | First `make add-lib` currently uninstalls pytest/mypy/ruff | S |
| **Fix `timer.py`**: `datetime.fromtimestamp(ts, tz=timezone.utc)`; make the pandas import local (or drop the DataFrame return) | Deprecation on the supported range; removes pandas from the Logger/exception import chain | S |
| **Fix `test_checker.py`**: give `test_empty_file` its body; remove the misplaced assertions | A permanently-green no-op test masks an intended edge case | S |

### P1 — docs truth & trust gaps

| Item | Why | Effort |
|---|---|---|
| **README sweep**: `.conf`/HOCON → TOML reality, `uv.lock` claim, drop `set-up-repo` docs or add the target, drop `-i` from recommended `make all`, remove `LIBRARIES_LIST.md` refs, dedupe the "Make Documentation" section, fix the Marimo sections to match D1's plan | The highest-traffic onboarding doc actively mis-teaches | M |
| **Tutorial sweep** (`PERSISTENT_RUN.md`, `CHECKER_SCHEDULER_SET_UP.md`): paths, worker filenames, wmic→CIM, timing constants, `winotify`, broken AUDIT.md link | The flagship tutorial fails verbatim for its non-developer audience | S |
| **CLAUDE.md fixes**: py311→py313, candidate-search sentence, CVE-ignore claim, checker description, doctest claim | Contradicts enforced invariants; misleads both humans and AI agents | S |
| **Watchdog hardening**: restart backoff + crash-loop breaker; single-instance guard (reuse the checker's identity check); real graceful stop (`CREATE_NEW_PROCESS_GROUP` + CTRL_BREAK) or honestly document hard-kill semantics; fail-safe `is_process_alive`; touch/delete `.hb` on worker restart | The four trust gaps between "works for demos" and "trust with real workers" | M–L |
| **Logger/exceptions wire-up, phase 1 (per D3)**: add `Logger.exception()`; `ExceptionExecutioner` → `NoReturn`, use `exception()`, add tests, remove the `ENV_RUNNING_UNIT_TESTS` branch; type `get() -> logging.Logger`; stdlib `.git/HEAD` read instead of GitPython (fallback `"unknown"`) | Fixes tracebackless error logs and makes the mandated pathway trustworthy before it's widely consumed | M |
| **uv-native modernization (D4)**: `package = false`, dependency-groups, plain `uv run`, collapse sync targets, merge `-linux` pairs, fix `mypy-f` (run from root; per-module ignore overrides; strictness into the config file; delete the dead `[tool.mypy]` block) | Removes the stale-venv and false-green failure classes wholesale | M |
| **Windows CI job (D5)** | Windows-first without Windows CI is unenforced | M |
| **Marimo real integration (D1)**: template with `src/` imports + Config/Logger, one documentation notebook, `.gitignore` fixes (`apps`→`app`), fix the `marimo-convert` recipe | Converts the empty shell into the promised second ecosystem | M |
| **BaseTransformer defect fixes (D2)**: preserve the `get_params`/`restore_from_params` interface (it serves transformers pending migration) but make the datetime encoder populate `_params` and round-trip it, as the in-repo reference; align the encoder's `fit` with the base signature (options via `__init__` or a config NamedTuple); real `inverse` (sklearn's `inverse_transform` is available); fix `min_inerval`/`numberical` typos; document sklearn-compat as a non-goal | Must land **before** the DS/ML transformer migration copies the flaws | M |
| **Config overlay (D6, second half)**: layer `python_personal.toml` over `python_repo.toml` (missing keys fall back) | Kills the "new key breaks every clone" failure mode | M |

### P2 — wire-up, coverage, consolidation

| Item | Why | Effort |
|---|---|---|
| **Monitoring wire-up design (D3, phase 2)**: `ClassInfo` consumed by the Logger; error codes surfaced in reports; decide what `MLModelDescription` becomes as ML models arrive; rename `MetaClass` (it is an ABC, not a metaclass) | The decided direction — design doc first, alongside the DS/ML migration spec | M–L |
| **Merge the notebook executioners** (keep the spawn/`imap_unordered` implementation, one class, no `platform.system()` branch); automate `jupyter_server_config.py` creation in `create-venv` | Removes ~145 divergent duplicated lines and the biggest silent jupytext friction | S–M |
| **Tests for the untested riskiest code**: extract watchdog decision logic into pure functions + unit tests; heartbeat with a mocked session; visualisation smoke tests (construct each class, assert `go.Figure` + trace counts) | 0 % on the production centerpiece and the largest DS package | M–L |
| **Plotly cleanup**: remove the `dashboard` no-op from 10 APIs; fix return docstrings; `HIGHT`→`HIGH`; add `vertical_line` to `get_colors_for_level`; `tuple[float, float]`; hoist the repeated layout block | Dead API + latent `KeyError` + doc lies in the teaching surface | S–M |
| **Strip the 32 pylint pragmas** and the CLAUDE.md pylint guidance (pylint never runs; mypy+ruff are the gates) | Dead ceremony enforced by imitation | S |
| **Doctest collection**: add `--doctest-glob="*.txt"` so the worked example runs in `make test`/CI | Prevents silent rot; makes the CLAUDE.md claim true | S |
| **Drop `fail_under` (D8)**; delete the dead CI coverage-artifact step; fix `cover_logger.py` (coverage json + stdlib json, no `input()`, drop bs4) | Honest gates only; removes a dependency and an interactive block | S |
| **`attributes.py` fix**: raise the constructed exception; `Path(__file__)`-anchored path; lazy (not import-time) load; move the `.xlsm` out of `src/`; add tests | CWD-dependent import-time side effects in library code | S |
| **Schema drift-check**: test comparing JSON-schema fields to the NamedTuple tree (or generate schemas) | Turns a documented manual chore into an invariant | M |
| **Fix notebook templates**: heading-based anchors, delete/reimplement `create_button()`, remove the Anaconda-era error log, dedupe `template_notebook_repo.py`; decide whether notebooks get a lint gate (ruff `--extend-exclude`-driven relaxed profile) | The teaching surface currently teaches broken navigation | S–M |
| **Singleton ergonomics**: test-only reset seam (`Singleton._instances.clear()` helper) + loud error when `set_config` is called after instantiation | Removes the silent ordering trap and the subprocess-test tax | S |
| **`SaverAndLoader`**: raise (or log loudly) on undersized files instead of returning empty data | Silent data-corruption masking | S |

### P3 — polish

| Item | Why | Effort |
|---|---|---|
| Consolidate color printing (`print_success` vs `print_in_color`/termcolor — one mechanism) | Two mechanisms for one job | S |
| `.gitignore` cleanup (author-personal residue, phantom paths); complete `.PHONY`; hooks via `core.hooksPath` (auto-updating) | Housekeeping | S |
| Typos & docstring drift sweep (per D7: keep convention, fix instances): "branche", "does not exit", "timerer", "yyyy-dd-yy", "for trades", "Visualizer" stubs, missing private-method docstrings | Teaching-quality polish | S |
| `date_time_functions`: f-string zero-padding, `strptime`, honor `sep` | Stdlib idioms in teaching code | S |
| Watchdog operator UX: `.bat` reads PID from the heartbeat dir; parametrize task name; cap the WMI respawn log; `timeout=` on `kill_process`; move supervision timings into the watchdog TOML | Operational polish | S |
| pip-audit against the lock (`uv export | pip-audit -r -`) so local and CI audit the same closure | Consistent audit surface | S |
| Refresh or mark `TESTING_CHECKLIST.md` historical; align logger-profile root levels (or document the DEBUG/INFO divergence); parametrize `test_exceptions.py`; add assertions to logger smoke tests | Long-tail consistency | S–M |

---

## 7. Closing assessment

Measured against the vision's single success metric — *"clone the template and immediately start real data-science work at high quality"* — the template today delivers the **architecture** for that promise but not yet the **experience**: a fresh clone hits failing tests, a README that describes a retired config system, an empty Marimo ecosystem, and a production tutorial with wrong paths. None of these are deep flaws; the P0+P1 backlog is dominated by S/M-effort items, and the repo's own best invention — decisions enforced by tests — is the template for preventing their recurrence. The foundation is worth the investment the backlog describes.
