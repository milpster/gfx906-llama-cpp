# PROVENANCE: SPEC-0001 pass-off golden fixtures

These goldens record what `llama-server` renders and reports when it has
**no** message-dedup feature. `docs/graph/specs/SPEC-0001-server-message-dedup.md`
§8 and §10 define them. They are the oracle for the off-state contracts
(`DEDUP_OFF_*`, AC_F01) and the pass-off reference for
`DEDUP_FIRST_OCCURRENCE_UNCHANGED` and `DEDUP_EQUIVALENT_TO_MANUAL_SUBSTITUTION`.

## Captured from

- Source commit: `c89e014cc`. `llama-server --version` prints
  `version: 0.4.1-dev (build 11114, commit c89e014cc)`. The checkout at capture
  time was `8cbfd3492`, and `git diff c89e014cc 8cbfd3492 -- . ':!docs'` is empty,
  so the source was feature-free.
- Build: the plan prescribes
  `ROCM_PATH=/opt/rocm/core TQ_LLAMA_BUILD_TARGETS="llama-server" scripts/owner/build_llama_cpp.sh`.
  That build step was skipped. The capture reused the earlier owner-script build
  from the same session: targets `llama-server test-arg-parser` at `c89e014cc`,
  built with `ROCM_PATH=/opt/rocm/core`. It is equivalent to a clean build,
  because HEAD had no non-docs diff from `c89e014cc`. The binary is
  `build-hip-vulkan/bin/llama-server`.
- Captured on 2026-09-23 with the GPUs hidden (SPEC-0001 gate env,
  `docs/graph/plans/grill.md` §10):
  `HIP_VISIBLE_DEVICES=-1 GGML_VK_VISIBLE_DEVICES= LLAMA_ARG_DEVICE=none PORT=18080 LLAMA_SERVER_BIN_PATH=$PWD/build-hip-vulkan/bin/llama-server`
- Models (HF cache snapshots under `tools/server/tests/tmp`):
  `ggml-org/test-model-stories260K` @ `479896ec924af6d40fd419ab8f4d1eb2101de00d`, and
  `ggml-org/tinygemma3-GGUF:Q8_0` @ `c287502cd9e278dac8eed805c112cce5d0081e0b`.
  The rendered prompt depends on the template, not on the weights.
- The server configurations are in `SERVER_CONFIGS` in `dedup_goldens.py`:
  tinyllama2 + `--jinja --chat-template chatml`; tinyllama2 +
  `--jinja --chat-template-file models/templates/Qwen3.5-4B.jinja`; and tinygemma3 +
  `--jinja --chat-template chatml` with `LLAMA_MEDIA_MARKER=<__media__>`.
  Media markers are otherwise random per process.

## Contents

- `manifest.json`: fixture name → server config key and the contracts it serves.
- `requests/<name>.request.json`: the exact body POSTed to `/apply-template`.
- `goldens/<name>.prompt.json`: `{"prompt": ...}`, the returned prompt. It is
  stored as JSON with ASCII escapes so that editors and `.editorconfig`
  (trailing whitespace, final newline, LF) cannot change a golden byte.
  CRLF and NFD fixtures depend on this.
- `timings_request.json` / `timings_keys.json`: a pass-off chat request with
  about 400-byte units (it fits tinyllama2's 2048-token slot), and the
  `timings` key set it returns, non-streaming and streaming. These equal the
  §8.4 set.
- `dedup_goldens.py`: the fixture definitions, the loader the tests use, and
  the capture and check procedure.

All content is synthetic text written in `dedup_goldens.py`. The image is a
16x16 gradient PNG that the code generates. No production data is used.

## Re-capture procedure (for example after an upstream sync)

Capture only from a build **without** the feature, meaning the feature-free
parent of the SPEC-0001 GREEN commits:

```sh
# repo root, SPEC-0001 gate env exported, feature-free binary built as above
cd tools/server/tests
../../../.venv/bin/python fixtures/message_dedup/dedup_goldens.py write   # rewrites requests, goldens, timings keys
../../../.venv/bin/python fixtures/message_dedup/dedup_goldens.py check   # fresh processes; must print "all ok"
```

Then update the commit and build lines above.

## Observations at capture (pass-off, chatml)

- chatml renders neither `tool_calls` nor `tools`. The goldens for
  `s8_1_reread_file`, `s8_4_off_override`, `tool_repeat_with_tools`,
  `truncated_history` and every `toolname_*` case with tool-call names are
  therefore byte-identical, and so are `toolname_msgname_ok` and
  `toolname_msgname_bad`. The tool name can show up only inside a stub
  (spec §10, harness constraints).
- `s8_5_escaping` and `s8_5_noname_variant` are identical for the same reason.
- `s8_4_off_override` (with `message_dedup: {enabled: false}`) equals
  `s8_1_reread_file`. The build ignores the field (spec §10, "Override field").
