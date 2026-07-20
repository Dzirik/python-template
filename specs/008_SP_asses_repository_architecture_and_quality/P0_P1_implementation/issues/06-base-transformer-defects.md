# BaseTransformer defect fixes

> **Status:** `ready-for-agent`

## Parent

[`../BRAINSTORM.md`](../BRAINSTORM.md) — P0+P1 implementation. Report item: P1 D2
(BaseTransformer defect fixes). Decision J. Must land before any DS/ML transformer migration
copies the flaws.

## What to build

Fix the defects in the house transformer interface and its flagship example so migrated
transformers copy a correct reference. The interface itself stays (`fit`/`predict`/
`fit_predict`/`inverse` + `get_params`/`restore_from_params`); sklearn-compat is a documented
non-goal.

1. **`datetime_one_hot_transformer.py`**
   - Fix the `TimeAttributes` typo: `min_inerval` → `min_interval`.
   - Move configuration to `__init__`: `__init__(self, time_attributes: TimeAttributes,
     handle_unknown: str = "ignore")`. Store `self._do_attribute = time_attributes`; drop
     `_set_configuration`.
   - Align to the base signature: `fit(self, dt_index: DatetimeIndex) -> None`,
     `predict(self, dt_index)`, `fit_predict(self, dt_index)` — data only, no config params.
     Remove the `# pylint: disable=arguments-differ/renamed/too-many-arguments` pragmas (the
     violation is gone; pylint isn't a gate).
   - Real `inverse`: `return self._encoder.inverse_transform(data)` (the numerical-attribute
     matrix). Document that the original `DatetimeIndex` is not recoverable from the encoded
     attributes, so `inverse` yields the pre-one-hot numerical columns.
   - Populate `self._params` on fit with the state needed to round-trip: the `TimeAttributes`,
     `self._dt_attr_names`, and the encoder's learned `categories_`. Implement
     `restore_from_params` to rebuild a working encoder (reconstruct `OneHotEncoder` from the
     saved categories and mark fitted) so `predict` works after restore without re-fitting.
   - Fix `_convert_datetime_index_to_numberical_attributes` → `..._numerical_attributes`.
2. **`base_transformer.py`** — add to the class docstring that the interface deliberately
   resembles but does not conform to sklearn's estimator contract; sklearn compatibility is a
   **non-goal** (mirrors the CONTEXT.md glossary entry, already added).
3. **Tests** — rewrite `test_datetime_one_hot_transformer.py`'s 62-config sweep to construct the
   encoder with a `TimeAttributes` per config and call `fit(dt_index)` (config no longer passed
   to `fit`). Add a **params round-trip** test: fit encoder A, `params = A.get_params()`, build
   fresh B, `B.restore_from_params(params)`, assert `B.predict(x) == A.predict(x)`. Update the
   `test_datetime_one_hot_transformer.txt` doctest to the new API.

Note: the encoder calls `ExceptionExecutioner` (changed in issue 04). Compatible in either
order — no shared files.

## Scope

- **OWNS:** `src/transformations/datetime_one_hot_transformer.py`,
  `src/transformations/base_transformer.py`,
  `tests/tests_transformations/test_datetime_one_hot_transformer.py`,
  `tests/tests_transformations/test_datetime_one_hot_transformer.txt`.
- **Does NOT touch:** `CONTEXT.md` (transformer glossary entry already added during the grill).

## Acceptance criteria

- [ ] `fit`/`predict`/`fit_predict` take only `dt_index`; configuration is supplied via the
      `TimeAttributes` NamedTuple at construction.
- [ ] `inverse` returns the encoder's `inverse_transform` result (documented as the numerical
      attributes, not the original datetimes).
- [ ] A fit encoder's `get_params()` restores into a fresh instance that predicts identically —
      the in-repo reference for the persistence interface.
- [ ] `min_inerval`/`numberical` typos fixed; the transformer's pylint pragmas removed.
- [ ] `BaseTransformer` docstring states the sklearn non-goal.
- [ ] The 62-config test sweep + doctest pass against the new API; `make all` green.

## Blocked by

- None — Wave 1.
