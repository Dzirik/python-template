---
status: brainstorm-complete
labels: [brainstorm]
supersedes: none
relates-to: docs/PROJECT_VISION.md
builds-on: none
---

# Brainstorm: Update & optimize Python version and libraries

> **Context:** The template currently supports Python `>=3.11,<3.14` and CI runs a
> 3.11 / 3.12 / 3.13 matrix. This brainstorm settles the move to a **Python 3.13–3.14
> support range** (floor **3.13**, admitting **3.14**; dropping 3.11 and 3.12 entirely),
> with **3.13 as the local development default** and CI proving *both* versions. It
> narrows CI to those two versions, updates every dependency to its latest release for
> 3.14 compatibility, trims the exhaustive Jupyter dependency list down to top-level
> packages (transitive deps stay pinned in the lock), and **keeps marimo's `recommended`
> suite** as a deliberate ready-to-work choice. No runtime behaviour or config/logger
> semantics change — this is a platform-and-dependency modernization.
>
> **Refined by a grilling session (2026-07-14):** two decisions moved from the original
> draft — the local default interpreter is **3.13, not 3.14** (stability daily-driver,
> CI proves 3.14), and marimo **stays `[recommended]`** rather than dropping to minimal.
> See Decisions 2 and 6 below.

## Scope

Matches the branch name `007_update_and_optimize_python_version_and_libraries`.

| In scope | Out of scope |
|---|---|
| Raise Python floor to 3.13, admit 3.14, drop 3.11/3.12 | Expanding the CI OS matrix to Windows (Windows-first stance noted, but explicitly **not** changed here) |
| Narrow CI matrix to `["3.13", "3.14"]` | Any change to config/logger loading, exceptions, transformers, or supervision runtime code |
| Bump every dependency floor to its current latest release | Adding or removing functional libraries beyond the marimo suite change |
| Trim explicitly-pinned Jupyter *transitive* deps to top-level only | Restructuring the notebook workflow itself |
| Add floors to the three currently-unpinned deps | Dropping marimo's `recommended` suite (reversed — it stays; see Decision 6) |
| Align mypy / ruff targets to the new 3.13 floor | |
| Prune now-moot `pip-audit` CVE ignores | |

## Approach

**Approach A — single coordinated change, lock-verified** (chosen). All edits land
together on this branch (broken into logical commits for readability), `uv.lock` is
regenerated once, and CI must go green on **both** 3.13 and 3.14 before merge. The
changes are tightly coupled — trimming transitive deps and bumping floors both force a
single re-lock — so staging them (Approach B) would mean three re-locks and needless
churn. A ceiling-only relaxation (Approach C) was rejected as it contradicts the
"latest everywhere" decision.

## Decisions

