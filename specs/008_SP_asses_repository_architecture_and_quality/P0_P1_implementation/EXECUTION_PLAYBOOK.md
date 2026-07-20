# Execution Playbook — P0 + P1 implementation

## Summary

- **Issues covered:** [01](./issues/01-config-tracked-base-and-overlay.md),
  [02](./issues/02-uv-native-workflow.md),
  [03](./issues/03-ci-interpreter-and-windows-matrix.md),
  [04](./issues/04-logger-exceptions-timer-wireup.md),
  [05](./issues/05-production-supervision-hardening.md),
  [06](./issues/06-base-transformer-defects.md),
  [07](./issues/07-marimo-real-integration.md),
  [08](./issues/08-docs-truth-sweep.md)
- **Verdict:** **Waved parallel.** Wave 1 (01, 04, 05, 06, 07) has disjoint file ownership and
  runs concurrently (max concurrency 5). Wave 2 (02) is the manifest/Makefile integrator and
  waits for 04. Wave 3 (03) is CI and waits for 01+02. Wave 4 (08) is docs and waits for
  everything.
- **Highest execution risk:** `pyproject.toml`/`uv.lock`/`Makefile` are single-owned by issue
  02, which folds in interface requirements *specified* by 01 and 07. If a Wave-1 issue quietly
  edits one of those files, the wave collides. Mitigation: the ownership map below is
  authoritative — Wave-1 issues state their Makefile/manifest needs as interfaces for 02 and
  never touch those files themselves.

## Waves

| Wave | Issues | Concurrency | Gate |
|---|---|---|---|
| 1 | 01, 04, 05, 06, 07 | up to 5 | `make all` per issue |
| 2 | 02 | 1 | `make all-secure` |
| 3 | 03 | 1 | `make all-secure` (locally; CI is the real proof once remote) |
| 4 | 08 | 1 | `make all-secure` |

### Why the waves

- **Wave 1** — five independent code areas: config (`utils/config_loader`, `application_config`,
  `constants`), logger/timer/exceptions (`utils/{timer,logger,cover_logger,helper_functions}`,
  `exceptions/`), supervision (`scripts_production/`), transformer (`transformations/`), marimo
  (`marimo/`, `.gitignore`). No shared files (see map). Cross-behaviour couplings (05 uses
  `Logger`, 06 calls `ExceptionExecutioner`) are order-independent at the file level.
- **Wave 2 after 04** — issue 02 drops the `gitpython` dependency and re-locks; that is only safe
  once 04 has removed the last `import git`. 02 also implements the create-venv personal-template
  (01's interface) and the playground-marimo copy + `marimo-convert -o` (07's interface).
- **Wave 3 after 01+02** — CI needs a clean checkout to pass (01) and invokes the new uv-native
  `make all-secure` (02).
- **Wave 4 after all** — the docs sweep describes the post-change reality.

## File-ownership map

| Issue | OWNS (writes) | Notes |
|---|---|---|
| 01 | `constants/env_constants.py`, `utils/config_loader.py`, `utils/application_config.py`, `.env.example`, `configurations/python_repo.toml`, `configurations/python_local.toml`, `tests_utils/test_config_loader.py`, `tests_utils/test_application_config.py`, `docs/adr/0006-*.md` | Does NOT touch Makefile/pyproject |
| 04 | `utils/timer.py`, `utils/logger.py`, `utils/cover_logger.py`, `utils/helper_functions.py`, `exceptions/exception_executioner.py`, `tests_utils/test_timer.py`, `tests_utils/test_logger.py`, `tests_exceptions/test_exceptions.py` | Leaves `gitpython` declared-but-unused for 02 |
| 05 | `scripts_production/watchdog.py`, `scripts_production/checker.py`, `scripts_production/run_cmd_status_print_01.py`, `scripts_production/run_cmd_status_print_02.py`, `configurations/watchdog_config.py` (docstring), `tests_scripts_production/test_checker.py`, `tests_scripts_production/test_watchdog.py` (new), `docs/adr/0007-*.md` | — |
| 06 | `transformations/datetime_one_hot_transformer.py`, `transformations/base_transformer.py`, `tests_transformations/test_datetime_one_hot_transformer.py`, `tests_transformations/test_datetime_one_hot_transformer.txt` | CONTEXT.md already updated (grill) |
| 07 | `marimo/template/*.py` (new), `marimo/documentation/*.py` (new), `.gitignore` (Marimo section) | Makefile bits are 02's |
| 02 | `pyproject.toml`, `uv.lock`, `Makefile`, `mypy.ini`, `scripts/install-hooks.ps1`, `scripts/install-hooks.sh` | Single owner of all manifest/Makefile edits |
| 03 | `.github/workflows/ci.yml`, `tests_utils/test_python_version_consistency.py` | — |
| 08 | `README.md`, `docs/tutorials/PERSISTENT_RUN.md`, `docs/tutorials/CHECKER_SCHEDULER_SET_UP.md`, `CLAUDE.md`, `docs/meta/TESTING_CHECKLIST.md` | — |

**Collision summary:** no two same-wave issues share a file. The only cross-wave contention is
the manifest/Makefile trio, resolved by single-owning it in 02 and passing 01/07 requirements as
interfaces.

## Frozen interfaces

- **`load_config(config_name, target, subfolder=None, base_name=None)`** — the overlay seam.
  Owned by 01, frozen once Wave 1 lands. Component/logger callers pass no `base_name`.
- **`get_git_branch() -> str`** in `utils/helper_functions.py` — owned by 04; 02 relies on it
  existing (no `import git` left) before dropping the dependency.
- **`configurations/python_personal.toml` template content** — specified by 01/ADR 0006,
  implemented by 02 in `create-venv`. Minimal commented overlay, never a full `python_repo` copy.
- **Worker stop-signal contract** — `SIGBREAK`(Windows)/`SIGTERM`(POSIX), owned by 05/ADR 0007;
  the worker examples are the reference implementation. Docs (08) describe it, do not redefine it.
- **CI env `EXPECTED_PYTHON`** — set by 03's `ci.yml`, consumed by the runtime-interpreter test.

## Merge order & gates

- One feature branch. Land Wave 1 issues (each to `make all`), then 02, then 03, then 08.
- Each issue commits after its own gate passes — small commits over one big integration.
- The branch as a whole must pass **`make all-secure`** before PR. Once the remote exists, CI
  (issue 03) proves it on ubuntu+windows × 3.13+3.14 — that is the real gate D5 makes live.
- ADRs 0006 (issue 01) and 0007 (issue 05) flip `proposed` → `accepted` as their issues go green.

## Serial fallback

If parallel Wave 1 is not desired (single developer/agent), run in the order
04 → 01 → 05 → 06 → 07 → 02 → 03 → 08. 04 before 02 is mandatory (GitPython); the rest of Wave 1
is any order. This is the safe linearization of the wave graph.
