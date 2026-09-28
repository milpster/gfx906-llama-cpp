# 2026-09-29 - Prompt message dedup adoption

Goal: adopt the opt-in prompt message deduplication pass from `llopresto87/llama.cpp-prompt-dedup` into this gfx906 fork, preserve the existing prompt-lookup worktree changes, document the source version, and validate without touching the running production server.

## Source

- Repository: https://github.com/llopresto87/llama.cpp-prompt-dedup
- Adopted implementation commit: `02957b773` (`server: add prompt message deduplication (opt-in)`).
- Shared base with this fork: `4098fdc922460470caa12659249e55f77c06730f`.
- Upstream documentation: `README_DEDUPLICATION.md` from the source repository.
- The source commit also carries its C++ conformance test, HTTP tests, synthetic scenarios, fixtures, and evaluation harness.

## Behavior adopted

- The pass is off by default.
- `--message-dedup` enables exact, same-role deduplication for large repeated message units.
- `--message-dedup-min-bytes` defaults to 1024 bytes.
- `--message-dedup-roles` defaults to `tool`; allowed roles are `tool`, `user`, and `system`.
- A request may override defaults through `message_dedup` on JSON chat endpoints.
- The first copy stays intact. Later byte-identical copies become short references.
- Assistant messages and non-text media parts are not deduplicated.
- Dedup statistics are written by the server and reported through completion timings.
- Disabled behavior is intended to leave rendered prompts unchanged.

## Integration

- Applied commit `02957b773` without creating the original commit, so fork-local documentation and validation could be added before the final local commit.
- One merge conflict occurred in `tools/server/server-context.cpp`. It was only the `handle_completions_impl()` signature: this fork had changed indentation while the source added `const std::optional<dedup_stats> & dedup`. The resolution kept the fork indentation and added the parameter.
- The other integration points merged automatically: server chat parameters, request parsing, route plumbing, task and slot statistics, CLI arguments, preset handling, CMake registration, and tests.
- Existing user work remained unstaged and was restored after applying the port. In particular, prompt-lookup changes in `common/arg.cpp` and `common/common.h` remain separate from the staged dedup hunks.
- The source repository's `AGENTS.md` fork marker was not retained because it described that repository rather than this gfx906 fork.
- `git diff --check` reports the source fixture `tools/server/tests/eval/message_dedup/tests/fixtures/snapshots/mini-snapshot-0001/story.txt` because its only line ends with a space. The byte is present in commit `02957b773` and was preserved because this is exact-content test data.
- The fork header in `README.md` now records the feature, source commit, flags, detailed documentation link, adoption date, and the distinction between source versions and retained production binaries.

## Build gate

Command:

```sh
BUILD_DIR=/home/srcds/dev/uf3_rocm6.1_llama.cpp/build-dedup FRESH=1 JOBS=16 TARGETS="llama-server test-server-message-dedup test-arg-parser" ./build-dflash-novega.sh
```

Result: pass.

- Fresh release build in `build-dedup`.
- Pinned ROCm 6.1, `gfx906`, Vulkan, and the fork's established Vega tuning flags.
- Built `llama-server`, `test-server-message-dedup`, and `test-arg-parser`.
- The script verified `build-dedup/bin/llama-server` as a valid ELF.
- The compiler emitted warnings in existing `fattn-tile.cuh` template instantiations, but the build completed successfully.
- Retained `build-rcfix`, `build-sync0909`, and other control directories were not modified.

## Test gate

Command:

```sh
ctest --test-dir build-dedup -R 'test-server-message-dedup|test-arg-parser' --output-on-failure
```

Result: pass, 2/2 tests in 2.67 seconds.

- `test-server-message-dedup`: pass in 2.02 seconds.
- `test-arg-parser`: pass in 0.64 seconds.

LSP diagnostics were attempted for every changed C++ source and header. The workspace clangd configuration did not use the new build lane's include paths and reported missing project headers such as `llama-cpp.h`, `common.h`, and `json.h` across the translation units. These results are not source diagnostics. The fresh CMake build above is the authoritative compile gate.

## Server isolation and blocked checks

The user reported that a live server is running and required explicit approval before any request, stop, restart, or competing server launch. No request was sent to the live server and it was not modified.

Two checks that were expected to be offline were stopped after their harness behavior proved otherwise:

1. `build-dedup/bin/llama-server --help` initialized a separate binary before printing help and failed before binding because no ROCm-capable device was available in that command environment.
2. The imported pytest scenario command inherited `tools/server/tests/conftest.py`, attempted to construct a server command at `../../../build/bin/llama-server`, and failed with `FileNotFoundError` before a process started.

At that point, HTTP and server checks remained blocked pending explicit user approval.

## Live server verification

The user stopped the previous server, approved live verification, and specified `swift_1.5_llama_start-q6_q8_q4.sh` as the launcher. The launcher was not edited. Its existing `BIN` and `LD_LIB` overrides were used to select the dedup build:

```sh
BIN=$PWD/build-dedup/bin/llama-server LD_LIB=$PWD/build-dedup/bin PORT=8009 ./swift_1.5_llama_start-q6_q8_q4.sh
```

Startup result: pass.

- PID: `4112673`.
- Executable: `build-dedup/bin/llama-server`.
- Endpoint: `http://127.0.0.1:8009`.
- Two slots initialized at `n_ctx_slot=200192` after context rounding.
- Target, DFlash2 draft model, and multimodal projector loaded successfully.
- The server was launched without `--message-dedup`, so default-off and per-request override behavior could be checked on the same process.

The live request used `tools/server/tests/fixtures/message_dedup/requests/three_copies.request.json`, with three byte-identical large `tool` results.

### Template gate

`POST /apply-template` without an override returned HTTP 200:

- Rendered prompt: 4,713 bytes.
- Full-copy markers: 3.
- Dedup stubs: 0.

The same request with `message_dedup={"enabled":true,"min_bytes":1,"roles":["tool"]}` returned HTTP 200:

- Rendered prompt: 2,825 bytes.
- Full-copy markers: 1.
- Dedup stubs: 2.
- Both stubs referenced `tool result #1 (read_file)`.

This proves that default-off preserved all copies and the per-request override preserved the first copy while replacing both later copies.

### Token-count gate

`POST /v1/chat/completions/input_tokens` with the same off/on requests returned HTTP 200:

- Dedup off: 1,473 input tokens.
- Dedup on: 769 input tokens.
- Saved: 704 input tokens.

### Timing-statistics gate

A non-streaming `POST /v1/chat/completions` used `tools/server/tests/fixtures/message_dedup/timings_request.json`, the same per-request override, and `max_tokens=1`. It returned HTTP 200 with one generated token:

- `dedup_n=1`.
- `dedup_bytes_saved=245`.
- `dedup_tokens_saved_est=61`.
- `prompt_n=440`, `cache_n=0`, `predicted_n=1`.

Post-test `GET /health` returned `{"status":"ok"}`. The verified server remains running on port 8009; it was not stopped or restarted after the checks.

## Promotion state

- Source adoption: complete.
- Fresh build and C++ conformance: complete.
- Retained production binary replacement: not done; `build-rcfix` remains unchanged.
- Launcher changes: not done; the live process uses `BIN` and `LD_LIB` overrides and the feature remains default-off.
- Live HTTP validation: complete for default-off rendering, per-request dedup rendering, token count reduction, timing statistics, and post-test health.
- Push: not requested and not performed.
