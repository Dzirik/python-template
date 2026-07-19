# Move `COLORS` → `src/visualisations/colors.py`

> **Status:** `ready-for-agent`

## Parent

[`specs/006_resolve_global_and_venv_constants/BRAINSTORM.md`](../BRAINSTORM.md) — *Resolve global & venv constants*

## What to build

Co-locate the visualisation palette with the domain that owns it. The `COLORS` dict is consumed only by `plotly_base.py`, yet lives in the catch-all `global_constants.py`. This slice moves it to a new `src/visualisations/colors.py` and repoints its single consumer.

End-to-end behaviour after this slice: `plotly_base.py` imports `COLORS` from `src.visualisations.colors`; the palette values are byte-for-byte unchanged; plots render identically.

Scope:

- **New `src/visualisations/colors.py`** — holds the `COLORS` dict verbatim (including the existing inline colour-name comments), with a house-style module docstring describing it as the visualisation palette.
- **`plotly_base.py`** — update the import to `from src.visualisations.colors import COLORS`; update the docstring reference (around line 48) that currently points at `src/constants/global_constants.py` to point at `src/visualisations/colors.py`.
- **`global_constants.py`** — remove the `COLORS` dict.

## Acceptance criteria

- [ ] `src/visualisations/colors.py` exists and contains the `COLORS` dict with unchanged values.
- [ ] `plotly_base.py` imports `COLORS` from `src.visualisations.colors` and its docstring reference points at the new module.
- [ ] `global_constants.py` no longer defines `COLORS`.
- [ ] No `COLORS` import from `global_constants` remains anywhere.
- [ ] `make all-secure` green on Python 3.11 / 3.12 / 3.13.

## Blocked by

- None - can start immediately.
