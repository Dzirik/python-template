# Record ADR 0003 — the TOML-over-HOCON decision

> **Status:** `ready-for-agent`

## Parent

[`specs/003_conf_files_form_resolution/PRD.md`](../PRD.md) — *Migrate the HOCON config family to TOML*

## What to build

A new architecture decision record (`docs/adr/0003-*`) capturing *why* the config family moved from HOCON to TOML, so a future contributor understands the trade-off without re-deriving it. Follow the house style of the existing ADRs (`0001-foundational-config-layering.md`, `0002-repo-root-path-anchoring.md`).

The record must include:

- The decision: app/component/watchdog profiles in TOML, parsed by stdlib `tomllib`.
- The four-way comparison of the options considered: keep HOCON / TOML / YAML / JSON — with why each was accepted or rejected (YAML adds a dependency, contradicting the drop-`pyhocon` goal; JSON loses comments; keeping HOCON carries a niche dependency for features never used).
- The `typedload`-orthogonality insight: the typed-`NamedTuple` guarantee comes from `typedload`, not the file format, which is what makes the swap a single parse-point change.
- The shared-extension wrinkle: the path helper became per-family (extension parameter) so the logger `.conf` path is unaffected.
- The "custom extension won't collide with future types" argument weighed and dismissed (it defends a non-cost; the real cost is self-description, which a standard extension fixes).
- The recorded-but-not-triggered reversal condition: if the template later adopts config composition (layered overrides, `include`d fragments, `${?ENV_VAR}` fallbacks), HOCON's unused features would earn their keep.

## Acceptance criteria

- [ ] `docs/adr/0003-*.md` exists, following the format/structure of ADRs 0001 and 0002.
- [ ] It states the decision, the four-way comparison with rationale, the `typedload`-orthogonality insight, the shared-extension wrinkle, the dismissed custom-extension argument, and the reversal condition.
- [ ] It is cross-referenced consistently with the PRD's `relates-to` / `builds-on` framing (ADR 0001).
- [ ] `make all-secure` stays green (docs-only change).

## Blocked by

- None - can start immediately.
