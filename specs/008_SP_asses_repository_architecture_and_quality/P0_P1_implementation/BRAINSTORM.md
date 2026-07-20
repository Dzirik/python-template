# BRAINSTORM — P0 + P1 implementation (gate integrity, truth, and the deferred direction decisions)

## Source

[`../STATUS_REPORT.md`](../STATUS_REPORT.md) — the architecture & quality assessment.
This spec implements the report's **P0** (§6, gate integrity & correctness) **and P1**
(docs truth + the direction decisions D1, D2, D4, D5, D6, and logger wire-up phase 1)
backlogs together. Excluded: the D3 phase-2 monitoring wire-up (P2, gated on the
not-yet-existent DS/ML migration) and everything else in P2/P3.

## Why P0 and P1 together

Two P0 items are stopgaps for P1 direction decisions, so doing them separately is
throwaway work:

- `add-lib`'s `--all-extras` patch (P0) is discarded the moment D4 rewrites the recipe onto
  dependency-groups.
- The `DEFAULT_CONFIG` flip (P0) is literally "D6 first half"; the overlay is the second
  half — same file, same concept.
- The CI interpreter fix (P0) and the Windows CI job (D5) edit the same `ci.yml`.
- The `timer.py` fix (P0) and the logger/exceptions wire-up (P1) are the same import-chain
  concern.

Combining also lets the **docs sweep describe the post-change reality once** instead of
twice, and surfaces one interaction that P0-alone would hide: strict typedload
(`failonextra=True`) forces the overlay to **merge-then-load** so a legitimately-partial
personal file is not rejected.

## Decisions carried in from the grill (2026-07-15)

| # | Area | Decision |
|---|---|---|
| A | Overlay design (D6) | Generalised base+overlay in `load_config` (`base_name` param); `python_repo` is the always-loaded base; deep-merge override over base; one strict `typedload.load(basiccast=False, failonextra=True)` on the merged dict. → **ADR 0006** |
| B | `name` field | `ApplicationConfig` sets `name = Envs().get_config()` authoritatively after merge; TOML `name` is advisory; partial overlays need not restate it. |
| C | Default profile UX | `.env.example` selects `python_repo`; overlay activates explicitly via `ENV_CONFIG`; a partial file's missing keys fall back; selecting an absent profile errors; `create-venv` generates a minimal commented `python_personal.toml` template (inert until selected). |
| D | Dep structure (D4) | `[tool.uv] package = false`; `dev` and `windows` as PEP-735 `[dependency-groups]`; `default-groups = ["dev","windows"]`; plain `uv run` everywhere; `add-lib` → `uv add [--group …]`. |
| E | CI (D5) | Full `os × python` matrix (ubuntu + windows-latest × 3.13/3.14); `setup-uv` `python-version` input, drop `setup-python`; `choco install make` on Windows so `make all-secure` runs identically; drop the dead coverage-artifact step. |
| F | Version assert | pytest test gated on `EXPECTED_PYTHON` env var (CI sets it); skips locally; lives with the existing version-policy tests. |
| G | GitPython | Full drop: shared `get_git_branch()` stdlib helper (reads `.git/HEAD`, fallback `"unknown"`) used by `logger.py` + `cover_logger.py`; remove the `gitpython` dependency. |
| H | Timer | Drop the `DataFrame` return from `get_data()` (no `src` consumer); use `datetime.fromtimestamp(ts)` **local** time to unmix the Timer-UTC / echo-local mismatch. |
| I | Watchdog (D2/§3.6) | Exponential backoff to a cap, never permanently give up, alert via healthcheck lapse; atomic lockfile single-instance; real graceful stop (`CREATE_NEW_PROCESS_GROUP` + `CTRL_BREAK` + worker signal handlers). → **ADR 0007** |
| J | Transformer (D2) | `TimeAttributes` NamedTuple passed to `__init__` so `fit(dt_index)` matches the base; real `inverse` via `OneHotEncoder.inverse_transform`; `_params` round-trip demonstrated + tested; fix `min_inerval`/`numberical` typos; sklearn-compat non-goal in the `BaseTransformer` docstring + CONTEXT.md. |
| K | Marimo (D1) | Self-contained marker-walk `__file__` bootstrap for `src/` imports; template + documentation notebooks; `.gitignore` fixes (`apps`→`app`, drop `temporal`); `marimo-convert` writes via `-o`. |

Glossary language for the config profiles and the Transformer concept was updated in
[`../../../CONTEXT.md`](../../../CONTEXT.md) during the grill (base/overlay relationship;
transformer sklearn non-goal). Issues must not re-edit those glossary entries.

## Issues

| # | Issue | Report items | ADR |
|---|---|---|---|
| 01 | [Config model: tracked base + strict overlay loader](./issues/01-config-tracked-base-and-overlay.md) | P0#2, P0#3, D6 | 0006 |
| 02 | [uv-native workflow modernization](./issues/02-uv-native-workflow.md) | P0#4, D4 | — |
| 03 | [CI: interpreter selection + Windows matrix](./issues/03-ci-interpreter-and-windows-matrix.md) | P0#1, D5 | — |
| 04 | [Logger / exceptions / timer wire-up + drop GitPython](./issues/04-logger-exceptions-timer-wireup.md) | P0#5, logger P1 | — |
| 05 | [Production supervision hardening](./issues/05-production-supervision-hardening.md) | P0#6, watchdog P1 | 0007 |
| 06 | [BaseTransformer defect fixes](./issues/06-base-transformer-defects.md) | D2 | — |
| 07 | [Marimo real integration](./issues/07-marimo-real-integration.md) | D1 | — |
| 08 | [Docs truth sweep](./issues/08-docs-truth-sweep.md) | README/tutorial/CLAUDE.md P1 | — |

## Dependency waves (see [EXECUTION_PLAYBOOK.md](./EXECUTION_PLAYBOOK.md))

- **Wave 1 (parallel):** 01, 04, 05, 06, 07 — independent code areas, disjoint file
  ownership.
- **Wave 2:** 02 — owns `pyproject.toml`/`uv.lock`/`Makefile`/`mypy.ini`; depends on 04
  (GitPython import removed before the dependency is dropped); integrates the Makefile-facing
  requirements specified by 01 (personal-template generation) and 07 (playground copy,
  `marimo-convert -o`).
- **Wave 3:** 03 — CI; depends on 01 (clean checkout passes) and 02 (new uv workflow CI
  invokes).
- **Wave 4:** 08 — docs; depends on all code waves (describes post-change reality).

## Out of scope (deferred to later specs)

D3 phase-2 monitoring wire-up; global pylint-pragma strip (beyond the transformer's own);
`--doctest-glob` collection; `cover_logger.py` bs4/`input()` rework; `SaverAndLoader`
undersized-file handling; singleton reset seam; schema drift-check; notebook lint gate;
moving all supervision timings to TOML; the P3 polish tail.
