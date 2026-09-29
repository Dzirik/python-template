# Experiment Logging

# Initial state

Both consoles clear, no log in request logger log folder.

# Terminal 1

PS D:\courses\mai\ai-coding-crash-course> npm run request-logger

> request-logger
> tsx request-logger/proxy.ts


------------------------------------------------------------------------
  Agent      Claude Code (Anthropic)
  Listening  http://localhost:8787
  Forwards   https://api.anthropic.com
  Logs       D:\courses\mai\ai-coding-crash-course\request-logger\logs
------------------------------------------------------------------------

  Run your agent in another terminal with:

      $env:ANTHROPIC_BASE_URL = 'http://localhost:8787'; $env:ENABLE_TOOL_SEARCH = 'true'; claude

  Note: ENABLE_TOOL_SEARCH=true is important. Claude Code trusts one host
        only. When the base URL points somewhere else, it turns off tool
        search, stops deferring tools, and writes every tool schema into
        the request. Your capture is then larger than a real one and has a
        different shape. The flag turns that effect off, so what you read
        is what Claude Code really sends.

  Note: This works with a Claude subscription login. Your login stays
        active. Only the model traffic moves.

  Using a different agent now? Run: npm run request-logger -- --force
  Press Ctrl+C to stop logging.
------------------------------------------------------------------------

# Terminal 2


 ▐▛███▛█   Claude Code v2.1.268
▝▜██████▀  Sonnet 5 with medium effort · Claude Enterprise
  ▝▝ ▝▝    D:\courses\mai\ai-coding-crash-course

First logs appered now both on Terminal 1 and log folder:
- [request-logger] Claude Code  HEAD /api/hello -> 200  (housekeeping, not logged)
- [request-logger] Claude Code  POST /v1/messages?beta=true -> 429  logs/2026-09-11T07-20-48-290_claude-code.md

# Runs

## Group A

### Usage After

Session

Total cost:            $0.2297
Total duration (API):  6s
Total duration (wall): 3m 13s
Total code changes:    0 lines added, 0 lines removed
Usage by model:
     claude-sonnet-5:  1.7k input, 43 output, 102.6k cache read, 51.4k cache write ($0.2297)
Prompt cache (main):   2 requests · 50% of input tokens from cache · no misses · warm (1h TTL, last activity 36s ago)

What's contributing to your limits usage?
Approximate, based on local sessions on this machine — does not include other devices or claude.ai

Last 24h · these are independent characteristics of your usage, not a breakdown

41% of your usage was at >150k context
 Longer sessions are more expensive even when cached. /compact mid-task, /clear when switching to new tasks.

17% of your usage came from subagent-heavy sessions
 Each subagent runs its own requests. Be deliberate about spawning them — and consider configuring a cheaper model for simpler subagents.

10% of your usage came from subagents under "general-purpose"
 If this runs frequently, consider configuring its subagents with a cheaper model or tightening their prompts.

Skills                  % of usage
/to-implementation-plan         4%
/implement                      2%
/grill-with-docs                2%
/to-issues                      1%
/to-prd                         1%

Subagents               % of usage
general-purpose                10%
implement                       3%

d to day · w to week

Usage credits
$128.10 spent

Esc to cancel

## Terminal 1 after

[request-logger] Claude Code  HEAD /api/hello -> 200  (housekeeping, not logged)
[request-logger] Claude Code  POST /v1/messages?beta=true -> 429  logs/2026-09-11T07-20-48-290_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-23-08-217_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-23-20-602_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-23-20-573_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-23-22-265_claude-code.md

## Group B

### After 5

They are separated

### Terminal 1 after

------------------------------------------------------------------------

[request-logger] Claude Code  HEAD /api/hello -> 200  (housekeeping, not logged)
[request-logger] Claude Code  POST /v1/messages?beta=true -> 429  logs/2026-09-11T07-20-48-290_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-23-08-217_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-23-20-602_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-23-20-573_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-23-22-265_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-26-00-968_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-26-03-702_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-26-06-473_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-26-15-766_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-26-41-194_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-26-53-824_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-27-32-355_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-27-56-517_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-27-58-990_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-31-02-075_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-34-24-919_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-34-28-552_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-34-30-793_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-34-32-256_claude-code.md