| # | Decision | Choice made |
|---|---|---|
| 1 | Python support range | Floor **3.13**, ceiling admits **3.14** → `requires-python = ">=3.13,<3.15"`. Drop 3.11 and 3.12. |
| 2 | Local default interpreter | **3.13** — the proven, year-old interpreter is the daily driver (stability first); CI proves 3.14 continuously so a later flip of the default to 3.14 is already green. `.python-version` and `make create-venv`/`-linux` install & pin **3.13**. *(Refined from 3.14 during grilling.)* |
| 3 | mypy / ruff targets | Move to the new floor: mypy `python_version = "3.13"`, ruff `target-version = "py313"`. Targeting the floor means local checks catch 3.13-incompatible syntax even when the interpreter is newer. |
| 4 | CI matrix | `["3.13", "3.14"]` only. Keep `ubuntu-latest`, `make all-secure`, per-version coverage artifacts. |
| 5 | Jupyter transitive deps | **Trim to top-level** — keep only packages actually imported/invoked; let `uv.lock` pin the rest transitively. Verified no `src/` code imports any of the dropped 17 packages, so the trim is **footprint-neutral** (they still install via the lock) — only the declaration surface shrinks. |
| 6 | marimo suite | **Keep `marimo[recommended]`** — the full editor suite (Altair / duckdb / polars / AI assist) ships ready-to-work; the ~90–120 MB cost is small against an already-heavy env (~500 MB–1 GB) and avoids future "not installed" friction. *(Reverses the original "minimal" lean during grilling.)* |
| 7 | Version-floor strategy | **Latest everywhere** — bump every kept dep's `>=` to its current latest release, frozen via a single `uv lock`. Also add floors to the three currently-unpinned deps (`types-requests`, `openpyxl`, `termcolor`). Floors are *posture/documentation*; the committed `uv.lock` is the real contract. |
| 8 | `pip-audit` ignore list | Re-run after the bump under a **three-case policy**: drop ignores that no longer fire; drop those a newer release fixes (the bump *is* the fix); keep only genuinely-unfixable ones — and **annotate each kept `--ignore-vuln` with a one-line reason** (per `CLAUDE.md`'s "suppress with a reason" rule). Final list surfaced to the user for sign-off. |
| 9 | Straggler without a 3.14 wheel | If `uv lock` cannot satisfy 3.14 for some package, **surface it to the user** — do not silently pin an old version or drop the package. |

## Current state (findings)

### Version settings are spread across five files

| Setting | File | Current value |
|---|---|---|
| `requires-python` | `pyproject.toml` | `">=3.11,<3.14"` |
| Trove classifiers | `pyproject.toml` | `3.11`, `3.12`, `3.13` |
| `[tool.mypy] python_version` | `pyproject.toml` | `"3.11"` |
| `[tool.ruff] target-version` | `pyproject.toml` | `"py311"` |
| pinned interpreter | `.python-version` | `3.12` |
| `uv python install/pin` + comment | `Makefile` (`create-venv`, `create-venv-linux`) | `3.12` |
| CI matrix | `.github/workflows/ci.yml` | `["3.11", "3.12", "3.13"]` |

(`mypy.ini` has **no** `python_version`; it lives in `[tool.mypy]` in `pyproject.toml`.)

### The dependency list pins many transitive Jupyter deps explicitly

`pyproject.toml` lists ~40 dependencies, of which a large block are transitive
dependencies of `jupyter` / `notebook` / `ipykernel` that were pinned by hand:
`traitlets`, `parso`, `jedi`, `pyzmq`, `tornado`, `mistune`, `pandocfilters`,
`send2trash`, `nest-asyncio`, `decorator`, `qtconsole`, `qtpy`, `jupyter-core`,
`jupyterlab-pygments`, `terminado`, `prompt-toolkit`, `pygments`. These get pulled in
automatically and only bloat the direct-dependency surface.

### marimo is installed with the `recommended` extra

`marimo[recommended]>=0.23.9` pulls in a broader optional suite than needed; the base
`marimo` install is sufficient for this template's use.

### The `pip-audit` ignore list may be stale after a bump

The `security-check` recipe in the `Makefile` ignores seven specific vulnerabilities
(`PYSEC-2023-157`, `PYSEC-2023-155`, `PYSEC-2023-272`, `PYSEC-2024-165`,
`PYSEC-2023-23`, `PYSEC-2023-24`, `GHSA-pjjw-68hj-v9mw`). Some of these are tied to
package versions that "latest everywhere" will move past, so the ignore may become moot.

## Target design

### Part 1 — Python version & tooling targets

| Setting | File | From → To |
|---|---|---|
| `requires-python` | `pyproject.toml` | `">=3.11,<3.14"` → `">=3.13,<3.15"` |
| Trove classifiers | `pyproject.toml` | drop `3.11`, `3.12`; add `3.14` (keep `3.13`) |
| `[tool.mypy] python_version` | `pyproject.toml` | `"3.11"` → `"3.13"` |
| `[tool.ruff] target-version` | `pyproject.toml` | `"py311"` → `"py313"` |
| pinned interpreter | `.python-version` | `3.12` → `3.13` |
| `uv python install` / `uv python pin` + "Python 3.12" comment | `Makefile` (`create-venv`, `create-venv-linux`) | `3.12` → `3.13` |

### Part 2 — Dependencies

**Kept as explicit top-level deps** (floors bumped to latest; the three currently-unpinned
deps — `openpyxl`, `termcolor`, `types-requests` — gain floors too, set to their locked latest):

- Data / utility stack: `pandas`, `numpy`, `scikit-learn`, `plotly`, `openpyxl`,
  `python-dotenv`, `gitpython`, `typedload`, `requests`, `aiohttp`, `urllib3`, `idna`,
  `termcolor`, `types-requests`.
- Notebook stack (top-level only): `jupyter`, `jupyter-client`, `jupyter-console`,
  `jupyter_server`, `notebook`, `jupyterlab`, `nbclient`, `nbconvert`, `nbformat`,
  `jupytext`, `papermill`, `ipykernel`, `ipython`, `ipywidgets`, `debugpy`.
- `marimo[recommended]` (**kept** — full ready-to-work editor suite; see Decision 6).
  Note its compiled extras (`duckdb`, `polars`, `pydantic-core`) join the 3.14-wheel
  surface under Decision 9.

**Dropped as explicit deps** (remain pinned transitively in `uv.lock`): `traitlets`,
`parso`, `jedi`, `pyzmq`, `tornado`, `mistune`, `pandocfilters`, `send2trash`,
`nest-asyncio`, `decorator`, `qtconsole`, `qtpy`, `jupyter-core`,
`jupyterlab-pygments`, `terminado`, `prompt-toolkit`, `pygments`.

**Optional-dependency groups** get the same latest-floor treatment:
- `dev`: `pytest`, `pytest-cov`, `mypy`, `ruff`, `bandit[toml]`, `pip-audit`,
  `beautifulsoup4`.
- `windows`: `pywin32`, `pywinpty` (markers unchanged).

**Lock:** a single `uv lock` regenerates `uv.lock`. Per Decision 9, any package that
cannot resolve a 3.14-compatible release is surfaced to the user rather than silently
pinned back or dropped.

**Stale comments:** update the dependency-block comments in `pyproject.toml` (e.g. the
"Upgraded Feb 2026: notebook 6.x → 7.x …" and "Notebook 7.x requires …" notes) so they
reflect the trimmed, re-bumped state rather than the old upgrade history.

### Part 3 — CI/CD

`.github/workflows/ci.yml` matrix `["3.11","3.12","3.13"]` → `["3.13","3.14"]`.
Everything else unchanged: `ubuntu-latest`, `uv sync --extra dev`, `make all-secure`,
per-version coverage artifact upload.

### Part 4 — Security-check ignore list

After the dependency bump, re-run `make security-check` (bandit + pip-audit) and rebuild
the `--ignore-vuln` list under a **three-case policy**:

1. **No longer fires** (latest moved past the vulnerable version) → remove the ignore.
2. **Still fires, a fixed release exists** → remove the ignore; the "latest everywhere"
   bump *is* the fix (upgrade, don't suppress).
3. **Still fires, no upstream fix even at latest** → keep the ignore as an accepted risk.

Each **kept** `--ignore-vuln` gets a **one-line reason comment** (package, why it's
unfixable/accepted, advisory date/link) to comply with `CLAUDE.md`'s "suppress with a
reason" rule. The final list is surfaced to the user for sign-off rather than decided
silently. The goal is that the suppression list reflects the actual post-update advisory
state.

### Part 5 — ADR & docs

- **New `docs/adr/0005-python-version-support-strategy.md`** (next in sequence after
  0004), **scoped narrowly to the Python version strategy** — the one decision here that
  is hard-to-reverse, surprising, and a real trade-off: drop 3.11/3.12, floor **3.13**,
  admit **3.14**, and the **local-default-3.13-but-CI-ceiling-3.14 split** with its
  stability rationale. The reversible dependency-posture items (trim transitive, keep
  `marimo[recommended]`, latest floors, pip-audit rebuild) are recorded in the
  **CHANGELOG and commit messages**, *not* the ADR — bundling them would dilute it.
  `CONTEXT.md` needs no change: no domain term is added or altered.
- **`docs/CHANGELOG.md`** entry, matching the recent commit cadence.
- **Doc sweep** for hardcoded `3.11` / `3.12` mentions and the "Python 3.12" setup text
  across `README.md`, `docs/PROJECT_VISION.md`, and `CLAUDE.md`; update the CI-matrix
  description and any dependency notes that reference the removed packages or the
  marimo `recommended` suite.

### Part 6 — Verification

- Regenerate `uv.lock` via `uv lock`.
- `make all-secure` locally on the new default **3.13** (mypy `--strict` + ruff format +
  lint + docstrings + pytest + security); optionally smoke 3.14 locally too.
- Confirm CI passes on **both 3.13 and 3.14** before merge (3.14 is proven in CI even
  though it is not the local default).
- Grep-audit that no `3.11` / `3.12` version reference survives in `pyproject.toml`,
  `Makefile`, `.python-version`, CI, or docs. (Note: marimo's `[recommended]` extra is
  **kept**, so there is no dropped-marimo-extra reference to audit for.)

## Open items / notes

- **No behavioural change intended** — config/logger loading (ADR 0001–0004),
  exceptions, transformers, and supervision runtime are untouched. This is purely a
  platform + dependency modernization.
- **3.14-wheel risk (Decision 9):** a straggler dependency without a 3.14 wheel is the
  one place this could stall. Resolution rule agreed during grilling: **core runtime**
  (`numpy`, `pandas`, `scikit-learn`, `requests`, `aiohttp`) must have real stable 3.14
  wheels — non-negotiable; **notebook/dev conveniences** (`qtconsole`, `papermill`, and
  the compiled marimo extras `duckdb`/`polars`/`pydantic-core`) may lag temporarily and
  are tracked with a `# TODO(3.14)` note. Stable releases only — no RCs pinned into the
  template. Every straggler is surfaced to the user with this core-vs-convenience framing
  rather than resolved silently. At ~9 months post-release the risk is low but real.
- **OS matrix stays ubuntu-only** — expanding CI to Windows is explicitly out of scope
  despite the Windows-first stance.
