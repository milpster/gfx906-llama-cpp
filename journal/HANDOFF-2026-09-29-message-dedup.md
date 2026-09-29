## Objective
- User: "can we adopt this for our own fork?"
- User: "make sure to add this feature to our README versions documentation. Journal and Git."
- User: "go live server verification"
- User: "made sure performance TG1024/PP16384 and temp 0 sha are ok?"
- User: "update the prod launchers to all use this latest build"
- User: "commit all and make sure its on master"
- User now asks: "so were done? did you update the ngcache launcher too? did we integrate ngcache changes?"

## Constraints
- User: "always journal, dont delegate."
- Do not delegate.
- Ask before stopping, restarting, replacing, or sending new workload to the live server.
- Preserve unrelated dirty work. Do not stage, revert, or silently combine prompt-lookup/ngcache WIP.
- User rejected temporary source worktrees/builds under `/tmp`. If another build is needed, create a new build directory inside `/home/srcds/dev/uf3_rocm6.1_llama.cpp` and use existing launcher-selected builds as controls.
- Commit only work related to this task, directly on `master`. Do not push.
- llama.cpp policy: no PR creation/comments; no push; commits require explicit approval and use `Assisted-by: Sisyphus`, not `Co-authored-by`.

## Work State
### Completed
- Message dedup feature adopted in commit `e3c7d23cc57abb6556c3ad88b2dc3f55e54ea904`: `server: add prompt message deduplication (opt-in)`.
- Source was ported from https://github.com/llopresto87/llama.cpp-prompt-dedup commit `02957b7733b41615725a9e0a6d4f36a356c9e715`.
- Documentation/live-proof commit: `efa50cee6`, `journal: record message dedup live verification`.
- Production promotion commit on branch `master`: `522753719`, `scripts: promote dedup build to production launchers`.
- `build-dedup` contains all committed fork history through embedded commit `edae69411`, the dedup implementation, and working-tree changes present when compiled. Its embedded version predates `e3c7d23cc` because CMake configured before the feature commit; live behavior proves dedup is present.
- Fresh `build-dedup` build and C++ gates passed: `test-server-message-dedup` and `test-arg-parser`, 2/2.
- Live API proof on `build-dedup`:
  - `/apply-template` default-off: 4,713 bytes, 3 full copies, 0 stubs.
  - Per-request on: 2,825 bytes, 1 full copy, 2 stubs.
  - `/v1/chat/completions/input_tokens`: 1,473 -> 769, saving 704 tokens.
  - Completion HTTP 200: `dedup_n=1`, `dedup_bytes_saved=245`, `dedup_tokens_saved_est=61`.
- Six interleaved production lanes completed with `swift_1.5_llama_start-q6_q8_q4.sh`: candidate/control/candidate/control/candidate/control.
  - `build-dedup` vs `build-rcfix`: PP16384 400.0 vs 399.2 t/s (+0.21%).
  - Full fill 386.0 vs 385.4 t/s (+0.16%).
  - TG1024 22.07 vs 22.0 t/s (+0.30%).
  - All lanes: acceptance 0.653, `n_ctx_slot=200192`, `tg_n=1024`, `repro_ok=true`.
  - All lanes: repro SHA `10d2416fc589`, TG SHA `162cd5d138f8`.
  - No ROCm, allocation, Vulkan, assertion, invalid-device, segmentation, bus, or fatal errors.
- `build-dedup/bin` is now the default in all 26 active root scripts marked `Production launcher`, plus `run-qwen38f-fast.sh`.
- Seven previously ignored local production launchers were intentionally force-added by commit `522753719` so the complete promotion is on `master`.
- `README.md` now records `build-dedup/bin` as production and `build-rcfix/bin` as rollback.
- Shell syntax and `git diff --check` passed for all promoted launchers.
- Live server restored after performance tests: PID `875823`, port `8009`, executable `build-dedup/bin/llama-server`; last `/health` was `{"status":"ok"}`.
- Dedup adoption and production-launcher promotion are done.
- The dedicated ngcache launcher now defaults to `build-dedup`, has a valid shebang, and defaults to isolated port 8010. Static checks passed; it was not launched.
- Ngcache source changes are still not integrated or committed.

### Active
- Message dedup remains default-off. It works through per-request `message_dedup` or server flag `--message-dedup`.
- Raw benchmark evidence is untracked under `bench/logs/message-dedup-perf-20260929-{candidate,control}-r{1,2,3}/`.
- Unrelated prompt-lookup/ngcache WIP remains modified and unstaged:
  - `bench/run-sync0924-validation.sh`
  - `common/arg.cpp`
  - `common/common.h`
  - `common/ngram-cache.cpp`
  - `common/ngram-cache.h`
  - `common/speculative.cpp`
  - `journal/JOURNAL-2026-09-26.md`
  - `run-qwen38f-200k.sh`
  - `tools/server/server.cpp`