## Group C

### Terminal Addition After C1

[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-35-55-622_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-36-02-237_claude-code.md
[request-logger] Claude Code  POST /v1/messages/count_tokens?beta=true -> 200  (housekeeping, not logged)
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-36-05-497_claude-code.md

### Terminal Addition After C2

[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-39-56-266_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-39-58-903_claude-code.md

## Group D

### Terminal Addition After D1

[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-41-12-036_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-41-15-777_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-41-17-933_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-41-26-452_claude-code.md

### Terminal Addition After D2

[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-43-01-846_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-43-04-580_claude-code.md

### Terminal Addition After D3

[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-44-24-891_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-44-27-150_claude-code.md

## Group E

### Terminal Addition After E1

[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-46-20-041_claude-code.md

### Terminal Addition After E2

#### Claude Terminal
 Ask for something long — Write a 600-word explanation of how HTTP streaming works. — and press Esc to interrupt it halfway

● API Error: Connection lost mid-response. The response above may be incomplete.

✻ Worked for 7s · done 9:47 AM

#### Terminal 1

[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-46-20-041_claude-code.md
PS D:\courses\mai\ai-coding-crash-course>

## Group F

### Terminal Addition After F1

[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-50-21-262_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-50-25-776_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-50-27-574_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-50-29-763_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-50-27-551_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-50-32-803_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-50-34-662_claude-code.md
[request-logger] Claude Code  POST /v1/messages/count_tokens?beta=true -> 200  (housekeeping, not logged)
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-50-37-477_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-50-47-795_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-50-49-331_claude-code.md

### Terminal Addition After F2

[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-53-23-405_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-53-25-979_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-53-28-057_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-53-29-736_claude-code.md]

### Terminal Addition After F3

[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-54-05-278_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-54-11-433_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-54-14-847_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-54-18-155_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-54-22-393_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-54-30-341_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-54-36-443_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-54-41-476_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-55-07-451_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-55-10-436_claude-code.md

### Terminal Addition After F4

[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-55-41-503_claude-code.md
[request-logger] Claude Code  POST /v1/messages/count_tokens?beta=true -> 200  (housekeeping, not logged)
[request-logger] Claude Code  POST /v1/messages/count_tokens?beta=true -> 200  (housekeeping, not logged)
[request-logger] Claude Code  POST /v1/messages/count_tokens?beta=true -> 200  (housekeeping, not logged)

### Terminal Addition After F5

[[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-58-47-095_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-59-07-555_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-59-12-637_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-59-41-105_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-59-51-538_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T07-59-57-916_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T08-00-03-769_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T08-00-46-701_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T08-00-49-166_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T08-01-18-710_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T08-01-28-150_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T08-01-38-898_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T08-01-43-009_claude-code.md

## Group G

### Terminal Addition After G1

[request-logger] Claude Code  HEAD /api/hello -> 200  (housekeeping, not logged)
[request-logger] Claude Code  POST /v1/messages?beta=true -> 429  logs/2026-09-11T08-05-27-092_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T08-05-31-704_claude-code.md

### Terminal Addition After G2

[request-logger] Claude Code  HEAD /api/hello -> 200  (housekeeping, not logged)
[request-logger] Claude Code  POST /v1/messages?beta=true -> 429  logs/2026-09-11T08-06-28-718_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T08-06-37-155_claude-code.md

## Group H

### Terminal Addition After H1

[request-logger] Claude Code  HEAD /api/hello -> 200  (housekeeping, not logged)
[request-logger] Claude Code  POST /v1/messages?beta=true -> 429  logs/2026-09-11T08-07-24-924_claude-code.md
[request-logger] Claude Code  POST /v1/messages?beta=true -> 200  logs/2026-09-11T08-07-29-536_claude-code.md

### After H2

✻ Connection refused — a firewall or proxy may be blocking it (ConnectionRefused) · Retrying in 5s · attempt 4/10







