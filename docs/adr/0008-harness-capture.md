---
status: accepted
amended-by: 0009-harness-capture-raw-record-and-sessions.md
---

# Harness Capture: own Python reimplementation, Claude-Code-on-Anthropic scope, stdlib-only proxy

This decision introduces **Harness Capture** (see `CONTEXT.md` for the term, and
**Agent Harness** alongside it): a local reverse proxy that sits between the coding agent
and the model provider, forwards every request untouched, and writes a readable copy of the
exchange to `captures/`. It is the first shipped artefact of the AI-assisted-development
layer added to [`docs/PROJECT_VISION.md`](../PROJECT_VISION.md) in the same change, and the
concrete expression of its guiding principle 7, *"Agent-legible by design"*.

The idea is not ours. It comes from the request logger in the AI Coding Crash Course
(`ai-coding-crash-course/request-logger/`), a ~6,000-line TypeScript tool covering nine
agents across many providers. The problem it solves is real and specific: what a developer
types is a small fraction of what the harness sends. A trivial "Hello!" turn measured
through that tool produced a 123,914-byte request — a full system prompt, twenty-odd tool
schemas, injected context — of which roughly two thirds was tool definitions. A team that
has never read one of those requests reasons about agent context, cost and tool bloat by
guesswork.

The three choices below are the ones that are hard to reverse, surprising without context,
and genuine trade-offs. The rest of the design — capture allowlist, redaction boundary,
retention, module split, test strategy, output format — is specification and lives in
[`../../specs/010_custom_request_logger/PRD.md`](../../specs/010_custom_request_logger/PRD.md).

We decided:

1. **We write our own Python implementation rather than vendoring the original.** The
   course repository is licensed *"for students of the AI Coding Crash Course. All rights
   reserved."* Copying its source into a team repository is not available to us, and the
   question "why not just use Matt's tool?" has no answer visible in the code. The output
   *format* is reproduced deliberately, so the team reads the same shape in the course and
   in this repo — but it is derived from **observed output**, never from transcribing
   `render.ts`. This was carried out: a 77-capture corpus was harvested on 2026-09-11, and
   every rule in
   [`CAPTURE_FORMAT_SPEC.md`](../../specs/010_custom_request_logger/analysis/CAPTURE_FORMAT_SPEC.md) was
   established by writing a reconstructor and diffing its output against that corpus —
   77/77 byte-exact for `<messages>` and `<params>`, 66/66 for `<tools>`. Reproducing
   behaviour and verifying against behaviour is the whole of the method. The corpus was
   never committed and no longer exists; committed fixtures are synthetic payloads written
   by us.
2. **Scope is Claude Code talking to the direct Anthropic API, and nothing else.** One
   upstream host, one wire format, one renderer, no agent catalogue and no selection wizard;
   the launch command is a constant the proxy prints. Upstream's own documentation states
   that Claude Code on the direct Anthropic API is the only agent route tested end to end —
   the other cells of its matrix were verified by reading published code. Rebuilding
   unverified breadth would be rebuilding unverified breadth. The `upstream_host` config key
   is the named seam: Google Vertex is one host string and one env-var name away, and is
   added when someone actually needs it. AWS Bedrock is excluded on technical grounds —
   SigV4 signs the `Host` header, so a transparent proxy invalidates the signature.
3. **The proxy is stdlib-only: `ThreadingHTTPServer` plus `http.client`. No new dependency,
   and no `asyncio`.** Because the agent points `ANTHROPIC_BASE_URL` at us we are a reverse
   proxy, not a forward one — there is no `CONNECT` tunnelling and no TLS interception, so
   the stdlib is sufficient. Threading (not the single-threaded server) is required: Claude
   Code issues concurrent requests, and serialising them would alter the timing of the thing
   we are measuring.

## Considered options

- **Vendor the TypeScript tool and add Node to the repository** — rejected on licensing
  first, and on toolchain second. It would put ~6,000 lines outside every quality gate this
  repository has (`mypy --strict`, ruff, pytest, bandit all run over `src` and `tests`),
  introduce a second package manager against guiding principle 3, and leave a vendored fork
  drifting from an upstream we cannot merge from.
