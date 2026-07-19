# Project Vision

## Why this project exists

Every data-science project quietly re-builds the same infrastructure — configuration, logging, error handling, project structure, tooling — before any real work begins. That work is repetitive, easy to get subtly wrong, and a poor use of a team's time. On top of that, junior engineers left to set things up themselves tend to improvise habits (no types, no tests, ad-hoc structure) that are hard to unlearn later, and the hard-won know-how that would prevent this stays trapped in senior engineers' heads.

This project exists to **solve that infrastructure once and capture the accumulated know-how in the scaffold itself.** It is a batteries-included, Windows-first template for data-oriented Python: clone it and the plumbing — plus the explanations a newcomer needs to use it — is already there. (The "minimal" label from the original README title is retired; the presence of a production-supervision stack, dual notebook ecosystems, and visualisation helpers makes this a rich starting point, and richness is the point.)

## Scope

The template scaffolds **data-science projects for the author's team, across their entire lifecycle from data collection to production run**, at single-machine (pandas-scale) data sizes. Anything a data-science project reliably needs at any stage — and would be wasteful to rebuild each time — is in scope. General-purpose plumbing is in; the data-science problem itself is the user's to solve.

## Inputs and outputs

Describing a *project built with* the template:

- **Inputs:** raw data from files, databases, or APIs, plus a declarative configuration (TOML config profiles + `.env`) describing paths, credentials, and run settings.
- **Outputs:** exploratory analyses and visualisations, trained/fitted transformers and models, and — for productionised work — a supervised long-running process emitting structured logs, timing data, and healthcheck pings.

## Workflow

A project moves through the template as a single arc, never re-tooling between stages:

**clone → configure → collect data → explore → build → run in production**

| Stage | What the template provides |
| --- | --- |
| **Data collection / ingestion** | Configuration (TOML + env vars), path management, structured exceptions for data problems (`NoData`, `FileNotFound`, `IncorrectDataStructure`, …) |
| **Exploration & analysis** | Jupyter (jupytext-paired `.py`) and Marimo reactive notebooks, Plotly visualisation helpers |
| **Building / feature engineering** | sklearn-style `BaseTransformer` (`fit`/`predict`/`fit_predict`/`inverse`), `MetaClass` monitoring, the datetime one-hot encoder as a worked example |
| **Production run** | Process supervision (`watchdog`/`heartbeat`/`checker`), logging with timers and git-branch capture, healthchecks.io integration |

Cross-cutting throughout: the Singleton config + logger, strict quality gates, and the Makefile-driven workflow. Config profiles moved from HOCON to TOML (parsed by the stdlib `tomllib`); see [ADR 0003](adr/0003-toml-config-profiles.md) for the rationale and [`docs/tutorials/CONF_TO_TOML.md`](tutorials/CONF_TO_TOML.md) for the migration walkthrough.

## Primary users

The primary user is **the author's own team, including junior members.**

- It is a **team standard**: the same opinionated config, logging, tooling, and project structure every time, so setup decisions are made once and reused.
- The **extensive, hand-holding documentation is deliberate onboarding capital** — practices accumulated over years, written so junior engineers get productive quickly and absorb good habits (strict typing, tests, git hygiene, house style) they wouldn't set up on their own. The high engineering bar and the beginner-friendly prose are two halves of one goal: impose good practice while teaching it.

## What pain it removes

1. **Re-deciding infrastructure per project** — config, logging, error handling, and tooling no longer get re-litigated every time.
2. **Slow, senior-dependent onboarding** — juniors don't need a senior to walk them through setup and conventions.
3. **Drift between projects** — repos stop looking different from one another.
4. **Juniors improvising bad practices** — types, tests, and structure are there from the first commit rather than bolted on later.
5. **Time bled on plumbing** — effort goes to the data-science problem, not the scaffolding around it.
6. **Know-how trapped in people's heads** — hard-won practices are captured in the scaffold and its docs instead of living only in senior engineers' memory.

## What success looks like

The single measure of success: **you clone the template and immediately start real data-science work at high quality — with zero time spent on low-level plumbing or general settings.**

- The primary goal is that **infrastructure is never re-litigated.** It is provided as general-purpose capability with enough explanation that no low-level coding is needed to use it.
- Two consequences follow: onboarding is fast (clone to productive without a senior), and projects stay consistent (anyone can move between them and navigate immediately).

"Work" means genuine progress on a data-science project — not configuring the environment, wiring up a logger, or arguing about style.

## Guiding principles

1. **Windows-first, cross-platform-capable.** Windows is a hard requirement, not a convenience. A change that breaks Windows is rejected even if it is cleaner on Linux. Linux/macOS are fully supported and CI runs on Ubuntu, but Windows comes first.
2. **Quality is non-negotiable and fully automated.** `make all-secure` gates every push and is exactly what CI runs — strict `mypy`, enforced house style, tests, and security scans. There is no "I'll clean it up later."
3. **Reproducibility via `uv`.** Dependencies are pinned in `uv.lock`, never hand-edited, and only change through `make add-lib` / `make remove-lib`.
4. **Convention over configuration; one house style.** New code must be indistinguishable from existing code. Shared state is centralized in Singletons; environment variables are touched only through `Envs`.
5. **Teach by example.** Worked examples, `__main__` self-test blocks, and thorough documentation exist to onboard juniors — teaching is a first-class purpose.
6. **One entry point: the Makefile.** Every workflow runs through `make`, so there is one interface to learn.

## Constraints

Hard limits the template must live within:

- **Windows target.** Windows 10/11 with Cygwin `make` and PowerShell hooks must always work first-class.
- **Python 3.13–3.14.** The supported interpreter range; code must pass on both (CI matrix).
- **Single-machine data scale.** The workflow assumes data that fits pandas-scale processing on one machine.
- **Persistent-host runtime.** Production work runs as long-lived processes on a machine or VM under the watchdog — not in containers or serverless (today).
- **Reproducible dependencies.** All dependency changes flow through `uv` and the lock file; no ad-hoc installs.

## What we refuse to optimize for

Deliberate trade-offs — things we consciously choose *not* to be good at:

- **Broad public / open-source adoption.** It is a team standard, not a mass-market template; strong opinions are a feature.
- **Being a pip-installable library.** It is a *clone-and-build-in* scaffold — package root `src/`, absolute imports from `src.`. You start your project inside it; you do not depend on it.
- **Web / API serving.** No FastAPI/Flask/Django; it produces pipelines and analyses, not web apps.
- **Big-data / distributed compute.** No Spark, Dask, or Ray.
- **Minimal footprint.** Richness beats leanness; breadth across the lifecycle is intentional.

## Long-term direction

Deliberately out of scope today, but intended directions:

- **Containerization / cloud-native deployment** may follow the current persistent-host model.
- **Experiment tracking** (MLOps-style) is planned as a future addition to the build stage.
- **A feedback loop** — general improvements flowing back from projects into the template — may be adopted if project count grows (see Current stage).

## Current stage

The template is a **one-way seed**: a starting snapshot. Once a project is cloned, it is on its own — improvements discovered in that project stay there, with no feedback loop back into the template. The template evolves only when its maintainer deliberately edits it.

## What we hope to learn / open questions

1. **Feedback loop** — will the one-way-seed model hold, or will we eventually need improvements to flow back from projects into the template?
2. **Containerization trigger** — what would actually justify adding Docker / cloud-native support?
3. **Experiment-tracking choice** — which tool (MLflow, W&B, DVC, homegrown) fits the team when we add it?
4. **Two notebook ecosystems** — does maintaining both Jupyter and Marimo pay off, or will one win and the other be dropped?
