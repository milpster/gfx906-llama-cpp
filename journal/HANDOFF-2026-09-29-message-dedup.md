## Objective
- User: "can we adopt this for our own fork?"
- User: "make sure to add this feature to our README versions documentation. Journal and Git."
- User: "go live server verification"
- User: "took down server, use it like this: swift_1.5_llama_start-q6_q8_q4.sh"
- User: "commit everything related to you only"
- User: "commit all and make sure its on master"

## Constraints
- User: "always journal, dont delegate."
- Do not delegate any work.
- A live server is now running again. Ask user before stopping, restarting, replacing, or otherwise touching it beyond explicitly approved checks.
- Preserve unrelated dirty work. Never stage or revert the prompt-lookup WIP listed below.
- Do not edit `swift_1.5_llama_start-q6_q8_q4.sh` unless explicitly requested. It already supports `BIN`, `LD_LIB`, `PORT`, and other environment overrides.
- No push was requested. No push was performed.
- llama.cpp repository policy applies: no PR creation/comments or push. The user explicitly approved committing all dedup-related documentation on `master`. Use `Assisted-by: Sisyphus`, not `Co-authored-by`.

## Work State
### Completed
- Adopted https://github.com/llopresto87/llama.cpp-prompt-dedup commit `02957b7733b41615725a9e0a6d4f36a356c9e715` from shared base `4098fdc922460470caa12659249e55f77c06730f`.
- Local feature commit: `e3c7d23cc57abb6556c3ad88b2dc3f55e54ea904`, subject `server: add prompt message deduplication (opt-in)`, author preserved as Luigi Lopresto, trailer `Assisted-by: Sisyphus`.
- Commit scope: 357 files, 61,787 insertions, 33 deletions. Includes implementation, C++ tests, HTTP tests, scenario/eval fixtures, `README_DEDUPLICATION.md`, fork README update, and initial journal.
- Only merge conflict was `server_routes::handle_completions_impl()` signature in `tools/server/server-context.cpp`; kept fork indentation and added `const std::optional<dedup_stats> & dedup`.
- Fresh pinned build passed:
  `BUILD_DIR=/home/srcds/dev/uf3_rocm6.1_llama.cpp/build-dedup FRESH=1 JOBS=16 TARGETS="llama-server test-server-message-dedup test-arg-parser" ./build-dflash-novega.sh`
- C++ tests passed twice. Latest proof:
  `ctest --test-dir build-dedup -R 'test-server-message-dedup|test-arg-parser' --output-on-failure`
  Result: 2/2 passed; `test-server-message-dedup` 4.23 s, `test-arg-parser` 0.70 s.
- Live server launched with the user-specified launcher and dedup build overrides:
  `BIN=$PWD/build-dedup/bin/llama-server LD_LIB=$PWD/build-dedup/bin PORT=8009 ./swift_1.5_llama_start-q6_q8_q4.sh`
- Initial live PID was `4112673`, executable `build-dedup/bin/llama-server`, endpoint `http://127.0.0.1:8009`, two slots, `n_ctx_slot=200192`. It was later stopped for the approved performance gate.
- Live `/apply-template` proof using `tools/server/tests/fixtures/message_dedup/requests/three_copies.request.json`:
  - Default off: HTTP 200, 4,713 prompt bytes, 3 full copies, 0 stubs.
  - Per-request on with `{"enabled":true,"min_bytes":1,"roles":["tool"]}`: HTTP 200, 2,825 prompt bytes, 1 full copy, 2 stubs.
  - Both stubs reference `tool result #1 (read_file)`.
- Live `/v1/chat/completions/input_tokens` proof:
  - Off: 1,473 input tokens.
  - On: 769 input tokens.
  - Saved: 704 tokens.
- Live one-token `/v1/chat/completions` proof using `tools/server/tests/fixtures/message_dedup/timings_request.json`:
  - HTTP 200, `completion_tokens=1`.
  - `dedup_n=1`, `dedup_bytes_saved=245`, `dedup_tokens_saved_est=61`.
  - `prompt_n=440`, `cache_n=0`, `predicted_n=1`.
- Post-test `GET http://127.0.0.1:8009/health` returned `{"status":"ok"}`. Server was left running.
- Live proof appended to `journal/JOURNAL-2026-09-29-message-dedup.md`.
- Production-shaped A/B used `bench/run-sync0924-validation.sh`, the exact `swift_1.5_llama_start-q6_q8_q4.sh` launcher, PP16384, TG1024, and temp-0 SHA checks.
- Six interleaved lanes completed: candidate/control/candidate/control/candidate/control.
- Candidate means versus `build-rcfix`: PP 400.0 vs 399.2 t/s (+0.21%), full fill 386.0 vs 385.4 t/s (+0.16%), TG1024 22.07 vs 22.0 t/s (+0.30%).
- All lanes had acceptance 0.653, `n_ctx_slot=200192`, 1,024 generated tokens, `repro_ok=true`, repro SHA `10d2416fc589`, and TG SHA `162cd5d138f8`.
- All six logs were clean of ROCm, allocation, Vulkan, assertion, invalid-device, segmentation, bus, and fatal errors.
- Performance/output verdict: pass for the complete `build-dedup` candidate as built. This was not a source-isolated dedup-only comparison because the candidate also contains the prior fork state and working-tree changes present at compilation time.
- The candidate server was restored after benchmarking as PID `875823` on port 8009; `/health` returned `{"status":"ok"}`.
- Promoted `build-dedup/bin` as the default binary and shared-library path in all 26 active root production launchers and `run-qwen38f-fast.sh`.
- Launcher syntax and diff checks passed. PID `875823` already used `build-dedup`, so no promotion restart was needed.

