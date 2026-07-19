---
status: ready-for-agent
labels: [ready-for-agent]
supersedes: none
relates-to: docs/adr/0004-logger-profiles-toml-dictconfig.md
builds-on: none
---

# PRD: Consolidate colored console echo into the `Logger`

> **Context:** The **Logger** (`src/utils/logger.py`) is the process-wide logging
> facility. A separate `log_and_print` helper in `src/utils/helper_functions.py`
> currently duplicates a slice of that responsibility — it logs *and* prints a colored
> copy to the console — and to do so it imports the Logger, splitting "log this, and
> optionally show it on the console" across two modules. This PRD folds that capability
> into the Logger itself. It does not touch config loading, so ADR 0001's rule (nothing
> in the Config Loader depends on the Logger) and ADR 0004 (Logger profiles are
> TOML/`dictConfig`) are untouched.

## Problem Statement

As a developer using this template for production data pipelines, I log heavily through
the **Logger** (`Logger().info(...)`, etc.). For a *selected subset* of those log calls
I also want a colored copy printed to the console, so I can eyeball main behavioural
changes and progress live while the full record still goes to the log.

Today that capability lives in a second module. `src/utils/helper_functions.py` defines
`log_and_print(message, color=..., on_color=..., attrs=..., log_only=...)`, which calls
`Logger().info(message)` and then prints a timestamp-prefixed, optionally colored copy
to the console via a sibling `print_in_color` helper. This split has concrete costs:

- **The responsibility is fragmented.** "Log, and optionally echo to console" is a
  Logger concern, but half of it lives in a general-purpose `helper_functions` module.
  A developer reaching for the Logger does not discover the echo capability; it is not
  where you would look for it.
- **The dependency runs the wrong way.** `helper_functions.py` imports `Logger` purely
  to implement `log_and_print`, so a grab-bag helper module depends on the Logger.
- **It is effectively dead and undiscoverable.** `log_and_print` and `print_in_color`
  are not called anywhere in the codebase — the only mentions are `# log_and_print`
  comments sitting above bare `print()` calls in the two
  `src/scripts_production/run_cmd_status_print_*.py` example scripts. There are no tests
  for the module, and both functions' docstrings point readers to a
  `src/utils/color_console_print.py` file that does not exist.
- **The echo is bolted onto one level only.** `log_and_print` always logs at `INFO`.
  There is no clean way to echo a `warning`/`error` line to the console in color.

There is no active breakage — logging works. The problem is a fragmented
responsibility, an inverted dependency, and an undiscoverable, untested, `INFO`-only
convenience that the developer wants to keep using but in a nicer, consolidated form.

## Solution

As a developer, I want the five **Logger** level methods (`debug`, `info`, `warning`,
`error`, `critical`) to each accept optional presentation parameters — `color`,
`on_color`, `attrs` — so that passing a `color` makes the method **log as usual *and*
echo the message to the console in that color** (timestamp-prefixed), while omitting it
logs only, exactly as today. This makes "log this, and also show it on the console in
green" a first-class, discoverable option on every log call, at the natural place
(`Logger().info(msg, color="green")`), with no separate function to remember.

`log_and_print` is deleted. `print_in_color` is **kept** as a standalone, log-free
public utility for colored console output, and becomes the coloring primitive the
Logger reuses for its echo — so the color-handling logic is not duplicated.

The decisive simplifications this unlocks:

- **The dependency direction flips cleanly.** Once `log_and_print` is gone,
  `helper_functions.py` no longer imports `Logger` (it needs only `termcolor`), and the
  Logger imports `print_in_color` from it. `logger.py → helper_functions.py`, no cycle.
- **The `log_only` flag disappears.** Under the new shape, *not passing a color* is the
  log-only case, so the separate `log_only` boolean is no longer needed.
- **Echo becomes available at every level**, not just `INFO`, because the parameters
  live on each level method.

The echo keeps its current timestamp prefix (`%y-%m-%d %H:%M:%S: <message>`) so live
console monitoring shows when each line printed, independent of the log handler's own
timestamp.

