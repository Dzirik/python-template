# Route `HEALTHCHECK_PING_URL` through `Envs`

> **Status:** `ready-for-agent`

## Parent

[`specs/006_resolve_global_and_venv_constants/BRAINSTORM.md`](../BRAINSTORM.md) — *Resolve global & venv constants*

## What to build

Thread C's "`Envs` is the single place env vars are read" fix. Today `watchdog.py` reads `os.getenv("HEALTHCHECK_PING_URL")` directly, bypassing the **Env Selector**. This slice routes that access through `Envs` so all *application* environment access goes through one place, while leaving the JSON parsing (domain logic) in the watchdog.

End-to-end behaviour after this slice: `watchdog.resolve_ping_url` obtains the raw healthcheck configuration string via `Envs.get_healthcheck_ping_url()` instead of `os.getenv`; the JSON decode, list validation, and key lookup stay exactly where they are. No behaviour change — the same raw string flows through the same parsing.

Scope:

- **`env_constants.py`** — add `ENV_HEALTHCHECK_PING_URL = "HEALTHCHECK_PING_URL"` with an inline comment noting the symbol is `ENV_`-prefixed by convention but the **live env var deliberately has no `ENV_` prefix** (name ≠ value), so nobody "fixes" it by renaming the variable.
- **`Envs`** — add `get_healthcheck_ping_url() -> str | None` returning the **raw** env value (or `None` when unset — no `DEFAULT_*`, mirroring `get_project_root_override`). Follow the one-static-method-per-var house style.
- **`watchdog.py`** — replace `os.getenv("HEALTHCHECK_PING_URL")` in `resolve_ping_url` with `Envs.get_healthcheck_ping_url()`. Keep `json.loads`, the list/`isinstance` validation, and the warning messages as-is.
- **`checker.py`** — `SYSTEMROOT` stays a direct `os.environ` read (OS builtin, not application config); add a one-line clarifying comment stating that and that it is intentionally not routed through `Envs`.
- **Do not rename** the `HEALTHCHECK_PING_URL` env var, its `.env.example` entry, or the watchdog warning strings.

## Acceptance criteria

- [ ] `ENV_HEALTHCHECK_PING_URL = "HEALTHCHECK_PING_URL"` exists in `env_constants.py` with the name≠value clarifying comment.
- [ ] `Envs.get_healthcheck_ping_url()` returns the raw string when set and `None` when unset; no default is applied.
- [ ] `watchdog.resolve_ping_url` no longer calls `os.getenv`; it uses `Envs.get_healthcheck_ping_url()`. JSON parsing and validation are unchanged.
- [ ] `checker.py`'s `SYSTEMROOT` read is unchanged in behaviour and carries a one-line comment explaining why it stays a direct OS read.
- [ ] The `HEALTHCHECK_PING_URL` env var name is unchanged everywhere (env, `.env.example`, warning strings).
- [ ] `make all-secure` green on Python 3.11 / 3.12 / 3.13.

## Blocked by

- [`01-env-constants-single-source-of-truth.md`](./01-env-constants-single-source-of-truth.md) — needs `env_constants.py` to exist.
