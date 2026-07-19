# Rebuild the `pip-audit` ignore list against the post-lock advisory state

> **Status:** `ready-for-agent` · **HITL** (the maintainer signs off which residual suppressions are accepted)

## Parent

[`specs/007_update_and_optimize_python_version_and_libraries/PRD.md`](../PRD.md) — *Update & optimize Python version and libraries*

## What to build

After the single re-lock, the seven hand-maintained `--ignore-vuln` entries in the
`security-check` recipe reflect the *old* dependency versions and are likely stale. This
slice re-runs the security gate against the freshly-locked set and rebuilds the suppression
list so it describes the actual post-update advisory state, with every kept entry justified.
Because keeping a suppression means *accepting a security risk*, the final list is surfaced
to the maintainer for sign-off — this is the human-in-the-loop step.

End-to-end behaviour after this slice: `make security-check` passes on the re-locked
environment, and the `--ignore-vuln` list contains only genuinely-unfixable advisories, each
carrying a one-line reason comment explaining why it is accepted.

Scope:

- **Re-run `make security-check`** (bandit + pip-audit) against the regenerated `uv.lock`.
- **Classify each existing ignore** (`PYSEC-2023-157`, `PYSEC-2023-155`, `PYSEC-2023-272`,
  `PYSEC-2024-165`, `PYSEC-2023-23`, `PYSEC-2023-24`, `GHSA-pjjw-68hj-v9mw`) and any newly
  surfaced advisory under the three-case policy:
  1. **No longer fires** (latest moved past the vulnerable version) → remove the ignore.
  2. **Still fires, a fixed release exists** → remove the ignore and take the fix (the
     "latest everywhere" bump *is* the fix — upgrade, don't suppress).
  3. **Still fires, no upstream fix even at latest** → keep the ignore as an accepted risk.
- **Annotate every kept `--ignore-vuln`** in the `Makefile` recipe with a one-line reason
  (affected package, why it is unfixable/accepted, advisory date/link), per `CLAUDE.md`'s
  "suppress a specific rule … with a reason" rule.
- **Surface the final proposed list to the maintainer for sign-off** before it is considered
  done; do not silently decide what counts as an acceptable residual risk.

## Acceptance criteria

- [ ] `make security-check` has been re-run against the regenerated `uv.lock` and passes.
- [ ] Every retained `--ignore-vuln` entry still fires and has no available upstream fix; entries that no longer fire, or that a newer release fixes, are removed.
- [ ] Each retained `--ignore-vuln` carries a one-line reason comment (package, rationale, advisory reference) in the `Makefile` recipe.
- [ ] The final ignore list was surfaced to and approved by the maintainer.
- [ ] `make all-secure` green in CI on **both Python 3.13 and 3.14**.

## Blocked by

- [`01-python-modernization-and-relock.md`](./01-python-modernization-and-relock.md)
