---
status: proposed
labels: [prd, ai-assisted-development]
supersedes: none
relates-to: docs/adr/0008-harness-capture.md, docs/adr/0009-harness-capture-raw-record-and-sessions.md, specs/010_custom_request_logger/analysis/CAPTURE_FORMAT_SPEC.md, specs/010_custom_request_logger/analysis/EXPERIMENT_SESSIONS.md, specs/010_custom_request_logger/analysis/EXPERIMENT_SESSIONS_RESULTS.md
builds-on: specs/010_custom_request_logger/analysis/REQUEST_LOGGER_NAIVE_USAGE.md
implemented-on: not yet
---

# PRD: Harness Capture — record everything the coding agent sends, per session

> **Status note (2026-09-29): on hold, under investigation.** For now
> [Claude Tap](https://github.com/liaohch3/claude-tap) (MIT, installed machine-wide via
> `uv tool install`, not a repository dependency) is used as the capture tool and evaluated.
> How to proceed is decided later, based on that experience: a custom implementation per this
> PRD, something built on top of Claude Tap, contributing to Claude Tap itself, or none of
> these. Until then this PRD stays as the reference design; an outcome that departs from
> [ADR 0008](../../docs/adr/0008-harness-capture.md) gets its own ADR.

> **Forward-looking PRD, second revision.** The first revision treated the course-style
> Markdown render as the product. The design session of 2026-09-24 moved the goal: Harness
> Capture is now the **data base for monitoring how the agent operates** — context
> evolution, subagent spawning, tool use — across several concurrent sessions. The raw
> record is the product; the render is a view of it. The session model was verified against
> real traffic the same day ([`analysis/EXPERIMENT_SESSIONS_RESULTS.md`](analysis/EXPERIMENT_SESSIONS_RESULTS.md)).
> The byte-exact render rules stay in [`analysis/CAPTURE_FORMAT_SPEC.md`](analysis/CAPTURE_FORMAT_SPEC.md);
> the decisions that changed are recorded in
> [ADR 0009](../../docs/adr/0009-harness-capture-raw-record-and-sessions.md).

## Problem Statement

What a developer types into a coding agent is a small fraction of what reaches the model.
A "Hello!" turn measured through the AI Coding Crash Course's request logger produced a
**123,914-byte request**: the full harness system prompt, twenty-odd tool schemas, injected
`<system-reminder>` context, and — last and smallest — the six characters the developer
typed. Roughly two thirds of it was tool definitions.

Reading one request is only the start. How the agent *operates* is visible only across
requests: how the context grows turn by turn, when a subagent is spawned and what it is
given, how many side calls (safety classification, prompt suggestions, token counting,
quota probes) one user turn fans out into. The session-model experiment measured **1–15
requests per user turn**, interleaved with subagent and auxiliary traffic. A developer who
runs several agent sessions at once and switches between them needs each session's traffic
kept apart, complete and in order — otherwise nothing downstream can be trusted.

A team that has never looked at that traffic reasons about agent context, cost and tool
bloat entirely by guesswork. That is exactly the class of hard-won know-how
[`docs/PROJECT_VISION.md`](../../docs/PROJECT_VISION.md) says this template exists to
capture, and the template currently has nothing to say about it.

The course's tool solves the per-request half of the problem but is unavailable to us:
~6,000 lines of TypeScript, licensed *"All rights reserved"*, needing Node in a uv-only
repository, and sitting outside every quality gate here. It also drops the parts a monitoring
layer needs — housekeeping calls, response headers — and has no notion of a session. See
[ADR 0008](../../docs/adr/0008-harness-capture.md).

A related failure the tool must also address: the naive route to this capability is *quietly
wrong*. A capture that filters, prunes or reinterprets traffic at record time teaches a false
fact confidently, and nothing recorded later can correct it. A plausible-but-wrong record is
worse than no record.

## Solution

