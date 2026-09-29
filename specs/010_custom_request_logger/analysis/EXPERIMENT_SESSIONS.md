# Experiment: how Claude Code identifies a Harness Session on the wire

**Purpose.** The redesigned Harness Capture stores its raw records per **Harness Session**
(see [`../../../CONTEXT.md`](../../../CONTEXT.md)), keyed by the `x-claude-code-session-id` request
header, with subagents told apart by `x-claude-code-agent-id`. That layout rests on
assumptions nobody has observed yet. This experiment checks them **before** any code is
written, using the course's request logger — its `.md` already shows `<headers>`, so none of
our implementation is needed.

**What we are learning.** Only header *values* and how they change across session events.
Not the render format — that is settled in [`CAPTURE_FORMAT_SPEC.md`](CAPTURE_FORMAT_SPEC.md).

| # | Assumption | If it is false |
| --- | --- | --- |
| A1 | `/clear` issues a **new** session id | the layout still works, but "one folder per `/clear`" is wrong and the tutorial must say so |
| A2 | `--continue` / `--resume` — reuse the old id, or issue a new one? | no design change; tutorial wording only |
| A3 | subagents **share** the parent's session id and add `x-claude-code-agent-id` | **design change** — subagent traffic lands in its own folder and needs parent linking |
| A4 | `/compact` keeps the session id | the layout splits a session at every compaction; tutorial and analysis must handle it |
| A5 | two concurrent sessions through **one** proxy get different ids and do not interfere | **design change** — one-proxy-for-all is unsound |
| A6 | non-conversation calls (the auto-mode safety classifier) carry the session id | **design change** — they would land in `_unattributed/` and the timeline would have holes |

A6 is only partly checkable here: the course logger writes classifier calls (non-streamed
200s) but **not** `count_tokens` calls, which it prints as `(housekeeping, not logged)`. Whether
`count_tokens` carries the session id stays open until our own proxy runs; note it as such.

---

## 0. Before you start

- **Working directory: the course repository** (`d:/courses/mai/ai-coding-crash-course`), for
  the same reason as [`EXPERIMENT_ON_MAT.md`](EXPERIMENT_ON_MAT.md) §0 — captures contain
  whatever the agent reads.
- **Clear `request-logger/logs/` first.** This time a clean folder is what we want: every
  file in it should belong to this experiment.
- Keep a scratch file **`RUN_LOG_03.md`** (outside both repositories until the end), one line
  per run, local time is fine:

  ```
  S03 | 14:22:07 | T2 | asked for a subagent | expect: agent-id appears, same session id
  ```

  At the top record: `claude --version`, your UTC offset, and the exact launch command the
  logger printed.
- You will not hand over the captures themselves — only the table from §3 and your run log.
  The captures hold `account_uuid`, `device_id` and session ids; delete them when done.

---

## 1. Setup

```
Terminal 1 (course repo):  npm run request-logger
Terminal 2 (course repo):  <the exact command Terminal 1 printed>
Terminal 3 (course repo):  (used only in Group P, later)
```

Keep Terminal 1 visible; copy its scrollback into `RUN_LOG_03.md` at the end — the
`(housekeeping, not logged)` lines are the only record of `count_tokens` traffic.

---

## 2. The runs

### Group S — one session through its lifecycle (Terminal 2)

Run in order, in the **same** Claude Code process unless a row says otherwise.

| Run | Do this | Checks |
| --- | --- | --- |
| S1 | `Hello!` | baseline id |
| S2 | `What is 2 + 2?` | id is stable across turns |
| S3 | `Run: git status` | a tool call; in auto mode this is also the most likely trigger for a **safety-classifier** call (A6) |
| S4 | `Use a subagent to list the files in request-logger/ and report how many there are.` | **A3** — subagent requests |
| S5 | `/compact`, then `Hello again.` | **A4** — the compaction request and the turn after it |
| S6 | `/clear`, then `Hello!` | **A1** |
| S7 | Exit Claude Code (`/exit`). Relaunch with the printed command **plus `--continue`**, send `Hello!` | **A2** — continue |
| S8 | Exit again. Relaunch with the printed command **plus `--resume`**, pick the **pre-`/clear`** conversation (the one from S1–S5), send `Hello!` | **A2** — resume of an older conversation |

