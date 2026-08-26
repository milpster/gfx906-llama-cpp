# gfx906 fork survey - 2026-08-25

User mission: measure PP 16384 first-batch / TG 1024 / 120k deep fill for each
fork against our prod (Qwen3.8-27B-UD-Q6_K_XL, mixed KV f16 K + q8_0 V,
triple device rocm0,vulkan1,rocm1). Reference numbers (our fixed binary,
prod config, same day):

| metric | value |
|---|---|
| PP first-batch 16384 | 325.4 t/s |
| TG 1024 fresh KV | 10.1 t/s (acc 0.686) |
| TG@120k deep fill | 10.1 t/s (acc 0.774) |
| n_ctx | 210176 |

Reference binaries: eaman-prod build (10547, 40e61a4a7) and old Aug-18
build-vega20 (10078, a76bbfd04) - both measured, identical outputs
(sha d5267dcc9d17 at 120k fill).

## Verdicts

| fork | builds | loads our model | bench | verdict |
|---|---|---|---|---|
| iacopPBK/llama.cpp-gfx906 | n/a (no qwen35 arch, base build 7924 ~Jan-2026) | NO | none | kernel backport candidates only |
| arte-fact/llamacpp-gfx-906-turbo | OK on ROCm 7.15 (/opt/rocm), NOT on 6.1 (hip_bfloat16 ctor) | NO (`missing tensor blk.64.ssm_conv1d.weight`) | none | turbo3 KV feature backport candidate |
| ollo12-prog/...-solve-tri-fix | OK on ROCm 6.1 | NO (same nextn-ssm failure) | none | SOLVE_TRI fix irrelevant to us |
| mixa3607/ML-gfx906 | n/a (distro: TheRock containers, offload-calculator; no kernel tree) | n/a | none | tooling reference only |

Root incompatibility (both qwen35-era forks): our Qwen3.8 GGUF's layer 64 is
an ATTENTION-ONLY nextn/MTP layer; March/May-2026-era qwen35 code requires
the nextn layer to be hybrid (ssm tensors). Fixing = porting current
upstream qwen35 hybrid-nextn handling into 4-5-month-old divergent model
code - out of scope per "skip if fix too complicated".

## Adoptable changes analysis

### iacopPBK kernels (ggml/src/ggml-cuda/gfx906/)
- `fattn-q8.cuh` 41.6K: dedicated Q8-K FA kernel family (Q8xQ8, D up to 512
  per their notes). We already have custom q8_0-V tile kernels; their Q8-K
  path would target full-q8 KV configs (our -ctk q8 direction).
- `q8-cache.cuh` 24.9K + gfx906-config.h: 128 MiB persistent VRAM cache of
  Q8-prequantized weights (layer-slotted). Aimed at TG (avoids re-quant in
  MMVQ). Our TG is 10 t/s - worth evaluating IF we go q8 KV.
- `sgemm.cuh`, `mmf.cuh`, `mmq-prefetch.cuh`, `mmvq-q{4_0,4_1,8_0}.cuh`:
  hand-tuned GCN GEMM/MVQ variants (Wave64, DPP reductions via
  gfx906-common.cuh). Our MMQ already has the vega20 tile config; theirs adds
  prefetch + fused epilogues - candidate diff-study for PP gains.
- `graph-fusion.cuh`, `norm-fused-q8`: fused op chains (norm+mul, rope).
  Upstream has since added rms_norm_mul fused ops; overlap.