**Harness Capture** — a local reverse proxy, written in Python, living in
`src/harness_capture/`. It listens on `localhost:8787`, forwards every request to
`api.anthropic.com` untouched, streams responses straight back, and records every exchange
that passes through it into `captures/<session-id>/`.

Each exchange produces two layers (terminology fixed in [`CONTEXT.md`](../../CONTEXT.md)):

- the **raw record** — authoritative and lossless: the request body byte-exact, the decoded
  response stream verbatim, and a small JSON file with everything the bodies leave out
  (ordering, identity, headers in both directions, status);
- the **render** — the course-style `.md` view, derived from the raw record, written as each
  `POST /v1/messages` exchange completes, and regenerable from the raw record at any time.

One proxy serves every concurrent session. Traffic is partitioned by **Harness Session**,
keyed by the harness's own `x-claude-code-session-id` header, and ordered within a session
by a sequence number assigned on arrival. That ordering — not wall-clock time — is the
session's timeline.

Started with `make harness-capture`. On startup it prints the exact command — PowerShell and
POSIX variants both — for launching Claude Code through it, plus the current size and session
count of `captures/`. The developer pastes the command into as many terminals as they like,
works normally, and reads the newest `.md` in the session's folder.

The course's name, "request logger", is recorded in `CONTEXT.md` as a known external alias;
it is not used in code, because **Logger** already means something else in this repository.

## User Stories

1. As a developer, I want one `make` command to start the capture proxy, so that I do not have to remember a script path or environment variables.
2. As a developer, I want the exact agent-launch command printed for my shell, so that I do not reconstruct it wrongly and get an empty folder.
3. As a Windows developer, I want the PowerShell form printed too, so that the primary platform is not a second-class path.
4. As a developer, I want my agent session to behave exactly as it normally does, so that I am observing my real workflow rather than a distorted one.
5. As a developer, I want responses streamed rather than buffered, so that the agent does not appear to hang while I am capturing.
6. As a developer running several agent sessions at once, I want one proxy to serve them all and keep each session's traffic in its own folder, so that I can switch between terminals and still read each session separately.
7. As a developer, I want a way to tell session folders apart at a glance — when it started, which directory it ran in, which model — so that I do not have to open files to find the session I am looking at.
8. As a developer, I want **every** request recorded — token counting, quota probes, classifier calls, retries, endpoints nobody has seen yet — so that the fan-out of one turn is data, not a console impression.
9. As a developer, I want each session's exchanges numbered in arrival order without gaps, so that I can treat the session as a series over iterations and trust that nothing is missing.
10. As a future analyst, I want request and response headers, status and identity recorded alongside the bodies, so that rate limits, retries and subagent attribution can be analysed without re-running the session.
11. As a future analyst, I want the raw record to be lossless and never reinterpreted, so that context evolution, subagent trees and tool-use patterns can be derived — and re-derived when the derivation is wrong.
12. As a learner, I want each model call rendered the same way the course renders it, so that what I learn there transfers here unchanged.
13. As a learner, I want the section sizes stated numerically, so that "tool schemas dominate the request" is a measurement rather than an impression.
14. As a developer, I want to regenerate the renders of a session from its raw records, so that a renderer fix applies to sessions I have already recorded.
15. As a developer, I want my credentials never written to disk, so that a capture cannot leak access.
16. As a developer, I want captures gitignored bluntly and their total size shown on every start, so that source code copied into them cannot be committed or accumulate unnoticed.
17. As a developer about to share my screen, I want one command to wipe every capture — or one session's — so that I do not have to remember what is in them.
18. As a developer, I want a capture failure to never break my coding session, so that the observation tool cannot cost me work.
19. As a developer whose port 8787 is taken, I want an immediate readable error naming the config key, so that I fix it instead of debugging an empty folder.
20. As a maintainer, I want the whole thing under `mypy --strict`, ruff and pytest like everything else, so that it does not rot.
21. As a maintainer, I want to move to Google Vertex later by changing configuration rather than refactoring, so that today's narrow scope is not a dead end.

