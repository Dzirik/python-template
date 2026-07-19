---
status: accepted
---

# Application, Component, and Watchdog config profiles are TOML, parsed by stdlib `tomllib`

This decision records the outcome of the config-migration effort scoped in
[`specs/003_conf_files_form_resolution/PRD.md`](../../specs/003_conf_files_form_resolution/PRD.md),
which itself builds on the naming refactor of
[spec 002](../../specs/002_config_naming_refactoring/PRD.md) and relates to
[ADR 0001](0001-foundational-config-layering.md): both concern the same Config
Loader, and this decision leaves ADR 0001's "config loading stays Logger-free"
guarantee untouched.

The application profiles (`python_repo`, `python_personal`, `python_local`), the
watchdog profiles (`watchdog_cmd_01`, `watchdog_cmd_02`), and any future
`BaseComponentConfig` profile were HOCON, parsed by the third-party `pyhocon`
library, and carried the generic `.conf` extension — an extension `.conf` also
shared with the unrelated stdlib-INI Logger profiles and the JSON runtime
snapshots, so it described nothing about a given file's actual syntax. A scan of
every tracked profile found zero use of HOCON-specific features — no `${...}`
substitutions, no `include`, no duration/size units — so the files were
effectively JSON-with-unquoted-keys plus `#` comments, and `pyhocon` (plus its
`pyparsing` transitive dependency) was a niche addition to the `pip-audit` /
`bandit` supply-chain surface for capabilities never exercised. We decided to
express these profiles in **TOML** and parse them with the **standard-library
`tomllib`**, dropping `pyhocon` without adding a replacement dependency. This is
safe because the typed-`NamedTuple` guarantee callers rely on
(`ApplicationConfigData`, the watchdog config tree) comes from `typedload`, not
from the file format: the loader parses a profile into a plain mapping and hands
that mapping to `typedload.load(...)`, and `tomllib.load()` produces exactly the
kind of plain `dict` `typedload` already consumes. The migration is therefore a
single parse-point change in the Config Loader, not a rewrite of the typed
layer. The one structural consequence is that the path helper
(`config_file` in `src/utils/project_paths.py`), previously hard-coding `.conf`
for every caller, gained an explicit extension parameter so profile callers
resolve `.toml` while the Logger's `.conf` resolution is untouched — the two
families were always different formats wearing the same extension, and the
extension parameter makes that difference explicit instead of implicit.

## Considered options

- **Keep HOCON (status quo)** — rejected: carries `pyhocon` (and its
  `pyparsing` transitive dependency) purely for composition features — substitutions,
  `include`, env-var fallbacks — that no profile in this repo uses, and gives no
  IDE (PyCharm) recognition out of the box.
- **TOML, parsed by stdlib `tomllib` (chosen)** — removes `pyhocon` while adding
  **no** replacement runtime dependency (`tomllib` ships with every
  `requires-python` interpreter this project supports), keeps `#` comments, and is
  auto-recognised by PyCharm for highlighting, structure view, and formatting.
- **YAML** — rejected: has no stdlib parser, so adopting it means trading
  `pyhocon` for `PyYAML` (or similar) — a lateral dependency swap that contradicts
  the actual goal of dropping a third-party config parser, and it inherits YAML's
  well-known footguns (implicit typing, whitespace sensitivity).
- **JSON** — rejected: has a stdlib parser (`json`) but no comment syntax, and
  several profiles carry human-facing guidance comments (e.g. `python_local`'s
  "customize this path for your local data directory") that would be lost.

A related, narrower question was whether the new format should keep the existing
`.conf` extension rather than switch to `.toml`, on the theory that a
generic extension protects against future config-type collisions. That argument
was weighed and dismissed: it defends against a cost that was never real —
nothing about a distinct extension causes a collision, since the resolution path
already keys off name and subfolder, not extension. The actual cost the generic
extension imposes is a loss of self-description: a `.conf` file's contents could
be HOCON, INI, or JSON depending only on which folder it lives in, and neither a
reader nor an IDE can tell without opening it. A standard, format-specific
extension (`.toml`) fixes exactly that cost, so the collision-avoidance argument
was not enough to keep it.

## Consequences

`.conf` stops being overloaded: once the profiles carry `.toml`, `.conf` means
exactly one thing again — the Logger's stdlib-INI profiles, which are out of
scope here because `logging.config.fileConfig` dictates their format. If the
template later adopts genuine config composition — layered overrides,
`include`-d fragments, or `${?ENV_VAR}` inline fallbacks — the features that made
HOCON's dependency cost hard to justify today would start earning their keep,
and this decision should be revisited; no such need exists yet, so this is
recorded but not acted on.