- Successor fork: README points to mxxm-t/mx-llama.cpp (not surveyed; not in
  the user's list).

### arte-fact turbo3 KV compression
- turbo3: 3.5 bits/value KV (4.6x vs f16), 3.3x context claims on MI50
  rigs; wired into kv-cache + memory-hybrid (would apply to our hybrid
  model). Code: ggml-cuda/turbo-quant.cu + llama-memory integration at a
  ~May-2026 base. Backporting into our Aug-2026 tree = memory-interface
  surgery + quality validation (their notes: "matches vllm performance",
  quality not independently verified). Biggest potential CTX lever of the
  survey (4.6x KV compression vs our mixed-KV ~1.7x vs f16).
- Requires ROCm 7.1+ APIs (hip_bfloat16 float-ctor); our stack is 6.1 ->
  backport must replace those constructs (or we bump toolchain per-component
  like we did for this survey build).

### ollo12-prog solve-tri
- The SOLVE_TRI/rocBLAS gfx906 failure does not affect us: we run the custom
  gfx906-xnack rocBLAS on ROCm 6.1 and hit no solve_tri errors. No value.

### mixa3607 ML-gfx906
- Distro (Docker/TheRock builders, amd-memory-tweak, offload-calculator).
  The `llamacpp-offload-calculator` could complement our
  dual-gpu-context-balancing skill. No kernels.

## Files

- forks/ (shallow clones; turbo build-t715 + solve-tri build-st kept for
  future work; both binaries functional, just cannot load Qwen3.8)
- bench/logs/turbo1.log, bench/logs/st1.log: load failure evidence
- trials.md rows appended for all survey attempts

## Re-evaluation 2026-08-26 (post adaptive-MTP + PP profiling)

Context shift since original survey: adaptive MTP shipped (TG 10.2 -> 19.3+,
PP parity 326); PP profiling during the PR27210 tax hunt showed MUL_MAT = 92%
of PP GPU time (FA 2%, ROPE ~0.1%), VRAM 90/97% at 210k, KV @210k = 10.06
GiB mixed. Ranked verdicts:

1. turbo3 KV compression - ONLY ceiling breaker. Est. KV 10.06 -> ~3-4 GiB
   (f16-equiv ~13.1 GiB * 3.5/16), frees ~6.5-7 GiB -> 262k full / -ub 768 /
   more checkpoints; TG@depth also improves (attention reads shrink). Cost:
   port surgery + ROCm 7.1 constructs replacement + MANDATORY quality gate
   (greedy-sha divergence + MTP acceptance; 3.5-bit V touches verify logits).
   Days of work. THE candidate if we ever want >210k.
2. iacopPBK sgemm/mmf/mmq-prefetch - only family targeting our real PP
   bottleneck (MUL_MAT 92%), but build-7924-era internals vs our rewritten
   MMQ + own vega config = diff-study for ideas, single-digit % hope.
   Successor fork: mxxm-t/mx-llama.cpp (unsurveyed).
3. fattn-q8 - redundant (own tile kernels; FA 2% of PP; full-q8 measured
   slower than mixed anyway). Skip.
4. q8-cache 128MiB - VRAM-disqualified at 90/97% full; revisit only if
   turbo3 frees headroom. TG already doubled by adaptive MTP.
5. fusion/rope/gather - negligible vs profile. Skip.
6. solve-tri - still zero value (custom rocBLAS 6.1, no solve_tri path).
7. offload-calculator - our manual skill already beats auto approaches.

Net: useful residue = turbo3 (strategic) + iacopPBK GEMM ideas (tactical).
Current shipped stack remains best measured config for this machine.

## Deep-dive 2026-08-26: iacopPBK kernel family (user-requested) + final sweep

Read the actual kernels (not filenames). Two corrections to the original survey:

- q8-cache is NOT a weight cache: it is a Q8_1 ACTIVATION cache with graph
  analysis - quantize-once per multi-consumer tensor, feed all its MUL_MATs
  via the prequantized MMQ path (skips re-quant per consumer). Mechanism
  targets PP too (our 92% MUL_MAT profile includes per-consumer activation
  quant). 128 MiB default, size-configurable. VRAM-tight at 210k but not
  structurally disqualified.
- sgemm.cuh ("2x vs rocBLAS, M<=64") targets the cuBLAS/rocBLAS path -
  irrelevant to us: GGML_CUDA_FORCE_MMQ=ON routes all our Q6_K GEMMs to MMQ.

Their measured gains (benchmarks.svg, Qwen3-VL-30B-A3B Q4_1 MoE, single
MI50): pp512 1404->1683, pp2048 1801->2222, pp8192 1280->1573, tg128
101->131, tg2048 101->124 = consistent +20-23% BUNDLE (sgemm+prefetch+
cache+fattn-q8+rope+fusion combined; no per-piece attribution). Regime
caveat: A3B Q4_1 single-GPU = small-GEMM/launch-latency bound; our 27B
Q6_K_XL 3-GPU PP = big-tile MUL_MAT bound. Transfer fraction unknown,
likely low single digits per piece.

Transferable to us, ranked:
1. mmq-prefetch.cuh (L2 y-tile warming via 16 spare lanes, global_load_dword
   discard-load): TYPE-AGNOSTIC (y side is always Q8_1 in MMQ), zero VRAM,
   self-contained ~50 lines, directly targets our 92% profile. Spike: 1-2h
   incl. build+bench. Risk low (prefetch is functionally a no-op).
2. q8 activation cache + prequantized MMQ (mmq-prequantized.cuh + q8-cache.cuh
   710 lines): PP-oriented medium surgery (graph analysis, name-keyed cache,
   slot routing). Consider only after (1) proves out. Shrink cache to 32-64MiB.
3. Not transferable: fattn-q8 (Q4/Q8 KV focus; our FA=2% of PP), rope (0.1%),
   mmvq-q4_0/q4_1 (type mismatch, we are Q6_K), sgemm (rocBLAS path unused).
4. gfx906-common.cuh (sgpr_broadcast via readfirstlane, DPP reductions):
   free riders to import alongside any port.

Final sweep answers ("really nothing else?"):
- turbo fork's "9 HIP bug fixes": no extractable list; their own dense-27B
  result (18.5 tg on 4x MI50) does not beat our shipped 19.3-20.5 on 3 GPUs
  -> nothing latent we are missing.
- mixa3607 amd-memory-tweak: HBM2 timing tightening would help our
  bandwidth-bound deep-fill TG (11.2 @120k) but requires root (unavailable)
  + stability risk. Blocked, documented.
- launch-flag mining: their -ub 2048 trick = known (OOMs at our 210k);
  ngram windows similar to ours. Nothing new.

Next action if wanted: prefetch spike (item 1).

## Prefetch spike result 2026-08-26: NEGATIVE, closed

Ported iacopPBK Y-tile prefetch (v4) verbatim into our mul_mat_q_process_tile
(branch perf/mmq-prefetch @ 80ba7ec6a, kept for reference). Interleaved A/B
x2 each, 2.2k PP, plain mtp n10, prod triple: prefetch 241.3/240.5 vs
baseline 259.5/261.2 t/s = consistent **-7.5% PP**. Their win regime (small
MoE tiles, cold next-Y) does not transfer: our big-tile PP keeps Y L2-warm;
the discard-loads only add instruction + VGPR pressure. X-tile prefetch and
v2/v1 variants not tried - given the Y result and the same L2-warm argument
for X, expected also negative; closing the family. iacopPBK transferables
now fully triaged: prefetch dead here, q8-activation-cache untested but
VRAM-costed, sgemm/fattn/rope N/A. Nothing further actionable from this fork
on current hardware/config.
