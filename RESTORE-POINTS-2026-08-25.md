# Restore points + session state - 2026-08-25

Journal so we can return to the pre-eaman / pre-fork-survey state at any
time. Everything below is a durable pointer; nothing pre-eaman was modified.

## Pre-eaman restore point (our version before eaman's fixes)

| item | value | status |
|---|---|---|
| Fork line before eaman | branch `master` @ `a76bbfd04` ("Q6_K_XL KV-mode ladder, mixed-KV winner at 210k") | untouched, ahead 18 / behind 555 vs origin/master |
| Aug-20 merge tree (no eaman) | branch `sync/upstream-2026-08` @ `a3fbc9321` | untouched |
| Production binary (pre-eaman) | `build-vega20/bin/llama-server`, build 10078, commit `a76bbfd04`, Aug-18, FA_ALL_QUANTS=ON in its CMakeCache | intact, verified loads |
| Launcher default | `llama-start-q6v.sh` BIN/LD_LIB default = `build-vega20/bin` | already runs the pre-eaman binary; no env override needed |

To go back completely:
```
git checkout master                       # pre-eaman source
./llama-start-q6v.sh                      # already runs the pre-eaman binary
```
Optionally delete the eaman artifacts (only if never returning to them):
`git branch -D eaman-prod eaman-rs; rm -rf build-vega20-eaman patches-eaman forks/`.

## Eaman artifacts (keep, do not lose)

| item | value |
|---|---|
| `eaman-prod` branch | `05e686752` = a3fbc9321 + eaman 8144f31 cumulative + upstream 2fb989b9e + rs revert + docs. Validated drop-in replacement (PP 325.4, outputs bit-identical) |
| `eaman-rs` branch | `337d55023` = full cumulative incl. experimental rs (deadlocks on client abort; reference only) |
| eaman binary | `build-vega20-eaman/bin/llama-server` build 10547 @ 40e61a4a7-lineage, FA_ALL_QUANTS=ON rebuild. Run via `BIN=.../build-vega20-eaman/bin/llama-server LD_LIB=.../build-vega20-eaman/bin ./llama-start-q6v.sh` |
| patches | `patches-eaman/` (a3b1eff, rs_cumulative_8144f31, mtp_rs_only_8144f31) |
| docs | `EAMAN-INTEGRATION-2026-08-24.md` (incl. 08-25 corrections), `bench/trials.md` |
| remote | pushed to gfx906 (milpster/gfx906-llama-cpp): eaman-prod, eaman-rs (watcher fired 2026-08-25 15:13) |

## Fork survey artifacts

| item | value |
|---|---|
| clones | `forks/` (shallow): llama.cpp-gfx906, llamacpp-gfx-906-turbo (+ build-t715 on /opt/rocm 7.15), llama.cpp-gfx906-solve-tri-fix (+ build-st on 6.1), ML-gfx906 |
| bench | none possible: all runnable forks fail to load Qwen3.8 (nextn layer is attention-only in our GGUF, hybrid-ssm expected in their March/May-2026 code) |
| analysis | `FORK-SURVEY-2026-08-25.md` (turbo3 KV 4.6x compression = biggest ctx lever; iacopPBK kernel inventory) |

## Session conclusions (one paragraph)

Eaman = speed/ctx parity on our prod config; adopt for alignment only. The
19x PP collapse ("F2") and abort wedge ("F1") were OUR rebuild recipe missing
`GGML_CUDA_FA_ALL_QUANTS=ON` - the Aug-20 merge tree is healthy. Auto-fit
slowness unpinned = deliberate host-layer placement (max-ctx-over-speed), not
misplacement. Forks: nothing runnable; turbo3 KV compression is the one
serious ctx candidate if we ever want >210k.

## Housekeeping

- push-retry.sh watcher: completed (PUSH OK 15:13), self-exited; safe to delete
- git bisect: reset (no state left)
- stashes: trials-wip + f2-instrumentation were for the deleted bisect branch;
  dropped with it? NO - verify with `git stash list` before cleaning; the
  instrumentation stash is obsolete (diagnosis complete)
- GPU state at journal time: idle (all test servers killed)
