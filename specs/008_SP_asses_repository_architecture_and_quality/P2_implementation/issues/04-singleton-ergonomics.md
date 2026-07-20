# Singleton ergonomics: reset seam + loud error

> **Status:** `ready-for-agent`

## Parent

[`../BRAINSTORM.md`](../BRAINSTORM.md) — P2. Report item 11. Decision K (**both**
mechanisms).

## What to build

1. **Test-only reset seam** on the `Singleton` metaclass (`src/utils/singleton_meta.py`):
   a classmethod-style helper `Singleton.reset()` (clears `Singleton._instances`) so tests
   can reset config/logger Singletons between cases instead of paying the subprocess-isolation
   tax. Document it as test-only in the docstring.
2. **Loud error on late `set_config`** (`src/utils/envs.py`): make `Envs.set_config` raise a
   `CustomException` (development exception) when the config Singleton has **already been
   instantiated** — currently the write is silently ignored (the ordering trap). Detect
   instantiation via `Singleton._instances` keyed by the `ApplicationConfig` class; **import
   `ApplicationConfig` lazily inside the method** to avoid the `ApplicationConfig → Envs`
   import cycle. (Scope the guard to `set_config`; a parallel guard on `set_logger` is
   optional and may be added if trivial.)
   - The two compose: `Singleton.reset()` clears the instance, re-opening the legitimate
     "before instantiation" window so a reset-then-`set_config` sequence works.
3. **Prove the seam** with tests (`tests/tests_utils/test_singleton_meta.py`, extend
   `test_envs.py` if present): reset then re-instantiate yields a fresh instance; calling
   `set_config` after instantiation (without reset) raises.
4. **Optional cleanup:** if the reset seam lets an existing subprocess-based Singleton test
   become a plain in-process test, migrate it — but do not destabilize the suite; leaving the
   subprocess tests as-is is acceptable (the seam is additive).

## Scope

- **OWNS:** `src/utils/singleton_meta.py`, `src/utils/envs.py`,
  `tests/tests_utils/test_singleton_meta.py`, `tests/tests_utils/test_envs.py`.
- **Interface (frozen for other issues):** `Singleton.reset()` — available to any test.

## Acceptance criteria

- [ ] `Singleton.reset()` clears instances; a reset-then-instantiate produces a new object.
- [ ] `Envs.set_config` after `ApplicationConfig` instantiation raises loudly (no silent
      no-op); no import cycle introduced.
- [ ] New/updated tests pass; `make all` green.

## Blocked by

- None — Wave 1.
