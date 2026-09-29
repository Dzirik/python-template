---
status: verified
labels: [spec, reference]
relates-to: docs/adr/0008-harness-capture.md
derived-from: 77-capture reference corpus, harvested 2026-09-11, since deleted
---

# Capture format specification

The byte-exact rendering rules `capture_renderer.py` must reproduce.

> **Scope: the render only.** Since
> [ADR 0009](../../../docs/adr/0009-harness-capture-raw-record-and-sessions.md) this document
> governs the **render** — the derived, regenerable `.md` layer. The **raw record**
> (`.request.txt`, `.response.txt`, `.exchange.json`) is authoritative; when the two disagree,
> the raw record is right. Renders exist only for `POST /v1/messages`; every other request
> gets a raw record only.

## Provenance and status

Derived from a 77-capture reference corpus harvested on 2026-09-11 (Claude Code v2.1.268,
`claude-sonnet-5`, direct Anthropic API), plus four captures from a 2026-09-24 re-run.

**Derived from observed output only.** No rule here was taken from the course's
`render.ts`; every section below was established by writing a reconstructor and diffing its
output against the corpus. Validation results:

| Section | Reconstruction match |
| --- | --- |
| `<messages>` | **77 / 77** byte-exact |
| `<params>` | **77 / 77** byte-exact |
| `<tools>` | **66 / 66** byte-exact |

That method — reproduce behaviour, diff against behaviour — is the licensing position
recorded in [ADR 0008](../../../docs/adr/0008-harness-capture.md).

**The corpus no longer exists.** It was deleted from `request-logger/logs/` before the
2026-09-24 re-run. This document is therefore the sole record. A gap found during
implementation cannot be resolved by re-reading the corpus; it needs a fresh harvest per
[`EXPERIMENT_ON_MAT.md`](EXPERIMENT_ON_MAT.md).

---

## 1. Document skeleton

The `.md` starts immediately with `<meta>` — no title, no front-matter — and ends with
`</response>` plus exactly one newline. Line endings are **LF**; `CRLF` occurring inside
captured content passes through verbatim, so a capture can be mixed-ending.

Every top-level section uses the identical wrapper:

```python
f"<{tag}>\n\n{body}\n\n</{tag}>"
```

Sections are joined with `"\n\n"`, so exactly one blank line separates them.

Section order, and the three shapes observed across all 77 captures:

| Order | Count |
| --- | --- |
| `meta, headers, request[params, system-prompt, tools, messages], response` | 66 |
| `meta, headers, request[params, system-prompt, messages], response` | 7 |
| `meta, headers, request[params, messages], response` | 4 |

**Absent sections are omitted entirely, never emitted empty.**

- `<system-prompt>` is omitted iff the body has no `system` key.
- `<tools>` is omitted iff `tools` is absent **or is an empty array**.
- `<meta>`, `<headers>`, `<request>`, `<params>`, `<messages>`, `<response>` are always present.

`<request>` is a wrapper following the same convention, containing `<params>`,
optionally `<system-prompt>` and `<tools>`, then `<messages>`.

---

## 2. Filenames

Upstream pattern:

```
<YYYY>-<MM>-<DD>T<HH>-<mm>-<ss>-<mmm>_<agent-slug>.<ext>
2026-09-11T07-23-08-217_claude-code.md
```

The `T` separator stays literal; both `:` and `.` become `-`; the trailing `Z` is dropped.
`ext` is one of `md`, `request.txt`, `response.txt`. UTC, millisecond precision.

**Upstream bug we do not reproduce:** the filename and the `<meta>` timestamp are two
independent clock reads. In 75/77 captures they matched; in 2 they differed by 1–2 ms. We
take **one** `datetime` and derive both, so the filename stem is always exactly the `<meta>`
timestamp.

