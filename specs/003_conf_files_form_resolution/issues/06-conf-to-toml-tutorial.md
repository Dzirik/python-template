# Write the `docs/tutorials/CONF_TO_TOML.md` authoring tutorial

> **Status:** `ready-for-agent`

## Parent

[`specs/003_conf_files_form_resolution/PRD.md`](../PRD.md) — *Migrate the HOCON config family to TOML*

## What to build

A hands-on tutorial that teaches a template adopter to confidently author and edit the config profiles in TOML without reading the full TOML spec. It is a practical authoring reference for *this repo's* profiles, not a language spec. Follow the existing tutorial house style (title, short overview, numbered Table of Contents, then numbered sections with copy-pasteable fenced examples — as in `PERSISTENT_RUN.md` and `CHECKER_SCHEDULER_SET_UP.md`).

Each of the following must be covered with a runnable snippet:

- **Scalars** — strings (and quoting rules), integers, floats, booleans (`true`/`false`, lower-case), and how each lands in the typed `NamedTuple`.
- **Lists / arrays** — homogeneous arrays (`args = ["--delay", "3"]`) in both single-line and multi-line (trailing-comma) forms.
- **Dictionaries / tables** — the `[table]` header form and the inline `{ key = value }` form, and when to prefer each.
- **Nested tables** — dotted/nested headers (e.g. `[param_ntb_execution]`) mapped to the nested `NamedTuple` tree.
- **Lists of objects** — the `[[array-of-tables]]` form (as used by the watchdog `workers`) *and* the compact inline-table-in-array form (as used by `notebook_executioner_params`), showing both produce the same list-of-mappings for `typedload`.
- **Comments** — `#` line comments, mirroring the guidance comments preserved in `python_local`.
- **HOCON→TOML cheat-sheet** — a side-by-side table translating each structure this repo actually uses, plus the gotchas: `True`→`true`, unquoted-key differences, no HOCON substitutions/includes, and choosing `[[...]]` vs inline tables.

Cross-link the profile examples in the PRD (the "how the profiles look" before/after appendix).

## Acceptance criteria

- [ ] `docs/tutorials/CONF_TO_TOML.md` exists in the house tutorial style (title, overview, numbered ToC, numbered sections with fenced snippets).
- [ ] Every listed topic (scalars, arrays single/multi-line, tables + inline tables, nested tables, `[[array-of-tables]]` + inline-table-in-array, comments) has a runnable snippet.
- [ ] A HOCON→TOML side-by-side cheat-sheet covers the structures this repo uses and the listed gotchas.
- [ ] The snippets reflect the actual converted profile shapes from issue 01.
- [ ] `make all-secure` stays green (docs-only change).

## Blocked by

- [`01-core-toml-migration.md`](./01-core-toml-migration.md)
