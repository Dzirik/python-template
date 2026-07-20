# Plotly cleanup + real `dashboard`

> **Status:** `ready-for-agent`

## Parent

[`../BRAINSTORM.md`](../BRAINSTORM.md) — P2. Report item 4 (plotly cleanup) + item 5 (strip
the 50 pylint pragmas in `visualisations/`). Decisions D and E.

## What to build

1. **Make `dashboard` real** (it is currently a silent no-op — both branches of
   `_plot_single_figure` return the same figure). Semantics for the user's future Dash app:
   - `dashboard=True` → return the `go.Figure` (for embedding in a `dcc.Graph`).
   - `dashboard=False` → `fig.show()` then `return None` (standalone rendering).
   Implement this once in `plotly_base._plot_single_figure`; the 10 public plot APIs keep
   threading the flag through. **Ripple:** audit every in-repo caller that relies on the
   returned figure — those must now pass `dashboard=True` (notably issue 08's viz smoke
   tests, and any documentation notebook that captures the return).
2. **Fix the return docstrings** on all plot APIs to state the true contract
   (`dashboard=True` → `go.Figure`; `dashboard=False` → shows and returns `None`).
3. **`get_colors_for_level`** (`visualisation_functions.py`): add the missing
   `"vertical_line"` key so combining a plot with `vertical_lines_positions` no longer
   raises `KeyError`.
4. **`ATTR_HIGH`** (`plotly_time_series_base.py`): `"HIGHT"` → `"HIGH"` (stop forcing a
   misspelled column name on users).
5. **`tuple[float]` → `tuple[float, float]`** wherever a 2-tuple is required.
6. **Hoist the repeated layout block** duplicated across the plot classes into a shared
   helper on `plotly_base` (or `visualisation_functions`).
7. **Strip all 50 `# pylint:` pragmas** in `src/visualisations/` (pylint is not a gate).

## Scope

- **OWNS:** `src/visualisations/*.py` (all modules).
- **Does NOT touch:** `tests/tests_visualisations/*` (new tests are issue 08),
  `CLAUDE.md`/`pyproject.toml` (issue 09).

## Acceptance criteria

- [ ] `dashboard=True` returns a `go.Figure`; `dashboard=False` shows and returns `None`;
      docstrings match.
- [ ] A plot with `vertical_lines_positions` renders without `KeyError`; `"HIGH"` used.
- [ ] No `# pylint:` pragma remains under `src/visualisations/`.
- [ ] `make all` green.

## Blocked by

- None — Wave 1. (Issue 08 depends on this.)
