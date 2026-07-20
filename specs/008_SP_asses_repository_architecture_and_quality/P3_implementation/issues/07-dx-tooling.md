# DX / tooling: `.gitignore`, `.PHONY`, hooks, pip-audit

## Parent

[`../PRD.md`](../PRD.md) — P3 implementation (polish), Items 2 and 6 (merged: both edit the
`Makefile`). Covers user stories 18, 19, 20, 21.

## What to build

A developer-experience cleanup across the ignore file, the Make target declarations, the git
hook installation mechanism, and the security audit.

- **`.gitignore` cleanup.** Remove the author-personal entries (`ws.sh`, `a.sh`) and the phantom
  `archive_gen_01_ma` paths. Leave the already-correct marimo `app` and attributes entries
  untouched.
- **`.PHONY` completeness.** Audit the `.PHONY` declaration against the actual target list and
  add any missing phony targets. This is a completeness pass, not a rewrite.
- **Hooks via `core.hooksPath`.** Move the tracked `pre-commit`/`pre-push` scripts into a
  dedicated hooks directory and point `git config core.hooksPath` at it, so edits to the tracked
  hooks take effect immediately with no copy/re-install step. `install-hooks.ps1` and
  `install-hooks.sh` collapse to setting the config value; the `Makefile`'s OS-detecting
  `install-hooks` entry stays. Preserve the current onboarding messaging (the blocked-commit
  output that teaches the feature-branch workflow).
- **pip-audit against the lock.** Change the audit to run against the exported lock
  (`uv export ... | pip-audit -r -` or equivalent) so the audited closure matches the committed
  `uv.lock`, aligning local and future-CI audits. Wired through `make security-check`.

Scope boundary: owns `.gitignore`, `Makefile`, `scripts/install-hooks.*`, and the
`scripts/pre-commit`/`pre-push` hook scripts. No other P3 slice edits the `Makefile`.

## Acceptance criteria

- [ ] `.gitignore` no longer contains `ws.sh`, `a.sh`, or `archive_gen_01_ma`; the marimo `app` and attributes entries are unchanged.
- [ ] `.PHONY` lists every phony target in the `Makefile`.
- [ ] `make install-hooks` sets `core.hooksPath` (OS-detecting) instead of copying; editing a tracked hook takes effect with no re-install; the blocked-commit onboarding message is preserved; the pre-commit branch-block and pre-push security behaviors still work.
- [ ] `make security-check` runs `pip-audit` against the exported `uv.lock` closure.
- [ ] `make all-secure` is green.

## Blocked by

None - can start immediately.