## Implementation Decisions

### Placement and shape

- Package: **`src/harness_capture/`**, flat modules, matching the `src/utils/` convention. Tests mirror it at `tests/tests_harness_capture/`.
- Config classes go to **`src/configurations/`**, following `WatchdogConfig` — not into the component package.
- Seven modules, chosen so the seams are the test boundaries:

| Module | Responsibility |
| --- | --- |
| `capture_renderer.py` | pure: request/response payloads to the Markdown render |
| `exchange_record.py` | pure: the `.exchange.json` content — identity, headers with redaction, status, timestamps |
| `launch_command.py` | pure: platform + port to the PowerShell and POSIX launch commands |
| `session_store.py` | session routing, `session.json` index, thread-safe persisted sequence numbers |
| `capture_writer.py` | filenames and the four files of one exchange, inside the session folder |
| `upstream_client.py` | the only module that touches the network; the injected seam |
| `harness_capture_proxy.py` | request handler, `ThreadingHTTPServer`, banner, `__main__` |

A small render entry point (`make harness-capture-render`) reads raw records back and feeds
`capture_renderer`; it needs no network and no server.

### Runtime

- **Stdlib only**: `ThreadingHTTPServer` + `http.client`. No new dependency, no `asyncio`. Threading is required — Claude Code issues concurrent requests, several sessions share one proxy, and serialising them would alter the timing of the thing being measured.
- We are a **reverse** proxy (`ANTHROPIC_BASE_URL` points at us): no `CONNECT`, no TLS interception.
- **Forwarding is the contract; capturing is best-effort.** Every capture write — raw record, index, render — is wrapped and can only ever warn. Recording the maximum makes a full disk more likely; that must still produce a warning, never a broken session.
- The render is written **after** the response stream has completed, never inline with it.
- Port in use → immediate readable failure naming the config key. **No** fallback port: a proxy on a port the agent is not pointed at is precisely the silent-empty-folder failure.
- No upstream reachability preflight; the first real request reports the truth.

### Configuration

`HarnessCaptureConfig(BaseComponentConfig[HarnessCaptureConfigData])`, profile at
`configurations/harness_captures/harness_capture_default.toml`:

```toml
name = "harness_capture_default"
port = 8787
upstream_host = "api.anthropic.com"
```

`skip_housekeeping` and `max_captures` from the first revision are **removed** (see *What is
recorded* and *Retention*).

Deliberately **not** configurable: the redacted-header lists (a key whose only use is to
disable a safety measure is not configuration), the file layout, and chunk size. **No
retention or filtering configuration exists in v1.** The goal is to learn from complete data
first; options for what to keep become configuration later, once the recorded data shows
which ones are worth having — the original draft's `max_captures = 200` was sized by
assumption and was wrong by an order of magnitude (corrected to 100 only after the corpus
was measured).

### What is recorded

- **Everything that passes through the proxy gets a raw record**: `POST /v1/messages`, `POST /v1/messages/count_tokens`, `HEAD /api/hello`, 429 quota probes, the non-streamed safety-classifier calls, and any endpoint not yet seen. There is no filtering at record time — filtering is the one mistake that cannot be undone afterwards; hiding housekeeping is a view concern for the analysis layer.
- **Only `POST /v1/messages` gets a render.** Other endpoints have the raw record only; a generic render can be added later if it proves useful.
- Non-2xx responses are recorded and rendered like any other.
- A console line is printed for every request, carrying the session-id prefix so interleaved output from several sessions stays legible.
- **No retry-storm suppressor**, as before.

**The boundary is harness↔model-provider traffic.** The proxy sees what Claude Code sends to
`ANTHROPIC_BASE_URL`, and nothing else: the harness's own telemetry and error reporting,
WebFetch, MCP servers, git and local tool execution are invisible. Their *effects* on the
conversation still appear, as `tool_result` content in the next request — so everything the
model saw and said is in the record.

