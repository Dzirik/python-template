# Experiment Sessions Results

PS D:\claude --versionoding-crash-course>
2.1.281 (Claude Code)

## 1 Setup


 ▐▛███▛█   Claude Code v2.1.281
▝▜██████▀  Opus 5.5 (1M context) · Claude Enterprise
  ▝▝ ▝▝    D:\courses\mai\ai-coding-crash-course

## Group S

[request-logger] Claude Code  HEAD /api/hello -> 200  (housekeeping, not logged)
[request-logger] Claude Code  POST /v1/messages?beta=true -> 429  logs/2026-09-24T11-53-37-516_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T11-54-27-905_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T11-54-45-184_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T11-54-45-188_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T11-54-48-824_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T11-54-55-973_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T11-55-30-488_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T11-55-32-341_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T11-56-03-198_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T11-56-09-866_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T11-56-09-859_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T11-56-12-301_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T11-56-26-058_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T11-56-38-728_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T11-56-40-819_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T11-57-05-923_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T11-57-49-536_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T11-57-56-559_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T11-58-10-723_claude-code.md
[request-logger] Claude Code  HEAD /api/hello -> 200  (housekeeping, not logged)
[request-logger] Claude Code  POST /v1/messages?beta=true -> 429  logs/2026-09-24T11-58-40-474_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T11-58-52-720_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T11-58-56-098_claude-code.md

## Group P

I started two claudes at the same time.
- Put hello in the first one.
- Then 'Read every file in @D:\courses\mai\ai-coding-crash-course\request-logger and summarize each in one line.' in second
- I exit session one, then entered, said hello

[request-logger] Claude Code  HEAD /api/hello -> 200  (housekeeping, not logged)
[request-logger] Claude Code  POST /v1/messages?beta=true -> 429  logs/2026-09-24T11-59-53-933_claude-code.md
[request-logger] Claude Code  HEAD /api/hello -> 200  (housekeeping, not logged)
[request-logger] Claude Code  POST /v1/messages?beta=true -> 429  logs/2026-09-24T12-00-07-697_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T12-00-29-738_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T12-02-03-383_claude-code.md
[request-logger] Claude Code  POST /v1/messages/count_tokens?beta=true -> 200  (housekeeping, not logged)
[request-logger] Claude Code  POST /v1/messages/count_tokens?beta=true -> 200  (housekeeping, not logged)
[request-logger] Claude Code  POST /v1/messages/count_tokens?beta=true -> 200  (housekeeping, not logged)
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T12-02-03-392_claude-code.md
[request-logger] Claude Code  HEAD /api/hello -> 200  (housekeeping, not logged)
[request-logger] Claude Code  POST /v1/messages?beta=true -> 429  logs/2026-09-24T12-02-54-511_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T12-02-48-613_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T12-02-56-121_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T12-03-09-739_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T12-03-09-737_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-24T12-06-10-894_claude-code.md

---

## Analysis (2026-09-24)

33 captures, read from `request-logger/logs/` on the day. Session ids anonymised as `S0…S5`,
agent ids as `A0`. `metadata.user_id.session_id` equalled the `x-claude-code-session-id`
header in **33/33** captures.

| Assumption | Result | Evidence |
| --- | --- | --- |
| A1 `/clear` issues a new id | **confirmed** | S0 until 11:57:56, first post-`/clear` `Hello` at 11:58:10 is S1 (2 messages) |
| A2 `--continue` | **reuses the id** | the relaunch's `Hello` at 11:58:52 is S1 with 5 messages — S1's history continued |
| A2 `--resume` | **not run** (S8 skipped) | expected to behave like `--continue`; unverified, tutorial wording only |
| A3 subagents share the parent id | **confirmed** | 11:56:09.859 and 11:56:26.058 carry S0 plus `x-claude-code-agent-id` A0; different system prompt ("You are a Claude agent…"), 7 tools vs 16 |
| A4 `/compact` keeps the id | **confirmed** | the compaction request (11:57:05, "…summary> block") and `Hello again.` (11:57:49, 5 messages) are both S0 |
| A5 concurrent sessions | **confirmed** | S3 and S4 interleaved 11:59–12:06, distinct ids, no reported errors |
| A6 auxiliary calls carry the id | **confirmed for everything logged** | security classifier (11:56:38, `max_tokens` 64, not streamed), prompt-suggestion calls ("Reply with ONLY the suggestion"), a 1-message 0-tool side call per session — all carry their session's id and **no** agent id. `count_tokens` (3 calls in Group P) not logged; still open |

### Findings not asked for

1. **Every launch's startup quota probe is a 429** (`max_tokens` 1, content `quota`). On a
   fresh launch it carries the new session's id (S0, S3, S4, S5). On `--continue` it carries
   a **throwaway id (S2) that never appears again** — the probe is sent before the continued
   session is resolved. Our layout would give it a one-exchange session folder of its own.
2. **"No agent id" is not "the main conversation".** Prompt-suggestion calls use the main
   system prompt and all 16 tools, and their `messages` are the main chain plus one extra user
   message — a side branch that looks like the chain. The classifier and the 1-message side
   calls also lack an agent id. Chain membership must be derived from content, as decided;
   the agent-id header alone cannot supply it.
3. **Filename (arrival) order and console (completion) order disagree** for concurrent
   requests — `11-56-09-866` printed before `11-56-09-859`; `12-02-48-613` printed after
   `12-02-54-511`. Arrival timestamps 2–7 ms apart confirm that the sequence number, not the
   timestamp, has to be the ordering key.
4. Header set unchanged from the corpus: 22 names, `x-claude-code-agent-id` the only
   optional one.
