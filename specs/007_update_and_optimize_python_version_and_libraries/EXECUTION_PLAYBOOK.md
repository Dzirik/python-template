# Execution Playbook — Update & optimize Python version and libraries

> Execution map over the ready issues. It does not restate them — read each issue for scope
> and acceptance criteria. Issues live in [`issues/`](./issues/); requirements in
> [`PRD.md`](./PRD.md); rationale in [ADR 0005](../../docs/adr/0005-python-version-support-strategy.md).

## Summary

- **Issues covered:**
  [01](./issues/01-python-modernization-and-relock.md) ·
  [02](./issues/02-version-consistency-test.md) ·
  [03](./issues/03-rebuild-pip-audit-ignore-list.md) ·
  [04](./issues/04-docs-sweep-and-changelog.md)
- **Verdict:** parallel — **2 waves + 1 HITL side-step, max concurrency 2**. A single
  unblocked core (01) fans out to three dependents; 02 and 04 are disjoint AFK slices that
  parallelize, 03 is human-gated and kept separate.
- **Highest execution risk:** the single `uv lock` in 01 hitting a dependency with no stable
  3.14 wheel. Per ADR 0005 / Decision 9, a *core-runtime* straggler stops the wave and
  escalates to the maintainer; conveniences may lag behind a tracked `# TODO(3.14)`.

## Waves

### Wave 1 — gate: `make all-secure` green on Python 3.13 **and** 3.14 (CI)

| Issue | Agent | Owns (files/dirs) | Must not touch | Depends on frozen interface |
|---|---|---|---|---|
| [01](./issues/01-python-modernization-and-relock.md) | A | `pyproject.toml`, `.python-version`, `Makefile` (create-venv recipes + echo text), `.github/workflows/ci.yml`, `uv.lock` | `tests/**`, `README.md`, `docs/**`, `CLAUDE.md`, the `Makefile` `security-check` recipe | — (produces the frozen interfaces) |

Effectively serial (one issue) — it is atomic by design (single re-lock; see PRD Approach A).

### Wave 2 — blocked by Wave 1 — gate: `make all-secure`

| Issue | Agent | Owns (files/dirs) | Must not touch | Depends on frozen interface |
|---|---|---|---|---|
| [02](./issues/02-version-consistency-test.md) | B | one **new** test file under `tests/tests_utils/` | `pyproject.toml`, `.python-version`, `ci.yml`, `Makefile`, `docs/**` | *Version-bearing settings* (from 01) |
| [04](./issues/04-docs-sweep-and-changelog.md) | C | `README.md`, `docs/PROJECT_VISION.md`, `CLAUDE.md`, `docs/CHANGELOG.md` | `pyproject.toml`, `.python-version`, `ci.yml`, `Makefile`, `tests/**`, `CONTEXT.md`, `docs/adr/**` | *Version-bearing settings* + *re-locked dependency set* (from 01) |

02 (tests) and 04 (docs) own strictly disjoint paths → collision-safe in parallel.

### HITL side-step — blocked by Wave 1 — gate: `make security-check` + maintainer sign-off

| Issue | Agent | Owns (files/dirs) | Must not touch | Depends on frozen interface |
|---|---|---|---|---|
| [03](./issues/03-rebuild-pip-audit-ignore-list.md) | D (human-in-the-loop) | `Makefile` (`security-check` recipe only) | `pyproject.toml`, `.python-version`, `ci.yml`, `Makefile` create-venv recipes, `tests/**`, `docs/**` | *re-locked dependency set* (from 01) |

May run in wall-clock alongside Wave 2 — its `Makefile` recipe does not overlap 02/04's paths.
Kept out of the parallel AFK wave because keeping a suppression is a human risk-acceptance
decision. Its `security-check`-recipe edits build on 01's `Makefile` changes, so rebase on
Wave 1 before starting.

## Frozen interfaces

No code contracts (config/dependency work). Two artifacts must be frozen by **01** before the
Wave 2 / HITL agents start — both already fixed in the PRD and ADR 0005, so 01 lands them verbatim:

- **Version-bearing settings** — canonical target values (`requires-python ">=3.13,<3.15"`,
  classifiers `{3.13, 3.14}`, mypy `python_version "3.13"`, ruff `target-version "py313"`,
  `.python-version 3.13`, CI matrix `["3.13","3.14"]`). Owned by 01; consumed by 02 (asserts)
  and 04 (documents).
- **Re-locked dependency set** — the regenerated `uv.lock` + final `pyproject.toml` dependency
  declaration (latest floors, `marimo[recommended]` kept, transitive Jupyter pins trimmed).
  Owned by 01; consumed by 03 (audits advisories) and 04 (describes).

