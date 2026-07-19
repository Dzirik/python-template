# Add colored console echo to the `Logger` level methods

> **Status:** `ready-for-agent`

## What to build

The consolidation payload: make the "log this, and optionally echo a colored copy to the console" capability a first-class, discoverable option on every `Logger` level method, replacing the deleted `log_and_print`. This depends on the previous slice having removed the `helper_functions → Logger` import, so that `logger.py` can import `print_in_color` from `helper_functions.py` without a cycle.

End-to-end behaviour after this slice: `Logger().info("Batch 3/10 done", color="green")` logs the line as usual **and** prints a timestamp-prefixed green copy to the console; `Logger().info("Pipeline started")` (no color) logs only, exactly as today. The same optional parameters work on all five level methods, so a warning can echo in yellow and an error in red. The log record itself is unchanged — the echo is an additional console `print()`, not a change to any logging handler.

Scope:

- **Optional presentation params on each level method** — `debug`, `info`, `warning`, `error`, `critical` each gain `color: str | None = None`, `on_color: str | None = None`, `attrs: list[str] | None = None` after the existing `message: str`. Signatures stay backward compatible (all default to `None`), so existing positional `logger.info("...")` calls are unaffected.
- **Private echo helper** — each level method logs first (`self._logger.<level>(message)`), then calls one private helper (conceptually `_echo(message, color, on_color, attrs)`). The helper echoes to the console **only when `color is not None`**, building the timestamp-prefixed string `f"{datetime.now().strftime('%y-%m-%d %H:%M:%S')}: {message}"` and delegating the colored print to `print_in_color`. The timestamp lives in the Logger (it is specific to the log-echo use case), not in `print_in_color`.
- **Reuse `print_in_color`** — the Logger imports `print_in_color` from `helper_functions.py` rather than re-implementing `termcolor` handling; its tolerant fallback (bad color → plain print, no raise) is what makes the echo crash-safe.
- **New imports in `logger.py`** — `datetime` and `print_in_color`. `logger.py` must still **not** import `src.utils.config_loader` or `src.utils.application_config` (ADR 0001 — `test_logger_module_imports_no_config_loader_or_config` must keep passing); neither new import pulls in config machinery.
- **`__main__` demo** — add one colored-echo call (e.g. `my_logger.info("info with echo", color="green")`) to the module's `if __name__ == "__main__":` block so the feature is visible on direct run.
- **Untouched** — the timer methods (`start_timer`, `set_meantime`, `end_timer`) and all current logging behaviour (message, level, formatter, handler set, profiles, branch-name init line).
- **Echo tests added to `tests/tests_utils/test_logger.py`** — via `capsys`: `logger.info("msg", color="green")` produces a console line containing `msg` and the timestamp prefix (`NN-NN-NN NN:NN:NN:`); `logger.info("msg")` (no color) produces no such timestamp-prefixed echo line; and the echo path does not raise across `debug`/`warning`/`error`/`critical` when given a color (mirroring the existing "should not raise" level-method tests). The session-autouse `conftest.py` (`ENV_LOGGER=logger_console`) is the fixture; assertions target the distinctive timestamp-prefix format to separate the echo from handler output.

## Acceptance criteria

- [ ] All five level methods accept optional `color`/`on_color`/`attrs` params with `None` defaults; existing positional calls are unaffected.
- [ ] Passing a `color` both logs and prints a timestamp-prefixed colored copy to the console; omitting it logs only (no echo).
- [ ] The echo delegates coloring to `print_in_color` and inherits its graceful fallback on a bad color (no raise).
- [ ] The log record (message, level, format) is unchanged by the echo; the timer methods are untouched.
- [ ] `logger.py` imports `datetime` and `print_in_color` but neither `config_loader` nor `application_config`; `test_logger_module_imports_no_config_loader_or_config` passes.
- [ ] The `__main__` block demonstrates a colored echo.
- [ ] `test_logger.py` gains the echo tests (echo fires + is timestamped with color; no echo without color; no raise across levels) and all pre-existing `test_logger.py` tests still pass unchanged.
- [ ] `make all-secure` green on Python 3.11 / 3.12 / 3.13.

## Blocked by

- [`specs/005_resolve_log_and_print/issues/01-remove-log-and-print-slim-helper-functions.md`](01-remove-log-and-print-slim-helper-functions.md) — the `helper_functions → Logger` import must be removed first, or importing `print_in_color` into `logger.py` creates a circular import.
