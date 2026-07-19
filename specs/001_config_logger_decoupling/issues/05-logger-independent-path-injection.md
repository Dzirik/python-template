# Logger initializes independently and injects its resolved log path

> **Status:** `ready-for-agent`

## Parent

[`specs/001_config_logger_decoupling/PRD.md`](../PRD.md) — *Decouple Config Loading from Logging & Anchor All Paths to Project Root*

## What to build

Make the **Logger** startup independent of config *loading*: it must initialize without depending on the **Config Loader** or the **Application Config**, so config and logging are independently usable. The Logger resolves its own profile file and its log-output directory via **Project Paths**, and — because stdlib `logging.config.fileConfig` profiles cannot compute paths themselves — injects the resolved **absolute** log path into `fileConfig` at init. Drop the Logger's own 2-path candidate search.

`Logger()` stays a **Singleton**. The common public API is unchanged: `info/debug/warning/error/critical(...)` and the timer methods (`start_timer`, `set_meantime`, `end_timer`) behave as today, and the Logger keeps logging the active git branch and host on init. The profile is still chosen by the **Env Selector** (`ENV_LOGGER` → a `logger_*.conf`). Leaky low-value surface — `Logger().get() -> Any` and the `_is_logger` flag — may be removed surgically where it doesn't break the common public API.

At this stage the `logger_*.conf` files stay where they currently are (their move under `configurations/loggers/` and the `../../` strip are a later slice); the injected absolute path already overrides any in-file path, so this change merges with `make all-secure` green.

## Acceptance criteria

- [ ] `Logger()` initializes with no dependency on the Config Loader or Application Config (asserted).
- [ ] The log file lands in the **Project Paths**-resolved `logs/` directory (verified independent of CWD).
- [ ] The resolved absolute log path is injected into `logging.config.fileConfig` at init.
- [ ] The Logger's own 2-path candidate search is removed.
- [ ] `Logger()` is a Singleton; all log-level and timer methods behave as before; the git-branch/host breadcrumb is preserved.
- [ ] Profile is selected via `ENV_LOGGER` through `Envs`.
- [ ] `get()` and `_is_logger` are removed surgically iff the common public API stays intact.
- [ ] Existing `test_logger.py` behaviors pass (adjusted only if `get()` is removed); `make all-secure` green on 3.11 / 3.12 / 3.13.

## Blocked by

- [`01-project-paths-service.md`](./01-project-paths-service.md)
