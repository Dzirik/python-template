# Config model: tracked base + strict overlay loader

> **Status:** `ready-for-agent`

## Parent

[`../BRAINSTORM.md`](../BRAINSTORM.md) — P0+P1 implementation. Realises **ADR 0006**
([`docs/adr/0006-config-tracked-base-and-overlays.md`](../../../../docs/adr/0006-config-tracked-base-and-overlays.md)).
Report items: P0#2 (clean checkouts pass), P0#3 (strict typedload), P1 D6 (config overlay).

## What to build

Make `python_repo` the tracked, default, always-loaded **base** config profile, with
`python_personal`/`python_local` as optional **partial overlays** deep-merged over it, and
load the merged result strictly. This fixes the clean-checkout failure (default was the
git-ignored `python_personal`, so a fresh clone / CI failed three `test_application_config.py`
tests) and closes the "add one key, break every teammate's profile" trap.

1. **`env_constants.py`** — `DEFAULT_CONFIG = "python_repo"` (was `python_personal`).
2. **`config_loader.py`** — add an optional `base_name: str | None = None` parameter to
   `load_config`. When given, parse `base_name` and `config_name` separately, **deep-merge**
   the override dict over the base dict (nested tables merged recursively; scalars/lists
   replaced wholesale) via a private `_deep_merge`, then run a single
   `typedload.load(merged, target, basiccast=False, failonextra=True)`. When `base_name` is
   `None` (component/logger configs), behaviour is unchanged except strictness now applies.
   A missing `config_name` file still raises `FileNotFound`; a missing `base_name` file is
   the same error.
3. **`application_config.py`** — load via
   `load_config(self._env.get_config(), ApplicationConfigData, base_name="python_repo")`,
   then set `name` authoritatively: `self._data = self._data._replace(name=self._env.get_config())`
   (before or after the existing path `_replace`). Add a docstring note that `name` derives
   from the selection, not the file.
4. **`.env.example`** — set `ENV_CONFIG=python_repo`; update the "Default: python_personal"
   comment to `python_repo` and note personal is an opt-in overlay.
5. **Tracked profiles** — verify `python_repo.toml` and `python_local.toml` load cleanly
   under `basiccast=False, failonextra=True` against `ApplicationConfigData`; fix any extra
   keys or wrong-typed scalars in the tracked files (not by loosening the flags).
6. **Tests** — `test_config_loader.py`: add cases for a partial overlay (missing keys fall
   back to base), a typo'd key in the override (rejected by `failonextra`), and a
   wrong-typed value (rejected by `basiccast=False`). `test_application_config.py`: keep the
   `data.name == Envs().get_config()` assertion (now passes on a clean checkout) and add a
   partial-overlay round-trip.
7. **ADR 0006** — flip `status: proposed` → `accepted` once the above is green.

**Interface handed to issue 02 (Makefile owner):** `create-venv` must generate a minimal,
git-ignored `configurations/python_personal.toml` **template** — commented-out example
overrides only (no full copy of `python_repo`), inert until the developer sets
`ENV_CONFIG=python_personal`. Content specified in ADR 0006 / BRAINSTORM decision C. Do **not**
edit the Makefile here.

## Scope

- **OWNS:** `src/constants/env_constants.py`, `src/utils/config_loader.py`,
  `src/utils/application_config.py`, `.env.example`, `configurations/python_repo.toml`,
  `configurations/python_local.toml`, `tests/tests_utils/test_config_loader.py`,
  `tests/tests_utils/test_application_config.py`,
  `docs/adr/0006-config-tracked-base-and-overlays.md`.
- **Does NOT touch:** `Makefile` (create-venv personal-template is issue 02), `pyproject.toml`,
  `CONTEXT.md` (glossary already updated during the grill).

## Acceptance criteria

- [ ] A clean checkout (no `.env`, no `python_personal.toml`) passes the full suite; the
      default profile resolves to the tracked `python_repo`.
- [ ] `load_config(..., base_name="python_repo")` deep-merges a partial overlay; keys omitted
      by the overlay fall back to the base.
- [ ] A misspelled key or a wrong-typed scalar in any profile fails loading loudly
      (`failonextra=True`, `basiccast=False`), with the existing diagnostic-rich exception.
- [ ] `ApplicationConfig().get_data().name == Envs().get_config()` regardless of what the TOML
      `name` field says; a partial overlay need not set `name`.
- [ ] `ADR 0006` is `accepted`.
- [ ] `make all` green.

## Blocked by

- None — Wave 1.
