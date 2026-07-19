---
status: accepted
---

# Logger profiles are TOML `dictConfig` documents, parsed by stdlib `tomllib`

This decision records the outcome of
[`specs/004_check_logger_config_format/PRD.md`](../../specs/004_check_logger_config_format/PRD.md),
which relates to [ADR 0003](0003-toml-config-profiles.md) and closes the thread its
*Consequences* paragraph deliberately left open: "the Logger's stdlib-INI profiles ...
are out of scope here because `logging.config.fileConfig` dictates their format." That
was true only because ADR 0003 never asked whether `fileConfig` was the sole stdlib
front-end available — it is not.

The five Logger profiles (`logger_console`, `logger_file`, `logger_file_console`,
`logger_file_limit`, `logger_file_limit_console`) were stdlib INI, loaded through
`logging.config.fileConfig`. INI forced two costs on `Logger` (`src/utils/logger.py`):
handler constructor arguments were passed as `args=` strings that `fileConfig`
`eval()`s as Python source (opaque, positional, an `eval`-on-config-text smell under
`make security-check`'s `bandit` gate), and those arguments were CWD-relative file
paths that `logging.FileHandler` opens eagerly, which forced a
`try/except FileNotFoundError` retry-with-`mkdir` in `_load_profile` and a separate
post-hoc `_redirect_file_handlers_to_project_paths()` pass that closed and reopened
every file handler onto `ProjectPaths().logs` after the fact. After ADR 0003, `.conf`
INI was also the template's last non-TOML config format.

The enabling insight: **the stdlib exposes two config front-ends over the same
logging machinery.** `fileConfig` consumes INI; `dictConfig` consumes a plain `dict`.
`tomllib.load()` produces exactly the kind of plain `dict` `dictConfig` accepts, and a
`dictConfig` document expresses every construct these profiles use — formatters,
`StreamHandler`, `FileHandler`, `RotatingFileHandler`, a configured `root` logger —
natively, with named keys instead of positional eval'd tuples. Because `dictConfig`
takes a `dict` rather than a file handle, the absolute log path can be **computed in
Python and injected into the dict before any handler is instantiated**. That seam is
what retires both hacks: `_load_profile` now `tomllib.load()`s the profile, rewrites
each handler's `filename` to `str(ProjectPaths().logs / Path(filename).name)` on the
plain dict (keeping the basename, forcing the directory), and calls
`logging.config.dictConfig(parsed)`. Since `ProjectPaths.__init__` already `mkdir`s the
logs directory, the handler always opens an existing path, so there is nothing to
catch and nothing to reopen — the `FileNotFoundError` retry and
`_redirect_file_handlers_to_project_paths()` are both deleted outright rather than
adapted.

We decided to express the five Logger profiles in **TOML**, loaded via
**`logging.config.dictConfig`**, parsed by the standard-library `tomllib` — no new
runtime dependency, no change to logging behaviour (levels, formatter string,
rotation sizes/counts, handler set per profile, and the `root`/named-logger
propagation structure are all preserved verbatim).

## Considered options

- **Keep `fileConfig`/INI (status quo)** — rejected: keeps the `eval`'d `args=`
  strings, the CWD-relative-path retry-with-`mkdir`, and the post-hoc handler
  reopen — three pieces of fragile mechanism with no offsetting benefit now that
  ADR 0003 established TOML + stdlib parsing as the template's config standard.
- **TOML, loaded via `dictConfig`, parsed by stdlib `tomllib` (chosen)** — removes
  the `eval`, lets the absolute log path be injected before handler instantiation
  (retiring both hacks), keeps `#` comments, and gives the profiles the same native
  PyCharm recognition ADR 0003 already won for the other config families — all
  with no new dependency.
- **A Python-dict-in-code configuration** (drop the profile files, build the
  `dictConfig` dict in `logger.py`) — rejected: loses the file-based,
  non-programmer-editable config the template provides, for no benefit given the
  migration only needs a single injected path, not code-computed handler wiring.
- **JSON** — rejected: has a stdlib parser (`json`) but no comment syntax, and the
  profiles carry human-facing guidance comments (the level cheat-sheet
  `NOTSET=0 DEBUG=10 INFO=20 ...`, the rotation-size note, reference links) that
  would be lost.
- **YAML** — rejected: has no stdlib parser, so adopting it means adding a
  third-party dependency (`PyYAML` or similar) purely to reach parity with what
  `tomllib` already gives for free — directly contradicting the stdlib-only stance
  ADR 0003 established for exactly this reason.

## Consequences

`disable_existing_loggers` is a gotcha in the switch: `fileConfig` was called with
`disable_existing_loggers=False`, but `dictConfig` defaults the *dict key* to `true`.
Every one of the five profiles sets `disable_existing_loggers = false` explicitly in
its TOML, so already-created loggers are not silently disabled — this is not an
incidental style choice but a required behavioural equivalence.

`.conf` is now retired from the repository entirely, completing what ADR 0003 started:
after that decision `.conf` meant exactly one thing (the Logger's stdlib-INI
profiles); now no file in the tree carries it, and `ProjectPaths.config_file`'s
`extension` default flips from `".conf"` to `".toml"` since no caller relies on the
old default any longer.

ADR 0001's "config loading stays Logger-free" guarantee is preserved in the direction
that matters here too: `Logger` does not start importing `src.utils.config_loader` or
`src.utils.application_config` to parse its own profile. It calls stdlib `tomllib`
directly — the same stdlib-only posture it already had via `logging.config` — so
`test_logger_module_imports_no_config_loader_or_config` keeps passing unchanged.

If profiles ever needed genuinely dynamic, code-computed handler wiring beyond a
single injected path — for example, handlers chosen at runtime from application
state — a Python-dict-in-code approach would start earning its keep over static TOML
files. No such need exists yet, so this is recorded but not acted on.
