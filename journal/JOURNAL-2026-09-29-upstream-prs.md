# 2026-09-29 - upstream PR isolation campaign + #29478 adoption

## Goal

Test the five ranked upstream PRs from the 2026-09-29 audit against the
production ngcache lane, then adopt what wins.

## Method

Each PR applied in isolation onto the dirty ngcache tree, built with the
pinned production config (build-dflash-novega.sh flags), measured with
bench/ab-bench.sh on port 8013 (1 discarded warmup per arm, interleaved
controls). Identical server args across all arms: Swift-Qwen3.8-27B-Q6_K
+ DFlash2-Q4_K_M, ngram-mod,ngram-cache,draft-dflash, -c 398000 -np 2,
q8_0 K / q4_0 V, force_convert, -ts 35,23,43 -sm layer, pipeline off,
draft pinned to ROCm0, -lcd read-only. 9 runs total; full table and
per-run logs: bench/logs/upstream-prs-20260929/summary.md.

## Results (TG t/s, temp-0 SHA all identical cbebfdee4e8e, acc all 0.578)

- baseline a1/a2/a3: 19.4 / 19.7 / 19.4 (PP drifted 394.5 -> 408.3 on
  the same binary across the session; PP not decisive today)
- #29478 b1/b2: 21.2 / 21.4 -> +9-10% TG, reproducible
- #29638 b1: 19.9 -> neutral; correctness-only EOG guard
- #29660 b1: 19.1 -> neutral; no "re-synced" lines (override already
  agrees with --spec-draft-device on this launcher)
- #29019 b1: 19.5 -> single-slot neutral; concurrency arm not run
  (baseline 2-slot reference captured: 9.6 t/s per slot, acc 0.562,
  slot-cross SHA 7f0b2389f96c, conc-pr29019-baseline-slot*.json)
- #29509 b1: 4.4 -> REJECT; draft wall 3628 ms vs ~1009 ms. Upstream
  assumes draft KV stays resident with replay rebuild; our checkpoint
  rewind + on-device spec-ckpt machinery violates that. Binary archived
  at bench/logs/upstream-prs-20260929/archive-bin-pr29509/.

## Decision

- ADOPTED: #29478 (gfx906 packed-byte subtraction, __vsubss4 ->
  __vsub4 in fattn-vec V dequant, MMQ q2-q6 tile loads, q3_K/q6_K MMVQ;
  operands bounded so saturation never triggers -> bit-identical
  outputs, confirmed by SHA). Gain comes from the weight MMQ/MMVQ
  paths, independent of the force_convert attention lane.
  Launcher BIN/LD_LIB now default to build-pr29478 (rollback:
  build-promptlookup-baseline). vgpr-check allowlist line carried.
  Residual: 2 candidate runs today vs 3 controls; keep an eye on the
  next routine A/B.
- RIDING AT NEXT SYNC: #29638 (EOG acceptance guard), #29660
  (dev_layer/dev_output resync; loader.cpp hunk needs the hand port,
  see summary.md).
- DEFERRED: #29019 (needs concurrent-slot A/B + review against the
  DFlash per-sequence contiguity assumption in common/speculative.cpp).
- REJECTED: #29509 on this fork (see above).
- #29534 (gfx906 wave64 q8_0 FA): watchlist only - it speeds the
  NATIVE q8-K fattn path, which this lane does not run
  (GGML_CUDA_FATTN_PATH=force_convert; native measured slower at every
  depth, E184-E190). Only worth a trial if we re-challenge
  convert-vs-native.

## Commits

- 939b9ffec: ngcache WIP consolidation (5-PR port, strict gate, p_min,
  -lcd persistence, vendored deps, journals) - prerequisite: the
  ngcache launcher's flags are not in prior HEAD.
- (this commit): #29478 adoption + records.
