# Implementation Plan: Decouple Config Loading from Logging & Anchor All Paths to Project Root

> **Source PRD:** [`PRD.md`](./PRD.md)
> **Issues:** [`issues/01`](./issues/01-project-paths-service.md) … [`issues/07`](./issues/07-cwd-independence-acceptance-test.md)
> **Decisions of record:** [ADR 0001](../../docs/adr/0001-foundational-config-layering.md) (foundational layering), [ADR 0002](../../docs/adr/0002-repo-root-path-anchoring.md) (repo-root path anchoring)
> **Domain terms:** [`CONTEXT.md`](../../CONTEXT.md) — *Application Config, Component Config, Config Loader, Env Selector, Logger, Project Paths, Config/Logger Profile*

## Goal

Make **config loading** and **logging** independent and independently usable, resolve every path **deterministically against a computed project root**, and delete the duplicated loading logic — while keeping the everyday public API call-compatible so notebooks and tests don't churn. Shipped as one coherent task, phased internally so each phase leaves `make all-secure` green on the 3.11 / 3.12 / 3.13 ubuntu matrix.

## Non-negotiable constraints (from the ADRs)

- **One-way dependency (ADR 0001).** `ProjectPaths` and `ConfigLoader` are foundational and must **never** import the project `Logger`. Any breadcrumb they need uses stdlib `logging.getLogger(__name__)`, never the singleton.
- **Share the mechanism, not the identity (ADR 0001).** `Config` and `BaseConfig` reuse one `ConfigLoader` by **composition**; they stay separate classes (singleton vs. multi-instance lifecycles).
- **Never resolve against CWD (ADR 0002).** All paths anchor to the computed project root or the explicit env override. No `os.chdir`, no growing candidate-path searches.
- **Env override owned by the Env Selector.** The base-directory override is read/written only through `Envs`; nothing touches `os.environ` directly.
- **Fail loudly, succeed quietly.** Config parsing emits nothing on success; raises diagnostic exceptions on failure.

## Current state (what we're changing)

| Concern | Today | Problem |
| --- | --- | --- |
| `Config._get_config_file_path` (`src/utils/config.py`) | 4-candidate-path search, hand-rolled parse | Fork of `BaseConfig`; divergent path strategy |
| `BaseConfig.parse_config` (`src/utils/base_config.py:41`) | calls `Logger().debug(...)` at line 52 | Config→Logger wrong-way dependency |
| `Logger.__init__` (`src/utils/logger.py:37`) | 2-path search + `Path(__file__).parent.parent.parent` | CWD-fragile; own path strategy |
| `SPECIAL_LOGGER_FILE_NAME` (`src/constants/global_constants.py:18`) | hard-coded `"../../logs/..."` | CWD-relative |
| `configurations/*.conf` | `../../logs`, `../../data`, `../../reports`, `../../notebooks` in 10 places | CWD-relative; flat layout |

Confirmed `../../` occurrences to eliminate: `logger_file.conf`, `logger_file_console.conf`, `logger_file_limit.conf`, `logger_file_limit_console.conf`, `python_local.conf`, `python_personal.conf`, `python_repo.conf`, plus `global_constants.py`.

## Target end-state

**Modules (all under `src/utils/`):**

```
project_paths.py   NEW  — root-from-marker, canonical dirs, env override, no Logger import
config_loader.py   NEW  — locate(via ProjectPaths)→pyhocon→typedload[NamedTuple], diagnostic errors, no Logger import
config.py          MOD  — delegates to ConfigLoader; Singleton; get_data()/get_data_as_dict() unchanged
base_config.py     MOD  — parse_config() drops Logger(); delegates to ConfigLoader
logger.py          MOD  — init independent of config loading; resolves logs/ & profile via ProjectPaths; injects abs path into fileConfig
```

**Config layout:**

```
configurations/
├── python_repo.conf          (Application Config — top level, unchanged location)
├── python_personal.conf
├── python_local.conf
├── loggers/                  (Logger profiles — moved here)
│   ├── logger_console.conf
│   ├── logger_file.conf
│   ├── logger_file_console.conf
│   ├── logger_file_limit.conf
│   └── logger_file_limit_console.conf
└── watchdogs/                (Component Config — moved here)
    ├── watchdog_cmd_01.conf
    └── watchdog_cmd_02.conf
```

