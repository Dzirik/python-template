---
status: ready-for-agent
labels: [prd, ready-for-agent]
supersedes: none
relates-to: docs/adr/0005-python-version-support-strategy.md
builds-on: specs/007_update_and_optimize_python_version_and_libraries/BRAINSTORM.md
---

# PRD: Update & optimize Python version and libraries

## Problem Statement

The template is pinned to an ageing Python baseline. It declares
`requires-python = ">=3.11,<3.14"`, pins the local interpreter to `3.12`, targets mypy
`3.11` / ruff `py311`, and runs a three-version CI matrix (`3.11 / 3.12 / 3.13`). As the
foundation for a specific long-horizon project that will ramp over the coming year, this
baseline is already behind where it needs to be: it forces the template — and every
project forked from it — onto old-interpreter syntax targets, spends CI effort proving
versions the project will never use, and lets a large block of hand-pinned *transitive*
Jupyter dependencies bloat the direct-dependency surface. The maintainer wants to be
deliberately ahead on Python without sacrificing day-to-day stability, and wants the
dependency set refreshed to current releases in one coherent move.

## Solution

Move the template to a **Python 3.13–3.14 support range** and modernize the dependency
set in a single coordinated, lock-verified change:

- **Drop 3.11 and 3.12 entirely.** The floor becomes **3.13**; the ceiling admits
  **3.14** (`requires-python = ">=3.13,<3.15"`). Only 3.13 and 3.14 remain — anywhere.
- **Local development defaults to the proven 3.13**, while CI proves *both* 3.13 and
  3.14 on every pull request, so a future promotion of the default to 3.14 is already
  green rather than a scramble (see [ADR 0005](../../docs/adr/0005-python-version-support-strategy.md)).
- **Refresh every dependency to its current latest release**, frozen via a single
  `uv lock`; keep `marimo[recommended]` (the full ready-to-work editor suite); trim the
  hand-pinned transitive Jupyter dependencies down to top-level packages only, letting
  the lock carry the rest.
- **Rebuild the `pip-audit` ignore list** against the post-bump advisory state, keeping
  only genuinely-unfixable suppressions, each annotated with a reason.
- **A new version-consistency test** hard-fails the build if `3.11` or `3.12` ever
  reappears in the version-bearing project files, durably enforcing the exclusion.

No runtime behaviour changes: config/logger loading, exceptions, transformers, and the
supervision runtime are untouched.

## User Stories

