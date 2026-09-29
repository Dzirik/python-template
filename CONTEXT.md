# Context

Glossary of the ubiquitous language for this project. Definitions only — no
implementation details. When a term here conflicts with how code or conversation
uses a word, the conflict gets resolved here first.

## Terms

### Agent Harness
The local program that wraps the model and drives a coding session — Claude Code,
in this repository's case. It is the party that actually builds and sends each
request to the model provider: system prompt, tool schemas, injected context, and
the message the developer typed. Distinct from a *test harness* (pytest
scaffolding), which is always written hyphenated and qualified and is never called
"the harness" here.

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

### Harness Capture
A recorded copy of one complete exchange between the **Agent Harness** and the
model provider — the full request and the full response, taken at the boundary as
it passes. It captures everything crossing that boundary, including the
developer's own message and the model's reply; it is not limited to the harness's
own contribution. It has two layers: the **raw record**, which is authoritative and
lossless, and the **render**, a human-readable view derived from the raw record that
can always be regenerated from it. When the two disagree, the raw record is right.
Not a **Logger** concern: it writes captures, not application
logs, and has nothing to do with logger profiles. Known externally, and in the
course this idea came from, as a "request logger".

### Harness Session
One continuous conversation of the **Agent Harness**, as the harness itself
identifies it. Starting fresh (e.g. `/clear`) begins a new Harness Session;
continuing a previous conversation resumes that one, and compacting does not end it.
A subagent's traffic, and the harness's own auxiliary calls (safety classification,
title and prompt suggestions), belong to the Harness Session they serve. The working
directory is a descriptive label of a session, never its identity — two sessions in
the same directory are two sessions. The **Harness Captures** of one session are
ordered by arrival; that order, not wall-clock time, is the session's timeline.

### Logger
The process-wide logging facility, selected by its own profile. A higher-level
concern than config: it may depend on config, but nothing in the **Config
Loader** may depend on it.

### Project Paths (Project Root)
The single foundational service that computes the project root **once** (by
walking up from the source file to a marker such as `pyproject.toml`/`.git`) and
exposes the canonical input/output locations (`data`, `logs`, `reports`,
`configurations`, `captures`). All path resolution goes through it; nothing
resolves paths against the current working directory. An environment override (via **Env
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
