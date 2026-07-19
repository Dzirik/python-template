# Move transformer method ids → `src/transformations/transformer_methods.py`

> **Status:** `ready-for-agent`

## Parent

[`specs/006_resolve_global_and_venv_constants/BRAINSTORM.md`](../BRAINSTORM.md) — *Resolve global & venv constants*

## What to build

Give the transformer method-identifier vocabulary (`F`, `FP`, `P`, `INV`) a proper production home, co-located with the transformer domain instead of the catch-all `global_constants.py`. These four constants are the canonical method-id vocabulary for the transformer suite. Within *this* repo only `FP` and `P` are exercised (as test discriminators in `test_datetime_one_hot_transformer.py`), but all four are retained deliberately: a larger transformer suite not yet migrated into this repo uses all four heavily and needs one canonical import path. `F` and `INV` are **reserved, not dead** — do not prune them.

End-to-end behaviour after this slice: `test_datetime_one_hot_transformer.py` imports `FP`, `P` from `src.transformations.transformer_methods`; the parametrized cases behave identically; the new module also exposes `F` and `INV` for the incoming suite.

Scope:

- **New `src/transformations/transformer_methods.py`** — defines `F = "f"`, `FP = "fp"`, `P = "p"`, `INV = "i"` (values unchanged). Module docstring states this is the canonical method-identifier vocabulary for the transformer suite, and that `F`/`INV` are reserved for the not-yet-migrated suite (so they are not flagged as dead and pruned).
- **`test_datetime_one_hot_transformer.py`** — update the import of `FP`, `P` to `from src.transformations.transformer_methods import FP, P`.
- **`global_constants.py`** — remove the `F`/`FP`/`P`/`INV` lines.

## Acceptance criteria

- [ ] `src/transformations/transformer_methods.py` exists, defines all four ids with unchanged values, and documents `F`/`INV` as reserved for the incoming suite.
- [ ] `test_datetime_one_hot_transformer.py` imports `FP`, `P` from the new module; the parametrization is unchanged in behaviour.
- [ ] `global_constants.py` no longer defines `F`/`FP`/`P`/`INV`.
- [ ] No import of these ids from `global_constants` remains anywhere.
- [ ] `make all-secure` green on Python 3.11 / 3.12 / 3.13.

## Blocked by

- None - can start immediately.