### Sessions and ordering

- **One proxy for all sessions.** Each exchange is routed by its `x-claude-code-session-id` header to `captures/<session-id>/`. A request without the header goes to `captures/_unattributed/` rather than being dropped.
- The header semantics were verified before any code was written ([`analysis/EXPERIMENT_SESSIONS_RESULTS.md`](analysis/EXPERIMENT_SESSIONS_RESULTS.md), Claude Code v2.1.281): `/clear` issues a new id; `--continue` reuses the continued session's id; `/compact` keeps it; subagents share the parent's id and add `x-claude-code-agent-id`; the classifier, prompt-suggestion and title side calls carry their session's id with no agent id; two concurrent sessions got distinct ids with no interference; `metadata.user_id`'s `session_id` equalled the header in 33/33.
- **Sequence numbers are per session**, assigned **on request arrival**, gapless, and persisted in the session folder so they survive a proxy restart. Assignment is thread-safe: one session issues concurrent requests (subagent and main agent, parallel side calls). Arrival order is the only ordering the proxy knows for certain — completion order differs for concurrent requests, and arrival timestamps can sit 2–7 ms apart, so the sequence number, not the timestamp, is the ordering key.
- Each session folder holds a `session.json` index: first and last seen, model, next sequence number, and the working directory — **extracted best-effort** from the system prompt's "Primary working directory" line, marked as extracted, and used only as a human label, **never as a key**. Two sessions in one directory are two sessions.
- **The orphan quota probe is recorded as-is.** On `--continue`, the launch's startup 429 probe carries a throwaway session id that never recurs, so it gets a one-exchange session folder of its own. Its id is a fact on the wire; which session it "belongs" to is a conclusion, and conclusions belong to the analysis layer (it is identifiable by `max_tokens: 1` and its `quota` content).
- **The proxy records facts, never derived structure.** Chain membership, per-agent iteration, context evolution and the subagent tree are all derived later, offline, by the analysis layer. The experiment showed why this must be so: prompt-suggestion calls use the main system prompt and all tools, and their `messages` are the main chain plus one extra user message — a side branch that looks like the chain. The agent-id header cannot supply chain membership; only content can.

### Output

Per exchange, four files sharing one stem inside the session folder:

```
captures/
  <session-id>/
    session.json
    000001_2026-09-24T06-36-42-917Z_messages.request.txt
    000001_2026-09-24T06-36-42-917Z_messages.response.txt
    000001_2026-09-24T06-36-42-917Z_messages.exchange.json
    000001_2026-09-24T06-36-42-917Z_messages.md
    000002_2026-09-24T06-36-43-102Z_count_tokens.request.txt
    ...
  _unattributed/
```

The stem is `<seq:06d>_<utc-timestamp>Z_<endpoint-slug>`: the zero-padded sequence number
first, so listings and globs sort in timeline order; the UTC arrival timestamp (dash-separated
— `:` is illegal in Windows filenames) for humans; the endpoint slug (`messages`,
`count_tokens`, `api_hello`, …) so housekeeping is visible at a glance. One clock read serves
both the filename and every in-file timestamp.

**Raw record** — authoritative:

| File | Contents |
| --- | --- |
| `.request.txt` | the request body exactly as received — byte-exact and replayable (`content-length` = file size) |
| `.response.txt` | the decoded upstream stream verbatim — SSE lines, blank lines and trailing spaces preserved |
| `.exchange.json` | sequence number, session id, agent id (or absent), method + path-with-query, upstream status, request **and** response headers in send order with redaction applied, start and end UTC timestamps, `content-encoding` as received, and whether the client disconnected before the stream ended |

The bodies stay separate from `.exchange.json` so they keep their proven properties:
`curl --data @x.request.txt` replay, and `content-length` matching file size (77/77 in the
reference corpus) as a free integrity check.

