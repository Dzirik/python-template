---
status: accepted
---

# All paths anchor to the project root, and all configs live in one central tree

Both the *location* of `.conf` files and the paths *inside* them (`data`, `logs`,
`reports`) were resolved against the current working directory via `../../` and
per-class candidate-path searches (`ApplicationConfig` tried 4 paths, `Logger` 2,
`BaseComponentConfig` 1). CWD differs between `make`, notebooks, direct file runs, and CI,
so resolution was unreliable — the root cause of the "`.conf` debugging" and
"can't point at `logs/`" pain. We decided to introduce a **Project Paths** service
that computes the project root once (walking up from `__file__` to a marker such
as `pyproject.toml`/`.git`) and resolves every config file and every in/out path
against it, with an environment override (via `Envs`) for out-of-repo
deployments. All `.conf` files stay under one central `configurations/` tree
organized by kind: **Application Config** (`python_*`) at the top level, **Logger**
profiles under `loggers/`, and each **Component Config** kind in its own subfolder
(e.g. `watchdogs/`). No `.conf` file contains a CWD-relative path.

## Considered options

- **Unified CWD candidate-path search** — rejected: keeps the fragility, just
  in one place.
- **`os.chdir(project_root)` at startup** — rejected: a global side effect that
  breaks notebooks and any embedding context.
- **Per-module co-location of component configs** (`watchdog_*.conf` next to
  `watchdog.py`, found via `Path(__file__).parent`) — rejected: once Project
  Paths makes finding deterministic, co-location's only advantage disappears,
  while it scatters `.conf` files into `src/` and splits the mental model
  (`__file__`-relative vs. repo-root).

## Consequences

The stdlib `logger_*.conf` profiles cannot compute paths themselves, so the
resolved absolute log path is injected into `logging.config.fileConfig` at logger
init. The Project Paths env override becomes the natural seam for future
out-of-repo / containerized deployment.
