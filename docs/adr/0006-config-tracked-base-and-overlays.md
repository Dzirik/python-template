---
status: accepted
---

# Config profiles are a tracked base plus optional partial overlays, loaded strictly

This decision records the configuration-model outcome of
[`specs/SP_008_asses_repository_architecture_and_quality/implementation/BRAINSTORM.md`](../../specs/SP_008_asses_repository_architecture_and_quality/implementation/BRAINSTORM.md)
(issue 01) and continues the config-layer chain begun in ADR 0001–0003. It relates to
[`docs/PROJECT_VISION.md`](../PROJECT_VISION.md)'s single success measure — *clone the
template and immediately start real work* — because the model it replaces makes a fresh
clone fail its own test suite.

Until now there was exactly one config profile loaded per run:
`ApplicationConfig` called `load_config(Envs().get_config(), ...)` against a single
`.toml` file, and the default profile was `python_personal` — a **git-ignored** file
generated only by `make create-venv`. A clean checkout (and CI, which never runs
`create-venv`) therefore has no `python_personal.toml`, so the default resolves to a
missing file and three tests in `test_application_config.py` fail before any user change.

We decided that **`python_repo` is the canonical base**: tracked in git, the default when
no profile is selected, and always loaded first. `python_personal` and `python_local`
become **optional partial overlays** deep-merged over that base — the keys they set win,
any key they omit falls back to the base. The base+overlay merge lives in the shared
`load_config` via an optional `base_name` parameter, so it stays the one loading
mechanism (Config Loader per ADR 0001) that Application Config, Component Config, and the
Logger all share; component and logger configs simply pass no `base_name`. The merged
dict is loaded with **one strict `typedload.load(..., basiccast=False, failonextra=True)`**,
which catches a wrong-typed value or a typo'd key in *either* file (a typo becomes an
extra key in the merged dict). The profile's `name` is set **authoritatively from the
selection** (`Envs().get_config()`) after the merge rather than read from the file, so a
partial overlay never needs to restate `name` and a mislabelled file cannot misreport its
identity. Selecting a profile whose file is absent is a loud error; a present-but-partial
overlay is not.

## Considered options

- **Keep the single-profile model, just flip the default to `python_repo` (status quo+)**
  — rejected as insufficient: it fixes the clean-checkout failure but leaves the "add one
  config key and every teammate's git-ignored personal profile silently breaks" trap
  (§3.1) and gives personal profiles no fallback story.
- **Rewrite on `pydantic-settings`** — rejected (§3.1): the typed NamedTuple tree already
  gives mypy-strict, immutable, dependency-light access; the real pain points (default
  profile, strictness, overlay) are all fixable in place without taking a new dependency.
- **Automatic overlay: always layer `python_personal.toml` if it exists, regardless of
  selection** — rejected: conflicts with the existing `ENV_CONFIG` selection mechanism and
  with `python_local`, and makes "which profile am I running" ambient and surprising.
- **Personal-only overlay, special-cased inside `ApplicationConfig`** — rejected: it
  duplicates the loader's `typedload` step (weakening "one loading mechanism"), adds a
  special case for one profile name, and does not generalise to `python_local`.
- **Generalised base+overlay in `load_config`, strict-loaded, name-from-selection
  (chosen)** — one mechanism, any non-base profile may be partial, strictness rides on the
  merged dict, and the tracked base means a clean clone and CI pass with no generation
  step.

## Consequences

A fresh clone and CI now pass without running `make create-venv`, because the default
profile (`python_repo`) is tracked. `.env.example` selects `python_repo`; a developer opts
into a personal profile by setting `ENV_CONFIG=python_personal` and editing the minimal
overlay template that `create-venv` generates (which may set only the keys it overrides).

Strict loading (`basiccast=False`, `failonextra=True`) is a behavioural tightening: a
config file with a misspelled key or a value of the wrong scalar type now fails loudly at
load instead of being silently ignored or coerced. The tracked profiles must be clean
against the `ApplicationConfigData` shape for the suite to pass — verified as part of
issue 01.

`name` is derived from the selection, not the file, so the `name` field in every `.toml`
becomes advisory. A future reader who edits `name` in a profile file and expects it to
change the reported identity will be surprised — that is recorded here deliberately: the
selection is the source of truth for identity.

This decision should be revisited if a profile ever needs *nested-list* override
semantics (deep-merge here replaces lists wholesale, merges only nested tables) or if a
component/logger config later needs its own overlay — at which point the `base_name`
parameter already provides the seam.