**No per-chunk or first-byte timing** is recorded. The analysis axis is iteration order —
"step *i* of the session" — not wall-clock time; start and end timestamps are kept only
because they are free and break ties.

**Render** — derived, `POST /v1/messages` only, following
[`analysis/CAPTURE_FORMAT_SPEC.md`](analysis/CAPTURE_FORMAT_SPEC.md) so learning transfers from the course:

```
<meta> · <headers> · <request>{<params>, <system-prompt>, <tools>, <messages>} · <response>
```

All additions stay confined to `<meta>` so every taught section keeps its shape:

```
- **section sizes**: system 18,204 · tools 104,125 (18) · messages 22,891
- **total**: 154,522 bytes
- **tools**: 18 (ToolSearch present)
- **session**: 3f2a9c1e-…
- **agent**: (none)
- **seq**: 17
```

`agent` is the raw `x-claude-code-agent-id` value, or `(none)` when the header is absent —
**never `main`**, because the classifier and prompt-suggestion calls also lack it and are not
the main conversation. The size bullets are the quantitative form of the lesson: in the
reference corpus `<tools>` was **67.4% of the capture**. The `tool search: OFF` guard stays
withdrawn, for the reasons in [ADR 0008](../../docs/adr/0008-harness-capture.md).

`<params>` still reproduces upstream's fixed allowlist, so `output_config` and
`context_management` are absent from the render — a gap kept for format equivalence. It
no longer matters for data accuracy: the raw record has them.

`make harness-capture-render session=<prefix>` re-renders a session from its raw records, so
a renderer fix or a newly learned course-format detail applies retroactively, and exchanges
whose render failed on write can be recovered. When the render and the raw record disagree,
the raw record is right.

### Redaction

Hard-coded, not configurable. Redacted values are replaced with the literal `[REDACTED]` in
`.exchange.json` and in the render:

| Direction | Redacted |
| --- | --- |
| request | `authorization`, `x-api-key`, `api-key`, `cookie` |
| response | `set-cookie` |

The rule is unchanged from the first revision — anything that grants or carries access is
redacted — and simply extends to response headers now that they are recorded.

**Kept verbatim:** `request-id`, `anthropic-ratelimit-*`, `retry-after`,
`anthropic-organization-id`, `metadata.user_id`, and the session and agent ids. They are
identifiers and operating signals — the rate-limit headers are exactly the data that explains
a 429 — and masking them while `<messages>` carries proprietary source would falsely imply the
rest is safe to share. The bodies (`.request.txt`, `.response.txt`) never contain headers.

### Retention

- **Nothing inside a session is ever pruned.** A session with missing exchanges breaks the gapless sequence and corrupts every chain and context-growth analysis built on it. `max_captures` is removed.
- Hygiene operates on **whole sessions only**: `make harness-capture-clean` wipes everything; `make harness-capture-clean session=<prefix>` wipes one session. Anything smarter — newest-N sessions, a size cap — is deferred until the data says what is worth keeping.
- **Visibility instead of automation:** the startup banner prints the total size of `captures/` and the session count, so growth cannot go unnoticed.
- **No compression and no cross-request deduplication in v1.** Each request carries the whole conversation so far, so a session's volume grows roughly quadratically with its turns; the estimate is **~30–60 MB per 12-turn session** including `count_tokens`, and hundreds of MB for a long session with images. Gzip would break replay, the `content-length` check and editor readability; delta storage would save the most but is lossy until reconstruction is proven byte-exact. Both can be added later on top of lossless files; neither can be undone once data is stored that way.
- Recording is opt-in by nature: only sessions launched through the proxy are recorded.
- Captures land in **`captures/`**, the fifth `ProjectPaths` location. `.gitignore` gains `/captures/*` and `!/captures/.gitkeep`; `captures/.gitkeep` is tracked, mirroring `logs/` and `reports/`.