## User Stories

1. As a pipeline developer, I want `Logger().info("Batch 3/10 done", color="green")` to
   both log the line and print a green copy to the console, so that I can monitor main
   behavioural changes live without a second function call.
2. As a pipeline developer, I want `Logger().info("Pipeline started")` (no color) to log
   only, exactly as it does today, so that existing calls are unaffected.
3. As a developer, I want the same optional `color`/`on_color`/`attrs` parameters on all
   five level methods (`debug`, `info`, `warning`, `error`, `critical`), so that I can
   echo a warning in yellow or an error in red, not just `INFO` lines.
4. As a developer, I want the console echo to fire when (and only when) I pass a
   `color`, so that opting into console output is explicit and the default stays
   log-only.
5. As a developer, I want the echoed console line to keep a short timestamp prefix
   (`25-07-14 09:30:01: <message>`), so that live monitoring shows when each line
   printed.
6. As a developer, I want a bad or unsupported `color` value to degrade gracefully to a
   plain (uncolored) print rather than raising, so that a monitoring echo never crashes a
   pipeline — matching `print_in_color`'s current tolerant behaviour.
7. As a developer, I want the log record itself to be unchanged by the echo (same
   message, same level, no timestamp prefix in the log — the handler owns that), so that
   the file/console log format is exactly what it was.
8. As a developer, I want `log_and_print` removed, so that there is one obvious place —
   the Logger — that owns "log, and optionally echo to console."
9. As a developer, I want `print_in_color` kept as a standalone, log-free public utility
   in `helper_functions.py`, so that I can still print colored console output without
   logging, and so the Logger's echo reuses one coloring implementation.
10. As a developer, I want `helper_functions.py` to no longer import `Logger` (and to
    drop the now-unused `datetime` import), so that the module → Logger dependency is
    removed and the import direction becomes `logger.py → helper_functions.py` with no
    cycle.
11. As a developer, I want the `log_only` parameter gone, so that the API has one way to
    express "log only" (omit the color) instead of two.
12. As a developer, I want the `Logger.__main__` self-test to demonstrate a colored echo,
    so that the feature is visible when the module is run directly.
13. As a developer, I want the stale docstring references to the non-existent
    `src/utils/color_console_print.py` corrected (to point at `termcolor` / this module),
    so that the docs describe reality — consistent with spec 004's documentation
    truthfulness sweep.
14. As a developer, I want `Logger` to keep parsing its profile with stdlib `tomllib` and
    to **not** import `config_loader` / `application_config`, so that ADR 0001 and its
    guard (`test_logger_module_imports_no_config_loader_or_config`) keep passing — the
    only new import in `logger.py` is `datetime` and `print_in_color` from
    `helper_functions`, neither of which pulls in config machinery.
15. As a developer, I want all existing `test_logger.py` behaviour (singleton,
    initialisation, every level method, timer integration, `get()`, the config-free
    import guard, the CWD-independence subprocess regression) to keep passing unchanged,
    so that the consolidation is behaviourally invisible to current logging.
16. As a developer, I want the timer-related Logger methods (`start_timer`,
    `set_meantime`, `end_timer`) left untouched, so that the change stays scoped to the
    level methods.
17. As a developer running `make all-secure`, I want the full quality gate (mypy strict,
    ruff format/lint/docstring, pytest, bandit, pip-audit) to pass on the 3.11/3.12/3.13
    matrix, so that CI stays green.

## Implementation Decisions

- **API shape: optional presentation parameters on each level method.** Each of
  `debug`, `info`, `warning`, `error`, `critical` gains three optional keyword
  parameters — `color: str | None = None`, `on_color: str | None = None`,
  `attrs: list[str] | None = None` — after the existing `message: str`. The signatures
  are backward compatible (all new params default to `None`), so every current
  positional `logger.info("...")` call is unaffected.