1. As the template maintainer, I want `requires-python` to read `">=3.13,<3.15"`, so that the template only admits the interpreters my long-horizon project will actually use.
2. As the template maintainer, I want 3.11 and 3.12 removed from every version-bearing file, so that no stale interpreter reference survives anywhere in the repo.
3. As a developer setting up the template, I want `make create-venv` (and `create-venv-linux`) to install and pin Python 3.13, so that my local environment matches the supported floor out of the box.
4. As a developer, I want `.python-version` to pin 3.13, so that `uv` and my tooling select the proven daily-driver interpreter automatically.
5. As a developer running local checks, I want mypy to target `python_version = "3.13"` and ruff `target-version = "py313"`, so that my local checks catch any 3.13-incompatible syntax even if I happen to run a newer interpreter.
6. As the template maintainer, I want the trove classifiers to list 3.13 and 3.14 (and drop 3.11/3.12), so that the package metadata advertises the true supported range.
7. As a CI maintainer, I want the CI matrix to be exactly `["3.13", "3.14"]`, so that every pull request is proven on both the floor and the ceiling and nothing else.
8. As a CI maintainer, I want CI to keep running `make all-secure` on `ubuntu-latest` with per-version coverage artifacts, so that the modernization changes only the interpreter set, not the pipeline shape.
9. As a developer, I want the whole dependency tree to resolve and pass `make all-secure` on 3.14, so that I have confidence the template works on the newest admitted interpreter.
10. As a developer, I want the whole dependency tree to resolve and pass `make all-secure` on 3.13, so that the floor interpreter is proven, not just assumed.
11. As the template maintainer, I want every kept dependency's `>=` floor bumped to its current latest release, so that the declared baseline reflects a modern, coherent starting point.
12. As the template maintainer, I want the three currently-unpinned dependencies (`openpyxl`, `termcolor`, `types-requests`) to gain explicit floors set to their locked latest, so that the dependency declaration surface is uniform and auditable.
13. As the template maintainer, I want a single `uv lock` to regenerate `uv.lock` as the one reproducibility contract, so that everyone who runs `uv sync` gets identical, tested versions regardless of the `>=` floors.
14. As a developer, I want `marimo[recommended]` kept as a direct dependency, so that the full editor experience (Altair charts, SQL/duckdb cells, polars viewer, AI assist) is ready to work without me having to add extras later.
15. As the template maintainer, I want the hand-pinned transitive Jupyter dependencies removed from the explicit dependency list, so that the direct-dependency surface shows only packages the template actually imports or invokes.
16. As a developer, I want the trimmed transitive packages to remain installed via `uv.lock`, so that the notebook stack keeps working exactly as before (the trim is footprint-neutral).
17. As the template maintainer, I want the rationale-bearing pins (`notebook`, `jupyterlab` with their anchor-fix notes) kept top-level, so that the intent behind those specific floors is not lost in the trim.
18. As a security-conscious maintainer, I want `make security-check` re-run after the bump and the `--ignore-vuln` list rebuilt, so that suppressions reflect the actual post-update advisory state rather than stale history.
19. As a security-conscious maintainer, I want each surviving `--ignore-vuln` annotated with a one-line reason, so that the suppression list complies with the repo's "suppress with a reason" rule and a future reader understands why each is accepted.
20. As the template maintainer, I want any dependency that cannot resolve a stable 3.14 wheel surfaced to me with a core-vs-convenience framing, so that I make the call rather than having an old pin silently reintroduced.
21. As the template maintainer, I want the dependency-block comments in `pyproject.toml` refreshed, so that they describe the trimmed, re-bumped state instead of the old upgrade history.
22. As a future reader, I want ADR 0005 to record the version strategy — including why still-current 3.12 was dropped and why the local default trails the CI ceiling — so that the surprising parts are explained.
23. As a future reader, I want the CHANGELOG updated with this modernization, so that the change is discoverable in the project history at the usual cadence.
24. As a developer reading the docs, I want `README.md`, `docs/PROJECT_VISION.md`, and `CLAUDE.md` swept for hardcoded `3.11`/`3.12` mentions and the "Python 3.12" setup text, so that the documentation matches the new baseline.
25. As a developer reading the docs, I want the CI-matrix description and any dependency notes referencing the marimo suite updated, so that docs reflect that the matrix is `3.13/3.14` and `marimo[recommended]` is kept.
26. As the template maintainer, I want a test that fails the build if `3.11` or `3.12` reappears in `pyproject.toml`, `.python-version`, or the CI workflow, so that the exclusion is durably enforced against future drift.
27. As the template maintainer, I want that same test to assert the version-bearing files agree with each other (floor, pin, matrix, targets), so that the version references cannot silently diverge across files.
28. As a developer, I want the final resolved environment to still drive every existing Makefile target (jupyter, marimo, tests, quality checks), so that the modernization changes nothing about how I work.
29. As a maintainer of the supervision system, I want config/logger loading, exceptions, transformers, and the watchdog/checker runtime left untouched, so that this change carries zero behavioural risk.
30. As a future maintainer, I want the decision revisited when Python 3.15 ships, so that the template repeats the "proven default, newest-in-CI" shape rather than falling behind again.

## Implementation Decisions

**Version-bearing settings (single source per file, kept mutually consistent):**

- `pyproject.toml`: `requires-python = ">=3.13,<3.15"`; trove classifiers list `3.13`
  and `3.14` only; `[tool.mypy] python_version = "3.13"`; `[tool.ruff] target-version =
  "py313"`.
- `.python-version`: `3.13`.
- `Makefile` `create-venv` and `create-venv-linux`: `uv python install 3.13` /
  `uv python pin 3.13`, and the "Python 3.12" echo text updated to 3.13.
- `.github/workflows/ci.yml`: matrix `python-version: ["3.13", "3.14"]`; everything else
  (`ubuntu-latest`, `uv sync --extra dev`, `make all-secure`, per-version coverage
  artifact upload) unchanged.

**Dependencies (`pyproject.toml` `[project].dependencies` and optional groups):**

- Kept explicit, floors bumped to latest — data/utility stack (`pandas`, `numpy`,
  `scikit-learn`, `plotly`, `openpyxl`, `python-dotenv`, `gitpython`, `typedload`,
  `requests`, `aiohttp`, `urllib3`, `idna`, `termcolor`, `types-requests`); notebook
  top-level stack (`jupyter`, `jupyter-client`, `jupyter-console`, `jupyter_server`,
  `notebook`, `jupyterlab`, `nbclient`, `nbconvert`, `nbformat`, `jupytext`, `papermill`,
  `ipykernel`, `ipython`, `ipywidgets`, `debugpy`); and `marimo[recommended]` (kept).
- `openpyxl`, `termcolor`, `types-requests` gain explicit `>=` floors set to locked latest.
- Removed from the explicit list (remain pinned transitively in `uv.lock`): `traitlets`,
  `parso`, `jedi`, `pyzmq`, `tornado`, `mistune`, `pandocfilters`, `send2trash`,
  `nest-asyncio`, `decorator`, `qtconsole`, `qtpy`, `jupyter-core`, `jupyterlab-pygments`,
  `terminado`, `prompt-toolkit`, `pygments`. Verified: no `src/` code imports any of them.
