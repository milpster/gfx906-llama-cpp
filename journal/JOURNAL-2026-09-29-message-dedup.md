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

Post-test `GET /health` returned `{"status":"ok"}`. The verified server remained running on port 8009 until the later performance gate.

## Production performance and output gate

The user approved stopping the live candidate and running the established production-shaped gate. Each lane used `swift_1.5_llama_start-q6_q8_q4.sh`, port 8013, `bench/run-sync0924-validation.sh`, `FILL1=16384`, and `TG_N=1024`. The binary and matching shared libraries were selected with the harness's `BUILD` override:

```sh
BUILD=$PWD/build-dedup OUT=$PWD/bench/logs/message-dedup-perf-20260929-candidate-rN PORT=8013 LAUNCHER=$PWD/swift_1.5_llama_start-q6_q8_q4.sh FILL1=16384 TG_N=1024 ./bench/run-sync0924-validation.sh
BUILD=$PWD/build-rcfix OUT=$PWD/bench/logs/message-dedup-perf-20260929-control-rN PORT=8013 LAUNCHER=$PWD/swift_1.5_llama_start-q6_q8_q4.sh FILL1=16384 TG_N=1024 ./bench/run-sync0924-validation.sh
```

The sequence was candidate/control/candidate/control/candidate/control. Message dedup remained default-off in both arms.

- Candidate: `build-dedup`, embedded build 11331 at `edae69411`. It was configured while the dedup source was still uncommitted, so the embedded commit predates `e3c7d23cc`; the live functional checks above prove that the binary contains dedup.
- Control: launcher-default `build-rcfix`, build 11548 at `7d30edc55`.
- This is a gate for the complete `build-dedup` candidate as built, including the prior fork state and working-tree changes present at compilation time. It is not a source-isolated benchmark of only the dedup delta.

| order | arm | first PP t/s | full fill t/s | TG1024 t/s | acceptance | repro SHA | TG SHA | repro |
|---:|---|---:|---:|---:|---:|---|---|---|
| 1 | candidate r1 | 400.0 | 385.9 | 22.1 | 0.653 | `10d2416fc589` | `162cd5d138f8` | true |
| 2 | control r1 | 397.5 | 383.5 | 22.0 | 0.653 | `10d2416fc589` | `162cd5d138f8` | true |
| 3 | candidate r2 | 400.5 | 386.0 | 22.0 | 0.653 | `10d2416fc589` | `162cd5d138f8` | true |
| 4 | control r2 | 399.9 | 386.5 | 22.0 | 0.653 | `10d2416fc589` | `162cd5d138f8` | true |
| 5 | candidate r3 | 399.4 | 386.1 | 22.1 | 0.653 | `10d2416fc589` | `162cd5d138f8` | true |
| 6 | control r3 | 400.1 | 386.2 | 22.0 | 0.653 | `10d2416fc589` | `162cd5d138f8` | true |

| metric | candidate mean | control mean | delta |
|---|---:|---:|---:|
| first PP segment | 400.0 t/s | 399.2 t/s | +0.21% |
| full 16,387-token fill | 386.0 t/s | 385.4 t/s | +0.16% |
| TG1024 at 16k depth | 22.07 t/s | 22.0 t/s | +0.30% |

Every lane reported `n_ctx_slot=200192`, `pp_n=15999`, `fill_n=16387`, and `tg_n=1024`. Every lane matched both canonical hashes and returned `repro_ok=true`. Searches of all six launcher/runtime logs found no ROCm, allocation, Vulkan, assertion, invalid-device, segmentation, bus, or fatal error.

Verdict: pass. The complete candidate shows no PP16384 or TG1024 regression signal and preserves exact temperature-0 output identity against the launcher-default control.

After the gate, `build-dedup` was restored with the production launcher on port 8009 as PID `875823`. `GET /health` returned `{"status":"ok"}`. Startup log: `/tmp/opencode/dedup-live-restart.log`.

## Production launcher promotion

After the functional, compile, PP16384, TG1024, and exact-output gates passed, the user approved promoting `build-dedup` as the default for all active root production launchers.

- The 26 root scripts marked `Production launcher` now default their server binary and matching shared-library path to `build-dedup/bin`.
- `run-qwen38f-fast.sh` also selects `build-dedup/bin` for both the executable and `LD_LIBRARY_PATH`.
- `BIN` and `LD_LIB` overrides remain available in launchers that already supported them. Three older hardcoded production scripts were converted to the same override form.
- Benchmark archives, the explicit mainline-stock control, the ngram-cache experiment, and two scripts explicitly marked trial/pending were not changed.
- `bash -n` passed for every promoted production launcher and `run-qwen38f-fast.sh`.
- `git diff --check` passed for every promoted launcher.
- The only remaining tracked root `build-rcfix` references are `2llama-start-iq6v-dflash2-256k.sh` (pending validation) and `2llama-start-udv3v-dflash2.sh` (trial launcher).

PID `875823` was already running `build-dedup`, so launcher promotion required no server restart. Its `/health` response remained `{"status":"ok"}`.

## Ngcache launcher alignment

The user separately requested updating `swift_1.5_llama_start-q6_q8_q4-ngcache.sh`. This launcher was not part of the earlier production promotion.

- Fixed the malformed `s#!/usr/bin/env bash` first line to a valid shebang.
- Changed default `BIN` and `LD_LIB` from `build-promptlookup-baseline/bin` to the promoted `build-dedup/bin`.
- Corrected the default port from 8009 to the documented isolated port 8010, keeping the normal production lane on 8009 untouched.
- Retained `SPEC_TYPE=ngram-mod,ngram-cache,draft-dflash`, `--spec-ngram-cache-strict`, `--spec-ngram-cache-p-min`, and `-lcd` dynamic-cache persistence.
- `bash -n` and `git diff --check` passed.
- No ngcache server was launched. PID `875823` remained on `build-dedup` at port 8009 and `/health` stayed `{"status":"ok"}`.

This aligns the dedicated launcher with the binary that already contains the ngcache working-tree code. It does not integrate or commit the ngcache source changes themselves; those remain separate WIP.

## Promotion state

- Source adoption: complete.
- Fresh build and C++ conformance: complete.
- Production default: promoted to `build-dedup/bin`; `build-rcfix` remains unchanged as the rollback build.
- Launcher changes: complete for all active root production launchers; message dedup itself remains default-off.
- Ngcache launcher: aligned with `build-dedup` and isolated on port 8010; ngcache source integration remains incomplete.
- Live HTTP validation: complete for default-off rendering, per-request dedup rendering, token count reduction, timing statistics, and post-test health.
- Production-shaped validation: complete; three interleaved candidate and three control lanes passed PP16384, TG1024, acceptance, exact temperature-0 SHA, fit, and runtime-error gates.
- Push: not requested and not performed.
