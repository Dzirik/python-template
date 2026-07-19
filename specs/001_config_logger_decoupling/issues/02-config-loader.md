# Config Loader

> **Status:** `ready-for-agent`

## Parent

[`specs/001_config_logger_decoupling/PRD.md`](../PRD.md) — *Decouple Config Loading from Logging & Anchor All Paths to Project Root*

## What to build

A new shared **Config Loader** (a foundational module under `src/utils/`): one function or small class that, given a config file name and a target `NamedTuple` type, locates the file (via **Project Paths**), parses it with `pyhocon`, and loads it into the target `NamedTuple` with `typedload` — returning the typed, immutable result. This is the single loading mechanism that **Application Config**, **Component Config**, and (for its profile file) the **Logger** will all reuse, so the 4-path / 2-path / 1-path divergence can be retired.

Behavior: **silent on success** (no logging side effect). On failure it raises **diagnostic-rich exceptions** through the existing exception system:

- **Missing file** — names the profile, the folder searched, and the resolved absolute path.
- **Malformed HOCON** — surfaces the parse failure (so the user knows it's a syntax problem).
- **Shape mismatch** — surfaces the `typedload` type failure against the target `NamedTuple` (so the user knows it's a schema problem).

Foundational per ADR 0001: the module **must not import the project `Logger`**. It is parameterized by the target `NamedTuple` type so each config kind gets its own typed result.

## Acceptance criteria

- [ ] `(config_name, target_namedtuple_type)` returns a validated instance of that `NamedTuple` type for a valid profile.
- [ ] A missing file raises a diagnostic exception naming the profile, folder, and resolved absolute path.
- [ ] Malformed HOCON raises a diagnostic exception identifying a parse failure.
- [ ] A shape that doesn't match the target `NamedTuple` raises a diagnostic exception identifying a type/schema failure.
- [ ] The success path produces no logging output.
- [ ] The module imports no project `Logger` (asserted in a test).
- [ ] File location goes through **Project Paths** — no bespoke candidate-path search in the loader.
- [ ] Tests under `tests/tests_utils/` in house style; `make all-secure` green on 3.11 / 3.12 / 3.13.

## Blocked by

- [`01-project-paths-service.md`](./01-project-paths-service.md)
