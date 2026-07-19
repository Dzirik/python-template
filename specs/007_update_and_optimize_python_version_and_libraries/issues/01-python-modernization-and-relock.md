# Modernize Python to 3.13–3.14 and refresh dependencies with a single re-lock

> **Status:** `ready-for-agent` · **AFK** (escalate to the maintainer only if a *core-runtime* straggler appears — see Scope)

## Parent

[`specs/007_update_and_optimize_python_version_and_libraries/PRD.md`](../PRD.md) — *Update & optimize Python version and libraries*

## What to build

The atomic core of the modernization. Every version-bearing setting, the whole dependency
refresh, and the single `uv.lock` regeneration land **together**, and CI proves the result
on both admitted interpreters. These cannot be split: raising `requires-python` changes what
the resolver may pick, trimming transitive deps and bumping floors both force a re-lock, and
the only end-to-end proof that the new set resolves and works is `make all-secure` going
green on 3.13 *and* 3.14. Staging the parts (per the PRD's rejected Approach B) would mean
multiple needless re-locks and leave intermediate states that CI cannot verify.

End-to-end behaviour after this slice: the template supports Python **3.13–3.14 only**
(3.11 and 3.12 gone everywhere), a fresh `make create-venv` installs and pins **3.13**, the
CI matrix proves both 3.13 and 3.14, and every dependency is at its current latest release
frozen in a single regenerated `uv.lock`. Every existing Makefile target (jupyter, marimo,
tests, quality checks) behaves exactly as before — no runtime behaviour changes.

Scope:

- **Version-bearing settings (kept mutually consistent):**
  - `pyproject.toml`: `requires-python = ">=3.13,<3.15"`; trove classifiers list `3.13` and
    `3.14` only (drop `3.11`, `3.12`); `[tool.mypy] python_version = "3.13"`;
    `[tool.ruff] target-version = "py313"`.
  - `.python-version` → `3.13`.
  - `Makefile` `create-venv` and `create-venv-linux`: `uv python install 3.13` /
    `uv python pin 3.13`, and the "Creating virtual environment with Python 3.12" echo text
    updated to 3.13.
  - `.github/workflows/ci.yml`: matrix `python-version: ["3.13", "3.14"]`; everything else
    unchanged (`ubuntu-latest`, `uv sync --extra dev`, `make all-secure`, per-version
    coverage-artifact upload).
- **Dependency refresh (`[project].dependencies` + optional groups):**
  - Bump every **kept** dependency's `>=` floor to its current latest release.
  - Add explicit floors (set to locked latest) to the three currently-unpinned deps:
    `openpyxl`, `termcolor`, `types-requests`.
  - **Keep `marimo[recommended]`** (full ready-to-work editor suite) — do **not** reduce to base.
  - **Remove from the explicit list** (they remain pinned transitively in `uv.lock`):
    `traitlets`, `parso`, `jedi`, `pyzmq`, `tornado`, `mistune`, `pandocfilters`, `send2trash`,
    `nest-asyncio`, `decorator`, `qtconsole`, `qtpy`, `jupyter-core`, `jupyterlab-pygments`,
    `terminado`, `prompt-toolkit`, `pygments`. (Verified: no `src/` code imports any of them,
    so the trim is footprint-neutral.)
  - **Keep top-level** the rationale-bearing pins `notebook` and `jupyterlab` (their anchor-fix
    intent must not be lost) and the rest of the top-level notebook stack (`jupyter`,
    `jupyter-client`, `jupyter-console`, `jupyter_server`, `nbclient`, `nbconvert`, `nbformat`,
    `jupytext`, `papermill`, `ipykernel`, `ipython`, `ipywidgets`, `debugpy`).
  - Apply the same latest-floor bump to the `dev` group (`pytest`, `pytest-cov`, `mypy`,
    `ruff`, `bandit[toml]`, `pip-audit`, `beautifulsoup4`) and the `windows` group (`pywin32`,
    `pywinpty` — platform markers unchanged).
- **Re-lock once** — a single `uv lock` regenerates `uv.lock`. The lock is the reproducibility
  contract; the `>=` floors are posture/documentation on top of it.
- **Refresh stale comments** in the `pyproject.toml` dependency block (e.g. the "Upgraded Feb
  2026: notebook 6.x → 7.x …" and "Notebook 7.x requires …" notes) so they describe the
  trimmed, re-bumped state, not the old upgrade history.
- **Straggler policy (ADR 0005 / Decision 9):** core runtime (`numpy`, `pandas`,
  `scikit-learn`, `requests`, `aiohttp`) **must** resolve stable 3.14 wheels — non-negotiable;
  if one cannot, **stop and escalate to the maintainer**. Notebook/dev conveniences
  (`qtconsole`, `papermill`, compiled `marimo[recommended]` extras `duckdb`/`polars`/
  `pydantic-core`) may lag temporarily behind a tracked `# TODO(3.14)` note. **No
  pre-release/RC pins.** Surface any straggler with the core-vs-convenience framing.
- **No behavioural change** — config/logger loading (ADR 0001–0004), exceptions, transformers,
  and the watchdog/checker supervision runtime are untouched.

## Acceptance criteria

- [ ] `pyproject.toml` declares `requires-python = ">=3.13,<3.15"`; classifiers list only `3.13` and `3.14`; `[tool.mypy] python_version = "3.13"`; `[tool.ruff] target-version = "py313"`.
- [ ] `.python-version` is `3.13`; both `create-venv` targets install & pin `3.13` and their echoed setup text says 3.13, not 3.12.
- [ ] `.github/workflows/ci.yml` matrix is exactly `["3.13", "3.14"]`; no other CI change.
- [ ] Every kept dependency has a `>=` floor at its current latest; `openpyxl`, `termcolor`, and `types-requests` now carry explicit floors.
- [ ] `marimo[recommended]` is retained; the 17 named transitive Jupyter packages are gone from the explicit list but still present in `uv.lock`; `notebook` and `jupyterlab` remain top-level.
- [ ] `uv.lock` is regenerated by a single `uv lock`; `uv sync` produces a working environment.
- [ ] The `pyproject.toml` dependency-block comments describe the current trimmed/re-bumped state, with no leftover upgrade-history text.
- [ ] No core-runtime package was pinned to a pre-3.14 release or an RC to force resolution; any straggler encountered was surfaced to the maintainer.
- [ ] Every existing Makefile target still runs; no change to config/logger/exceptions/transformer/supervision behaviour.
- [ ] `make all-secure` green in CI on **both Python 3.13 and 3.14**.

## Blocked by

- None - can start immediately.