- `swift_1.5_llama_start-q6_q8_q4-ngcache.sh` is aligned with `build-dedup` and port 8010. It enables `ngram-mod,ngram-cache,draft-dflash`; the source implementation it relies on remains dirty WIP.

### Blocked
- Ngcache integration is not complete. It was intentionally excluded from dedup commits because it is separate dirty WIP and the user had not authorized combining it with this feature.
- The ngcache launcher was not live-tested after alignment, and its source/build state remains uncommitted.
- clangd diagnostics are unreliable because the workspace configuration lacks the `build-dedup` include paths. Fresh CMake compilation is the authoritative compile gate.
- Full imported Python scenario suite was not run; its harness tried `../../../build/bin/llama-server` and failed before launch. C++ and live HTTP gates passed.

## Key Decisions
- Keep message dedup opt-in even though the dedup-capable binary is now the production default.
- Validate the complete `build-dedup` binary as built against launcher-default `build-rcfix`; do not claim a source-isolated dedup-only performance comparison.
- Use `build-rcfix` as rollback. Do not replace or delete it.
- Exclude benchmark archives, explicit mainline-stock controls, ngcache experiment launcher, and trial/pending launchers from production promotion.
- Two tracked non-production scripts intentionally still reference `build-rcfix`: `2llama-start-iq6v-dflash2-256k.sh` (pending validation) and `2llama-start-udv3v-dflash2.sh` (trial launcher).
- Do not merge prompt-lookup/ngcache WIP into the dedup history without a separate explicit decision and validation campaign.
- Aligning the ngcache launcher with `build-dedup` does not count as integrating the ngcache source.
- Do not use `/tmp` worktrees for future builds; user wants build directories inside this repository.

## Files & Symbols
- `tools/server/server-message-dedup.h`, `tools/server/server-message-dedup.cpp`: `dedup_settings`, `dedup_stats`, `dedup_resolve()`, `dedup_apply()`, `dedup_tokens_saved_est()`.
- `tools/server/server-common.cpp`: per-request resolution and pre-template dedup application.
- `tools/server/server-context.cpp`: route plumbing and timing statistics.
- `common/arg.cpp`, `common/common.h`: dedup CLI flags; currently also contain unrelated ngcache WIP.
- `README.md`: production build and feature record.
- `README_DEDUPLICATION.md`: operator documentation.
- `journal/JOURNAL-2026-09-29-message-dedup.md`: complete implementation, live, performance, and promotion record.
- `journal/JOURNAL-2026-09-28-prompt-lookup.md`: ngcache/prompt-lookup investigation and benchmark record.
- `journal/HANDOFF-2026-09-29-message-dedup.md`: this handoff.
- `swift_1.5_llama_start-q6_q8_q4.sh`: production launcher, now tracked and defaults to `build-dedup`.
- `swift_1.5_llama_start-q6_q8_q4-ngcache.sh`: dedicated ngcache launcher; valid shebang, `build-dedup` default, isolated port 8010.
- `build-dedup/bin/llama-server`: current dedup-capable production binary.
- `build-rcfix/bin/llama-server`: retained rollback/control.
- `bench/run-sync0924-validation.sh`, `bench/cmp-client.py`: PP16384/TG1024/temp-0 SHA gate.
- `/tmp/opencode/dedup-live-restart.log`: current server startup log.
- Commits: `e3c7d23cc` feature, `efa50cee6` live journal, `522753719` production promotion.

## Next Moves
1. Answer clearly: dedup work and ngcache launcher alignment are done; ngcache source integration is not.
2. Ask whether the user wants a separate ngcache source integration now. Do not assume launcher alignment authorized merging that WIP.
3. If approved, inspect `journal/JOURNAL-2026-09-28-prompt-lookup.md` and every current ngcache diff, fix `swift_1.5_llama_start-q6_q8_q4-ngcache.sh` shebang/default, then build into a new directory inside this repository.
4. Gate ngcache separately with focused tests, lifecycle/save-load checks, production PP16384/TG1024/temp-0 SHA A/B, and live HTTP verification before promotion.
5. Ask before touching PID `875823`. Keep unrelated WIP unstaged. Do not push.

## Open Questions
- Does the user want the separate prompt-lookup/ngcache WIP integrated and promoted now?
- Should message dedup remain per-request opt-in, or should production launchers add `--message-dedup` globally?
