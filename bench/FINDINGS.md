# Optimization findings - Qwen3.8-27B-Q8_0 on 2x Radeon VII (ROCm) + RTX 3080 Laptop (Vulkan)

Decision record from the 2026-08-14/15 optimization pass (llama.cpp 604fca587,
build-vega20, gfx906). Raw trial rows: `trials.md`. How to re-measure: `README.md`.

Production launcher: `../run-qwen38-155k-fast.sh` (155k ctx, pipeline parallel,
`-sm cost -ts 41,20,39`, MTP SPEC=2, F16 KV).

## Measured Pareto frontier @ 155k

| config | pp1 tok/s | tg tok/s | acc | verdict |
|---|---:|---:|---:|---|
| SPEC=2 MTP (production) | 323.9 | 21.3 | 0.57 | keep - best TG |
| SPEC=1 MTP | 323.9 | 20.3 | 0.45 | worse on both |
| SPEC=3 MTP | 270.8 | 20.3 | 0.60 | worse on both |
| no speculative | 350.8 | 15.3 | - | clears 350 pp1, TG -28% |
| ngram-map-k4v | 351.3 | 14.9 | 0.00 | equals no-spec on novel prose |

pp1 = first 16384-token batch. tg = greedy 1024 tokens (21.3 also held at 256).

**There is no configuration with pp1 > 350 that keeps TG.** The ~27 tps PP gap
between MTP and no-MTP is the MTP catch-up decode: the draft context replays
every prompt ubatch through the single nextn layer (`common/speculative.cpp`,
`draft_mtp::process`). It fills the draft KV for every prompt position; skipping
it breaks drafting (the `begin()` warning documents this) and deferring it to
first generation would stall TTFT by a full prompt-length replay.

## Failed routes to 350 pp1 (each measured, do not retry blindly)

| route | result | why |
|---|---|---|
| SPEC=1 (shallower draft) | pp1 unchanged 323.9 | catch-up cost is per-ubatch, independent of draft depth |
| larger draft ubatch (16384) | OOM at startup | single full decoder layer at 16k tokens genuinely needs ~7 GB f32 activations |
| larger draft ubatch (2048) | OOM at startup | still 878 MiB on ROCm1; no headroom at 155k |
| larger target ubatch (896) | wedges startup fit | PP compute buffers scale with ubatch; ROCm0 has no margin |
| ngram speculative | acc 0.0 | n-gram drafting never fires on novel prose without prefix matches |
| 165k ctx without pipeline | pp ~301 | old calibration, reconfirmed as below target |
| 165k ctx with pipeline | OOM | needs ~706 MiB extra PP compute buffer on ROCm0; no split fits |

155k is the ctx ceiling for this model+quant on this hardware, with or without
the 350 target.

## Code patches shipped this session (all in build-vega20, uncommitted)

1. `src/llama-context.cpp` - tensor overrides (`-ot`) no longer disable
   pipeline parallelism. Verified: PP + `-ot nextn->ROCm0` runs, byte-identical
   greedy output. Costs ~3% pp1 at 155k, so the launcher stays override-free.
