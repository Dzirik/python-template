# Project Paths service

> **Status:** `ready-for-agent`

## Parent

[`specs/001_config_logger_decoupling/PRD.md`](../PRD.md) — *Decouple Config Loading from Logging & Anchor All Paths to Project Root*

## What to build

A new foundational **Project Paths** service (a module under `src/utils/`) that computes the project root **once** by walking up from its own source file to a marker (`pyproject.toml` or `.git`), and exposes the canonical I/O locations the rest of the code asks for: `root`, `data`, `logs`, `reports`, `configurations`, plus a resolver that turns a named `.conf` file into an absolute path.

Resolution must never depend on the current working directory — the same absolute locations resolve whether the code is launched from the repo root, a notebook, a direct `uv run` of a source file, or CI. A base-directory **environment override**, read through the **Env Selector** (`Envs`), repoints the root for out-of-repo deployments (e.g. containers). The `logs/` directory is created if it does not exist.

This is foundational per ADR 0001: it **must not import the project `Logger`**. Any breadcrumb it genuinely needs uses stdlib `logging.getLogger(__name__)`, never the singleton. All path work uses `pathlib` (Windows-first; verify on the Linux CI matrix too).

## Acceptance criteria

- [ ] `root` resolves to the marker directory regardless of the process CWD (verified by `chdir`-ing elsewhere in a test).
- [ ] `data`, `logs`, `reports`, `configurations` all resolve under `root`.
- [ ] A named-`.conf` resolver returns the correct absolute path under `configurations` (and its per-kind subfolders).
- [ ] The base-directory override, supplied via `Envs`, repoints the computed root; nothing touches `os.environ` directly.
- [ ] The `logs/` directory is created if absent.
- [ ] The module imports no project `Logger` (enforced by a test asserting the import graph, or equivalent).
- [ ] Tests mirror `src/` under `tests/tests_utils/`, follow the parametrized house style, and do not depend on the caller's CWD.
- [ ] `make all-secure` is green on Python 3.11 / 3.12 / 3.13.

## Blocked by

None - can start immediately.