## Per-agent dispatch specs

### Agent A — Wave 1 — issue [01](./issues/01-python-modernization-and-relock.md)

- **Goal:** move the template to the 3.13–3.14 range and refresh every dependency to latest, frozen in one `uv.lock`, proven by CI on both interpreters.
- **Scope (OWNS):** `pyproject.toml`, `.python-version`, `Makefile` (create-venv/-linux recipes + echo text), `.github/workflows/ci.yml`, `uv.lock`.
- **Inputs:** issue 01; the two frozen-interface definitions above (from PRD/ADR 0005).
- **Outputs:** updated version settings, refreshed dependency block, regenerated `uv.lock`.
- **Constraints:** must NOT touch `tests/**`, docs, `CLAUDE.md`, `CONTEXT.md`, or the `Makefile` `security-check` recipe. Must not pin a core-runtime package to a pre-3.14 release or an RC — escalate a core straggler to the maintainer.
- **Integration:** merge to the feature branch first — gate: `make all-secure` green on 3.13 and 3.14 in CI.
- **Dispatch:** serial (atomic core; single re-lock).

### Agent B — Wave 2 — issue [02](./issues/02-version-consistency-test.md)

- **Goal:** add the regression test that forbids 3.11/3.12 and pins the version files in sync.
- **Scope (OWNS):** one new test file under `tests/tests_utils/`.
- **Inputs:** frozen *Version-bearing settings*; issue 02; prior-art test `test_logger_module_imports_no_config_loader_or_config`.
- **Outputs:** a passing pytest asserting the version contract; fails if 3.11/3.12 reappears.
- **Constraints:** must NOT touch `pyproject.toml`, `.python-version`, `ci.yml`, `Makefile`, or docs; must not invoke `uv lock`/`uv sync`.
- **Integration:** merge after Wave 1 — gate: `make all-secure`.
- **Dispatch:** isolated subagent (parallel-safe).

### Agent C — Wave 2 — issue [04](./issues/04-docs-sweep-and-changelog.md)

- **Goal:** align docs with the 3.13–3.14 baseline and record the change in the CHANGELOG.
- **Scope (OWNS):** `README.md`, `docs/PROJECT_VISION.md`, `CLAUDE.md`, `docs/CHANGELOG.md`.
- **Inputs:** frozen *Version-bearing settings* + *re-locked dependency set*; issue 04.
- **Outputs:** swept docs (no stale 3.11/3.12), CI-matrix text → 3.13/3.14, CHANGELOG entry referencing ADR 0005.
- **Constraints:** must NOT touch `pyproject.toml`, `.python-version`, `ci.yml`, `Makefile`, `tests/**`, `CONTEXT.md`, or `docs/adr/**` (ADR 0005 already exists — do not duplicate).
- **Integration:** merge after Wave 1 — gate: `make all-secure`.
- **Dispatch:** isolated subagent (parallel-safe).

### Agent D — HITL side-step — issue [03](./issues/03-rebuild-pip-audit-ignore-list.md)

- **Goal:** rebuild the `pip-audit` ignore list against the post-lock advisory state, annotated and signed off.
- **Scope (OWNS):** the `Makefile` `security-check` recipe only.
- **Inputs:** frozen *re-locked dependency set*; issue 03.
- **Outputs:** a rebuilt, reason-annotated `--ignore-vuln` list; `make security-check` passing.
- **Constraints:** must NOT touch the `Makefile` create-venv recipes, `pyproject.toml`, `.python-version`, `ci.yml`, `tests/**`, or docs. Rebase on Wave 1's `Makefile` edits first.
- **Integration:** merge after maintainer approves the residual-suppression list — gate: `make security-check` + sign-off.
- **Dispatch:** serial (human-in-the-loop).

## Merge order & gates

1. **Wave 1 (01)** merges first; gate: `make all-secure` green on **both 3.13 and 3.14** in CI.
2. **Wave 2 (02, 04)** fan out in parallel once Wave 1 is green; each merges independently behind `make all-secure`.
3. **HITL 03** may run alongside Wave 2 but merges only after maintainer sign-off; gate: `make security-check`.
4. **Final integration gate:** `make all-secure` green on 3.13 and 3.14 with all four merged, plus a grep-audit confirming no `3.11`/`3.12` reference survives (now backstopped by 02's test).

Prefer frequent small merges (01, then 02/04/03 as each lands) over one large integration event.

## Serial fallback

If Wave 2's concurrency is not worth the coordination (02 and 04 are both small), collapse to a
single branch in order **01 → 02 → 04 → 03**. This is a legitimate outcome — the only genuine
parallelism here is 02 ∥ 04, and the atomic core (01) plus the human-gated tail (03) are serial
regardless.
