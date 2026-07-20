# Context

Glossary of the ubiquitous language for this project. Definitions only — no
implementation details. When a term here conflicts with how code or conversation
uses a word, the conflict gets resolved here first.

## Terms

### Application Config
The single, process-wide configuration for one execution of a project. There is
exactly one. Which underlying config profile it reads is chosen ambiently via
the environment (see **Env Selector**), not passed in by a caller. Implemented
today as the `ApplicationConfig` singleton. Contrast with **Component Config**.

### Component Config
A configuration object for one specific component or pipeline (e.g. the watchdog,
a data pipeline). Many can exist at once, each created explicitly with its own
config profile name and its own data shape. Implemented today via the
`BaseComponentConfig` base class. Its config profiles live in a per-kind subfolder
of the central configurations folder (e.g. `configurations/watchdogs/`), not
co-located with the owning module. Contrast with **Application Config**.

### Config Loader
The shared mechanism that turns a config profile into a typed, immutable settings
object: locate the file, parse it, and load it into a NamedTuple. One
implementation, reused by both **Application Config** and **Component Config**.
Foundational: it must not depend on the **Logger**.

### Env Selector
The single place that reads and writes **application** environment variables —
including but not limited to those governing which config and logger profiles are
active (e.g. which profile name to load), and any other app-level setting sourced
from the environment (e.g. healthcheck ping URLs). Implemented today as `Envs`,
which exposes one explicit accessor per variable. All *application* environment
access goes through it; **operating-system builtins** (e.g. `SYSTEMROOT`) are not
application config and may be read directly at their point of use.

### Logger
The process-wide logging facility, selected by its own profile. A higher-level
concern than config: it may depend on config, but nothing in the **Config
Loader** may depend on it.

### Project Paths (Project Root)
The single foundational service that computes the project root **once** (by
walking up from the source file to a marker such as `pyproject.toml`/`.git`) and
exposes the canonical input/output locations (`data`, `logs`, `reports`,
`configurations`). All path resolution goes through it; nothing resolves paths
against the current working directory. An environment override (via **Env
Selector**) can repoint the base directory for deployments outside the repo tree.
Foundational: it must not depend on the **Logger**.

### Transformer
A data-transformation object exposing the house `fit` / `predict` / `fit_predict` /
`inverse` interface, plus `get_params` / `restore_from_params` for persistence.
Transformers manipulate data; they are **not** machine-learning models, and
**sklearn compatibility is a deliberate non-goal** — the interface deliberately
resembles sklearn's without conforming to its estimator contract. All configuration
is supplied at construction so `fit` takes only the data. Input-shape validation is
the concrete transformer's responsibility, not the base's.

### Config Profile / Logger Profile
A named file selecting a set of settings. Config profiles: `python_repo`,
`python_personal`, `python_local`. Logger profiles: the `logger_*` files (`.toml`).

Among the config profiles, `python_repo` is the **canonical base**: it is tracked
in git, is the default when no profile is selected, and always loads first.
`python_personal` and `python_local` are **optional partial overlays** layered over
that base — the keys they set win, and any key they omit falls back to the base.
`python_personal` is git-ignored (per-developer); selecting it is opt-in. A profile
is chosen explicitly via the **Env Selector**; selecting one whose file is absent is
an error, but a present-but-partial overlay is not.
