# Prompt message deduplication for llama-server

This fork of [llama.cpp](https://github.com/ggml-org/llama.cpp) adds an opt-in pass to `llama-server`. It shortens the prompt when a chat request contains the same large message more than once. Agent clients such as coding agents send the whole conversation on every turn, and that conversation often repeats: the same file is read three times, the same linter output comes back after each edit, a long reminder is re-sent before every user turn. Each copy costs prefill time and context space, yet the model already has the first copy in front of it.

The pass keeps the first copy of a repeated message in full. Each later copy that is byte-for-byte identical, from the same role, is replaced by a short reference to that first copy. Nothing else in the request changes.

## What it does

A message unit is a message's text content, or one text part of a multi-part message. The pass considers only units that:

- come from a participating role (`tool` by default; `user` and `system` can be added),
- are at least `min_bytes` long (1024 by default), and
- repeat an earlier unit of the same role byte for byte.

Such a repeat is rendered as a stub like this:

```
[duplicate content omitted: byte-identical to tool result #1 (read_file), which begins "def apply_surcharge(subtotal):\n    su..."; unchanged since then]
```

The stub names the role, the 1-based position of the first copy among that role's messages, the tool name when it is safe to print, and a short excerpt, so the model can locate the earlier copy.

Properties the pass guarantees, each backed by tests:

- **Nothing is lost.** The first copy is always rendered in full. Only exact repeats are replaced. Near-duplicates, such as one byte different, CRLF against LF, or NFC against NFD, are left alone. Assistant messages and non-text parts (images, audio) are never touched.
- **Stateless and deterministic.** Each request is processed on its own. No index, cache or statistic survives the request, and the output does not depend on slot state, time, hash seed or iteration order.
- **Prompt-cache friendly.** Appending a turn never changes the rendering of earlier turns, so the server's prompt cache keeps hitting from turn to turn.
- **Safe with the model's special tokens.** Stubs never contain the served vocabulary's control or special-token text. Tool names and excerpts are escaped, so a stub cannot open a fake role boundary.
- **Off by default.** With the pass off, the rendered prompt is byte-identical to upstream llama.cpp.

This works on the prompt text. It is not a KV-cache change and needs no model support. It fits hybrid and recurrent models such as Qwen3.5/3.6, where partial KV reuse is impossible, because the rewritten prompt is still an ordinary prompt.

## How to use it

Server flags (with environment variables):

| Flag | Env | Default | Meaning |
|---|---|---|---|
| `--message-dedup` / `--no-message-dedup` | `LLAMA_ARG_MESSAGE_DEDUP` | off | enable the pass for every request |
| `--message-dedup-min-bytes N` | `LLAMA_ARG_MESSAGE_DEDUP_MIN_BYTES` | 1024 | smallest unit, in UTF-8 bytes, that takes part |
| `--message-dedup-roles LIST` | | `tool` | comma-separated roles from `tool,user,system` |

A request can override the server defaults on any JSON chat endpoint: `/v1/chat/completions`, `/chat/completions`, `/v1/responses`, `/v1/messages`, their count-tokens routes, and `/apply-template`.

```json
{
  "messages": [ ... ],
  "message_dedup": { "enabled": true, "min_bytes": 512, "roles": ["tool", "user"] }
}
```

A malformed override is rejected with HTTP 400. The error never echoes the value the client sent.

When the pass runs, the response `timings` object reports what it did:

- `dedup_n`: units replaced by a stub
- `dedup_bytes_saved`: bytes removed from the rendered prompt
- `dedup_tokens_saved_est`: estimated prompt tokens saved

Anthropic `/v1/messages` and non-streaming Responses have no `timings` object, so they report nothing.

## How it is built

- `tools/server/server-message-dedup.{h,cpp}` holds the pass: settings resolution, the unit index (SipHash-2-4 keyed per process, with byte-exact confirmation), stub construction, and the statistics.
- The chat parser (`oaicompat_chat_params_parse` in `tools/server/server-common.cpp`) runs the pass after the request is converted and before the template is applied. It is the one place every JSON chat endpoint goes through.
- The special-text check is built once from the loaded model's vocabulary at startup.
- Statistics travel from the parser to the slot's `timings` through a server-written channel, so a client cannot forge them.

Code comments cite `SPEC-0001` sections. That is the internal design specification the work was built from; it is not part of this repository.

## How it was tested

Development was test-first: each behaviour got a failing test before the code. The tests live under `tools/server/tests/`.

### Conformance tests

- `tests/test-server-message-dedup.cpp` (ctest) covers the stub grammar, the matching rules, the special-text predicate built from a real vocabulary, and the token-estimate rounding.
- `unit/test_message_dedup*.py` (299 tests, run against a real server) covers:
  - matching and stubs over HTTP: the length rule, same-role references, near-duplicates left alone, and tool-name escaping;
  - every JSON endpoint, including count-tokens;
  - the prompt cache: stable prefixes on append, and the effect of enabling the pass mid-conversation;
  - the `timings` statistics, including multimodal requests;
  - hardening: malformed overrides never cause a 500 or echo client values, and no message content reaches the logs;
  - non-text parts left untouched, and special-token detection on a second model vocabulary.

### Cost and cache gates on the target model

These ran on Qwen3.x 27B Q4_K_M, Vulkan, RX 7900 XTX, production settings.

| Check | Result |
|---|---|
| Pass cost, pass on (41-turn, 108k-token transcript) | 0.99 ms summed over all turns; worst turn 0.114 ms |
| Cost with the pass off vs an unmodified build | no measurable difference: mean −0.075 ms per turn, 8 balanced runs |
| Pass off vs an unmodified build | rendered prompt, token counts and `timings` keys byte-identical on all 15 scenarios |
| Prompt cache on the 41-turn replay | prompt tokens processed fell from 107,771 to 71,271; no turn processed more than with the pass off |

### Quality: the agentic scenario suite

The quality question is whether the model does its job as well when repeats are replaced by stubs. A suite of 15 synthetic agent scenarios measures this. Each scenario has a scripted conversation prefix with real repeats: repeated file reads, linter runs, reminders, and lookalike text designed to trip the pass. A live model tail follows, with simulated tools (read, grep, edit, run tests, lint, fetch). Model-written code runs inside a bubblewrap sandbox.

Every scenario runs on two arms, pass off and pass on, with two runs each: one greedy and one seeded. The model gets 12 turns. A deterministic checker judges each run: an exact answer, a diff, the tests passing, or a required tool-call sequence.

A scenario counts as a pass only if both runs on the pass-off arm pass and both runs on the pass-on arm pass. The adversarial scenarios also check that the stub cannot be used to smuggle in instructions (R1–R3) and that rules repeated in the prompt are still followed (B1, R3).

Final run: all 15 scenarios pass on both arms, 60 of 60 runs. Prompt tokens are for the whole prefix with the pass off and on:

| Scenario | What it exercises | Stubs | Prompt tokens, off → on |
|---|---|---:|---|
| A1 | fix a bug after re-reading a file (~4k deep) | 1 | 5,919 → 5,315 |
| A2 | answer from a file read ~32k tokens earlier | 1 | 41,112 → 36,350 |
| A3 | answer from a file read ~96k tokens earlier | 1 | 127,367 → 108,460 |
| A4 | same flow through the Anthropic `/v1/messages` API | 4 | 18,092 → 6,820 |
| A5 | re-read after an edit (a near-duplicate, must not fire) | 0 | 5,531 → 5,531 |
| B1 | a rule re-sent 8 times; the answer must obey it | 7 | 9,843 → 6,301 |
| B2 | repeated reminders, long conversation | 7 | 9,594 → 6,003 |
| B3 | embedded repeated block, widest role set | 0 | 10,094 → 10,094 |
| B4 | fix code with repeated linter output | 5 | 7,481 → 4,221 |
| M1 | 41-turn coding session, 4 tools, 108k tokens | 10 | 108,197 → 71,697 |
| M2 | pass enabled mid-conversation at turn 8 | 6 | 23,086 → 9,928 |
| M3 | nothing repeats (must be a no-op) | 0 | 20,843 → 20,843 |
| R1 | injected instructions in a fetched page | 2 | 5,517 → 3,379 |
| R2 | stale copy vs edited value (must answer the new one) | 1 | 4,631 → 3,162 |
| R3 | injected instructions plus a rule to obey | 1 | 4,348 → 4,049 |

Static checks run against the same scenarios on the served template. Every listed unit renders. The first copy of every repeat is present. The pass-on render equals the pass-off render of the prompt with the stubs substituted by hand. Nothing fires where it must not.

### What the evidence does and does not show

- It shows that on these 15 agent workloads the pass removes up to 62% of the prompt, and the model still completes every task on both greedy and seeded decoding.
- It is 2 runs per arm per scenario, not a statistical study. It can rule out breakage of these use cases, but not a small change in success rates.
- The first full run failed 4 scenarios. Three (A1, B3, R2) also failed with the pass off, so they were scenario defects and were fixed in the scenario data. One (A4) came from a checker that was stricter than the specification. The fixes were reviewed and recorded, and the pass criteria were not loosened; the one relaxed check (A4) still fails any re-read of the stubbed file. Still, the green result comes from a suite corrected after seeing results.
- It was measured on one model family (Qwen3.x) and one GPU. Other models may react to stubs differently.
- Only exact repeats are handled. Large content that is merely similar is out of scope.

## Running the tests

```sh
# C++ unit tests
ctest --test-dir build -R test-server-message-dedup

# server conformance tests (needs a built llama-server)
cd tools/server/tests
LLAMA_SERVER_BIN_PATH=../../../build/bin/llama-server python -m pytest unit/test_message_dedup*.py

# scenario suite: offline checks
python -m pytest eval/message_dedup/tests/ -k "not server"

# scenario suite: full run against a model (needs bubblewrap for the tool sandbox)
LLAMA_DEDUP_SUITE_GGUF=/path/to/model.gguf python eval/message_dedup/gate_suite_qwen35.py --help
```

The scenarios are regenerated deterministically by `eval/message_dedup/gen_scenarios.py` (`--check` reports drift). All scenario data is synthetic.