No `.conf` file contains `../../`; internal paths become root-relative values resolved through `ProjectPaths`.

## Execution order & dependency graph

```
01 project-paths ──┬── 02 config-loader ──┬── 03 config-delegates ──┐
                   │                       └── 04 baseconfig-drops-logger ──┼── 06 migrate-conf ── 07 cwd-acceptance
                   └────────────────────────── 05 logger-independent ───────┘
```

- Critical path: `01 → 02 → 03 → 06 → 07` (5 hops).
- After **02** merges, slices **03**, **04**, **05** are independent and can be built in parallel.
- **06** is the single coordinated file-move + `../../`-strip; it must land after all three module rewires.
- **07** is the capstone acceptance test.

**Green-at-every-step principle:** during slices 03–05 the `.conf` files stay in their current locations with their existing `../../` internals — modules resolve the old paths via `ProjectPaths`, and the Logger's injected absolute path overrides any in-file path. Slice 06 does the coordinated move.

---

## Slice-by-slice plan

### 01 — Project Paths service  *(Foundation, no blockers)*

**Build** `src/utils/project_paths.py`:
- Compute root **once** by walking up from `Path(__file__)` to the first ancestor containing a marker (`pyproject.toml` or `.git`).
- Expose read accessors: `root`, `data`, `logs`, `reports`, `configurations`, and a resolver `config_file(name) -> Path` (absolute) that also handles per-kind subfolders (`loggers/`, `watchdogs/`).
- Base-directory **env override** read via `Envs` (add a getter to `envs.py` for the override var); when set, it repoints `root`.
- Create `logs/` if absent.
- Type everything for mypy `--strict`; `pathlib` only; **no `Logger` import**.

**Tests** `tests/tests_utils/test_project_paths.py`: root resolves regardless of CWD (`monkeypatch.chdir(tmp_path)`); child dirs resolve under root; env override repoints; `logs/` created; assert no `src.utils.logger` in the module's imports.

### 02 — Config Loader  *(Foundation, blocked by 01)*

**Build** `src/utils/config_loader.py`: a function/small class `load_config(config_name: str, target: type[_T]) -> _T` that resolves the file via `ProjectPaths`, parses with `pyhocon.ConfigFactory`, and loads via `typedload` into `target`. Silent on success. Raise diagnostic exceptions through the existing `src/exceptions/` system:
- missing file → names profile, folder, resolved absolute path;
- bad HOCON → surfaces parse failure;
- shape mismatch → surfaces `typedload` type error.
- **No `Logger` import.**

**Tests** `tests/tests_utils/test_config_loader.py`: valid profile → typed result; each failure mode → its diagnostic exception; success path emits no log; assert no Logger import. Use a small fixture `.conf` + `NamedTuple` under the test tree.

### 03 — `Config` delegates to Config Loader  *(Decouple, blocked by 02)*

**Modify** `src/utils/config.py`: delete `_get_config_file_path` (the 4-path search) and the `_is_profile` flag where unused; delegate loading to `ConfigLoader` with target `ConfigData`. Keep `Singleton` metaclass, profile selection via `Envs` (default `python_personal`), and `get_data()` / `get_data_as_dict()` signatures & return values identical. `.conf` files stay at top level for now.

**Tests:** existing `Config` tests pass unchanged; add Singleton-identity + "loads without importing Logger" assertions.

### 04 — `BaseConfig` drops `Logger`  *(Decouple, blocked by 02)*

**Modify** `src/utils/base_config.py`: remove the `from src.utils.logger import Logger` import and the `Logger().debug(...)` call at line 52; delegate `parse_config()` to `ConfigLoader` with the generic `data_structure` target. Keep `BaseConfig[_T]`, `get_data()`, `get_data_as_dict()`. `WatchdogConfig(name).get_data() -> WatchdogConfigData` unchanged; watchdog `.conf` stays at current location this slice.