### Active
- The benchmark journal, handoff, README, and production launcher promotion are approved for commit on `master`.
- Server PID `875823` on port 8009 is running with dedup default-off. Per-request overrides are verified.
- Existing unrelated tracked WIP remains modified and unstaged:
  - `bench/run-sync0924-validation.sh`
  - `common/arg.cpp`
  - `common/common.h`
  - `common/ngram-cache.cpp`
  - `common/ngram-cache.h`
  - `common/speculative.cpp`
  - `journal/JOURNAL-2026-09-26.md`
  - `run-qwen38f-200k.sh`
  - `tools/server/server.cpp`

### Blocked
- clangd/LSP diagnostics are unusable with the current workspace configuration because it lacks `build-dedup/compile_commands.json` include paths. Errors included missing `llama-cpp.h`, `common.h`, and `json.h`. Fresh CMake compilation is the authoritative diagnostic gate.
- The full Python scenario suite was not run locally. A prior supposedly offline pytest command inherited `tools/server/tests/conftest.py` and failed before launch with `FileNotFoundError: ../../../build/bin/llama-server`.
- A prior `llama-server --help` check unexpectedly initialized a separate binary and failed before binding with `failed to initialize ROCm: no ROCm-capable device is detected`. Do not repeat server-related commands casually.
- `build-rcfix` remains unchanged as the rollback build. The production launcher default is now `build-dedup`.

## Key Decisions
- Imported the complete source commit, including its large scenario/eval suite, instead of a reduced hand port. Reason: preserve conformance evidence and future reproducibility.
- Kept message dedup off by default. Live checks used per-request `message_dedup` overrides on one unchanged process.
- Initially used `BIN` and `LD_LIB` overrides to select `build-dedup`, then promoted it as the production-launcher default after all gates passed.
- Used launcher-default `build-rcfix` as the performance control and the existing `build-dedup` as the candidate, as directed by the user.
- Preserved source test fixture trailing byte in `tools/server/tests/eval/message_dedup/tests/fixtures/snapshots/mini-snapshot-0001/story.txt`; `git diff --check` flags it, but it is exact-content test data from `02957b773`.
- Dropped the source repository's `AGENTS.md` fork-marker change because it misdescribed this gfx906 fork.
- Promoted the dedup-capable binary without enabling dedup globally. Requests still opt in per request or through `--message-dedup`.
- Restored the verified candidate server after the six-lane benchmark.

## Files & Symbols
- `tools/server/server-message-dedup.h`, `tools/server/server-message-dedup.cpp`: core types and pass; `dedup_settings`, `dedup_stats`, `dedup_resolve()`, `dedup_apply()`, `dedup_special_text_predicate_from_vocab()`, `dedup_tokens_saved_est()`.
- `tools/server/server-common.cpp`, `tools/server/server-common.h`: `oaicompat_chat_params_parse()` resolves per-request settings and applies dedup before the chat template; `server_slot_stats::to_json()` publishes stats.
- `tools/server/server-context.cpp`, `tools/server/server-context.h`: defaults/predicate setup, route plumbing, token estimate, task/slot stats; `server_routes::handle_completions_impl()`.
- `tools/server/server-task.h`: `task_params::dedup` server-written statistics channel.
- `common/arg.cpp`, `common/common.h`: `--message-dedup`, `--no-message-dedup`, `--message-dedup-min-bytes`, `--message-dedup-roles`; `common_message_dedup_role_allowed()`.
- `tests/test-server-message-dedup.cpp`: C++ conformance gate.
- `tests/test-arg-parser.cpp`: CLI/env validation.
- `README.md`: fork version/features record.
- `README_DEDUPLICATION.md`: operator behavior, flags, endpoints, evidence, tests.
- `journal/JOURNAL-2026-09-29-message-dedup.md`: source, integration, build, failures, live verification, promotion state.
- `journal/HANDOFF-2026-09-29-message-dedup.md`: this handoff.
- `swift_1.5_llama_start-q6_q8_q4.sh`: user-specified production launcher; now defaults to `build-dedup`.
- `build-dedup/`: verified ROCm 6.1 + Vulkan build lane.
- `/tmp/opencode/dedup-live-start.log`: current server startup log.
- `/tmp/opencode/dedup-apply-off.json`, `/tmp/opencode/dedup-apply-on.json`: live rendered-prompt evidence.
- `/tmp/opencode/dedup-tokens-off.json`, `/tmp/opencode/dedup-tokens-on.json`: live token-count evidence.
- `/tmp/opencode/dedup-completion-on.json`: live timings evidence.
- `bench/logs/message-dedup-perf-20260929-{candidate,control}-r{1,2,3}/`: six-lane PP/TG/SHA evidence.
- `/tmp/opencode/dedup-live-restart.log`: restored candidate startup log.
- Remote source: https://github.com/llopresto87/llama.cpp-prompt-dedup

## Next Moves
1. After the launcher-promotion commit on `master`, verify that all unrelated WIP remains unstaged and do not push.
2. Leave PID `875823` running unless user explicitly asks to stop or restart it. Check `/health` before any further test.
3. Ask whether dedup should remain per-request only or be enabled globally by adding `--message-dedup` to the launcher. Do not decide silently.

## Open Questions
- Should `--message-dedup` become a global launcher default, or remain per-request opt-in?