- **Echo trigger: `color is not None`.** Each level method logs first
  (`self._logger.<level>(message)`), then calls a single private echo helper. The helper
  echoes to the console only when `color is not None`. This matches the underlying
  `print_in_color` contract, where `on_color`/`attrs` take effect only alongside a
  `color`; passing them without a `color` is a no-op echo (documented, minor).
- **One private echo helper.** A private method on `Logger` (conceptually
  `_echo(message, color, on_color, attrs)`) builds the timestamp-prefixed console string
  `f"{datetime.now().strftime('%y-%m-%d %H:%M:%S')}: {message}"` and delegates the actual
  colored print to `print_in_color`. The timestamp lives in the Logger (not in
  `print_in_color`), because it is specific to the log-echo use case.
- **`print_in_color` is the reused coloring primitive.** Its tolerant behaviour is
  retained verbatim: on an invalid `color` it falls back to a plain print rather than
  raising. The Logger reuses it rather than re-implementing `termcolor` handling.
- **`log_and_print` deleted; `log_only` removed with it.** The "log only" case is now
  expressed by omitting `color`, so the boolean flag is dropped rather than migrated.
- **`helper_functions.py` slimmed.** Removing `log_and_print` also removes the module's
  `from src.utils.logger import Logger` and `from datetime import datetime` imports;
  only `from termcolor import colored` (used by `print_in_color`) remains. Its module and
  function docstrings are corrected to stop referencing the non-existent
  `color_console_print.py`.
- **Import direction / cycle.** After the change the dependency is
  `logger.py → helper_functions.py`. Because `helper_functions.py` no longer imports the
  Logger, there is no import cycle, and `helper_functions` pulls in only `termcolor` —
  no config-loading modules — so `logger.py`'s config-free-import guarantee is preserved.
- **`__main__` demo.** The Logger's `if __name__ == "__main__":` block gains one colored
  echo call (e.g. `my_logger.info("info with echo", color="green")`) so running the
  module directly shows the feature.
- **Out-of-scope call sites left alone.** The `# log_and_print` comments in
  `src/scripts_production/run_cmd_status_print_*.py` sit above bare `print()` calls that
  are not being rewired to the Logger here (see *Out of Scope*); the dangling comment is
  removed or corrected so it no longer references a deleted function.

## Testing Decisions

- **Good tests exercise observable behaviour, not internals.** Tests drive the public
  `Logger` level methods and the public `print_in_color` function and assert on what a
  user observes — console output captured via pytest's `capsys` — never on how the echo
  string is assembled or which private helper is called.
- **Primary seam — reuse `tests/tests_utils/test_logger.py` (the highest available
  seam).** Add tests that:
  - `logger.info("msg", color="green")` produces a console line containing `msg` and the
    timestamp prefix (`NN-NN-NN NN:NN:NN:`), proving the echo fired and is timestamped.
  - `logger.info("msg")` (no color) produces no such timestamp-prefixed echo line,
    proving the default stays log-only.
  - the echo path does not raise across the other levels (`debug`/`warning`/`error`/
    `critical`) when given a color — mirroring the existing "should not raise" style of
    the current level-method tests.
  The existing `test_logger.py` tests (singleton, init, level methods, timer, `get()`,
  `test_logger_module_imports_no_config_loader_or_config`, and the
  `test_logger_file_handler_lands_in_project_paths_logs` subprocess regression) must all
  keep passing unchanged.
- **New seam — `tests/tests_utils/test_helper_functions.py`** (new file, but a
  pre-existing *public-function* seam: `print_in_color` was simply untested). Unit-test
  `print_in_color` via `capsys`: it prints the message; it falls back to a plain print
  when handed a bad/unsupported color (does not raise); and it plain-prints when
  `color is None`.
- **Prior art.** The `capsys`-free "call it, assert no exception" pattern already used by
  `test_logger_debug`/`_info`/`_warning`/… is the model for the new level-method echo
  smoke tests; the new `print_in_color` assertions add explicit `capsys` output checks in
  the same test-tree location (`tests/tests_utils/`, mirroring `src/utils/`).
