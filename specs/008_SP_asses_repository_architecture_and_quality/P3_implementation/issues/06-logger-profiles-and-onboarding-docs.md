# Logger profiles + onboarding docs refresh

## Parent

[`../PRD.md`](../PRD.md) — P3 implementation (polish), Item 7 (profiles/docs half). Covers user
stories 22, 23.

## What to build

Make the logger profiles' root-level policy intentional and refresh the stale onboarding
checklist.

- **Logger-profile root levels.** Compare the root `level` across the five
  `configurations/loggers/logger_*.toml` profiles. Either align them to a single deliberate
  policy, or, where a difference is intentional (e.g. a DEBUG file profile vs an INFO console
  profile), document the rationale in the profile's leading comments so the divergence reads as
  a decision, not an accident. Record which choice was made in this issue's resolution.
- **`TESTING_CHECKLIST.md` refresh.** Update it to current reality — drop retired concepts
  ("Python 3.11+", "Minimal Template") — or, if it is no longer worth maintaining, mark it
  clearly as a historical document. Update the README pointer that routes new users to it
  accordingly.

Scope boundary: owns the logger `.toml` profiles, `TESTING_CHECKLIST.md`, and the single README
pointer line to it. Does not touch `logger.py`, test files, or the `Makefile`.

## Acceptance criteria

- [ ] Every logger profile's root level is either consistent with the others or carries a comment explaining the intentional divergence; the chosen approach is recorded in this issue.
- [ ] `TESTING_CHECKLIST.md` no longer references "Python 3.11+" or "Minimal Template" (either refreshed to current reality or plainly marked historical).
- [ ] The README pointer to `TESTING_CHECKLIST.md` reflects the document's new state.
- [ ] `make all-secure` is green.

## Blocked by

None - can start immediately.

## Resolution

- **Logger-profile root levels.** The five profiles were not uniformly `DEBUG` as assumed: the two
  byte-capped `RotatingFileHandler` profiles (`logger_file_limit.toml`,
  `logger_file_limit_console.toml`) were already at root `level = "INFO"`, while the three
  unconstrained profiles (`logger_console.toml`, `logger_file.toml`, `logger_file_console.toml`)
  were at `DEBUG`. This divergence is sensible (DEBUG noise would burn through a 5MB/2-backup
  rotating budget quickly and evict older, higher-signal entries), so it was kept as-is rather than
  forced to a single level — each of the five files now carries a leading comment next to `[root]`
  explaining the DEBUG-vs-INFO policy and cross-referencing the other group, so the split reads as
  a decision, not an accident. `logger_console.toml` stays at root `DEBUG` (required by the
  Wave-1 test-suite-quality agent's `capsys`/`caplog` assertions) and was otherwise untouched
  functionally — only the explanatory comment was added.
- **`TESTING_CHECKLIST.md`.** The file no longer exists in the repository: it lived at
  `docs/meta/TESTING_CHECKLIST.md`, was marked historical during the P0/P1 docs-truth sweep
  (issue 08), and was subsequently deleted outright by an untracked commit ("Delete obsolete
  file") before this P3 wave started. Since removal is the strongest form of "no longer worth
  maintaining," it was left deleted rather than recreating ~1,900 lines of retired content; the
  work here was to finish making the README consistent with that reality instead of refreshing
  content that no longer exists. Both README mentions (the `docs/` file-tree entry and the
  dedicated "Testing Checklist" section) were updated to state plainly that the checklist was
  removed and to route readers to [Installation](../../../../README.md#installation) and
  `make all` / `make all-secure` instead.
