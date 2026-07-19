# Record ADR 0004 — Logger profiles are TOML loaded via `dictConfig`

> **Status:** `ready-for-agent`

## Parent

[`specs/004_check_logger_config_format/PRD.md`](../PRD.md) — *Migrate the Logger profiles from INI (`fileConfig`) to TOML (`dictConfig`)*

## What to build

A new architecture decision record (`docs/adr/0004-*`) capturing *why* the Logger profiles moved from stdlib INI (`fileConfig`) to TOML (`dictConfig`), so a future contributor understands the trade-off without re-deriving it. Follow the house style of the existing ADRs (`0001-foundational-config-layering.md`, `0002-repo-root-path-anchoring.md`, `0003-toml-config-profiles.md`). It explicitly closes the loop left open by ADR 0003's *Consequences* paragraph, which deferred the Logger profiles as dictated by `fileConfig`.

The record must include:

- The decision: the five logger profiles are TOML `dictConfig` documents, parsed by stdlib `tomllib`, loaded via `logging.config.dictConfig`.
- The comparison of options considered — keep `fileConfig`/INI (status quo) / TOML+`dictConfig` (chosen) / a Python-dict-in-code config / JSON / YAML — with why each was accepted or rejected (Python-dict-in-code loses file-based editable config; JSON loses `#` comments; YAML adds a third-party parser, contradicting spec 003's stdlib-only stance).
- The enabling insight: the stdlib exposes two front-ends over the same logging machinery (`fileConfig` takes INI, `dictConfig` takes a `dict`); because `dictConfig` takes a `dict`, the absolute log path can be injected in Python before any handler is instantiated.
- The two hacks this retires: the `_load_profile` `FileNotFoundError` retry-with-`mkdir`, and the post-hoc `_redirect_file_handlers_to_project_paths()` close-and-reopen pass.
- The `disable_existing_loggers` gotcha: `dictConfig` defaults the dict key to `true`, unlike the previous `fileConfig(..., disable_existing_loggers=False)`, so it is set `false` in every profile.
- That `.conf` is now retired from the repository entirely (completing spec 003's de-overloading), and the config-free import constraint (ADR 0001) is preserved — the Logger parses TOML with `tomllib` directly rather than reusing `load_config`.
- A recorded-but-not-triggered reversal condition: if profiles ever needed genuinely dynamic, code-computed handler wiring beyond a single injected path, a Python-dict-in-code approach would start earning its keep.

## Acceptance criteria

- [ ] `docs/adr/0004-*.md` exists, following the format/structure of ADRs 0001–0003.
- [ ] It states the decision, the option comparison with rationale, the two-front-ends insight, the two retired hacks, the `disable_existing_loggers` gotcha, the `.conf`-retirement/ADR-0001 note, and the reversal condition.
- [ ] It is cross-referenced consistently with the PRD's `relates-to: docs/adr/0003-toml-config-profiles.md` framing and closes ADR 0003's deferred *Consequences* thread.
- [ ] `make all-secure` stays green (docs-only change).

## Blocked by

- None - can start immediately.
