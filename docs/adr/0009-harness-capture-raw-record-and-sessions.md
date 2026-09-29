---
status: accepted
amends: 0008-harness-capture.md
---

# Harness Capture: authoritative raw record, per-session storage, no pruning inside a session

[ADR 0008](0008-harness-capture.md) introduced **Harness Capture** as a teaching tool: a
proxy whose product was a course-style Markdown render of each `POST /v1/messages` call,
with a `max_captures` cap on the folder. During design the goal widened. The captured data
is now the base for a later analysis layer covering context growth over a session, subagent
spawning and tool use. It also has to keep several **Harness Sessions** (see `CONTEXT.md`)
apart, because the developer runs several at once and switches between them. For that
purpose the accuracy of the data matters more than the look of the render, and a record
missing information cannot be repaired afterwards.

The three numbered decisions in ADR 0008 stand: our own Python implementation, Claude Code
on the direct Anthropic API only, and a stdlib-only proxy. This ADR replaces what ADR 0008
said about **what is kept and how it is organised**. The detailed specification is in
[`../../specs/010_custom_request_logger/PRD.md`](../../specs/010_custom_request_logger/PRD.md). The
render rules are in
[`CAPTURE_FORMAT_SPEC.md`](../../specs/010_custom_request_logger/analysis/CAPTURE_FORMAT_SPEC.md).

The session model was checked before any code was written. A controlled run through the
course's request logger
([`EXPERIMENT_SESSIONS_RESULTS.md`](../../specs/010_custom_request_logger/analysis/EXPERIMENT_SESSIONS_RESULTS.md),
33 captures, Claude Code v2.1.281) showed the following:
- `/clear` issues a new `x-claude-code-session-id`.
- `--continue` reuses the old id.
- `/compact` keeps the id.
- Subagents share their parent's id and add `x-claude-code-agent-id`.
- Two concurrent sessions through one proxy got distinct ids and did not interfere.
- The safety classifier and the prompt-suggestion calls also carry their session's id.
- The `session_id` inside `metadata.user_id` equalled the header in 33/33 captures.

We decided:

1. **The raw record is authoritative; the render is derived.** Each exchange writes three
   raw files:
   - `.request.txt`: the request body, byte-exact.
   - `.response.txt`: the decoded response stream, verbatim.
   - `.exchange.json`: sequence number, session and agent ids, method and path, status,
     headers in both directions with credentials redacted, start and end timestamps,
     `content-encoding`, and whether the client disconnected.

   The course-style `.md` is kept as the first-layer, human-facing product. It is rendered
   from the raw record after the stream closes, it can always be regenerated, and when the
   two disagree the raw record is right.
2. **Every request that passes through the proxy is recorded.** That includes
   `count_tokens`, `HEAD /api/hello`, 429 quota probes and classifier calls. There is no
   filtering at capture time, and `skip_housekeeping` is removed. Deciding what is "noise"
   belongs to the analysis layer, which can hide it without having thrown it away. Only
   `POST /v1/messages` gets a render.
3. **Storage is partitioned per Harness Session, keyed on `x-claude-code-session-id`.**
   - One proxy serves every session. Captures land in `captures/<session-id>/`, and
     requests without the header land in `captures/_unattributed/`.
   - Each session folder carries a small `session.json` index: first and last seen, model,
     and the working directory extracted best-effort from the system prompt.
   - The working directory is a **label only**, never the key.
4. **The timeline is a gapless, per-session sequence number assigned at arrival.** It is
   stored in the session folder so that it survives proxy restarts, and it prefixes every
   file name. The analysis axis is iteration order (i ∈ ℕ), not wall-clock time. The
   proxy records only facts: arrival order, ids and two timestamps. Per-agent chains and
   iterations are **derived** offline from content, because no header can supply them.
5. **Nothing inside a session is ever pruned.** `max_captures` is removed.
   - Cleanup works on whole sessions only.
   - The startup banner reports the total size and session count.
   - There is no retention configuration until real data shows what is worth keeping.
   - v1 uses no compression and no cross-request deduplication.

## Considered options

- **Keep the `.md` as the primary artefact.** Rejected. The render drops
  `output_config` and `context_management`, drops `server_tool_use` blocks, and replaces
  images with placeholders. It also does not record headers or timing. None of that can be
  recovered once only the render exists.
- **Key sessions by working directory.** Rejected. It would merge two concurrent sessions
  in the same repository, which is the exact case this change exists for. It also depends
  on parsing prose from a system prompt that subagent and classifier requests may not
  carry.
- **One proxy per session, on its own port.** Rejected. The developer would have to track
  several ports, and pairing a terminal with the wrong port would silently put one
  session's traffic in another's folder.
- **One sequence counter per proxy run.** Rejected. It resets on restart, so numbers from
  different runs would collide inside the same session folder.
- **Count-based pruning** (the old `max_captures`). Rejected. Removing individual
  exchanges breaks the gapless sequence and corrupts every chain and context-growth
  analysis built on it.
- **Gzip or delta storage now.** Deferred, not rejected.
  - Gzip breaks `curl --data @x.request.txt` replay and the `content-length` = file-size
    integrity check, which held 77/77.
  - Delta storage (keeping only each request's new suffix) is lossy until byte-exact
    reconstruction is proven.
  - Either can be layered onto lossless files later. Neither can be undone once data is
    stored that way.

## Consequences

**Storage grows roughly quadratically with session length.** Every request carries the
whole conversation so far, with the ~18 KB system prompt and ~104 KB of tools repeated each
time. The estimate is 30–60 MB for a 12-turn session including `count_tokens`, and more
with images. This is accepted for now: recording is opt-in, since only sessions launched
through the proxy are captured, and the size banner keeps growth visible.
Forwarding-is-the-contract from ADR 0008 applies more than ever: a full disk must warn and
never break a session.

**Every `--continue` leaves an orphan probe folder.** The startup quota probe (a 429,
`max_tokens` 1) is sent before the continued session is resolved, so it carries a
throwaway session id that never appears again. We record it as it arrived. Linking it to
the session it preceded is a conclusion for the analysis layer, which can match it by time
and shape.

**"No agent id" does not mean "the main conversation".** Prompt-suggestion calls use the
main system prompt and all the tools, and their messages are the main conversation plus one
extra message. That makes them a side branch that looks like the main conversation. The
classifier and title calls also have no agent id. The render therefore shows the raw header
value or `(none)`, never `main`, and chain membership has to be derived from content.

**Arrival order is not completion order.** In the experiment, concurrent requests 2–7 ms
apart completed out of order, and the console printed them out of order. The sequence
number, assigned at arrival, is the ordering key. Timestamps only break ties.

**Recording response headers widens the redaction list** to include `cookie` and
`set-cookie`, alongside `authorization`, `x-api-key` and `api-key`. Identifiers and operating
signals (`request-id`, `anthropic-ratelimit-*`, `retry-after`, `anthropic-organization-id`)
stay verbatim, for the same reason ADR 0008 gives for `user_id`.

**Open, and not blocking:**
- Whether `--resume` reuses the resumed session's id; it was not run, and is expected to
  behave like `--continue`.
- Whether `count_tokens` carries the session id; the course logger does not write those
  calls. If it does not, those calls land in `_unattributed/`.

Our own proxy will answer both on its first real session.
