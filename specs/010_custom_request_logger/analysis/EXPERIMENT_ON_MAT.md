# Experiment: harvesting a reference corpus from the course request logger

**Purpose.** Produce a set of real captures rich enough to pin down every branch the
`capture_renderer` will have to handle, so the renderer is derived from observed output
rather than from guesswork. This is the outstanding prerequisite named in
[`../PRD.md`](../PRD.md) — implementation of `capture_renderer.py` should not start until this
corpus exists.

**What we are learning.** Not "does the logger work" — it does. We are learning **the exact
rendered form** of every request and response shape Claude Code can produce, plus the
console behaviour and failure modes we need for our own error handling and tutorial.

---

## 0. Before you start — read this bit

### Where to run the session

**Run the whole experiment with the course repository as the working directory**
(`d:/courses/mai/ai-coding-crash-course`),

Reason: once the agent starts doing real work, `<messages>` contains the full contents of
every file it reads. Those captures then live on disk for weeks and get read during
development. Harvesting against the course's own TypeScript keeps the corpus free of
proprietary source and safe to keep around.

### Where the output goes

When you are done, move `request-logger/logs/` to a folder **outside both repositories** —
something like `d:/temp/harness-capture-corpus/`. It must never be committed to
`python-template`: it holds your `account_uuid`, `device_id`, session ids, and whatever the
agent read.

### One thing not to do

Do not clear `request-logger/logs/` between runs. The whole point is one accumulating
corpus, and the run log below is how we tell the files apart.

### Record as you go

Keep a scratch file next to the session — `RUN_LOG.md` — with one line per run:

```
R03 | 14:22:07 | asked it to read agents.ts        | expect: tool_use + tool_result
R04 | 14:23:41 | asked it to run a failing command | expect: tool_result is_error
```

Timestamps matter more than anything else here: capture filenames are UTC timestamps, and
this log is what maps forty near-identical filenames back to what you actually did. Note
your local-to-UTC offset once at the top.

Also record at the top: output of `claude --version`, and the **exact command the logger
printed** (copy it verbatim, we are reproducing it).

---

## 1. Setup

```
Terminal 1 (course repo):   npm run request-logger
Terminal 2 (course repo):   <the exact command Terminal 1 printed>
```

Before the first prompt, note in `RUN_LOG.md`:

- the full banner Terminal 1 printed
- whether any captures appeared **before** you typed anything (the startup quota probe)

**Keep Terminal 1 visible for the whole experiment.** Its console output is part of what we
are harvesting — every `(housekeeping, not logged)` line tells us about fan-out we would
otherwise never see. If your terminal can log to a file, do that; otherwise copy the
scrollback into `RUN_LOG.md` at the end.

---

## 2. The runs

Groups A–F run in **one continuous session** unless a run says otherwise — a long
accumulating history is itself something we need to see rendered. Groups G and H are
separate sessions.

### Group A — baseline and control

| Run | Do this | Why it matters |
| --- | --- | --- |
| A1 | `Hello!` | The control. You already have this; do it again so it sits at the head of one coherent session. |
| A2 | `What is 2 + 2?` | A second minimal turn — shows what a *second* request in the same session looks like, and whether cache-read tokens replace cache-creation. |

**Note in the log:** for A2, the `usage` line — specifically whether
`cache_read_input_tokens` is now non-zero. That transition is the clearest demonstration of
prompt caching we will ever show a junior, and we want a real example of it.

### Group B — tool use, the biggest gap in the current corpus