### Makefile and repository wiring

- `make harness-capture`, `make harness-capture-no-clear`, `make harness-capture-render session=<prefix>`, `make harness-capture-clean [session=<prefix>]`.
- No `.env` or `Envs` change; nothing here is environment-sourced.
- `make create-venv` seeds nothing new — the config profile and `.gitkeep` are both tracked.
- `harness_capture_proxy.py` carries the house `if __name__ == "__main__":` block.

## Testing Decisions

- **Mock-heavy, house style.** `upstream_client` is the injected seam; a fake replaces it everywhere else. The bulk of the suite is pure tests of `capture_renderer` against synthetic Anthropic payloads, and of `exchange_record` against synthetic header lists.
- `launch_command` is unit-tested per platform. It looks over-split for two strings until you notice one of them is PowerShell quoting on the primary platform — the single place a wrong character costs a junior an afternoon of "the folder is empty".
- `exchange_record`: header order preserved in both directions; every request- and response-side redaction applied, including `set-cookie`; the kept-verbatim headers untouched; agent id absent vs present.
- `session_store`, against `tmp_path`:
  - routing by session-id header, and to `_unattributed/` when it is missing;
  - sequence numbers gapless under **concurrent** assignment from many threads in one session;
  - sequence numbers continue — not restart — after the store is re-created over an existing folder (the proxy-restart case);
  - the `session.json` index, including a working-directory label that cannot be extracted.
- `capture_writer` is tested against `tmp_path`: the stem format and sort order, the four files, no headers in either body file, and that a failing render leaves the raw record intact.
- **One real-socket test runs in `make all` and CI.** Streaming passthrough is the highest-risk behaviour here and mocks cannot test it — a fake `wfile` accepts every write in any order. Bind `127.0.0.1` on **port 0**, serve a canned deterministic SSE stream from a local fake upstream, `shutdown()` + `server_close()` in fixture teardown, short socket timeouts so a hang fails fast. It also asserts that two concurrent requests with different session ids land in two folders.
- Fallback if it proves flaky on the Windows runners: move it behind the declared-but-unused `integration` marker and deselect it in CI, rather than letting it rot.
- Fixtures are **synthetic payloads written by us**, built from [`analysis/CAPTURE_FORMAT_SPEC.md`](analysis/CAPTURE_FORMAT_SPEC.md) and [`analysis/EXPERIMENT_SESSIONS_RESULTS.md`](analysis/EXPERIMENT_SESSIONS_RESULTS.md). Neither corpus is committed; a gap found during implementation needs a fresh harvest per [`analysis/EXPERIMENT_ON_MAT.md`](analysis/EXPERIMENT_ON_MAT.md) or [`analysis/EXPERIMENT_SESSIONS.md`](analysis/EXPERIMENT_SESSIONS.md), not a re-read.
- Branches never exercised, to be implemented defensively without claiming fidelity: `redacted_thinking`, `document` blocks, empty content arrays, a stream that genuinely dies before `message_delta`, and any model other than `claude-sonnet-5`.

## Out of Scope

- **The analysis and monitoring layer** — context evolution over iterations, chain membership, the subagent tree, tool-use statistics, housekeeping filtering, linking orphan quota probes to their session. That is the next phase; this one produces the data it is built on, and records nothing it would have to un-derive.
- **Retention policy and configuration** beyond whole-session cleanup — deferred until the recorded data shows what is worth keeping.
- **Compression and cross-request deduplication** — see Retention.
- **Traffic outside harness↔model-provider** — telemetry, WebFetch, MCP servers, local tool execution.
- **Any agent other than Claude Code**, and any provider other than the direct Anthropic API. `upstream_host` is the seam; Google Vertex is one host string and one env-var name away when someone needs it.
- **AWS Bedrock** — excluded on technical grounds: SigV4 signs the `Host` header, so a transparent proxy invalidates the signature.
- **The selection wizard, agent catalogue, model discovery and custom base URLs** — all of upstream's breadth exists to serve thousands of students on unknown setups.
- **Retry-storm suppression.**
- **Toggling `ANTHROPIC_BASE_URL` via `.claude/settings.local.json`** — hidden persistent state that fails silently when the proxy is stopped.
- **Redacting account identifiers** — see Redaction above.
- **AI engineering** (LLM code inside a project). Parked deliberately in `PROJECT_VISION.md`'s Long-term direction.