See [§12](#12-deviations-we-adopt-deliberately) for our filename form:
`<seq:06d>_<utc-timestamp>Z_<endpoint-slug>.<ext>` inside `captures/<session-id>/`.

---

## 3. `<meta>`

Exactly six bullets, always present, always this order, **no blank lines between them**:

```
- **timestamp**: 2026-09-11T07:20:48.290Z
- **agent**: Claude Code
- **wire format**: anthropic
- **model**: claude-sonnet-5
- **endpoint**: POST /v1/messages?beta=true
- **upstream status**: 429
```

Format is literally `- **` + key + `**: ` + value, one space after the colon.

- `model` is the request body's `model`.
- `endpoint` is `METHOD` + space + path-with-query.
- `upstream status` is the bare numeric status.
- The key set **does not vary** — a 429 capture has the same six keys as a 200.

Timestamp value is ISO-8601 UTC, millisecond precision, trailing `Z`:

```python
datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")
```

---

## 4. `<headers>`

Body is a **plain unlabelled fence** (no language tag):

````
<headers>

```
accept: application/json
authorization: [REDACTED]
...
content-length: 313
```

</headers>
````

- Header names **lowercased**.
- **Send order preserved, not sorted.** Observed order is `accept, authorization,
  content-type, user-agent, x-claude-code-session-id, x-stainless-*, anthropic-beta,
  anthropic-dangerous-direct-browser-access, anthropic-version, x-app,
  [x-claude-code-agent-id], connection, host, accept-encoding, content-length` — neither
  alphabetical nor grouped, which proves insertion order.
- Line format: `name` + `: ` + value.
- **Redaction:** upstream redacts exactly one header — `authorization` → the literal
  `[REDACTED]`, 77/77. `x-api-key` and `api-key` are named in its README but never occur in
  the corpus, so they are unexercised rather than handled. See
  [§12](#12-deviations-we-adopt-deliberately).

22 distinct header names seen; 21 in all 77 captures, `x-claude-code-agent-id` in 3.

**Headers are never written to `.request.txt` or `.response.txt`** — those hold only bodies.

---

## 5. `<params>`

Bullets in the `<meta>` format, no blank lines between them.

**A fixed allowlist in a fixed order** — verified by exact reconstruction, 77/77:

```python
PARAM_ORDER = ["max_tokens", "stream", "stop_sequences", "tool_choice", "thinking", "metadata"]
```

Absent keys are skipped. This is provably an allowlist, not "everything except
system/tools/messages": `output_config` (68 captures) and `context_management` (65) are
present in the body and **never rendered**. The emission order also differs from JSON key
order, and `model` goes to `<meta>` instead.

Value rendering:

| Type | Rendering | Example |
| --- | --- | --- |
| number | bare | `- **max_tokens**: 64000` |
| boolean | bare lowercase | `- **stream**: true` |
| object / array | **compact** JSON, no spaces | `- **thinking**: {"type":"adaptive"}` |

i.e. `json.dumps(value, separators=(",", ":"))`. Observed key sets:
`max_tokens|stream|thinking|metadata` ×67, `max_tokens|stop_sequences|thinking|metadata` ×5,
`max_tokens|metadata` ×4, `max_tokens|stream|tool_choice|thinking|metadata` ×1.

> **Privacy note.** The `metadata` bullet renders `user_id` verbatim, exposing `device_id`,
> `account_uuid` and `session_id` in cleartext in every capture. This is deliberate — see
> the redaction reasoning in [ADR 0008](../../../docs/adr/0008-harness-capture.md).

---

## 6. `<system-prompt>`

**Verbatim.** No fence, no escaping, no indentation, no added prose. `system` is always a
list of typed text blocks (never a bare string): 3 blocks in 70 captures, 2 in one, absent
in 4.

The only renderer-added token is the cache marker:

```python
"\n\n".join(
    blk["text"] + ("\n\n<!-- cache_control breakpoint -->" if "cache_control" in blk else "")
    for blk in system_blocks
)
```

The marker is a **suffix appended to each block carrying `cache_control`**, not a separator
between blocks. Marker count equalled the system-block `cache_control` count in 77/77.
Typical is 2; 1 in five captures; 0 in seven.

**Markers are emitted for `system` blocks only.** Never in `<tools>`. Messages *do* carry
`cache_control` in the raw JSON (1 block in 65 captures, 2 in 5) and it is **not** rendered.

The leading `x-anthropic-billing-header: cc_version=...; cc_entrypoint=cli;` line is
**part of the system prompt itself** — it is the full text of `system[0]`, a block the
client sends. It is not an HTTP header and the renderer did not add it.

---

## 7. `<tools>`

The full `input_schema` **is** rendered. Per-tool template, verified 66/66:

```python
s = "### " + tool["name"] + "\n"
if tool.get("description"):
    s += "\n" + tool["description"] + "\n"
if tool.get("input_schema") is not None:
    s += "\n```json\n" + json.dumps(tool["input_schema"], indent=2, ensure_ascii=False) + "\n```"
```

Tools joined with `"\n\n"`. **No `---` rules, no grouping headings.**

- Heading is `###` with the raw tool name, including MCP names (`### mcp__wmux__workspace_list`).
- The description is emitted **verbatim, un-escaped and un-re-levelled** — its own `##`
  headings and code fences land directly in the document, nested under the `###`. Do not
  escape or re-level them; upstream lets the collision happen.
- JSON uses `indent=2`, `ensure_ascii=False`, **source key order preserved** (not sorted).
- Other tool-object keys are **dropped**: `defer_loading` (on 110 tool objects), `type`,
  `max_uses`.
- Degenerate case: a server tool with neither description nor schema renders as `### name`
  plus its trailing newline, producing an extra blank line before `</tools>`.

Tool counts observed: 0 (×2), 1 (×1), 11 (×3), 18 (×38), 19 (×9), 20 (×12), 22 (×3).
1,195 tool objects total; 1,194 are `{name, description, input_schema}`.

**Scale:** in a representative capture `<tools>` was **104,125 of 154,522 bytes — 67.4%**.
The single largest tool was 39,791 bytes, 40% of the whole tools array.

---

## 8. `<messages>`

```python
section = "<messages>\n\n" + "\n\n".join(rendered) + "\n\n</messages>"
message = f'<message index="{i}" role="{role}">\n\n{body}\n\n</message>'
```

- `index` counts **messages**, 1-based, contiguous, never restarting. A message with nine
  content blocks still consumes one index.
- Roles observed, exactly three: `user` (1045), `system` (997), `assistant` (968). The
  `system` role here is a mid-conversation system message inside the `messages` array — the
  top-level system prompt is rendered separately as `<system-prompt>`.
- Body: string content is emitted as-is; array content is `"\n\n".join(render_block(b))`.
  **There is no visible difference** between `content: "x"` and `[{"type":"text","text":"x"}]`.
- Block text is emitted **untrimmed**, so a block ending in `\n` produces a doubled blank
  line. Do not strip.
- No escaping, no entity encoding, no added indentation — content containing `<message>`-like
  or fence-like markup passes straight through.

### Block renderings

**`text`** — the raw string.

**`thinking`**

```python
f"<thinking>\n\n{b.get('thinking', '')}\n\n</thinking>"
```

`signature` is **never** rendered. In the corpus all 224 thinking blocks had
`thinking: ""` (the `redact-thinking-2026-02-12` beta), so every instance is the degenerate
open-tag / three-blank-lines / close-tag form. **Emit the tag on block presence, not on
non-empty content**, and do not collapse the blanks.

**`tool_use`**

````python
f'<tool-use name="{b["name"]}" id="{b["id"]}">\n\n'
f'```json\n{json.dumps(b["input"], indent=2, ensure_ascii=False)}\n```\n\n</tool-use>'
````

The block `id` **is** shown. Sibling fields (`caller`, `cache_control`) are dropped. Key
order preserved. Empty input renders as `{}`.

**`tool_result`**

```python
f'<tool-result tool-use-id="{b["tool_use_id"]}" is-error="{err}">\n\n{body}\n\n</tool-result>'
```

- `is-error` is **always emitted**, defaulting to `"false"` (295 of 483 blocks omit
  `is_error` on the wire).
- String content is emitted **raw and unfenced** — no code fence, no indent.
- List content: elements joined `"\n\n"`; a `text` element yields its text, an `image`
  element yields the image placeholder, **anything else yields the whole element as a
  ```json fence**.
- An `is_error: true` result differs **only** by the attribute value. No prefix, no marker,
  no styling.

**`image`** — base64 is fully replaced by a single line of inline code:

```
`[image: image/jpeg, 490308 base64 chars — full data in .request.txt]`
```

```python
src = b["source"]
label = src.get("media_type") or src.get("type") or "unknown"
f"`[image: {label}, {len(src.get('data', ''))} base64 chars — full data in .request.txt]`"
```

The dash is **U+2014 EM DASH**, one space either side. The number is the **character length
of the base64 string**, not decoded bytes. MCP inline data uses the sibling form
`` `[inline data: <mimeType>, <N> base64 chars — full data in .request.txt]` ``.

**Unknown block type** — the whole block as a ```json fence.

### Parallel tool calls

Several `tool_use` blocks in one assistant turn produce **one `<message>` with sibling
`<tool-use>` elements**, blank-line separated; the matching results likewise sit in one user
`<message>`. Results arrive in **completion order, not call order** — preserve array order,
do not re-sort.

### Truncation

**There is none.** All 2,772 text and string-valued `tool_result` strings appear
byte-verbatim; largest `tool_result` 32,911 chars and largest text block 104,077 chars both
rendered in full. No threshold, no ellipsis, no marker. **The image placeholder is the only
lossy transformation in the entire section.**

---

## 9. `<response>`

**The branch is streamed-vs-not, not success-vs-error.**

| Upstream | Count | Rendering |
| --- | --- | --- |
| SSE | 68 | bullets + block tags |
| non-streamed 200 | 5 | one pretty ```json fence |
| error (429) | 4 | one pretty ```json fence |

### Streamed

```
<response>

- **stop reason**: end_turn

- **usage**: {...single line of raw JSON...}



<assistant-text>

Hi! What would you like to work on?

</assistant-text>

</response>
```

- Two bullets, this order, key is the two-word lowercase **`stop reason`** (not
  `stop_reason`). Separated by **one blank line** — they are not a tight list.
- `usage` is compact single-line JSON taken from the **`message_delta`** event, not
  `message_start`. It therefore has no `service_tier` / `inference_geo`, but does carry
  `output_tokens` and `iterations`.
- **Both bullets come solely from `message_delta`. If no `message_delta` arrived, omit both.**
- **Exactly three blank lines** between the last bullet and the first content block.
- Content blocks in stream order, each wrapped `TAG\n\n...\n\n/TAG`, separated by exactly one
  blank line, then one blank line before `</response>`.

Block tags in `<response>`: `<thinking>`, `<assistant-text>`, `<tool-use name="..." id="...">`.

- `<assistant-text>` content is the **verbatim concatenation of `text_delta` fragments** — no
  escaping, re-wrapping or trimming.
- **One tag per content block, not one per response.** A 13-text-block response emits 13
  consecutive `<assistant-text>` blocks, some containing only a fragment. No tag at all when
  the response has no text block.
- **`server_tool_use` and `web_search_tool_result` blocks are silently dropped**, along with
  citations. A reader cannot tell a web search happened except from `usage`.

> **Critical asymmetry.** `tool_use` JSON renders **differently in the two sections**:
> `<messages>` re-serializes with `indent=2`; `<response>` emits the **verbatim
> concatenation of `input_json_delta.partial_json` fragments on one line**, preserving the
> model's own serialization (hence `": "` spacing and `\\` escapes). Empty accumulation
> renders `{}`. These are two code paths, not one shared helper.

### Non-streamed (both 200 and error)

````
<response>

```json
{
  "type": "error",
  "error": {
    "type": "rate_limit_error",
    "message": "Error"
  },
  "request_id": "req_..."
}
```

</response>
````

`json.dumps(body, indent=2)`, wire key order. **No bullets, no `<assistant-text>`, no
`stop reason`, no `usage`.** For an error, the only structural record of failure is
`- **upstream status**` in `<meta>`.

The five non-streamed 200s are Claude Code's auto-mode safety classifier (`max_tokens: 64`,
`stop_sequences: ["</severity>"]`, no tools) — they render identically to the errors.

### Usage fields

```
input_tokens, cache_creation_input_tokens, cache_read_input_tokens, output_tokens,
output_tokens_details.thinking_tokens,
iterations[]: input_tokens, output_tokens, cache_read_input_tokens,
              cache_creation_input_tokens, type,
              cache_creation.{ephemeral_5m_input_tokens, ephemeral_1h_input_tokens}
```

Real values from the corpus:

| Point in session | `cache_creation` | `cache_read` |
| --- | --- | --- |
| first request | 51,287 | 0 |
| later request | 1,357 | 89,951 |

`input_tokens` is almost always **2** — essentially everything is cached.
`thinking_tokens` was non-zero in 18 captures, maximum 370.

---

## 10. The two `.txt` files

**`.request.txt` — the received body bytes, untouched.** Single-line minified JSON, zero
newlines. `content-length` matched file size in **77/77**, which is conclusive proof it is
byte-identical to the wire payload. Sizes 313 B – 756,751 B. The request body is never
compressed (`accept-encoding` is response negotiation).

**`.response.txt` — the decoded upstream stream, untouched.** SSE verbatim: `event:` and
`data:` lines and the blank line between events all preserved, including trailing spaces
inside `data:` lines — **do not strip**. Written decompressed. 68 of 77 are SSE; the other 9
are plain JSON (5 non-streamed 200s + 4 errors). Sizes 114 B – 233,914 B.

**Neither file ever contains headers**, and therefore never a credential — independently
verified by grepping all 154 files for `authorization`, `x-api-key`, `Bearer`, `sk-ant`:
every hit was prose inside captured message content, no live secret.

**`.exchange.json` — the third raw file (ours; upstream has no equivalent).** Holds
everything the two bodies do not: the per-session sequence number, `x-claude-code-session-id`
and `x-claude-code-agent-id` (if present), method and path-with-query, upstream status,
request and response headers in send order with credentials redacted (`authorization`,
`x-api-key`, `api-key`, `cookie`, `set-cookie` → `[REDACTED]`), start and end timestamps,
the response `content-encoding` as received, and whether the client disconnected before the
stream ended. Headers live **only** here, so the property above still holds: the two `.txt`
files never contain headers.

---

## 11. Capture sizes

| Turn kind | `.md` | `.request.txt` | `.response.txt` | Triple |
| --- | --- | --- | --- | --- |
| text | 213,614 | 211,289 | 2,513 | **~430 KB** |
| image | 214,338 | **702,176** | 5,223 | **~920 KB** |

An image inflates `.request.txt` by +490,887 bytes (3.3×) while `.md` grows only +0.3% —
the placeholder does its job. The image stays in conversation history, so **every
subsequent request in the session pays the same cost** in `.request.txt`.

One user turn produced **1–15 captures** (4–9 typical). Subagent calls are distinguishable by
`ephemeral_5m_input_tokens` versus the main agent's `ephemeral_1h_input_tokens`.

---

## 12. Deviations we adopt deliberately

Everything above is upstream's behaviour. These are the only places we differ:

| # | Deviation | Why |
| --- | --- | --- |
| 1 | **One clock read** for filename and `<meta>` timestamp | Upstream drifts 1–2 ms in 2/77; the stem should be a reliable key |
| 2 | Filename `<seq:06d>_<utc-timestamp>Z_<endpoint-slug>.<ext>` inside `captures/<session-id>/`, instead of `<timestamp>_claude-code` | The agent is constant in our scope; the endpoint discriminates; the zero-padded sequence number sorts in arrival order, which timestamps cannot guarantee for concurrent requests ([ADR 0009](../../../docs/adr/0009-harness-capture-raw-record-and-sessions.md)) |
| 3 | Redact **`x-api-key`** and **`api-key`** as well as `authorization` | A safe superset; unexercised upstream rather than handled |
| 4 | Two extra `<meta>` bullets: section sizes and total | The quantitative form of the lesson. Confined to `<meta>` so every taught section keeps its shape |
| 5 | One extra `<meta>` bullet: `- **tools**: N (ToolSearch present)` | Factual only. **Not** a judgement — see below |
| 6 | Three extra `<meta>` bullets: `session` (the `x-claude-code-session-id` value), `agent` (the raw `x-claude-code-agent-id` value, or `(none)`), `seq` (the per-session sequence number) | The only place a reader of one `.md` sees where the request sits in its session. `agent` is **never** `main`: prompt-suggestion, title and safety-classifier calls also carry no agent id, so "no agent id" does not mean "the main conversation". Confined to `<meta>` |

**On deviation 5.** The PRD originally specified a `tool search: OFF` warning. Two attempts
to produce a tool-search-off capture (2026-09-11 and 2026-09-24) both failed: the captures
were byte-identical, and `cache_read_input_tokens` in the second arm exactly matched
`cache_creation_input_tokens` in the first, proving the prefixes were identical since prompt
caching is prefix-exact. We therefore have **no evidence the observer effect still exists in
Claude Code v2.1.268+, and no capture of the off-state**. Shipping a detector for a condition
we have never observed would put an unfalsified claim inside a file whose whole purpose is
being trustworthy. We state the observable facts and let the reader judge.

---

## 13. Unverified branches

Not exercised by the corpus. Implement defensively, do not claim fidelity:

- **`redacted_thinking`** — does not occur. (An earlier grep reported two hits; both were the
  phrase as prose inside a loaded skill document.) Expected to fall through to the JSON-fence
  default, unverified.
- **`document` content blocks** — never sent.
- **`image_url`** (OpenAI-style) — not applicable to the Anthropic wire format.
- **Empty content arrays**, and a `tool_result` list element whose text is the empty string —
  upstream's truthiness check sends the latter to a JSON fence rather than emitting an empty
  string. Reproduce only if bit-exactness matters.
- **A genuinely truncated stream** — the one interrupted capture in the corpus was *complete*,
  because the proxy keeps consuming upstream after the client disconnects and upstream closed
  the message normally. A stream that really dies before `message_delta` was never observed;
  the rule is to omit both bullets.
- **Non-`claude-sonnet-5` models**, and any status other than 200/429.