| Run | Do this | Renderer branch |
| --- | --- | --- |
| B1 | `Read request-logger/config.ts and tell me in one sentence what it does.` | assistant `tool_use` block; following request carries a `tool_result` |
| B2 | `Run: git status` | a `Bash` tool_use with a short, clean result |
| B3 | `Run: git nonsense-subcommand` | **`tool_result` with `is_error: true`** — the error shape |
| B4 | `Search the repo for every use of styleText.` | a `Grep`/`Glob` tool_use, and a result that is a list rather than prose |
| B5 | `Read all four of agents.ts, proxy.ts, render.ts and config.ts.` | **parallel tool calls** — several `tool_use` blocks in one assistant message, several `tool_result`s in one user message. This is a distinct shape from B1 and easy to get wrong. |
| B6 | `Add a one-line comment at the top of request-logger/config.ts saying "// harvest test", then remove it again.` | an **`Edit`** tool_use — a tool whose input is large and multi-line, unlike Bash's single string |

**Note in the log:** after B5, whether the capture's `<messages>` shows the parallel calls as
one message or several.

### Group C — thinking

| Run | Do this | Renderer branch |
| --- | --- | --- |
| C1 | `Think carefully: what are the trade-offs between putting the proxy's renderer in one module versus three?` | `thinking` content blocks in the assistant message, and `thinking` deltas in the stream |
| C2 | Immediately follow with `Now summarise that in two lines.` | a request whose **history contains** a prior thinking block — how a *past* thinking block is rendered is a different branch from a live one |

**Note in the log:** whether `output_tokens_details.thinking_tokens` is non-zero, and whether
you see anything labelled `redacted_thinking` (opportunistic — we cannot force it).

### Group D — large and non-text payloads

| Run | Do this | Renderer branch |
| --- | --- | --- |
| D1 | `Read package-lock.json and tell me how many direct dependencies there are.` | a **very large `tool_result`** — does the render truncate it? |
| D2 | Paste or drag **any screenshot** into the prompt and ask `What is in this image?` | an **`image` content block** with base64 data. Critical: we need to see whether the render inlines megabytes of base64 into the `.md` or truncates it. This single question changes our writer design. |
| D3 | *(Optional, only if you ever do this in real work)* attach a small PDF and ask about it | a `document` content block |

**Note in the log:** the byte size of the D2 capture's `.md` versus the others.

### Group E — response edge cases

| Run | Do this | Renderer branch |
| --- | --- | --- |
| E1 | Ask for something long — `Write a 600-word explanation of how HTTP streaming works.` — and **press Esc to interrupt it** halfway | an **aborted stream**. What does the logger write when the client hangs up mid-response? Our writer must not produce a corrupt or half-written capture, and this is the only way to see the shape. |
| E2 | Anything that makes the agent run for a while, then **stop the proxy (Ctrl+C in Terminal 1) mid-turn** | what the *agent* shows the user when the proxy dies. This is for our tutorial's troubleshooting section, not the renderer. Restart the proxy afterwards. |
| E3 | Opportunistic — if you ever see a `429`, a `500`, or an `overloaded_error` in Terminal 1, note the timestamp | a **non-200 capture**. Cannot be forced; flag it if it appears. |

### Group F — session and context mechanics

| Run | Do this | Renderer branch |
| --- | --- | --- |
| F1 | `Use a subagent to summarise what request-logger/render.ts does.` | subagent traffic — likely a **different system prompt and a different tool set** in the same session |
| F2 | Use one of your **MCP tools** (anything from `wmux`) | tool names with an `mcp__` prefix, and MCP-shaped schemas |
| F3 | Enter **plan mode** and ask it to plan something small, then exit | a different tool set again, and possibly a different system prompt |
| F4 | Run `/compact` | compaction produces a distinctly shaped request; also confirms whether `count_tokens` traffic spikes around it |
| F5 | Keep chatting for **five or six more turns** about anything | a genuinely long `<messages>` history — we need to see how a large history renders, not just a two-message one |

**Note in the log:** roughly how many `(housekeeping, not logged)` lines Terminal 1 printed
across the whole session. That ratio is worth quoting in our tutorial.

### Group G — the observer effect, as a controlled experiment

This one is a **measurement**, and it validates the `tool search: OFF` guard we are building.
Do it as a **fresh session**.

