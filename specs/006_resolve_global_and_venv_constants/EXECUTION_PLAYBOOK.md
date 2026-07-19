# Execution Playbook — Resolve global & venv constants

## Summary

- **Issues covered:** [01](./issues/01-env-constants-single-source-of-truth.md), [02](./issues/02-route-healthcheck-through-envs.md), [03](./issues/03-move-colors-to-visualisations.md), [04](./issues/04-move-transformer-method-ids.md), [05](./issues/05-move-folder-configurations-to-project-paths.md), [06](./issues/06-move-special-logger-file-name-to-logger.md), [07](./issues/07-delete-global-constants-and-doc-cleanup.md)
- **Verdict:** **Serial** — single branch, one issue at a time, concurrency 1. Five issues (01, 03, 04, 05, 06) each remove their own cluster from the one file `src/constants/global_constants.py`, and 01+05 also both edit `tests/tests_utils/test_config_loader.py`. That shared-file overlap makes any parallel wave collision-unsafe, so parallelism is declined by design (chosen over a deferred-removal parallel variant).
- **Highest execution risk:** `global_constants.py` is mutated by five consecutive steps and deleted by the sixth — a stale import or a missed consumer repoint surfaces only at the final delete. Mitigation: each step repoints its consumers and runs the full gate before the next begins; 07 runs the grep-audit before deletion.

## Serial execution order

Single feature branch. Run each step to green before starting the next. Order respects the blocked-by graph (02 after 01; 07 after 01/03/04/05/06); the independent moves 03/04/05/06 are sequenced by convenience.

| Step | Issue | Delivers | Gate |
|---|---|---|---|
| 1 | 01 | `env_constants.py` single source; `Envs` rewire; `.env.example` fallback removed | `make all` |
| 2 | 03 | `COLORS` → `visualisations/colors.py` | `make all` |
| 3 | 04 | method ids → `transformations/transformer_methods.py` | `make all` |
| 4 | 05 | `FOLDER_CONFIGURATIONS` → `project_paths.py` | `make all` |
| 5 | 06 | `SPECIAL_LOGGER_FILE_NAME` → `logger.py` (independent literal) | `make all` |
| 6 | 02 | `HEALTHCHECK_PING_URL` routed through `Envs` | `make all` |
| 7 | 07 | delete `global_constants.py`; `.env.example`/README/notebook cleanup | `make all-secure` |

## File-ownership map (sequential — overlaps are serialized, not concurrent)

| Issue | Touches | Shared with |
|---|---|---|
| 01 | `constants/env_constants.py` (new), `utils/envs.py`, `constants/global_constants.py`, `tests_utils/test_config_loader.py`, `tests_utils/test_project_paths.py` | `global_constants.py` (03,04,05,06); `envs.py`/`env_constants.py` (02); `test_config_loader.py` (05) |
| 03 | `visualisations/colors.py` (new), `visualisations/plotly_base.py`, `constants/global_constants.py` | `global_constants.py` |
| 04 | `transformations/transformer_methods.py` (new), `tests_transformations/test_datetime_one_hot_transformer.py`, `constants/global_constants.py` | `global_constants.py` |
| 05 | `utils/project_paths.py`, `tests_utils/test_config_loader.py`, `constants/global_constants.py` | `global_constants.py`; `test_config_loader.py` (01) |
| 06 | `utils/logger.py`, `constants/global_constants.py` | `global_constants.py` |
| 02 | `constants/env_constants.py`, `utils/envs.py`, `scripts_production/watchdog.py`, `scripts_production/checker.py` | `env_constants.py`/`envs.py` (01) |
| 07 | `constants/global_constants.py` (delete), `.env.example`, `README.md`, `notebooks/**/*.py` | `global_constants.py` (all) |

**Collision summary:** `global_constants.py` (01,03,04,05,06,07) and `test_config_loader.py` (01,05) are the overlaps that force serialization. No two steps may run concurrently.

## Frozen interfaces

- **`env_constants` public surface** — the `ENV_*` name keys + `DEFAULT_*` values + module path. Owned by **issue 01**, frozen once step 1 is green. Steps 6 (02: adds `ENV_HEALTHCHECK_PING_URL` + `Envs.get_healthcheck_ping_url()`) and 4 (05) build on it.
- **New module paths** `src/visualisations/colors.py`, `src/transformations/transformer_methods.py` — fixed by issues 03/04; referenced by 07's README update and grep-audit.
- All moved constant **values are unchanged** — this is a relocation refactor, not a redefinition. No value or signature is a negotiable contract.

## Per-agent dispatch specs

Single serial agent (or human) on one branch. Each spec below runs to its gate before the next starts.

### Step 1 — issue 01
- **Goal:** Establish `env_constants.py` as the single source for env-var keys + defaults; rewire `Envs`; remove the `.env.example` live-fallback.
- **Scope (OWNS):** `src/constants/env_constants.py` (new), `src/utils/envs.py`, `tests/tests_utils/test_config_loader.py` (ENV_* import only), `tests/tests_utils/test_project_paths.py`; removes only the `ENV_*` lines from `src/constants/global_constants.py`.
- **Inputs:** issue 01.
- **Outputs:** side-effect-free `env_constants` module; `Envs` importing it; `.env.example` no longer loaded as fallback.
- **Constraints:** do NOT touch the other clusters in `global_constants.py`; do NOT change `Envs` getter/setter signatures.
- **Integration:** merge to branch — gate `make all`.
- **Dispatch:** serial.

