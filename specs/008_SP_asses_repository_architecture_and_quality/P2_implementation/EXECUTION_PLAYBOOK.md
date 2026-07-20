# Execution Playbook — P2 implementation

## Summary

- **Issues covered:** [01](./issues/01-monitoring-rename.md),
  [02](./issues/02-plotly-cleanup.md), [03](./issues/03-data-layer-hardening.md),
  [04](./issues/04-singleton-ergonomics.md), [05](./issues/05-notebook-template-fixes.md),
  [06](./issues/06-schema-drift-test.md), [07](./issues/07-executioner-merge.md),
  [08](./issues/08-untested-code-tests.md), [09](./issues/09-manifest-and-docs-sweep.md)
- **Verdict:** **Waved parallel.** Wave 1 (01–07) has disjoint file ownership across
  independent code areas and runs concurrently (max concurrency 7). Wave 2 (08) is the
  test push and waits for 02 (real `dashboard` return). Wave 3 (09) single-owns the
  manifest/Makefile/CLAUDE.md and waits for everything.
- **Highest execution risk:** `pyproject.toml`/`uv.lock`/`Makefile`/`CLAUDE.md` are
  single-owned by issue 09. Wave-1 issues must **not** edit those (esp. tempting: CLAUDE.md
  after the `MonitoredBase` rename, or pyproject for the `bs4` drop). Each Wave-1 issue
  passes its manifest/docs need to 09 as an interface and never touches those files.

## Waves

| Wave | Issues | Concurrency | Gate |
|---|---|---|---|
| 1 | 01, 02, 03, 04, 05, 06, 07 | up to 7 | `make all` per issue |
| 2 | 08 | 1 | `make all` |
| 3 | 09 | 1 | `make all-secure` |

### Why the waves

- **Wave 1** — seven independent code areas, no shared files (see map): monitoring rename
  (`utils/monitored_base` + importers), plotly (`visualisations/`), data layer (`data/`),
  singleton (`utils/{singleton_meta,envs}`), notebook templates (`notebooks/template/` +
  `utils/notebook_support_functions`), schema-drift test (new test file), executioner merge
  (`utils/notebooks_executioner*` + `scripts/param_notebook_execution`). Cross-behaviour
  couplings are order-independent at the file level. **Pylint-pragma removal is folded into
  each owning issue** (02 → 50 viz pragmas, 05 → support-fn, 07 → executioner; the 2
  `helper_functions` pragmas are 09's).
- **Wave 2 after 02** — the viz smoke tests assert on a returned `go.Figure`, which only
  exists once 02 makes `dashboard=True` return the figure. Everything else 08 tests
  (heartbeat, watchdog helpers) is independent, but the whole test issue waits on 02 for
  simplicity.
- **Wave 3 after all** — 09 removes `bs4` (only safe once `cover_logger` is reworked in the
  same issue), turns on doctest collection, drops `fail_under`, adds the `make jupyter`
  guard, and sweeps CLAUDE.md to match the `MonitoredBase` rename (01) and executioner merge
  (07). It must see the finished code.

## File-ownership map

| Issue | OWNS (writes) | Notes |
|---|---|---|
| 01 | `utils/monitored_base.py` (renamed from `meta_class.py`), `transformations/base_transformer.py`, `utils/base_component_config.py`, `tests_utils/test_monitored_base.py` (renamed), `tests_configurations/test_watchdog_config.py` | Does NOT touch CLAUDE.md (→09) |
| 02 | `visualisations/*.py` | Strips 50 viz pragmas; does NOT write viz tests (→08) |
| 03 | `data/attributes.py`, `data/saver_and_loader.py`, `tests_data/test_attributes.py`, `tests_data/test_saver_and_loader.py` | `.csv`/`.xlsm` stay in `src/data/` |
| 04 | `utils/singleton_meta.py`, `utils/envs.py`, `tests_utils/test_singleton_meta.py`, `tests_utils/test_envs.py` | Exposes `Singleton.reset()` |
| 05 | `notebooks/template/*.py`, `utils/notebook_support_functions.py` | Strips support-fn pragma; raw/ playgrounds untouched |
| 06 | `tests_utils/test_config_schema_drift.py` (new) | Reads schemas + NamedTuples only |
| 07 | `utils/notebooks_executioner.py`, `utils/notebooks_executioner_linux.py` (deleted), `scripts/param_notebook_execution.py`, `tests_utils/test_notebooks_executioner.py` | Strips executioner pragma; Makefile is 09's |
| 08 | `tests_scripts_production/test_heartbeat.py` (new), `tests_visualisations/*` (new), `tests_scripts_production/test_watchdog.py` (append) | Tests only |
| 09 | `pyproject.toml`, `uv.lock`, `Makefile`, `utils/cover_logger.py`, `utils/helper_functions.py`, `CLAUDE.md` | Single owner of manifest/Makefile/CLAUDE.md |

**Collision summary:** no two same-wave issues share a file. `test_watchdog.py` is appended
only by 08; `helper_functions.py` and CLAUDE.md only by 09; the manifest/Makefile only by 09.

## Frozen interfaces

- **`MonitoredBase` in `src/utils/monitored_base.py`** — owned by 01; 09 updates CLAUDE.md to
  match. No consumer wire-up (deferred to spec 009).
- **`dashboard` semantics** (`True` → `go.Figure`, `False` → `fig.show()`/`None`) — owned by
  02; 08's viz smoke tests depend on `dashboard=True` returning the figure.
- **`Singleton.reset()`** — owned by 04; available to any test.
- **Merged `NotebookExecutioner` API** — owned by 07; the `_linux` variant is gone.
- **`bs4` removal** — self-contained in 09 (only `cover_logger` used it); re-lock in the same
  issue.

## Merge order & gates

- One feature branch. Land Wave 1 (each to `make all`), then 08, then 09.
- Each issue commits after its own gate passes — small commits over one big integration.
- The branch as a whole must pass **`make all-secure`** before PR (09's gate), and CI proves
  it on ubuntu+windows × 3.13+3.14 once the remote exists.

## Serial fallback

If parallel Wave 1 is not desired (single developer/agent), run
**01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09**. 02 before 08 is mandatory (`dashboard`
return); 09 last (manifest/docs describe post-change reality). The rest of Wave 1 is any
order.
