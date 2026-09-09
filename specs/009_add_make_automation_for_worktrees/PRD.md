---
status: implemented
labels: [prd, retrospective]
supersedes: none
relates-to: docs/adr/0002-repo-root-path-anchoring.md
builds-on: none
implemented-on: 2026-09-08 (branch `worktree_automation`)
---

# PRD: Add make automation for git worktrees

> **Retrospective PRD.** This document was written *after* the feature was designed,
> implemented and acceptance-tested, to capture the decisions in the same form as the
> other specs in this repository. Every decision below reflects what was actually built
> and verified, not a forward-looking proposal. The acceptance evidence is recorded in
> [Testing Decisions](#testing-decisions).

## Problem Statement

The maintainer began using [git worktrees](https://git-scm.com/docs/git-worktree) to work
several branches in parallel without switching branches or re-cloning. A fresh worktree is
a complete checkout of the *tracked* files only — everything excluded from version control
is missing, because it was never in the git history to begin with:

- `.env` — real credentials and machine paths
- `configurations/python_personal.toml` — the personal config overlay
- `make_config.mk` — the single-file workflow pointer
- `notebooks/raw/playground_notebook.py`, `marimo/raw/playground_marimo.py`
- `.venv` — which must be per-worktree anyway
- the PyCharm `.idea` project settings

`make create-venv` creates all of those, but it creates them **from templates**, which is
right for a clean clone and wrong for a worktree: the two files that matter most — `.env`
and `python_personal.toml` — come out blank or all-comments, so the worktree cannot
actually run anything that needs credentials until they are copied over by hand. Every new
worktree therefore began with the same manual, forgettable ritual.

Whatever solves this has to respect what this repository *is*: a **template**, cloned under
arbitrary names and laid out wherever its users please. It cannot assume the main checkout sits
at any particular path, or carries any particular directory name.

## Solution

A single command, run from inside the worktree, that leaves it ready to work:

```bash
git worktree add ../python-template-my-feature -b my-feature   # from the main checkout
cd ../python-template-my-feature
make setup-worktree
```

`make setup-worktree` is the **worktree counterpart of `make create-venv`**, and splits the
missing files by their *nature*:

- Files carrying **personal content** are **copied from the main checkout**: `.env`,
  `configurations/python_personal.toml`, and the portable PyCharm `.idea` settings.
- Everything else is **created from templates** by the ordinary `create-venv` setup that
  runs immediately afterwards: `make_config.mk`, both playground notebooks, and the
  worktree's own `.venv`.

The main checkout is **derived from git** (`git rev-parse --git-common-dir`), never from a
hard-coded or CWD-relative path, so the command works whatever the repository and worktree
directories are named and wherever they live.

Two properties of this repository keep the command small:

1. **Git hooks need no re-install in a worktree.** `make install-hooks` sets
   `core.hooksPath` to the *relative* path `scripts/hooks`, stored in the shared repository
   config; git resolves it inside whichever worktree the hook runs in. Install once in the
   main checkout and every worktree has them.
2. **This repository's `.idea` is fully portable.** Every path in it is `$PROJECT_DIR$`-relative
   and there is no interpreter/SDK entry at all, so the only file that must not be copied is
   the machine-local `workspace.xml`.

## User Stories

1. As a developer who has just created a worktree, I want one command that sets it up completely, so that I can start working without a manual checklist.
2. As a developer, I want my real `.env` copied from the main checkout, so that the worktree can reach the databases and paths I already configured.
3. As a developer, I want my `configurations/python_personal.toml` overlay copied from the main checkout, so that the worktree resolves the same config profile I actually use.
4. As a developer, I want the worktree to get its own `.venv`, so that dependency state on this branch is independent of every other branch I have checked out.
5. As a developer, I want the venv built from *this* branch's `uv.lock`, so that a branch that changes dependencies is tested with the dependencies it declares.
6. As a developer, I want `make_config.mk` created from the template rather than inherited, so that it does not point at whatever file I was last working on in a different branch.
7. As a developer, I want the playground notebooks created from templates rather than inherited, so that unrelated scratch work is not dragged into this branch.
8. As a developer, I do not want to hard-code where my main checkout lives, so that the command keeps working when I rename or move directories.
9. As a developer working in a differently-named clone of this template, I want the command to work unmodified, so that the template is genuinely reusable.
10. As a developer, I want to see which main checkout was detected, so that a wrong detection is obvious immediately rather than after I wonder why my config is blank.
11. As a developer who occasionally wants to seed from a different checkout, I want an explicit override, so that the automation has an escape hatch.
12. As a developer who accidentally runs the command in the main checkout, I want it to stop and tell me to run `make create-venv`, so that it does not copy files onto themselves.
13. As a developer who runs the command outside a git repository, I want it to fail immediately, so that nothing is created in the wrong place.
14. As a developer whose main checkout has no `.env` yet, I want a warning rather than an abort, so that I still end up with a working worktree.
15. As a developer, I want any such warning repeated at the very end, so that it is not lost in the long `uv sync` output.
16. As a developer, I want to re-run the command safely, so that I can top up a partially-set-up worktree without losing edits.
17. As a developer, I want a file I already edited in this worktree never to be overwritten, so that branch-specific tweaks survive.
18. As a PyCharm user, I want the portable project settings seeded, so that I do not re-mark source roots and excluded folders for every worktree.
19. As a PyCharm user, I do **not** want `workspace.xml` copied, so that another checkout's window layout and run state do not follow me.
20. As a developer, I want the git hooks to work in the worktree, so that branch protection and pre-push security checks still apply.
21. As a developer, I do not want to re-run `make install-hooks` per worktree, so that setup stays a single command.
22. As a developer, I want `make all` to pass in a fresh worktree, so that I know the environment is genuinely usable before I start.
23. As a developer reading `make help`, I want the worktree command listed, so that I can discover it without reading the Makefile.
24. As a developer running the command, I want it to print its own documentation like every other target, so that the behaviour is explained at the moment it runs.
25. As a reader of the README, I want a Worktree Set Up chapter, so that the flow, the seeded-file table and the removal gotcha are written down.
26. As an agent working in this repository, I want `CLAUDE.md` to state the worktree entry point, so that I do not suggest `make create-venv` inside a worktree.
27. As the maintainer, I want the console cleared exactly once during the run, so that messages printed early are not wiped mid-command.
28. As the maintainer, I want the new target composed from existing targets rather than duplicating them, so that there is one code path for venv creation.
29. As a developer removing a worktree, I want to know that `git worktree remove` needs `--force`, so that the failure does not surprise me.
30. As the maintainer, I want the change recorded in the changelog, so that the repository history explains why the target exists.

## Implementation Decisions

- **A separate `setup-worktree` target**, not auto-detection inside `create-venv`. A command
  everyone runs should not change behaviour based on hidden git state, and a clean-clone path
  must not become coupled to "is there a main checkout with a filled `.env` somewhere".

- **`create-venv` split into `create-venv-no-clear` + `create-venv: clear-console create-venv-no-clear`**,
  matching the `-no-clear` convention already used by every quality target. `setup-worktree`
  then composes the pieces as **ordered prerequisites**, exactly as `all:` does:
  `setup-worktree: clear-console worktree-prep create-venv-no-clear`, with the closing banner
  as its own recipe. This avoids a recursive `make create-venv` call mid-recipe, which would
  clear the console and wipe every message printed before it — including the warnings the user
  most needs to see.

- **The main checkout is derived from `git rev-parse --git-common-dir`**, whose parent is the
  main worktree, resolved with `--path-format=absolute` so the printed paths are Windows-style
  and consistent. This follows the anchoring principle of
  [ADR 0002](../../docs/adr/0002-repo-root-path-anchoring.md): anchor to a real marker, never a
  CWD-relative guess or a hard-coded candidate path. Rejected: a fixed relative path such as
  `MAIN_REPO := ../<name>`, which cannot survive a renamed or relocated clone of a template.

- **Main-checkout detection uses `git-common-dir == git-dir`**, which is true only in the main
  worktree — a more direct signal than comparing directory strings.

- **`MAIN_REPO=<path>` overrides the derivation** and, deliberately, also bypasses the
  main-checkout guard, so seeding from an unrelated checkout is possible on purpose.

- **Copy set split by nature of the file**, as tabulated in [Solution](#solution). The
  judgement call worth recording: `make_config.mk` is **not** inherited from the main checkout
  even though it is untracked, because it names the file you were last working on *there*.

- **`.idea` seeded by denylist, not allowlist** — copy everything except `workspace.xml`,
  the tracked `jsonSchemas.xml`, and git's already-ignored `shelf/`, `httpRequests/`,
  `queries/`, `dataSources*`. The portable set is "everything", so an allowlist would silently
  drop portable settings PyCharm adds later (`codeStyles/`, `runConfigurations/`).
  Accepted limitation: `modules.xml` references `python-template.iml` by name, so a
  differently-named worktree shows that module name; harmless, and renaming would mean
  rewriting `modules.xml` too.

- **Skip-if-exists, per file, with no `force` flag.** `setup-worktree` is a one-shot
  bootstrapper that must never clobber a file already edited in this worktree. Rejected:
  always-overwrite (silent data loss) and a `force=` parameter (a flag people misfire).
  Rejected: symlinking `.env` to the main checkout — Windows symlinks need Developer Mode or
  admin rights, and the link breaks when the main checkout moves.

- **Failure policy.** Hard-fail when the command's premise is false — not a git repository, or
  run from the main checkout without an override. Warn-and-continue when a *source* file is
  missing, because the fallback (a template file, created by `create-venv`) still leaves a
  working worktree, and [ADR 0006](../../docs/adr/0006-config-tracked-base-and-overlays.md)
  makes the personal overlay optional by design.

- **Closing banner** prints the worktree path, the detected main checkout, any re-checked
  warnings, and OS-conditional next steps. The warnings are **re-evaluated in the final
  recipe** rather than passed between targets, which needs no shared state and puts the
  actionable line where the user is actually looking after `uv sync` has scrolled.

- **Git hooks are untouched by this feature.** Verified, not assumed: `core.hooksPath` is the
  relative `scripts/hooks`, resolved per worktree.

- **Scope held to `setup-worktree` alone.** Rejected: a `new-worktree` wrapper (it would have
  to run from the main checkout while `setup-worktree` runs from the worktree — two commands
  with opposite location requirements — and it drags in branch-naming policy the template
  should not own) and a `remove-worktree` wrapper (a target whose only job is to pass `--force`
  to a destructive git command). Both are one README line instead.

- **Documentation** follows the existing machinery: `make_print_documentation.py` prints the
  README section named after the target owning the recipe, so a `### setup-worktree` section
  was added and `### create-venv` renamed to `### create-venv-no-clear`. Also added: a
  `### help` entry, a README *Worktree Set Up* chapter with a ToC entry, a `CLAUDE.md`
  sentence, and a `docs/CHANGELOG.md` entry. **No ADR** — this is tooling ergonomics, not
  architecture; the README chapter cites ADR 0002 for the anchoring principle instead.

- **Incidental correction:** the README `### install-hooks` section claimed hooks are installed
  to `.git/hooks/`. They are not — `install-hooks` sets `core.hooksPath`. That false claim was
  the main reason to doubt the worktree hooks story, so it was fixed.

## Testing Decisions

**Seam.** The feature is a Makefile target composed of shell, git plumbing and file copies.
Its only meaningful seam is the **command boundary**: run `make setup-worktree` in a real
worktree and assert on the resulting filesystem, exit codes and printed output. There is no
lower seam worth inventing — a unit test of the copy logic would test a reimplementation of
`cp`, not the behaviour that can actually break (git path derivation, prerequisite ordering,
console clearing, hook resolution). This is consistent with the repository, which has **no
automated tests for the Makefile**; the closest prior art is
`tests/tests_utils/test_python_version_consistency.py`, which asserts consistency across
version-bearing project files rather than exercising make.

**A good test here** asserts externally observable outcomes — which files exist, where their
bytes came from, what exit code was returned, what the banner said — and never inspects how
the recipe is written internally.

**Acceptance pass executed on 2026-09-08**, against a real throwaway worktree, all green:

| # | Check | Result |
|---|---|---|
| 1 | `git worktree add` | pass |
| 2 | `make setup-worktree` | exit 0; `.env` and `python_personal.toml` byte-identical to the main checkout; `make_config.mk` and both playgrounds byte-identical to their **templates**; `.idea` seeded without `workspace.xml`; `.venv` created |
| 3 | `make all` in the worktree | 400 passed, 1 skipped, exit 0 |
| 4 | Hook resolution | `git rev-parse --git-path hooks/pre-commit` resolved into the **worktree's own** `scripts/hooks`; a real commit on a protected branch name from inside the worktree was **blocked** |
| 5 | Re-run | every file reported "already exists - keeping it"; nothing clobbered |
| 6 | Run from the main checkout | hard-fails with the "run `make create-venv` instead" message, touches nothing |
| 7 | `MAIN_REPO=` override | bypasses the main-checkout guard as designed |
| 8 | Missing-source warning path | prints `! .env not found in the main checkout - a template one will be created` |
| 9 | `git worktree remove` without `--force` | refuses, confirming the documented gotcha |

Test state was fully torn down: worktree removed, temporary branch deleted, `core.hooksPath`
restored to unset, fixtures deleted.

**Recommended future automation (not built):** a consistency test in the spirit of
`test_python_version_consistency.py`, asserting that every `### <target>` documentation section
in `README.md` corresponds to a real Makefile target and vice versa. The rename in this change
had a silent failure mode — a mismatched section name makes the target print *nothing*, with no
error — and only a manual check caught it.

## Out of Scope

- **Creating or removing worktrees.** No `new-worktree` / `remove-worktree` targets; `git worktree add`
  and `git worktree remove --force` are documented instead.
- **`git worktree` lifecycle management** — pruning, listing, or per-worktree branch policy.
- **Sharing or deduplicating `.venv` across worktrees.** Each worktree builds its own, which is
  the point.
- **Re-syncing a worktree when the main checkout's `.env` later changes.** Deliberately manual.
- **Any runtime behaviour change.** Config, logger, exceptions, transformers and the supervision
  runtime are untouched.
- **The pre-existing Cygwin-make / pyenv-shim problem on the maintainer's machine** (`make hello`
  fails without putting the real `uv`/`python` ahead of the pyenv shims on `PATH`). Unrelated to
  this feature and present on the previous Makefile; worth its own fix.
- **The stale `docs/TESTING_CHECKLIST.md` and `docs/meta/TESTING_CHECKLIST.md`**, which still
  reference the removed `make create-venv-linux` target. Pre-existing; reconciling the two
  near-duplicate checklists is a separate job.

## Further Notes

- Implemented on branch `worktree_automation` and left uncommitted at the time of writing, in
  four files: `Makefile`, `README.md`, `CLAUDE.md`, `docs/CHANGELOG.md`.
- `create-venv` already creates every git-ignored working file idempotently (`test -f … || cp`),
  which is what keeps `setup-worktree` this small: it only has to seed the two personal files
  plus `.idea`, and the guards in `create-venv` then skip regenerating them. Any future file
  added to `create-venv`'s setup block is inherited by the worktree flow for free — only a file
  that must carry *personal* content needs adding to the seeded set.
