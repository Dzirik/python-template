# Data-layer hardening: attributes.py + SaverAndLoader

> **Status:** `ready-for-agent`

## Parent

[`../BRAINSTORM.md`](../BRAINSTORM.md) — P2. Report items 8 (`attributes.py`) and 12
(`SaverAndLoader`). Decisions H and L. Two disjoint files in `src/data/`, grouped as
data-layer correctness.

## What to build

### `src/data/attributes.py`

Keep the module and its role (it exports `A` / `DICT_ATTRS_GROUPS`, consumed by the
documentation notebooks). Fix the defects; **keep the `.csv`/`.xlsm` in `src/data/`**.

1. **Path-anchor the load**: replace the CWD-relative `FILE_NAME_BASE = "../../src/data/attributes"`
   with a `Path(__file__).parent`-anchored path. Remove the Windows-only `os.chdir`/`getcwd`
   "because of the test" hack.
2. **Raise the constructed-but-unraised exception** at `attributes.py:82`
   (`NoProperOptionInIf(...)` → `raise NoProperOptionInIf(...)`).
3. `A` / `DICT_ATTRS_GROUPS` stay module-level constants (now deterministic because the path
   is anchored, not CWD-dependent).
4. **Add tests** (`tests/tests_data/test_attributes.py`): load both `file_type="csv"` and
   `"xlsm"` from an arbitrary CWD (subprocess or `monkeypatch.chdir`) and assert the parsed
   `AttributeNamedTuple` shapes; assert the invalid-type path now raises.

### `src/data/saver_and_loader.py`

5. **Fail fast on undersized files**: where the loader currently returns empty data when a
   file exists but is under `min_size`, **raise a `CustomException`** (data/development
   exception with the path + actual vs required size) instead. Silent-empty masks
   truncated/corrupt files.
6. **Add/extend tests** (`tests/tests_data/test_saver_and_loader.py`): write an undersized
   file, assert the raise; write an adequately-sized file, assert normal load.

## Scope

- **OWNS:** `src/data/attributes.py`, `src/data/saver_and_loader.py`,
  `tests/tests_data/test_attributes.py`, `tests/tests_data/test_saver_and_loader.py`.
- **Does NOT touch:** the `.csv`/`.xlsm` location (stays in `src/data/`); notebook consumers
  (the exported symbols and their meaning are unchanged).

## Acceptance criteria

- [ ] `attributes.py` loads correctly from any CWD; the invalid-type branch raises.
- [ ] `SaverAndLoader` raises on undersized files (no silent empty return).
- [ ] New data-layer tests pass; `make all` green.

## Blocked by

- None — Wave 1.