- **Port the full nine-agent catalogue** — rejected: `agents.ts` alone is 1,207 lines, most
  of it describing agents this team does not use, in a template whose vision explicitly
  refuses broad public adoption. Scope 2 above collapses that file to four config keys.
- **Build on `aiohttp`** (already pinned in `[project] dependencies`) — rejected. The pin is
  a security floor for a transitive Jupyter/marimo dependency, not something `src` imports;
  using it would promote it to a real dependency and, worse, introduce the repository's
  first `asyncio` code in a developer tool that nobody's application imports. A template
  whose primary users are junior data scientists should not spend that precedent here.
  `requests` with `stream=True` was rejected for the opposite reason: it manages buffering
  on our behalf when byte-level control is exactly what server-sent-event passthrough needs.
- **Toggle `ANTHROPIC_BASE_URL` through `.claude/settings.local.json`** instead of printing a
  launch command — rejected despite being the most ergonomic option. It is hidden persistent
  state that fails in the worst direction: left on with the proxy stopped, every agent
  session in the repository breaks with an error that names nothing. Stateless copy-paste can
  only fail while the developer is looking at it.

## Consequences

> **Amended by [ADR 0009](0009-harness-capture-raw-record-and-sessions.md).** The
> `max_captures` cap and capturing only `POST /v1/messages` are superseded. Every request is
> now recorded as an authoritative raw record, stored per Harness Session, and never pruned
> within a session; the `.md` is a derived render. The three numbered decisions above stand.

**Forwarding is the contract; capturing is best-effort.** This proxy sits in the critical
path of real work, so every capture write is wrapped: a full disk, a permissions error or a
renderer bug on an unexpected payload must warn and never interrupt the response stream. The
worst outcome is not a missing capture but a broken session, or a truncated response nobody
notices. Anything that later makes the write synchronous with the stream breaks this.

**A capture is a copy of your source code and must be treated like it.** Once the agent is
doing real work, `<messages>` contains the contents of every file it read. Credentials
(`authorization`, `x-api-key`, `api-key`) are redacted because they grant access; account
identifiers deliberately are not, since masking a UUID while the file carries proprietary
source would imply the rest is safe to share. The controls are therefore at the boundary —
`captures/` bluntly gitignored, capped at `max_captures`, and a `make` target to wipe it.

`captures/` becomes a fifth canonical `ProjectPaths` location alongside `data`, `logs`,
`reports` and `configurations`, because a capture is genuinely a new kind of output and does
not belong in any of the existing four — in particular not in `logs/`, which is a **Logger**
concern and is only partially tracked.

We now own a hand-rolled HTTP proxy in a data-science template, forever. It is small and
stdlib-only by design so that it stays cheap to own, but it is real maintenance: when Claude
Code changes its wire shape, the renderer is ours to fix.

**The observer effect could not be reproduced, and the guard that depended on it was
withdrawn.** Two controlled attempts (2026-09-11 and 2026-09-24) to capture a
tool-search-off request produced arms that were byte-identical; in the second, the off-arm's
`cache_read_input_tokens` exactly matched the on-arm's `cache_creation_input_tokens`, which
proves the prefixes were identical because prompt caching is prefix-exact. We therefore have
no evidence the effect still exists in Claude Code v2.1.268+ and no capture of the off-state.
Rather than ship a detector for a condition we have never observed, the capture states
observable facts only (`- **tools**: N (ToolSearch present)`) and makes no judgement. The
launch command still sets `ENABLE_TOOL_SEARCH=true`, because upstream documents the effect
and the flag costs nothing; the tutorial says plainly that we could not reproduce it.

**Because the corpus is gone, the format spec is the sole record.** Anything it does not
cover — `redacted_thinking`, `document` blocks, a stream that dies before `message_delta`,
models other than `claude-sonnet-5` — is unverified and must be implemented defensively,
without claiming fidelity. Closing such a gap requires a fresh harvest, not a re-read.
