---
status: accepted
---

# Python support range is 3.13–3.14; local development defaults to 3.13 while CI proves both

This decision records the version-strategy outcome of
[`specs/007_update_and_optimize_python_version_and_libraries/BRAINSTORM.md`](../../specs/007_update_and_optimize_python_version_and_libraries/BRAINSTORM.md)
and relates to [`docs/PROJECT_VISION.md`](../PROJECT_VISION.md): the template's floor
is the floor every project forked from it inherits, so this choice is deliberately a
statement about the *future* the template is built for, not just its present. Only the
Python-support strategy lives here — it is the one part of that brainstorm that is
hard to reverse, surprising without context, and a genuine trade-off. The reversible
dependency-posture decisions from the same effort (trimming explicitly-pinned
transitive Jupyter deps to top-level, keeping `marimo[recommended]`, bumping every
floor to its current latest, rebuilding the `pip-audit` ignore list) are recorded in
the CHANGELOG and commit messages, not here.

The template previously declared `requires-python = ">=3.11,<3.14"`, pinned the local
interpreter to `3.12` (`.python-version`, `make create-venv`/`-linux`), targeted mypy
`3.11` / ruff `py311`, and ran a `["3.11", "3.12", "3.13"]` CI matrix. We decided to
raise the **floor to 3.13** (dropping 3.11 *and* 3.12 entirely), **admit 3.14** as the
ceiling (`requires-python = ">=3.13,<3.15"`), narrow CI to `["3.13", "3.14"]`, and move
the mypy/ruff targets to the new floor (`3.13` / `py313`). The distinguishing, and
initially counter-intuitive, part of the decision is that the **local development
default is `3.13`, not the newest admitted version** — CI carries the burden of proving
3.14 on every pull request, so the interpreter a developer runs day-to-day is the
proven, ~year-old one while 3.14 readiness is validated continuously rather than lived.

Two forces shape this. First, the floor is a **forward investment**: this template is
the foundation for a specific long-horizon project that will ramp over the coming year,
so being one version ahead now buys years of runway before the floor feels old — which
is why still-current 3.12 is dropped rather than kept for reach the template does not
need. Second, "newest floor" and "stability first" are *different axes* that the naive
reading conflates: how far *back* you support (the floor) governs reach, not stability,
while the *local default interpreter* is the actual stability lever. Separating them
lets the template be simultaneously forward-looking (floor 3.13, small two-version
matrix) and stable to work in (daily driver 3.13), with 3.14 proven in CI so the
eventual flip of the default to 3.14 is already green rather than a scramble. At the
time of the decision Python 3.14 was ~9 months past its stable release, so the "no
3.14 wheel" risk that would dominate a fresh-release migration is small and mostly
confined to fringe tooling.

## Considered options

- **Keep `>=3.11` with the three-version matrix (status quo)** — rejected: carries two
  interpreters (3.11, 3.12) that the template's forward-looking purpose does not need,
  pins the mypy/ruff targets to the oldest syntax level, and grows the CI surface to
  keep green for no offsetting benefit to a single-maintainer foundation repo.
- **Floor 3.12 (keep the still-current version), matrix `["3.12","3.13","3.14"]`** —
  rejected: 3.12 is still a common distro/CI default, so keeping it buys *reach*, but
  this template is forked-and-owned rather than published for broad consumption, so that
  reach is unused weight. It also enlarges the matrix to three and forfeits 3.13-only
  syntax/stdlib — the opposite of the "get ahead now" driver.
- **Floor 3.13, admit 3.14, local default 3.14** (the brainstorm's original draft) —
  rejected: making the newest admitted interpreter the daily driver bets everyday
  development on the least-proven runtime for *no* gain, because CI already proves 3.14
  on every PR. The stability lever (local default) should point at the proven version;
  pointing it at 3.14 spends stability to buy nothing.
- **Jump the floor to 3.14 (drop 3.13 too)** — rejected: leaves no backward-compatibility
  floor at all, strands any environment not yet on 3.14, and removes the very safety
  margin the dev-default/CI-ceiling split exists to provide.
- **Floor 3.13, admit 3.14, local default 3.13, CI proves both (chosen)** — a forward
  investment in the floor, a proven interpreter as the daily driver, and continuous
  validation of the next version in CI. Targeting mypy/ruff at the floor (`3.13`) means
  local checks catch 3.13-incompatible syntax even when the interpreter is newer, so the
  floor is enforced, not merely declared.

## Consequences

The local default interpreter (`3.13`) **intentionally trails** the newest version CI
proves (`3.14`). A future reader who expects "develop on the newest thing you ship" will
find this surprising — that is exactly why it is recorded: the trailing default is the
stability lever, and because CI stays green on 3.14 throughout, promoting the default to
3.14 later is a one-line change to `.python-version` and the `create-venv` targets, not a
migration.

Because mypy and ruff target the floor (`python_version = "3.13"`, `target-version =
"py313"`), a developer running a newer interpreter locally still cannot introduce syntax
or stdlib usage that would break on 3.13 — the floor is a real constraint on the code,
not just a metadata claim. The committed `uv.lock` remains the reproducibility contract;
the `>=` dependency floors are posture/documentation layered on top of it.

The floor becomes the floor of every project forked from this template. This decision
should be revisited when Python **3.15** ships (~October 2026): the natural next step is
to shift the range to 3.14–3.15 and promote the local default to 3.14, repeating the
same "proven default, newest-in-CI" shape. No behavioural change accompanies this ADR —
config/logger loading (ADR 0001–0004), exceptions, transformers, and the supervision
runtime are untouched; this is a platform-and-dependency modernization only.

One residual risk lives in the ceiling: a dependency without a stable 3.14 wheel is the
single place the coordinated re-lock could stall. The agreed rule is that **core runtime**
packages (`numpy`, `pandas`, `scikit-learn`, `requests`, `aiohttp`) must ship real stable
3.14 wheels — non-negotiable — while **notebook/dev conveniences** (e.g. `qtconsole`,
`papermill`, and the compiled `marimo[recommended]` extras `duckdb`/`polars`) may lag
temporarily behind a tracked `# TODO(3.14)` note. Pre-release/RC wheels are never pinned
into the template, and any straggler is surfaced for a call rather than resolved silently.