### Step 2 — issue 03
- **Goal:** Move `COLORS` to `src/visualisations/colors.py`; repoint `plotly_base.py`.
- **Scope (OWNS):** `src/visualisations/colors.py` (new), `src/visualisations/plotly_base.py`; removes only `COLORS` from `global_constants.py`.
- **Inputs:** issue 03.
- **Outputs:** palette in its own module; consumer + docstring repointed.
- **Constraints:** do NOT touch other `global_constants.py` clusters; palette values unchanged.
- **Integration:** gate `make all`.
- **Dispatch:** serial.

### Step 3 — issue 04
- **Goal:** Move `F/FP/P/INV` to `src/transformations/transformer_methods.py` (reserved vocabulary); repoint the test.
- **Scope (OWNS):** `src/transformations/transformer_methods.py` (new), `tests/tests_transformations/test_datetime_one_hot_transformer.py`; removes only the id lines from `global_constants.py`.
- **Inputs:** issue 04.
- **Outputs:** all four ids in one module (docstring marks `F`/`INV` reserved); test imports repointed.
- **Constraints:** do NOT prune `F`/`INV`; do NOT touch other `global_constants.py` clusters; values unchanged.
- **Integration:** gate `make all`.
- **Dispatch:** serial.

### Step 4 — issue 05
- **Goal:** Move `FOLDER_CONFIGURATIONS` into `project_paths.py`; repoint `test_config_loader.py`.
- **Scope (OWNS):** `src/utils/project_paths.py`, `tests/tests_utils/test_config_loader.py` (FOLDER_CONFIGURATIONS import); removes only `FOLDER_CONFIGURATIONS` from `global_constants.py`.
- **Inputs:** issue 05.
- **Outputs:** constant local to `project_paths`; test repointed.
- **Constraints:** do NOT touch other `global_constants.py` clusters; `configurations` property behaviour unchanged; do not place it in `env_constants.py`.
- **Integration:** gate `make all`.
- **Dispatch:** serial.

### Step 5 — issue 06
- **Goal:** Move `SPECIAL_LOGGER_FILE_NAME` into `logger.py` as an independent literal (not derived from `DEFAULT_LOGGER`).
- **Scope (OWNS):** `src/utils/logger.py`; removes only `SPECIAL_LOGGER_FILE_NAME` (and its orphaned comment block) from `global_constants.py`.
- **Inputs:** issue 06.
- **Outputs:** literal defined in `logger.py`; false comment replaced with the error-path-fallback comment.
- **Constraints:** value unchanged; MUST NOT derive from `DEFAULT_LOGGER`; do NOT touch other `global_constants.py` clusters.
- **Integration:** gate `make all`.
- **Dispatch:** serial.

### Step 6 — issue 02
- **Goal:** Route `HEALTHCHECK_PING_URL` through `Envs`; keep JSON parsing in the watchdog.
- **Scope (OWNS):** `src/constants/env_constants.py` (add key), `src/utils/envs.py` (add accessor), `src/scripts_production/watchdog.py`, `src/scripts_production/checker.py`.
- **Inputs:** frozen `env_constants` surface (step 1), issue 02.
- **Outputs:** `ENV_HEALTHCHECK_PING_URL` key + `Envs.get_healthcheck_ping_url()`; watchdog reads via `Envs`; `checker` `SYSTEMROOT` comment.
- **Constraints:** do NOT rename the `HEALTHCHECK_PING_URL` env var; JSON parsing stays in the watchdog; no `DEFAULT_*` for it.
- **Integration:** gate `make all`.
- **Dispatch:** serial.

### Step 7 — issue 07
- **Goal:** Delete the emptied `global_constants.py` and clean up docs/comments.
- **Scope (OWNS):** `src/constants/global_constants.py` (delete), `.env.example`, `README.md`, `notebooks/template/*.py`, `notebooks/documentation/*.py`, `notebooks/raw/playground_notebook.py`.
- **Inputs:** all prior steps complete; issue 07.
- **Outputs:** no `global_constants.py`; `.env.example` `.toml` comments; README file tree updated; dead notebook comment lines removed; grep-audit clean.
- **Constraints:** confirm `global_constants.py` holds no definitions before deleting; keep `constants/__init__.py`; leave `docs/notebooks_freezes/*.html` untouched.
- **Integration:** final gate `make all-secure` on Python 3.11 / 3.12 / 3.13 (CI-equivalent).
- **Dispatch:** serial.

## Merge order & gates

- One branch, steps 1 → 2 → 3 → 4 → 5 → 6 → 7. Commit per step after its `make all` gate passes — frequent small commits over one big integration.
- The branch as a whole must pass **`make all-secure`** (mypy `--strict` + format + lint + docstrings + pytest + security) on the CI matrix (3.11/3.12/3.13) before the PR merges — this is each issue's stated acceptance gate.
- Step 7 is the integration checkpoint: the grep-audit for surviving `global_constants` references gates the deletion.

## Serial fallback

Serial is the primary verdict (see Summary). The parallel alternative — reassigning `global_constants.py` to a single owner (07) via deferred removal, unlocking Wave 1 = {01,03,04,06}, Wave 2 = {02,05}, Wave 3 = {07}, max concurrency 4 — was considered and **declined** in favour of honoring each issue's per-slice removal acceptance criteria. Revisit that variant only if execution time becomes a constraint and relaxing the per-slice "`global_constants.py` no longer defines X" ACs (deferring them to 07) is acceptable.
