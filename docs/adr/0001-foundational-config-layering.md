---
status: accepted
---

# Config loading must not depend on the Logger

The config-loading layer (the shared **Config Loader**, `BaseComponentConfig`,
and the main `ApplicationConfig`) previously logged through the project `Logger`
singleton, which pointed the dependency the wrong way — config is foundational,
logging is a higher-level concern that may itself need config — and forced the
main `Config` to be a hand-maintained fork of `BaseConfig` to dodge the
resulting cycle. We decided that foundational components (Config Loader,
Project Paths) must **never** import the project `Logger`: config parsing is
silent on success and reports failures via diagnostic-rich exceptions, which is
what actually helps debug `.conf` problems. Any breadcrumb a foundational
component genuinely needs uses stdlib `logging.getLogger(__name__)`, never the
singleton.

## Considered options

- **Inject a logger into the loader** — rejected: adds ceremony and the loader
  still conceptually depends on a logging abstraction it shouldn't need.
- **Lazy/indirect `Logger` reference to break the import cycle** — rejected:
  hides the coupling instead of removing it.
- **Remove logging from config loading entirely (chosen)** — the success-path
  breadcrumb was low value; the failure path is better served by exceptions.

## Consequences

With `Logger` gone from the shared loader, the circular-dependency reason for
forking `ApplicationConfig` disappears, so `ApplicationConfig` and `BaseComponentConfig` can share one loader
while remaining separate classes (their lifecycles differ: singleton vs.
multi-instance).