2. `--cost-attn-weight N` (llama.h, llama-model.cpp, common/*) - exposes the
   COST split-mode attention:recurrent weight (was hardcoded 4.0, now default).
3. `tools/server/server-context.cpp` - null-check `ctx_tgt` after context
   creation. Previously ANY context-alloc failure (oversized -c, OOM) segfaulted
   the server at startup instead of exiting with an error.

## Environment variables - verified status

| var | status |
|---|---|
| `HSA_OVERRIDE_GFX_VERSION=9.0.6` | REQUIRED. Without it warmup HIP-graph capture dies with "ROCm error: invalid device function" (rms_norm_mul_f32_cuda). Do not remove. |
| `GGML_VK_DISABLE_F16` | no-op for this setup. A/B tested: identical throughput and output hash. Vulkan1 holds only 13 of 93 pipeline positions. Dropped. |
| `HIP_GRAPH=1` | dead - no code reads it. Graphs are build-time `GGML_HIP_GRAPHS=ON`. Removed. |
| `HIP_FORCE_P2P=1` | dead - no code reads it (real gate is `GGML_CUDA_P2P`, never set; PCIe gfx906 has no P2P anyway). Removed. |
| `GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16` | kept; near-moot since `GGML_CUDA_FORCE_MMQ=ON` routes Q8_0 GEMMs to MMQ dp4a kernels |

## Ideas evaluated and rejected (with reasons, do not re-propose)

- **Gate MTP drafting during prompt processing**: load-bearing. The per-ubatch
  catch-up fills the draft KV and hands `pending_h` rows between ubatches.
- **Remove the per-token `ggml_backend_sched_synchronize` in PP decode**
  (llama-context.cpp:1345): guards a real hazard (set_inputs overwrites source
  tensors the previous async compute may still read); the server loop syncs on
  logits/embeddings reads anyway - zero gain, real risk.
- **Delta-encoded ctx checkpoints**: checkpoints are ~305 MiB at 40k tokens
  (~1 GiB near 155k), consecutive differ by <2 MiB, but delta-encoding needs
  serialization-layer surgery. `-cram 20000` + `--checkpoint-min-step 8192`
  bounds the cost acceptably. Not worth it.

## Standing measurements (production config, 2026-08-14)

- load to healthy: ~24 s
- pp1: 323-326 tok/s (batch 1 of 16384; aggregate over 33k prompt: ~291)
- tg: 21.0-21.3 tok/s greedy, acceptance 0.57 (SPEC=2)
- Greedy output is not bit-stable across runs with different KV/batch state
  (upstream-documented); treat content hashes as a signal, not an invariant.

## MMQ kernel headroom (2026-08-15, bench-dot4 microbenchmark)

gfx906 v_dot4_u32_u8 issue rate measured from register chains (2.27 T-instr/s,
9.06 T int8 MAC/s per Radeon VII at steady boost). MMQ demand at pp1=324 with
ts 41,20,39 (VIIs carry 80/93 of positions): 0.94 T-instr/s per VII.

=> the production MMQ kernels run at ~41% of the measured dp4a issue rate.
PP at batch 16384 is compute-bound (weights stream once per ~51 s batch,
nowhere near the 1 TB/s HBM2 limit), so this gap IS kernel efficiency, not
memory. If the inner loop can be brought from 41% to 55-65% of issue rate
(dequant + LDS overhead makes 100% unreachable), projected pp1:

| inner-loop eff. | GEMM gain | est. pp1 (GEMM ~70% of step) |
|---|---|---|
| 45% (small tuning) | +10% | ~335 |
| 55% | +34% | ~370-390 |
| 65% | +59% | ~410+ |

Caveats: the 41% figure assumes all 27B params sit in dp4a GEMMs (attention
quadratic terms add work, so real efficiency is somewhat higher than 41%
and real gains somewhat lower than the table). Next concrete step before
touching the kernel: rocprof a PP run to split MMQ cycle cost into
VALU-issue vs LDS vs stall - confirms whether the gap is schedulable
instruction mix (fixable by tiling/unroll) or structural.

Prior work already in the tree: vega20 MMQ tile config (468c164f4) addresses
LDS budget/occupancy; MFMA and rocWMMA paths are N/A on gfx906 (no matrix
cores, documented in BUILD-VEGA20.md).

## PMU profiling status (2026-08-15, attempted)

Goal: rocprof counter split of MMQ kernels (VALU-issue vs LDS vs stalls) to
classify the 59% issue-rate gap found by bench-dot4 as schedulable vs structural.

Outcome: BLOCKED - tool/runtime version mismatch. Details:

- rocprof binaries are absent from the local 6.1 install; a 6.4.4 user-mode
  stack was reconstructed by download-only extract and archived in
  bench/rocprof-stack (wrapper: bench/rocprof.sh, ~6.7 MB).
- The 6.4.4 interposer is incompatible with the ROCm 6.1 runtime:
  * child processes lose device enumeration ("no ROCm-capable device
    detected" under rocprofv2, while the profiler itself enumerates gfx906)
  * or the server reaches weight load and dies with a CP/UTCL2 page fault
    (CPF client, PERMISSION_FAULTS) - with and without HIP graphs and SDMA.
- Matching rocprofiler 6.1 debs are not reachable at the obvious repo paths
  (404/HTML); old releases appear relocated.

Requirements captured for a future attempt (see bench/rocprof-server.sh):
- prepend (not reset) LD_LIBRARY_PATH so the interposer survives the launch
- HSA_ENABLE_SDMA=0 for load-time stability
- GGML_CUDA_DISABLE_GRAPHS=1 (graph-replayed dispatches vs interposer)
- verify with a pure-HIP microbench first (bench-dot4), not the full server

Unrelated lead found while isolating: llama-bench on this fork allocates the
entire model to device 0 even with -ts 50/50 and -sm layer (26.4 GiB single-
buffer OOM). The server path splits correctly, so it is llama-bench-specific;
worth its own investigation before trusting llama-bench multi-GPU numbers.

Until PMU works, the bench-dot4-derived estimate stands (41% of issue rate,
projection table above), and kernel experiments should be evaluated
empirically with ab-bench.sh (reliable) rather than PMU-guided.

## PMU profiling verdict (2026-08-15, rocprofiler 6.1 build 60100)

RESOLVED (supersedes the BLOCKED note above): a 6.1-matched rocprofiler
was fetched from https://repo.radeon.com/rocm/apt/6.1 (suite "ubuntu"),
extracted into bench/rocprof-stack, and verified end-to-end: server loads,
listens, and PMU counters collect through the full production PP path.
Counter recipes archived as bench/rocprof-pmc-{a,b,c}.txt; aggregation in
bench/analyze-pmc.py. Raw CSVs kept in /tmp/opencode/rocprof/out-{a,b,c}/.

### What the counters say (16k-token PP, production shapes, both VIIs)

| metric | value | meaning |
|---|---|---|
| mul_mat_q share of GPU busy cycles | 82.9-83.8% | MMQ GEMM is THE kernel; speeding it directly speeds PP |
| mul_mat_q VALU issue vs measured dot4 ceiling | 40.6% | matches the 41% from bench-dot4 arithmetic - two independent methods agree |
| LDS bank conflicts | 0.00/kcyc | vega20 tile config (468c164f4) is doing its job |
| VMEM reads vs VALU insts | 1.5% | not memory-bound |
| LDS insts vs VALU insts | 1:5.18 | not LDS-throughput-bound |
| SALU / SMEM share | negligible | not scalar-bound |
| flash_attn busy share | 7.6-8.8% | co-residual |
| gdn recurrent (ssm/gated_delta) | ~5% | co-residual |

### Interpretation

Every classic bottleneck is cleared: no bank conflicts, negligible memory
and scalar traffic, LDS well under throughput. The MMQ inner loop simply
sustains only ~41% of the VALU issue rate the same silicon demonstrably
delivers (bench-dot4: 57.2 VALU-insts/busy-cycle; mul_mat_q: 23.2).
The gap is VALU-issue occupancy: instruction mix (Q8_0 dequant + address
arithmetic interleaved with dot4) and dependency stalls (register chains,
LDS latency at only 1-wave-per-CU occupancy from the I=128 tile).

=> the gap is SCHEDULABLE, not structural. Concrete kernel-level levers,
in expected-impact order:
1. deepen dot4 ILP: more independent accumulator chains per thread in the
   MMQ inner loop (register budget is the constraint; launch_bounds
   already relaxed by the tile config)
2. prefetch/swizzle the next K-tile into LDS while computing the current
   one (hides LDS latency behind dot4 chains)
3. reduce non-dot4 VALU work: Q8_0 dequant via fewer bit-ops, hoist
   address arithmetic into SALU/precomputed offsets

Projection (from FINDINGS top): 45% inner-loop eff. -> ~335 pp1; 55% ->
~370-390 pp1; 65% -> ~410+. All while keeping MTP SPEC=2 and TG.

### Profiler usage (verified)

  ./bench/rocprof.sh --list-counters
  ./bench/rocprof.sh -i bench/rocprof-pmc-a.txt --plugin file -d OUT ./bench/rocprof-server.sh
  # then one 16k-token PP request; python3 bench/analyze-pmc.py OUT [OUT2 ...]

rocprof-server.sh already carries the required env deviations
(LD_LIBRARY_PATH prepend, HSA_ENABLE_SDMA=0, GGML_CUDA_DISABLE_GRAPHS=1).
Note: profiling serializes kernels - do NOT compare wall-clock times
across profiled runs; use the counters.

## MMQ kernel experiment 1: k01 full unroll (2026-08-15) - REJECTED

Lever: restore the commented-out "#pragma unroll" on the k01 loop in
ggml_cuda_mmq_vec_dot_q8_0_q8_1_dp4a (mmq-vec-dot.cuh:122).

Result: CATASTROPHIC - pp1 99 tok/s vs 323 baseline (3.3x slower).
Output sha was bit-identical (4307c77073ee), so numerics were correct;
the regression is scheduling: full unroll explodes the basic block to
~1000 dp4a + 32 float accumulators + all LDS addressing -> register
spill to scratch. The commented-out pragma is deliberate protection,
not an oversight. Do not re-enable.

Analysis update: with nthreads=256/wave64 -> nwarps=4, J=64, I=128, each
thread already owns 32 independent accumulators (16 j0 x 2 i0), so ILP
is not the missing ingredient; the ~40% VALU issue-rate gap vs bench-dot4
comes from the per-8-dp4a group costs (I2F + 2 FMUL + FADD per group,
x_df/y_df scale LDS loads) and LDS latency at 1 block/CU occupancy.

CORRECTION (2026-08-15, second pass): the scale product is NOT loop-
invariant across k01 - each k01 step is exactly one Q8_0 block with its
own x_df/y_df (k0/QI8_0 advances every iteration). The "hoist the scale
product" candidate as originally written here does not exist. What
remains is micro-op shaping (I2F+FMUL+FMA in place of I2F+2*FMUL+FADD,
one VALU op per 8 dp4a, possibly already contracted by -ffast-math):
realistic ceiling ~0-5 pp1. The pipe is stall-bound (60% idle cycles),
so removing issue pressure alone buys little; only chain-shortening
attacks the stalls.

Remaining big lever: scale-free integer accumulation across k-blocks
(changes summation order -> logits shift beyond reassociation noise;
int32 overflow beyond ~4k blocks per accumulator demands careful
fixed-point/saturation handling; plausible silent-wrong-answer failure
mode on long contexts). Needs a stall-reason PMU pass (SQ_WAIT/SPI
counters) and a perplexity gate before attempting.

Production state: kernel experiment reverted, ggml tree at HEAD,
post-revert-verify trial confirms pp 321.4 / tg 21.2 (= baseline noise).

## "Trade ctx/pp for TG" sweep (2026-08-15) - NO TRADE AVAILABLE

Question: can PP or ctx be sacrificed for higher TG? Sweep at 155k:

| config | pp_tps | tg_tps |
|---|---:|---:|
| PP on, ts 41,20,39 (production) | 323.7-323.9 | 21.0-21.3 |
| PP off, ts 41,20,39 | 323.1 | 20.8 |
| PP off, ts 42,19,39 | 300.8 | 19.9 |
| PP off, ts 40,21,39 | Vulkan1 KV OOM | - |
| PP off, ts 44,16,40 | ROCm0 compute OOM | - |

TG is pinned at 20-21.5 tok/s across every reachable configuration:
the old "+15 pp from pipeline parallelism" does not reproduce with
-sm cost (PP on/off now perform identically at the calibrated split),
and rebalancing ts in either direction loses both pp and tg. Decode is
bound by the serial 3-stage pipeline + MTP draft sequencing (~2.5x above
the 42 ms weight-streaming floor), which no launcher knob touches.

Upside found instead: PP off lifts the ctx ceiling - 160k AND 165k both
reach listening (n_ctx_slot 160000 / 165120, verified 2026-08-15). That
is the reverse trade: +10k ctx for roughly -20 pp (old 165k no-PP
calibration ~301 pp). If long-context matters more than ingest speed,
PP off + -c 165000 is available.

Harness hardening from this sweep: SIGKILL teardown (Vulkan transfer-
queue teardown can hang graceful exit), server-death watchdog (failed
trials now surface in <60 s instead of the client 20-min health timeout).

## KV fill -> TG decay curve (2026-08-15, TG_FILL harness knob)

| KV fill at generation | tg_tps | acc |
|---:|---:|---:|
| ~16 (prompt only) | 20.7-21.3 | 0.56-0.57 |
| 16384 | 20.2 | 0.574 |
| ~60k | 18.4 | 0.602 |
| ~120k | 16.8 | 0.617 |

TG loses ~21% from empty to 120k fill (21.3 -> 16.8 tok/s). This is the
attention-KV read cost of the full-attention layers (hybrid arch: a few
full-attn layers + linear/GDN layers), compounding the ~2.5x-over-floor
serial-pipeline overhead. Draft acceptance rises slightly with fill.

Answer to "sacrifice ctx or PP for TG":
- PP on/off: no TG difference (measured both ways) - nothing to trade.
- Smaller -c per se does not help; TG speed depends on KV FILL, not the
  -c ceiling. A smaller -c only helps TG if conversations actually stay
  short (less fill), i.e. the trade is "manage context fill", not "set -c".
  At a realistic 60-100k working fill, expect 17.5-19.5 tok/s.
- The genuine TG lever for deep contexts would be quantized KV (q8_0),
  halving attention KV reads; rejected earlier for quality at F16-KV
  philosophy, and hybrid arch limits the win to the few full-attn layers.

Harness: TG_FILL=N env knob (filler prefill before the TG pass);
degenerate-EOS guard added after the first 120k attempt emitted EOS
immediately (empty-output sha e3b0c44298fc - rerun if you see it).

## "less ctx + other ts" sweep (2026-08-15) - CLOSED, NO TG GAIN

Mechanism tested: smaller -c frees KV VRAM on Vulkan1 -> tighter ts -> less
weight on the slow-per-byte 3080 -> shorter serial decode stage.

| config (TG_FILL=16384) | pp_tps | tg_tps |
|---|---:|---:|
| c=155k, ts 41,20,39 (production) | 323-326 | 20.2-21.3 |
| c=64k, ts 41,20,39 (control) | 324.3 | 20.6 |
| c=64k, ts 44,12,39 | 316.8 | 20.2 |

Verdict: TG flat at ~20-21 in every configuration ever measured (spec
depth, spec type, PP on/off, ctx 64k/155k, ts 41/42/44). The ts-44 point
is the falsifier: moving ~4 positions (~2.4 GB) off the 3080 should have
saved ~5 ms/step if decode were streaming-bound, but TG did not move.
Decode is overhead-bound (serial pipeline + MTP draft sequencing), not
bandwidth-bound, so weight redistribution between stages cannot help.
-c ceiling itself is also neutral at equal fill (20.6 vs 20.2).

Clarification recorded: -c IS VRAM (KV lives in per-device GPU buffers;
the 158k/165k probes OOMed on Vulkan1 KV allocation). -cram is the
host-RAM prompt cache and is not on the decode path at all.

## WINNER: max perf+ctx with perf>ctx (2026-08-15, ub 64-step sweep)

ub sweep at 155k (TG_FILL=16384, same output sha throughout):

| ub | pp1 (best of runs) |
|---:|---:|
| 320 | - |
| 384 | 328.5 / 328.9 / 329.4 |
| 448 | 323.1-326.6 (5 runs) |
| 512 | 320.3 |
| 576 | 327.5 |
| 896 (c64k) | 312.8 |

ub=384 beats 448 by ~1.6% consistently (non-monotonic pattern with a dip
at 512; cause unexplored, empirically stable across 3 runs + 1 confirm).
Side effect: 384 compute buffers are small enough that PP-mode ctx
ceiling lifts 155k -> 160k (ub 448 at 160k fails to fit):

| config | pp1 | tg |
|---|---:|---:|
| 155k, ub448 (old production) | 323.5 | 20.6 |
| 155k, ub384 | 328.9 | 20.6 |
| 160k, ub384, PP on (NEW PRODUCTION) | 328.5-329.4 | 19.8-20.7 |
| 165k, ub384, PP on | 282.7 (KV cliff) | 20.4 |

NEW PRODUCTION: -c 160000 -ub 384, everything else unchanged. Strictly
dominates old production: +5000 ctx AND +5-6 pp1, TG unchanged within
noise. Launcher verified end-to-end (health, n_ctx 160000, chat OK).
165k remains the cliff even with PP on - rejected for perf.

## MMQ stall-reason PMU pass (2026-08-18, rocprof group D)

Question: is the ~59% VALU issue-rate gap in mul_mat_q schedulable
(dependency stalls) or structural? gfx906 has no SPI wave-stall counters,
so group D isolates what can be counted (recipe bench/rocprof-pmc-d.txt,
raw CSVs /tmp/opencode/rocprof/out-d, analyzer /tmp/opencode/rocprof/analyze_stall.py):

  pmc: GRBM_COUNT, GRBM_GUI_ACTIVE, SQ_ACTIVE_INST_VALU, SQ_INSTS_VALU,
       SQ_INSTS_LDS, SQ_WAVES, SQ_THREAD_CYCLES_VALU, SQ_INST_CYCLES_SALU,
       SQ_WAIT_INST_LDS

16k-token PP, production shapes, both VIIs, GUI busy 100% (kernels
back-to-back, gaps are inside kernel execution). mul_mat_q, GPU0:

| metric | value | reading |
|---|---:|---|
| VALU insts / busy cycle | 23.0 | reproduces 2026-08-15 (23.2); dot4 ceiling 57.2 |
| VALU-active fraction (x4/240 SIMDs) | 38.7% | = 23.0/57.2/0.95 - three derivations agree |
| arbiter pitch (VALU-active qc / inst) | 1.006 | SATURATED: 1 inst per active quad-cycle (GCN wave64 max) |
| SQ_WAIT_INST_LDS / VALU-active | 2.2% | LDS-issue wait negligible |
| SQ_INSTS_LDS / VALU insts | 0.193 | LDS throughput fine (matches old 1:5.18) |
| SQ_INST_CYCLES_SALU / VALU-active | 1.1% | scalar pipe idle, not competing |

(flash_attn and gdn DO wait on LDS - 29%/28% of their VALU-active - but
they are 8%/5% of busy time, not the target.)

### Verdict: latency-bound, not throughput-bound - SCHEDULABLE

Mechanism, consistent with every counter: the I=128 tile config runs 1
block/CU = 4 waves = exactly 1 wave per SIMD. The arbiter issues at max
pitch whenever the wave has a ready instruction (1.006), but the wave's
ready-instruction density is only ~39%: each per-block group ends in a
dependent chain dot4 -> I2F -> FMUL -> FMA on the same accumulator, and
with no second wave on the SIMD to fill the chain latency, the SIMD idles
~61% of cycles. No counted wait (LDS 2.2%, VMEM 1.5%, SALU 1.1%, bank
conflicts 0) accounts for it - the residual is intra-wave register
dependencies at 1-wave-per-SIMD occupancy.

Lever fallout (updates the list in "MMQ kernel headroom"):
1. deepen dot4 ILP per thread - already REJECTED empirically (k01 unroll,
   register spill, 3.3x slower). Confirmed: the fix is not more ILP per
   wave but more ready instructions per chain step.
2. prefetch/swizzle next K-tile to hide LDS latency - KILLED by counter
   (LDS-wait 2.2%). Do not attempt.
3. scale-free integer accumulation across k-blocks (dot4 -> dot4 chains on
   independent int32 accumulators, scales applied once in the epilogue) -
   THE remaining lever. This converts the inner loop into exactly the
   bench-dot4 shape (independent chains, 95% issue) and removes the
   per-8-dp4a I2F+2xFMUL+FADD from the dependency path. Projected from
   the standing table: 55-65% eff -> ~370-410 pp1.
   Risks unchanged: summation-order change (perplexity gate required),
   int32 overflow past ~4k blocks/accumulator (fixed-point/saturation
   handling), silent-wrong-answer failure mode.

Occupancy route is closed separately: more blocks/CU needs smaller tiles
(64-col config measured dead, occupancy 1) - the LDS budget at I=128
cannot fit a second block.

## MMQ experiment 2: k01 phase-split (2026-08-18) - REJECTED

Lever: split each k01 step of ggml_cuda_mmq_vec_dot_q8_0_q8_1_dp4a into an
all-int phase (32 independent dot4 chains into int sumi[32]) and an all-float
phase (batched scale+FMAC), same per-accumulator dataflow. Intent: take the
I2F/FMUL tail off the dot4 dependency path (the PMU-verdict mechanism).

ISA (gfx906, J=64, exact build flags, mmq-instance-q8_0.cu -S):

| metric | base | phase-split |
|---|---:|---:|
| hot-loop VALU insts | 881 | 795 |
| dot4 / VALU | 0.581 | 0.644 |
| s_waitcnt in loop | 152 | 100 |
| max VGPR | 118 | 233 (no spill) |

Result: pp1 302.6 vs 332.8 same-day baseline (-9%), 160k/ub384 config.
Greedy sha also diverged (00f93a039058 vs 847d5d35a65): under -ffast-math the
isolated float tail contracted differently, so the change was not even
numerically identical - exact-math scheduling restructures are NOT guaranteed
sha-stable under this build's flags.

Mechanism of the regression (from the ISA run-signature): the unrolled int
phase needs 128 y-operand values live per k01 step; at 233 VGPR the scheduler
could not keep grouped loads, and the dominant inner pattern degraded to
scalar ds_read + s_waitcnt + 2 dot4s - full LDS latency exposed after every
2 dot4 instructions. The baseline's per-impl-call form (4x ds_read2 grouped,
then the 8-dot4 chain) is the structurally better memory schedule; it only
looks dependency-poor in counters.

Lesson for any further MMQ work: preserve the grouped quad-ds_read2 operand
loads; source-level phase hints make the LLVM scheduler worse, not better.
Post-revert verify: pp1 332.2, sha == baseline sha. Tree at baseline state.

## MMQ stage 2 (scale-free) - design economics, NOT yet attempted

The surviving lever from the PMU verdict requires per-block scales to leave
the inner loop. The naive routes measured/estimated:

- In-kernel requant of BOTH sides per tile: ~+450 VALU/thread in the load
  phase (serialized before the compute by __syncthreads) vs ~-670 saved in
  the compute phase - marginal on paper, and adds the stage-1 scheduler risk
  to the load path.
- Offline weight requant (side copy of x with per-group scales): dead on
  VRAM (+tens of GB next to a 27B Q8_0 already split across 2x16 GB.
- Y-side-only group requant at quantize time is ~free (folds into the
  existing quantize kernel: amax over 128 instead of 32), but only removes
  1 of 3 tail ops unless x scales also coarsen.

The full design (y group-quantize at source + x group-requant at tile load +
pure-int accumulation across the whole kb0 loop + one float tail per tile)
projects a 3x shorter compute phase IF the pure-dot4 section schedules at
~80% issue like bench-dot4 - but it changes numerics by design (requant
error), so it needs a perplexity gate, not a sha gate, and the stage-1
scheduler lesson says the load-side restructure is where it will actually
win or die. Decision pending.

## MMQ experiment 3: full scale-free design (2026-08-18) - IMPLEMENTED, MEASURED, REJECTED

Design (all env-gated GGML_CUDA_MMQ_SCALE_FREE, default OFF):
- y quantizer (quantize.cu, MMQ_Q8_1_DS_LAYOUT_SF): one scale per 128
  values (amax/127), written to d4[0] only.
- x tile loader (mmq-load-tiles.cuh, ggml_cuda_mmq_load_tiles_q8_0_sf):
  pass 1 computes Dg = max(d0..d3) per 4-block group via 2x shfl_xor and
  stores it in the df plane at slot 4g (extra __syncthreads between
  passes); pass 2 requantizes each int8 as q' = (q*m + 128) >> 8 with
  m = round(256*d/Dg) (m=256 identity verified exact).
- vec_dot (mmq-vec-dot.cuh, ..._dp4a_sf): pure-int accumulation, chains
  seeded from the previous k01 step's sumi (register-to-register dot4
  chains, no cvt/mul/fmac inside), flush sum += Dgx*Dgy*cvt(sumi) once
  per 128-value group (96 float ops/kb0 vs 768 legacy).
- Runtime selection: template <bool sf> on mul_mat_q (NOT a runtime
  branch - compiling both paths in one function unified register
  allocation at 169 VGPR and cost the LEGACY path 15% (283.2 pp1,
  measured). Compile-time separation restored legacy to base codegen:
  sf=0 = 512 dot4 / 118 VGPR, byte-shape identical to base, verified
  330.3 pp1 / baseline sha.)

Gates:
- Correctness/PPL: llama-perplexity, 2x2048 tokens of README text:
  SF=0 2.4753 vs SF=1 2.4800 (+0.19%, PASS - requant error negligible).
- ISA: sf=1 kernel = 512 dot4 + 66 requant mullo + 64 flush-only cvt,
  0 spills, VGPR 216; SF loop shape verified pure (register-seeded
  chains, zero float on the dependency path).

Result (production ab-bench, 160k/ub384):
- SF=0: 330.3 pp1 (= baseline), SF=1: **238.3 pp1 (-28%)**, tg 21.1.
  Independent confirmation from the ppl harness: 8.92 -> 12.67 s/pass.

Mechanism: the requant arithmetic (66 v_mul_lo_u32 + byte extract/shift/
repack, ~+800 VALU/thread/kb0) lives in the loader, which is serialized
against compute by __syncthreads - its latency adds 1:1 to the tile
critical path. The compute-side structural win (verified present in ISA)
is smaller than the load-side cost. This is the failure mode the stage-1
lesson predicted: load-path restructures lose on this scheduler.

Verdict: scale-free via in-loader x requant is DEAD on gfx906. The code
stays in-tree, env-gated default OFF, for reuse if an offline requant
(weight-side precompute) ever becomes VRAM-feasible. All three levers
from the PMU verdict are now measured dead (LDS prefetch: counter-killed;
ILP unroll: spill-killed; scale-free: requant-cost-killed). The ~41%
issue-rate ceiling of mul_mat_q on gfx906 stands as a structural limit of
the I=128 tile config on this silicon. Production remains: legacy MMQ,
330-333 pp1, sha 847d5d35a659.

## MMQ experiment 4: dual accumulator chains (2026-09-02) - REJECTED

Lever (the one variant not in the 2026-08-18 triple): caller-level chain
split in mul_mat_q_process_tile - the two per-kb0 vec_dot calls feed
separate sum/sum_b accumulators (merged pre-write_back), halving the
serial dot4->I2F->FMUL->FADD chain per element. vec_dot bodies untouched
(phase-split lesson respected). Gated GGML_CUDA_VEGA_TUNE_MMQ_DUALACC,
default OFF, build-dualacc only.

ISA pre-check: hot J=64 kernels +32 VGPR exactly (Q6_K 152->184, Q8_0
119->151), all instances <= 249, zero new spill. E91 attribution:
96.9% of mul_mat_q cycles run J=64 fb=0 - the clean shapes, not the
ballooned J=48/24 ones.

Result (UD-Q6_K_L @256k ab-bench, E92 scripts): A 350.3 pp1 / B 304.3
(-13.1%), tg 16.4 -> 16.6, acc 0.664 both, sha 6b38a21df2bf BOTH
(reassociation never flipped a greedy argmax in 1024 tokens - numerics
impact negligible, verdict purely perf). #23685 ruled out as confound
(same-day rows 374.0/375.2, PP-flat).

Mechanism: at 1 wave/SIMD, doubling live accumulators (32 -> 64) costs
more in operand-collector/register-file pressure (and a worse LLVM
global schedule) than the chain-shortening recovers. Fourth family of
inner-loop restructures to regress (unroll, prefetch, phase-split,
scale-free, dual-acc): the ~41% issue-rate ceiling of mul_mat_q on
gfx906 is a structural limit for C++-level work under this compiler.
Route is CLOSED. Remaining PP levers: #21698 q8_0 loader instruction-mix
(~7-8% cap on UD, E91-pro-rated), Q5_K->Q6_K requant in a UD rev
(~2-3%), fattn_tile class (14.3%). Production unchanged (DUALACC never
default-on; build-dualacc retained as the experiment dir).

## MMQ experiment 5: #21698 q8_0 loader GCN5 remap (2026-09-02) - NO GAIN on fork config

Port of upstream PR #21698 (open, iacopPBK; MI50 +28-36% pp on pure
Q8_0 models): threads_per_row 32 -> 16 + unrolled k-loop in the q8_0
dp4a loader. Bit-identical writes (verified by hand + sha), q6_k
instance byte-identical, VGPR +9 (hot J64 119 -> 128). Gated
GGML_CUDA_VEGA_TUNE_MMQ_Q8LDR, default OFF, build-q8ldr.

Result (UD @256k ab-bench): A 347.2 / B 350.6 pp1 (+1.0%, inside the
day-over-day noise band: yesterday's A was 350.3), tg 16.2/16.1, acc
.664 both, sha 6b38a21df2bf both. The E91 pro-rated +7-8% did NOT
materialize.

Explanation: the PR's MI50 numbers were measured under UPSTREAM's
gfx906 config = the RDNA2 fallback table, not our vega I=128/J=64/256thr
table. The 16-thread remap's benefit is config-dependent; on our tile
geometry it is neutral. Not worth keeping on. Q8LDR stays default OFF.

Side finding: raw `./ab-bench.sh` runs (defaults: CTX=155000, MTP
default drafter, BIN default build-vega20) produced pp_first 309-324 in
live.log and read as a "regression" - apples-to-oranges, see E88 note.
ab-bench.sh BIN default now updated to build-dflash-novega to kill this
trap at the source.

CORRECTION (2026-09-02, E95 side-finding): the "pp way down" report was
NOT the raw-harness live.log runs - those are dated 2026-08-15. Actual
cause: ab-q8ldr.sh was generated from ab-dualacc.sh with sed that
replaced the trial names but missed the summary grep pattern, so the
script's "== trial rows:" footer printed the previous experiment's rows
(dualacc-B 304.3, the E93 regression). The real q8ldr rows were correct
in trials.md all along (347.2/350.6). Grep fixed. The ab-bench BIN
default change stands on its own merits (stale build-vega20 pointer).

## MMQ experiment 6: UD v2 Q5_K->Q6_K splice (2026-09-02) - PP-NEUTRAL, model corrected

Lever: E91 attribution showed Q5_K at 1.30 cyc/byte vs Q6_K 0.74
(8.6% of MMQ cycles for 6.6% of bytes). v2 = L with all 38 Q5_K
tensors promoted to imatrix Q6_K (828/866 tensors byte-identical,
journal E96). Units model predicted +3.8% pp.

Result (ab-udv2.sh, same binary, only model differs): A 346.0 / B
345.8 pp1 (-0.06%, noise), tg 16.5 -> 16.8 (+1.8%, weak positive),
acc .664/.648 (band), sha moved as designed (weights changed).

Post-mortem of the model error:
- Drafter contamination ruled out: grid-size split of the attribution
  CSV shows 25.03/25.03 Gcyc of Q5_K ran in target PP shapes.
- Remaining explanation: pipeline stage criticality. The Q5_K class
  sat entirely on GPU0 (16% of GPU0 busy) - attribution shares count
  cycles, not critical-path contribution. Removing non-binding-stage
  work does not move a layer-split pipeline's end-to-end rate.
- LESSON: per-type attribution shares are UPPER BOUNDS on recoverable
  PP. Any mix-surgery projection must be discounted by stage
  criticality, which only an A/B measures. Update the cost model in
  .opencode/skills/requant-gguf-gfx906-perf accordingly.

Disposition: v2 is PP-neutral, TG mildly positive, quality strictly
>= L (38 tensors up-quantized, imatrix). Adopt for quality at +300
MiB if wanted; discard otherwise. Production L unchanged. This closes
the mix-surgery PP lever on this rig.

## FATTN experiment 1: pipelined KQ k-steps (2026-09-02) - REJECTED

Lever: iter_KQ f16 path, double-buffered register fragments prefetching
step s+1's LDS operands during step s's MADs, attacking the measured
31.1% SQ_WAIT_INST_LDS (E99). Gated GGML_CUDA_VEGA_TUNE_FATTN_QPIPE,
default OFF, build-qpipe. ISA gates passed: hot <256,256,16,2> VGPR
94 -> 111, no new spill, private_segment <= baseline.

Result (bench-fattn-tile kv120k): 130.459 ms vs 123.257 baseline
(-5.8%), max-abs 0.00000 (bit-identical as designed). Correct tooling,
wrong direction.

Verdict: 6th consecutive source-level scheduling restructure to regress
(k01 unroll, prefetch, phase-split, scale-free, dual-acc, qpipe - across
two different kernel families now). On gfx906 + ROCm 6.1 clang, tight
per-step loop scoping beats every manual latency-hiding structure; the
compiler's own schedule is a local optimum. Loop-restructure route is
closed for FATTN as well. QPIPE stays default OFF.

Remaining untried fattn lever (fork's PROVEN modality - config tables,
not loops): geometry swap via the launch switch threshold, forcing the
ncols=16 table row (256,256,16,256,5,32,256) = occupancy-5 config with
nbatch_fa 32 / nbatch_K 256 instead of the current (256,256,32,256,3,
64,128). One threshold flip + microbench run decides.