**Tests:** watchdog-config tests pass; add "loading a Component Config imports no logging stack" assertion.

### 05 — `Logger` independent + path injection  *(Decouple, blocked by 01)*

**Modify** `src/utils/logger.py`: resolve the profile file and `logs/` dir via `ProjectPaths` (drop the 2-path search at lines 40–44); inject the resolved **absolute** log path into `logging.config.fileConfig` at init (stdlib profiles can't compute paths — pass via `defaults=` or post-resolution). Keep `Singleton`, `ENV_LOGGER` selection, all log-level + timer methods, and the git-branch/host breadcrumb. Remove `get()` (line 146) and the `_is_logger` flag surgically **iff** the common public API stays intact. Must **not** import `ConfigLoader`/`Config`.

**Tests:** existing `test_logger.py` behaviors pass (adjust only if `get()` removed); assert log file lands in `ProjectPaths.logs` independent of CWD; assert init has no config-loading dependency.

### 06 — Migrate `.conf` layout & strip `../../`  *(Migrate, blocked by 03, 04, 05)*

**Move files** with `git mv`: `logger_*.conf → configurations/loggers/`, `watchdog_*.conf → configurations/watchdogs/`. **Repoint modules:** Logger resolves under `loggers/`; `WatchdogConfig` under `watchdogs/`; `python_*` stay top level. **Strip every `../../`:** the 4 logger confs' `args=(...)` log paths, and `data`/`ntb_path`/`output_folder` in the 3 `python_*` confs → root-relative values resolved by `ProjectPaths` so `Config().get_data().path.data` points at the real `data/`. **Fix** `SPECIAL_LOGGER_FILE_NAME` in `global_constants.py:18` to resolve via `ProjectPaths` (or expose the fallback path through it). Update `docs/tutorials/PERSISTENT_RUN.md` / watchdog docs if they reference the old `.conf` locations.

**Verify:** `grep -rn '\.\./\.\.' configurations/ src/` returns nothing.

### 07 — CWD-independence acceptance test  *(Verify, blocked by 06)*

**Build** `tests/tests_utils/test_cwd_independence.py`: with `monkeypatch.chdir(tmp_path)`, assert `Config().get_data()`, `Logger()` (log file absolute location), and `WatchdogConfig(name).get_data()` resolve identically to a repo-root run; assert `data`/`logs`/`reports`/`configurations` resolve to the same absolute paths regardless of CWD. Respect Singleton caching — set env via `Envs` before first instantiation (mirror `tests/conftest.py`). Keep coverage ≥ `fail_under = 25`.

---

## Global validation (every slice)

- `make all-f` while iterating on one module (set `FILE_FOLDER`/`FILE_NAME` in `make_config.mk`), then `make all-secure` before marking a slice done.
- New code passes mypy `--strict`, ruff format/lint, ruff docstring rules, and mirrors the house style (modern generics, `X | None`, reST/Sphinx docstrings starting on the line after `"""`, absolute `src.` imports).
- Every slice green on Python 3.11 / 3.12 / 3.13 (what CI runs).

## Risks & gotchas

- **Singleton caching in tests.** `Config` and `Logger` cache on first instantiation; env vars (via `Envs`) must be set *before* first call. CWD-varying tests must reset/instantiate carefully.
- **`ENV_RUNNING_UNIT_TESTS=True`** makes `ExceptionExecutioner` skip logging — keep in mind when testing the Config Loader's error paths (assert the raise, not a log).
- **`fileConfig` path injection.** stdlib `logging.config.fileConfig` can't compute paths; the absolute log path must be injected at init (via `defaults` substitution or equivalent) — this is why logger confs can drop `../../` safely.
- **CI config availability.** `python_personal.conf` is git-ignored/generated; the checked-in `python_repo.conf` / `python_local.conf` are the CI-safe profiles — ensure resolution still works when only those exist.
- **Windows-first.** All path work via `pathlib`; verify on Windows and the Linux CI matrix (separators, `git mv` casing).
- **`git mv` in slice 06** preserves history and keeps the move atomic with the module repointing so the branch never has a broken intermediate state.
