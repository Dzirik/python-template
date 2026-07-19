# Brainstorm / Research / Idea-Refinement Skills

**Created:** July 13, 2026
**Status:** Reference / Evaluation Notes

## Overview

Notes on agent skills that support **brainstorming, research, and idea refinement** for
Python coding, data science, and machine-learning work. Split into two parts: what is
**already installed** in this environment (our starting point), and **candidates from the
open skills ecosystem** worth adopting.

Skills are installed with the [Skills CLI](https://skills.sh/):

```
npx skills add <owner/repo@skill> -g -y      # -g = user-level, -y = no prompt
```

---

## Already available (starting point)

These are installed locally and cover a good part of the "refine my idea / plan" need
before reaching for anything external.

| Skill | What it does |
|-------|--------------|
| **`grill-me`** | Interviews you relentlessly about a plan or design, resolving each branch of the decision tree until there is shared understanding. Best for stress-testing an idea before committing. |
| **`grill-with-docs`** | Same grilling loop, but challenges the plan against the existing domain model, sharpens terminology, and updates docs (`CONTEXT.md`, ADRs) inline as decisions crystallise. |
| **`prototype`** | Builds a throwaway prototype to flesh out a design before committing — either a runnable terminal app for state/logic questions, or several toggleable UI variations. |
| **`deep-research`** | Fan-out web-search research harness: fetches sources, adversarially verifies claims, and synthesises a cited report. Good for the "research" leg. |

**Combination for now:** `grill-me` (or `grill-with-docs`) to sharpen the idea →
`prototype` to sanity-check it → `deep-research` when external facts are needed.

---

## Candidates from the ecosystem

### For brainstorm & idea refinement — recommended

**`obra/superpowers@brainstorming`** — ⭐ top pick
- ~274K installs; from the reputable [`obra/superpowers`](https://skills.sh/obra/superpowers) collection.
- Structured design dialogue *before* any code is written: explores context, asks
  clarifying questions, proposes approaches, documents a spec, iterates, and gets sign-off,
  then hands off to `writing-plans` for a roadmap. Explicitly aimed at technical work.
- Link: https://skills.sh/obra/superpowers/brainstorming
- Install: `npx skills add obra/superpowers@brainstorming -g -y`

Companion:
- **`obra/superpowers@writing-plans`** (~182K) — turns an agreed design into a detailed
  implementation roadmap. https://skills.sh/obra/superpowers/writing-plans

### For the data science / ML research side

**`lllllllama/rigorpilot-skills`** — suite purpose-built for AI/ML research workflows
- 11 skills, ~1.4M installs total. Author is not an "official" source — skim the repo
  before adopting.
- Notable skills: `ai-research-explore`, `ai-research-reproduction`, `run-train`,
  `analyze-project`, `explore-code`, `repo-intake-and-plan`, `safe-debug`,
  `env-and-assets-bootstrap`, `minimal-run-and-audit`, `explore-run`,
  `paper-context-resolver`.
- Link: https://skills.sh/lllllllama/rigorpilot-skills
- Install (example): `npx skills add lllllllama/rigorpilot-skills@ai-research-explore -g -y`

**`lllllllama/ai-paper-reproduction-skill`** — reproducing ML/AI research papers
- Notable skills: `paper-context-resolver` (~140K), `repo-intake-and-plan`,
  `minimal-run-and-audit`, `env-and-assets-bootstrap`, `ai-paper-reproduction`.
- Link: https://skills.sh/lllllllama/ai-paper-reproduction-skill
- Install (example): `npx skills add lllllllama/ai-paper-reproduction-skill@paper-context-resolver -g -y`

---

## Recommendation

1. Install **`obra/superpowers@brainstorming`** (+ `writing-plans`) for the
   brainstorm → plan workflow — highest quality and reputation.
2. Add **`rigorpilot-skills`** (or the paper-reproduction suite) if ML/DS research and
   paper reproduction become a recurring need.
3. For pure "refine my idea / plan" sessions, the already-installed **`grill-me`** +
   **`prototype`** already cover a lot — start there.