## Further Notes

**Two prerequisites are met.** The render format was derived from the 77-capture corpus
harvested on 2026-09-11 ([`analysis/EXPERIMENT_ON_MAT.md`](analysis/EXPERIMENT_ON_MAT.md),
[`analysis/RUN_LOG.md`](analysis/RUN_LOG.md), re-run in [`analysis/RUN_LOG_02.md`](analysis/RUN_LOG_02.md)) and verified by
reconstruction — 77/77 for `<messages>` and `<params>`, 66/66 for `<tools>`. The session
model was verified on 2026-09-24 against 33 captures from two lifecycle and concurrency runs
([`analysis/EXPERIMENT_SESSIONS.md`](analysis/EXPERIMENT_SESSIONS.md),
[`analysis/EXPERIMENT_SESSIONS_RESULTS.md`](analysis/EXPERIMENT_SESSIONS_RESULTS.md)).

**Open items, neither blocking:**

- `--resume` of an older conversation was not run. It is expected to behave like `--continue` (reuse the id); this affects tutorial wording only.
- Whether `count_tokens` requests carry the session id is unknown — the course logger does not record them. If they do not, they land in `_unattributed/`, which is still correct; our own proxy's first run answers it.

**What changed from the first revision**, and why, is recorded in
[ADR 0009](../../docs/adr/0009-harness-capture-raw-record-and-sessions.md): the raw record
became authoritative, recording became unfiltered, storage became session-partitioned, and
in-session pruning was abolished. ADR 0008's three decisions — own Python implementation,
Claude-Code-on-Anthropic scope, stdlib-only proxy — stand unchanged.

**The format is derived from observed output, never from `render.ts`.** Every rule in
[`analysis/CAPTURE_FORMAT_SPEC.md`](analysis/CAPTURE_FORMAT_SPEC.md) was established by writing a reconstructor
and diffing its output against the corpus — reproducing behaviour, verified against
behaviour. That is the licensing position recorded in
[ADR 0008](../../docs/adr/0008-harness-capture.md) and it must survive implementation.

**Documentation deliverables:** `docs/tutorials/HARNESS_CAPTURE.md` (the in-repo, Python
equivalent of [`analysis/REQUEST_LOGGER_NAIVE_USAGE.md`](analysis/REQUEST_LOGGER_NAIVE_USAGE.md), which stays
here as provenance), including the session layout, what `/clear`, `--continue` and
`/compact` do to it, and the traffic boundary; a `CLAUDE.md` architecture subsection plus the
`make` targets; and a README mention.

**Already landed from the design sessions:** `CONTEXT.md` gained **Agent Harness**,
**Harness Capture** (with its *raw record* and *render* layers) and **Harness Session**, and
`captures` on **Project Paths**; `PROJECT_VISION.md` gained the AI-assisted-development scope
paragraph, guiding principle 7 *"Agent-legible by design"*, AI engineering under Long-term
direction, and open question 5 *"The AI boundary"*;
[ADR 0008](../../docs/adr/0008-harness-capture.md) was accepted.

**Unrelated cleanup noticed en route:** `CLAUDE.md` states *".conf is retired from the
repository entirely"*, but `configurations/` still holds `python_repo.conf`,
`python_local.conf`, `python_personal.conf`, `logger_*.conf` and `watchdog_cmd_0*.conf`
alongside their `.toml` replacements. Not part of this work.