For S7 and S8, keep every environment variable from the printed command and append the flag
at the end. In PowerShell that means the same `$env:...` lines, then `claude --continue`.

### Group P — two sessions at once (Terminals 2 and 3)

| Run | Do this | Checks |
| --- | --- | --- |
| P1 | Start a **fresh** session in Terminal 2 (printed command, no flags). Ask something that takes a while: `Read every file in request-logger/ and summarise each in one line.` | — |
| P2 | **While P1 is still working**, start a fresh session in Terminal 3 with the same printed command and send `Hello!` | **A5** — distinct ids, both sessions complete normally, no errors in either terminal |

Note in the log whether either session misbehaved (hang, error, garbled output) during P2.

---

## 3. Extract the table

Run from the course repo root in Git Bash. It prints one row per capture, in filename
(= time) order, with only the fields this experiment needs:

```bash
cd request-logger/logs
printf '%-28s %-8s %-4s %-10s %-10s %-9s %s\n' FILE STATUS MAXT SESSION AGENT META_SID STREAM
for f in *.md; do
  sid=$(grep -m1 '^x-claude-code-session-id:' "$f" | cut -d' ' -f2)
  aid=$(grep -m1 '^x-claude-code-agent-id:'  "$f" | cut -d' ' -f2)
  st=$(grep -m1 'upstream status' "$f" | sed 's/.*: //')
  mt=$(grep -m1 '^- \*\*max_tokens\*\*' "$f" | sed 's/.*: //')
  msid=$(grep -m1 '^- \*\*metadata\*\*' "$f" | grep -o 'session_id[^,}]*' | grep -o '[0-9a-f]\{8\}-' | head -1)
  strm=$(grep -q '^- \*\*stream\*\*: true' "$f" && echo yes || echo no)
  printf '%-28s %-8s %-4s %-10s %-10s %-9s %s\n' \
    "${f%_claude-code.md}" "$st" "$mt" "${sid:0:8}" "${aid:0:8}" "${msid%-}" "$strm"
done
echo "--- distinct session ids:"
grep -h '^x-claude-code-session-id:' *.md | sort | uniq -c
echo "--- distinct agent ids:"
grep -h '^x-claude-code-agent-id:' *.md | sort | uniq -c
echo "--- captures with NO session-id header:"
grep -L '^x-claude-code-session-id:' *.md
```

Columns: `SESSION` / `AGENT` are the first 8 characters of each header (blank = header
absent); `META_SID` is the first block of the `session_id` inside `metadata.user_id`, to see
whether it agrees with the header; `MAXT` + `STREAM` identify classifier calls
(`max_tokens` 64, not streamed).

Only the id **prefixes** leave your machine. If even that is too much, replace each distinct
prefix with a letter (`A`, `B`, …) before pasting — equality is all we need.

---

## 4. Hand over

Paste into this conversation (or save as `/RUN_LOG_03.md`):

1. `RUN_LOG_03.md` — run-to-time map, `claude --version`, UTC offset, the printed command
2. the §3 table output
3. Terminal 1 scrollback (for `count_tokens` counts)
4. anything odd from Group P

Then delete `request-logger/logs/`.

---

## 5. Checklist

- [ ] Course repo as working directory; `request-logger/logs/` empty at the start
- [ ] `RUN_LOG_03.md` started with version, UTC offset, printed command
- [ ] S1–S3 baseline, stable id, tool call
- [ ] S4 subagent
- [ ] S5 `/compact`
- [ ] S6 `/clear`
- [ ] S7 `--continue`, S8 `--resume` of the pre-clear conversation
- [ ] P1–P2 two concurrent sessions
- [ ] §3 table extracted, Terminal 1 scrollback saved
- [ ] Captures deleted