- `dev` group (`pytest`, `pytest-cov`, `mypy`, `ruff`, `bandit[toml]`, `pip-audit`,
  `beautifulsoup4`) and `windows` group (`pywin32`, `pywinpty`; markers unchanged) get
  the same latest-floor treatment.
- `>=` floors are posture/documentation; the committed `uv.lock` (regenerated once via
  `uv lock`) is the reproducibility contract.

**Straggler policy (from ADR 0005 / Decision 9):** core runtime (`numpy`, `pandas`,
`scikit-learn`, `requests`, `aiohttp`) must have stable 3.14 wheels — non-negotiable;
notebook/dev conveniences (`qtconsole`, `papermill`, compiled marimo extras
`duckdb`/`polars`/`pydantic-core`) may lag behind a tracked `# TODO(3.14)` note. No
pre-release/RC pins. Any straggler is surfaced to the maintainer, not silently resolved.

**Security-check recipe (`Makefile` `security-check-no-clear`):** rebuild the
`--ignore-vuln` list under a three-case policy — drop entries that no longer fire; drop
entries a newer release fixes (the bump is the fix); keep only genuinely-unfixable ones,
each with a one-line reason comment. Final list surfaced for sign-off.

**Docs/ADR:** ADR 0005 already written (version strategy only). CHANGELOG entry added.
Doc sweep across `README.md`, `docs/PROJECT_VISION.md`, `CLAUDE.md`. `CONTEXT.md`
unchanged — no domain term added or altered.

## Testing Decisions

**What makes a good test here:** assert the template's *external contract* — which
interpreters it supports and that it installs-and-passes on them — not internal wiring.
The one genuinely behavioural proof is that the resolved environment passes `make
all-secure` on both admitted interpreters; that is owned by CI and must not be
duplicated by slow, network-bound `uv lock` tests in the suite.

**Modules tested / added:**

- **New version-consistency test** (a pytest under `tests/`, mirroring the `src`/`tests`
  layout convention). It reads the version-bearing project files (`pyproject.toml` via
  `tomllib`, `.python-version`, `.github/workflows/ci.yml`) and asserts: (a) `3.11` and
  `3.12` appear nowhere in them; (b) the declared floor, interpreter pin, CI matrix, and
  mypy/ruff targets are mutually consistent (floor 3.13, matrix `["3.13","3.14"]`). This
  hard-fails the build on any future drift, durably enforcing the 3.11/3.12 exclusion.
- **CI matrix** (`ci.yml`) is the end-to-end acceptance seam: `make all-secure` green on
  both 3.13 and 3.14 proves resolution, wheel availability, typing, lint, tests, and
  security together. This is an existing seam; only its matrix values change.

**Prior art:** `test_logger_module_imports_no_config_loader_or_config`
(`tests/tests_utils/test_logger.py`) is an architectural-invariant test that reads a
source artifact and asserts a property — the direct model for the version-consistency
test. `tests/tests_utils/test_project_paths.py` already reads `pyproject.toml` via
`ProjectPaths().root`, establishing how a test locates and opens project metadata. The
new test follows the repo's parametrized-pytest style and the house docstring/typing
rules so it passes `make all` like every other test.

## Out of Scope

- **Expanding the CI OS matrix to Windows.** The Windows-first stance is noted but the
  OS matrix stays `ubuntu-latest` only.
- **Any runtime/behavioural change** to config/logger loading (ADR 0001–0004),
  exceptions, transformers, or the watchdog/checker supervision runtime.
- **Adding or removing functional libraries** beyond the dependency-refresh described
  here. (The marimo suite is *kept* as `[recommended]` — no functional library change.)
- **Restructuring the notebook workflow** itself (jupytext pairing, marimo layout).
- **Python 3.15.** Admitting 3.15 / promoting the local default to 3.14 is a future
  decision to be taken when 3.15 ships (~October 2026).
- **Reducing the environment's overall size** by moving the Jupyter/scientific stack
  behind optional extras — a separate, larger conversation.

## Further Notes

- The change lands as one coordinated branch (logical commits for readability) with a
  single `uv.lock` regeneration, because trimming transitive deps and bumping floors both
  force a re-lock — staging them would mean multiple needless re-locks.
- At the time of writing, Python 3.14 is ~9 months past stable release, so the "no 3.14
  wheel" risk is small but real, and is concentrated in the compiled `marimo[recommended]`
  extras and fringe notebook tooling rather than the core stack.
- The `pip-audit` ignore list and any 3.14-wheel straggler are the two items that can
  only be finalized *after* the re-lock; both are surfaced to the maintainer for sign-off
  rather than decided silently.
- Verification closes with a grep-audit confirming no `3.11`/`3.12` reference survives in
  `pyproject.toml`, `Makefile`, `.python-version`, `ci.yml`, or docs — now also backstopped
  permanently by the version-consistency test.