- **Fixtures.** The session-autouse `conftest.py` forces `ENV_LOGGER=logger_console`, so
  the echo tests run under the console profile with no new fixture. `capsys` captures the
  `print()` echo (stdout); assertions target the distinctive timestamp-prefix format to
  separate the echo from any handler output.
- **Gate.** `make all-secure` must pass on the 3.11/3.12/3.13 matrix.

## Out of Scope

- **Rewiring the `run_cmd_status_print_*.py` example scripts to log-and-echo.** Their
  bare `print()` calls are left as-is (only the dangling `# log_and_print` comment is
  cleaned up). Converting them would change their behaviour (they would start logging)
  and is a separate decision.
- **A colored console *handler* driven by log level** (errors auto-red, etc.). Considered
  and rejected in design: the developer wants explicit, per-call color choice for a
  selected subset of lines, not level-keyed automatic coloring.
- **A separate `log_and_print` method on the Logger.** The chosen shape is optional
  parameters on the existing level methods, not a new dedicated method.
- **Changing logging behaviour** — the log record's message, level, formatter, handler
  set, profiles, or the branch-name init log line are all unchanged. The echo is an
  additional console `print()`, not a change to any logging handler.
- **Changing the config/logger profile format or loading** (ADR 0003 / ADR 0004 stand).
- **Removing or restructuring `print_in_color`** beyond dropping its stale docstring
  reference — it stays as a public log-free utility.
- **An ADR.** This is a small consolidation within one module's public surface, not an
  architectural decision reversal; no ADR is required (contrast spec 004, which recorded
  a format decision).

## Further Notes

### API before / after

**Before** (`src/utils/helper_functions.py`, a separate module that imports the Logger):

```python
log_and_print("Batch 3/10 done", color="green")           # logs at INFO + green console echo
log_and_print("internal detail", log_only=True)           # logs only, no console echo
# print_in_color lives beside it; nothing calls either.
```

**After** (`src/utils/logger.py`, on the Logger itself):

```python
logger.info("Pipeline started")                 # log only (the old log_only=True case)
logger.info("Batch 3/10 done", color="green")   # log + green console echo (timestamped)
logger.warning("Retrying", color="yellow")      # log + yellow console echo
logger.error("Row 42 failed", color="red")      # log + red console echo
# print_in_color remains as a standalone, log-free colored-print utility.
```

Level-method signature (illustrative — `info`; the other four match):

```python
def info(self, message: str, color: str | None = None,
         on_color: str | None = None, attrs: list[str] | None = None) -> None:
    self._logger.info(message)
    self._echo(message, color, on_color, attrs)
```

### Why keep `print_in_color` rather than fold it in

`print_in_color` is a genuinely reusable, log-free primitive (colored console output
with a graceful fallback on bad colors). Keeping it standalone lets the Logger reuse one
coloring implementation instead of duplicating `termcolor` handling, and preserves a
colored-print option for callers who explicitly do *not* want to log. The only change to
it is the corrected docstring reference.

### Estimated cost

Small, low risk: three optional parameters plus one private echo helper added to
`Logger`, five one-line additions to the level-method bodies, one function deleted and
two imports dropped from `helper_functions.py`, a `__main__` demo line, a corrected
docstring, and two focused test additions (echo behaviour in `test_logger.py`, a new
`test_helper_functions.py` for `print_in_color`). `make all-secure` is the acceptance
gate.

### Provenance

This PRD is the outcome of a design-review session. Findings that shaped it: both
`log_and_print` and `print_in_color` are defined but never called (only `# log_and_print`
comments above bare prints in `run_cmd_status_print_*.py`), there are no tests for the
module, and the docstrings reference a non-existent `color_console_print.py`. The
developer confirmed the real goal: preserve the "log heavily, echo a selected colored
subset to the console for live monitoring" workflow, but consolidate it into the Logger.
The API shape (color params on level methods vs. a dedicated method vs. a level-keyed
colored handler), the fate of `print_in_color` (kept standalone vs. folded in), and the
timestamp prefix (kept) were each decided explicitly during the session.