| Run | Do this |
| --- | --- |
| G1 | Start Claude Code through the proxy with the **full** printed command (`ANTHROPIC_BASE_URL` **and** `ENABLE_TOOL_SEARCH=true`), send exactly `Hello!`, then exit |
| G2 | Start Claude Code again with **only** `ANTHROPIC_BASE_URL` set — deliberately omit `ENABLE_TOOL_SEARCH` — send exactly `Hello!`, then exit |

Record for both: the `.md` byte size, the number of `###` tool headings in `<tools>`, and
**whether a tool named `ToolSearch` appears at all**.

This gives us three things: our own version of upstream's 63,596-vs-39,013 measurement using
our own numbers in our own docs; a real inflated capture to test the guard against; and
confirmation that "no `ToolSearch` in the tools array" is actually the right signal rather
than my assumption.

### Group H — the empty-folder failure modes

Short, and purely for the tutorial's troubleshooting section. Fresh session each time; just
note what happens, no capture expected.

| Run | Do this | What we learn |
| --- | --- | --- |
| H1 | Start `claude` with **no** environment variables at all, send `Hello!` | Confirms the bypass: does the folder genuinely stay empty, with no error anywhere? |
| H2 | Start Claude Code pointed at the proxy while the proxy is **not running** | The exact error text a developer sees. Our port-in-use and connection-refused messages should be at least this clear. |

---

## 3. Coverage check before you hand it over

Run this in the corpus folder. It tells us whether the corpus actually covers every branch,
without anyone having to read forty files:

```bash
cd <corpus folder>
echo "captures: $(ls *.md | wc -l)"
for marker in tool_use tool_result is_error thinking redacted_thinking \
              '"type":"image"' '"type":"document"' cache_control \
              count_tokens tool_choice stop_sequences; do
  printf '%-24s %s\n' "$marker" "$(grep -l -- "$marker" *.request.txt 2>/dev/null | wc -l)"
done
echo "--- non-200 upstream statuses seen:"
grep -h "upstream status" *.md | sort | uniq -c
echo "--- largest captures:"
ls -S *.md | head -5 | xargs wc -c
```

**Any marker showing `0` is a branch the renderer will be guessing at.** `redacted_thinking`,
`document` and a non-200 status are the three most likely legitimate zeros — the rest should
all be non-zero. If `image` is zero, D2 did not happen, and that is the one I would most want
you to go back and do, because base64 handling changes the writer's design and not just the
renderer's.

---

## 4. Handing it over

Move to `d:/temp/harness-capture-corpus/` (or wherever, outside both repos) and tell me the
path. It should contain:

1. every `.md` / `.request.txt` / `.response.txt` triple, unpruned
2. `RUN_LOG.md` — the run-to-timestamp map, the UTC offset, `claude --version`, the exact
   command the logger printed, and the Group G measurements
3. the Terminal 1 console scrollback, if you were able to save it
4. the coverage-check output from section 3

I will read them, write the format spec in our own words into
`docs/tutorials/HARNESS_CAPTURE.md`, and build synthetic fixtures from it. **The corpus
itself stays out of the repository** — real identifiers, and its exact byte formatting is
arguably the original author's expression. See
[ADR 0008](../../../docs/adr/0008-harness-capture.md).

---

## 5. Quick checklist

- [ ] Working directory is the **course repo**, not `python-template` or a work repo
- [ ] `RUN_LOG.md` started, with UTC offset and `claude --version`
- [ ] Exact printed launch command copied verbatim
- [ ] A1–A2 baseline
- [ ] B1–B6 tool use, including the failing command and the parallel reads
- [ ] C1–C2 thinking, live and in history
- [ ] D1–D2 large result and an **image**
- [ ] E1–E2 interrupted stream, proxy killed mid-turn
- [ ] F1–F5 subagent, MCP, plan mode, `/compact`, long history
- [ ] G1–G2 the observer-effect measurement, fresh sessions
- [ ] H1–H2 the two silent-failure modes
- [ ] Coverage check run, zeros understood
- [ ] Logs moved outside both repositories
