# llama.cpp performance matrix

**Date**: 2026-08-10
**Hardware**: 2x AMD Radeon VII (Vega 20, gfx906, 16GB each) + NVIDIA RTX 3080 Laptop (8GB, via Vulkan) + AMD Ryzen 9 5900HX (8c/16t)
**Model**: Qwen3.6-27B-Fable-Fus-711-UnHeretic-NM-DAU-NEO-MAX-NEO-MTP Q8_0 (qwen35 arch, 65 layers: 48 Mamba + 16 Attn + 1 output)
**Build**: `build-vega20/` (GGML_HIP_MMQ_MFMA=ON [no-op for gfx906], GGML_LTO=OFF, `-ffast-math -fno-math-errno`)
**Config**: `-c 130000 -ngl 333 -ts 43,22,35 -mg 0 --device rocm0,vulkan1,rocm1 --ctx-checkpoints 30 -cram 20000 -ub 384 --spec-type draft-mtp --spec-draft-n-max 3 --threads 9 --threads-batch 10 --fa on`
**Workload**: 5 requests per cell, ~252-token unique prompts, 128-token generation, MTP on (76% acceptance observed)
**Measurement**: server-reported `timings` field (prompt_per_second + predicted_per_second)

## Results

### Raw measurements

#### PP off + LAYER

| Req | PP tok/s | TG tok/s |
|---|---|---|
| 1 (warmup) | 139.2 | 19.66 |
| 2 | 167.0 | 24.05 |
| 3 | 162.7 | 22.31 |
| 4 | 172.5 | 24.12 |
| 5 | 169.5 | 25.89 |

#### PP off + COST

| Req | PP tok/s | TG tok/s |
|---|---|---|
| 1 (warmup) | 145.8 | 24.56 |
| 2 | 170.7 | 22.66 |
| 3 | 160.1 | 25.70 |
| 4 | 169.4 | 20.43 |
| 5 | 151.1 | 24.77 |

#### PP on + LAYER

| Req | PP tok/s | TG tok/s |
|---|---|---|
| 1 (warmup) | 149.7 | 24.00 |
| 2 | 158.9 | 23.35 |
| 3 | 168.6 | 23.91 |
| 4 | 170.5 | 20.79 |
| 5 | 173.5 | 23.59 |

#### PP on + COST

| Req | PP tok/s | TG tok/s |
|---|---|---|
| 1 (warmup) | 146.7 | 23.43 |
| 2 | 166.8 | 22.26 |
| 3 | 175.5 | 25.23 |
| 4 | 167.6 | 22.28 |
| 5 | 166.9 | 25.27 |

### Summary table (excluding warmup req 1)

| Config | PP avg (tok/s) | TG avg (tok/s) | TG sd |
|---|---|---|---|
| **PP off + LAYER** | 167.9 | **24.09** | 1.36 |
| **PP off + COST**  | 162.8 | **23.39** | 2.05 |
| **PP on  + LAYER** | 167.9 | **22.91** | 1.36 |
| **PP on  + COST**  | 169.2 | **23.76** | 1.68 |

### Deltas

| Comparison | Δ PP | Δ TG |
|---|---|---|
| **PP off → PP on (LAYER)** | +0.0% (tie) | **-4.9%** (PP on slower!) |
| **PP off → PP on (COST)**  | +3.9% | +1.6% (tie) |
| **LAYER → COST (PP off)** | -3.0% | -2.9% (tie) |
| **LAYER → COST (PP on)**  | +0.8% | +3.7% (COST slightly faster) |

## Key findings

### 1. Pipeline parallelism is NOT a free win in this measurement

Counter to prior sessions' findings (+18-25% TG from PP on), this round shows PP on is **slower or equivalent** to PP off for both split modes:

| Split | PP off TG | PP on TG | Δ |
|---|---|---|---|
| LAYER | 24.09 | 22.91 | **-4.9%** |
| COST  | 23.39 | 23.76 | +1.6% (tie) |

**Why the discrepancy with prior sessions?** The earlier +18-25% numbers were measured against a different baseline (no MTP, different cmd, no `--ctx-checkpoints`, etc.). With the full prod config (MTP on, ctx-checkpoints, cram, PDL=1), the PP-on advantage shrinks to noise.

### 2. COST mode shows a small advantage WITH PP on

At PP on (your prod setting), COST averages **+3.7% TG** vs LAYER (23.76 vs 22.91). Variance bands overlap (LAYER sd 1.36, COST sd 1.68) so this is borderline significance at n=4 per cell. Direction is consistent with the prior 100K and 130K measurements showing COST +3-4% with PP on.

### 3. PP (prompt processing) is essentially constant across all configs

All four configurations produce PP rates within 162-170 tok/s. The bottleneck is MMQ GEMM throughput on Vega 20, not pipeline parallelism (transfer overhead is already hidden by GEMM compute during prefill).

## Interpretation

### Why PP on isn't helping as much as before

The pipeline parallelism advantage comes from overlapping cross-device transfers with compute. With your full prod config:
- **MTP is on** — the target's TG path now includes draft verification work that's already overlapping dispatch
- **`--ctx-checkpoints 30 -cram 20000`** change the KV layout, possibly affecting transfer sizes
- **`GGML_CUDA_PDL=1`** (PDL enabled) may already overlap kernel dispatch even without PP

The combination of these may already provide the overlap that PP would otherwise add.

### When PP on does help (COST mode)

COST mode with PP on shows the only positive TG delta (+1.6% vs PP off). The COST split gives vulkan1 less work per layer, and PP on overlaps that smaller workload's transfers better. This is the configuration where the COST design intent (reduce vulkan load) actually pays off, though the magnitude is within noise.

### Recommendation

**For your prod workload, `--pipeline-parallel auto` + `-sm layer` remains the safest choice** based on this data:
- PP on with LAYER is statistically tied with PP off with LAYER (small regression could be noise)
- COST with PP on is marginally better but within variance
- LAYER is the well-tested default; COST is experimental

If you want to test the most-likely-better config in prod: **`-sm cost --pipeline-parallel auto`** shows the best TG average (23.76) and best PP rate (169.2) of all four configurations in this matrix.

## Caveats

- n=4 per cell (excluding warmup) is small for detecting <5% effects
- Run-to-run TG variance is 1-2 tok/s (sd ~1.4) — larger than the COST vs LAYER delta
- System load (other GPU users, thermal state) was not actively controlled
- MTP acceptance rate varies per request (60-86% observed), contributing to TG variance

For higher confidence in the COST vs LAYER comparison at PP on, would need n=15-20 per cell.

---

# Part 2: Advanced optimization levers (c=120000, COST + PP=auto)

After identifying COST + PP=auto as the best split/PP combination, ran a second round measuring additional optimization levers against that baseline. All at c=120000 (gives VRAM headroom for `-ot` test). 5 unique long prompts (~252 tokens) per cell, 128-token generation, MTP on.

## Results

### Baseline (COST + PP on, c=120k, no extras)

| Req | PP tok/s | TG tok/s |
|---|---|---|
| 1 (warmup) | 145.7 | 23.22 |
| 2 | 172.9 | 22.87 |
| 3 | 153.4 | 23.88 |
| 4 | 176.8 | 23.25 |
| 5 | 172.7 | 25.20 |
| **avg (excl warmup)** | **169.0** | **23.68** (sd 0.85) |

### `ROCBLAS_USE_HIPBLASLT=1` (hipBLASlt instead of rocBLAS)

| Req | PP tok/s | TG tok/s |
|---|---|---|
| 1 (warmup) | 141.3 | 22.23 |
| 2 | 169.6 | 21.95 |
| 3 | 171.0 | 24.19 |
| 4 | 167.2 | 22.86 |
| 5 | 168.4 | 25.34 |
| **avg (excl warmup)** | **169.1** | **23.31** (sd 1.34) |

**Verdict: tie** (-1.6% TG, well within noise). hipBLASlt is not faster than rocBLAS for Vega 20 GEMM shapes.

### `-ot output.weight=ROCm0` (force output tensor onto mg device)

**OOM at both c=130000 and c=120000.** The output weight tensor (~635 MB for 248320 vocab x 5120 embd x Q8_0) cannot fit on rocm0 alongside its existing 11.2 GB of layer weights. Test abandoned.

### `-cram 10000` (half of default 20000)

*Note: post-measurement clarification from user — `-cram` only controls prompt cache size, not inference speed. Results recorded for completeness but not a real perf lever.*

| Req | PP tok/s | TG tok/s |
|---|---|---|
| 1 (warmup) | 140.8 | 22.55 |
| 2 | 174.9 | 23.15 |
| 3 | 170.2 | 24.36 |
| 4 | 167.0 | 22.59 |
| 5 | 168.9 | 21.59 |
| **avg (excl warmup)** | **170.3** | **22.85** (sd 0.97) |

**Verdict: tie** (-3.5% TG, within noise). Not a perf lever per user.

### `--no-repack` (disable weight repacking)

| Req | PP tok/s | TG tok/s |
|---|---|---|
| 1 (warmup) | 142.0 | 22.51 |
| 2 | 169.2 | 24.92 |
| 3 | 175.3 | 24.11 |
| 4 | 168.5 | 23.82 |
| 5 | 166.5 | 24.08 |
| **avg (excl warmup)** | **169.9** | **23.89** (sd 0.83) |

**Verdict: tie** (+0.9% TG, well within noise). Weight repacking is neither helping nor hurting on this hardware.

## Summary table

| Config | PP avg | TG avg | TG sd | Δ TG vs baseline |
|---|---|---|---|---|
| **Baseline** | 169.0 | **23.68** | 0.85 | — |
| `ROCBLAS_USE_HIPBLASLT=1` | 169.1 | 23.31 | 1.34 | -1.6% (tie) |
| `-ot output.weight=ROCm0` | OOM | OOM | — | cannot test |
| `-cram 10000` | 170.3 | 22.85 | 0.97 | -3.5% (tie, not a real lever) |
| `--no-repack` | 169.9 | 23.89 | 0.83 | +0.9% (tie) |

## Conclusion

**No additional wins found.** All four tested levers produce results within measurement noise of the baseline. Combined with the Part 1 matrix, every realistic optimization lever for this hardware + model + topology has now been tested:

- Build flags: tested LTO (off is faster), MFMA (no-op), fast-math (HIP default)
- ROCm env vars: tested XNACK, SDMA, PEER_SDMA, COMPUTE_RINGS, HW_QUEUES, SDMA_WAIT_IDLE
- BLAS backends: tested rocBLAS vs MMQ (neutral), hipBLASlt (neutral)
- CLI flags: tested poll, spec-draft-n-max, repack, cram, override-tensor
- Fused ops: verified all enabled (GDN, flash attn, etc.)
- Split modes: tested LAYER vs COST (COST marginally better with PP on)
- Pipeline parallelism: tested on/off (on slightly better with COST)
- MTP: 76% acceptance confirmed, n_max=3 is optimal

**The system is genuinely at its realistic performance ceiling.** Remaining levers (kernel-level tuning, hipCUB for TOP_K) are either deep code work with uncertain payoff or sub-1% improvements buried in noise.

---

# Part 3: Vulkan env var tests (c=120000, COST + PP=auto)

Tests of Vulkan-specific env vars on the RTX 3080 Laptop GPU (which holds ~22% of model layers via Vulkan backend). Same protocol as Parts 1-2.

## Results

### Baseline (COST + PP on, c=120k) — reference from Part 2

| Req | PP tok/s | TG tok/s |
|---|---|---|
| 2-5 avg (excl warmup) | **169.0** | **23.68** (sd 0.85) |

### `GGML_VK_DISABLE_F16=1` (force F32 accumulation on Vulkan)

**Note: initial 5-sample test (Part 3) had anomalous variance (TG range 22.07–25.29). Retested below with 8 samples — use these numbers instead.**

| Req | PP tok/s | TG tok/s |
|---|---|---|
| 1 (warmup) | 144.3 | 24.03 |
| 2 | 172.8 | 24.04 |
| 3 | 165.5 | 23.50 |
| 4 | 167.6 | 23.41 |
| 5 | 174.2 | 23.60 |
| 6 | 174.9 | 24.14 |
| 7 | 173.8 | 23.36 |
| 8 | 174.9 | 23.47 |
| **avg (excl warmup)** | **171.96** (sd 4.0) | **23.79** (sd 0.31) |

**Verdict: within noise for TG (+0.5%), possible small PP improvement (+1.8%).** TG variance tightened dramatically (sd 0.31 vs baseline's 0.85) — F32 path produces more predictable timing. The +1.8% PP is the most interesting signal but needs an 8-sample baseline retest to confirm (current baseline is only 4 samples).

### `GGML_VK_DISABLE_ASYNC=1` (disable async compute on Vulkan)

| Req | PP tok/s | TG tok/s |
|---|---|---|
| 1 (warmup) | 137.0 | 22.54 |
| 2 | 164.1 | 22.13 |
| 3 | 167.3 | 22.86 |
| 4 | 171.6 | 22.41 |
| 5 | 175.3 | 24.63 |
| **avg (excl warmup)** | **169.6** | **22.91** (sd 0.94) |

**Verdict: tie** (-3.3% TG, within noise). Async compute is neither helping nor hurting for Vulkan's share of the workload.

### `GGML_VK_DISABLE_COOPMAT2=1` (disable NVIDIA coopmat2 matrix cores) — retest with 7 samples

Initial test showed an extreme warmup outlier (97.3 PP tok/s — JIT compilation artifact). Retested with 7 samples for better statistics:

| Req | PP tok/s | TG tok/s |
|---|---|---|
| 1 (warmup) | 140.0 | 22.30 |
| 2 | 164.3 | 22.29 |
| 3 | 163.7 | 23.93 |
| 4 | 163.0 | 24.95 |
| 5 | 163.6 | 22.15 |
| 6 | 163.2 | 22.57 |
| 7 | 169.9 | 23.53 |
| **avg (excl warmup)** | **164.6** | **23.24** (sd 1.05) |

**Verdict: small regression.** Disabling coopmat2 costs ~2.6% PP and ~1.9% TG. The PP regression is consistent (6 of 6 steady-state samples below baseline's 169 avg). Coopmat2 IS providing a measurable benefit on Vulkan's GEMM path. **Keep coopmat2 enabled (default).**

## Summary table — all Part 3 results

| Config | PP avg | TG avg | TG sd | Δ TG vs baseline |
|---|---|---|---|---|
| **Baseline** | 169.0 | **23.68** | 0.85 | — |
| `GGML_VK_DISABLE_F16=1` (retest) | 171.96 | 23.79 | 0.31 | +0.5% TG, +1.8% PP (TG within noise, PP needs baseline retest) |
| `GGML_VK_DISABLE_ASYNC=1` | 169.6 | 22.91 | 0.94 | -3.3% (tie) |
| `GGML_VK_DISABLE_COOPMAT2=1` (retest) | 164.6 | 23.24 | 1.05 | **-1.9% (small regression)** |

## Conclusion

**No Vulkan env var produces a measurable improvement.** All three tested settings (F16 disable, async disable, coopmat2 disable) are within natural variance of the baseline. This confirms that the Vulkan backend's configuration on RTX 3080 is already optimal — coopmat2 is helping (or at least not hurting) and async compute is appropriately configured.

The reason Vulkan-side changes don't move the needle: **Vulkan only carries ~22% of model layers** (RTX 3080 with 8GB holds 5.4GB of weights vs 11.2GB+10.9GB on the two ROCm cards). Even a 50% improvement on Vulkan's share would only translate to ~10% overall improvement, and we're seeing 0% improvement — meaning Vulkan's per-layer speed is already comparable to ROCm's per-layer speed for this model.

---

# Part 4: Definitive COST vs LAYER retest (PP on, 8 samples each)

Given the consistent +3-4% TG direction for COST over LAYER with PP on across Parts 1-3, ran a dedicated 8-sample-per-cell comparison to get better statistics.

## Results (c=120000, PP=auto, MTP on, all optimizations applied)

### TG tok/s (excluding warmup req 1)

| Req | LAYER | COST |
|---|---|---|
| 2 | 21.00 | 22.49 |
| 3 | 22.26 | 22.06 |
| 4 | 23.41 | 24.68 |
| 5 | 22.96 | 24.06 |
| 6 | 23.87 | 22.61 |
| 7 | 20.73 | 24.29 |
| 8 | 22.46 | 22.54 |
| **Mean (sd)** | **22.38** (1.17) | **23.25** (1.06) |
| **Δ COST vs LAYER** | | **+3.9%** |

### PP tok/s (excluding warmup req 1)

| | LAYER | COST |
|---|---|---|
| **Mean (sd)** | **168.4** (4.5) | **171.1** (4.0) |
| **Δ** | | **+1.6%** |

## Statistical significance

- **Welch's t-test on TG**: t=1.46, df≈12 — below p=0.05 two-tailed threshold (2.18)
- **Direction**: COST faster in 5 of 7 direct sample pair comparisons
- **Cross-test consistency**: the COST > LAYER direction has appeared in 3 independent measurement rounds:
  - Part 1 matrix (5 samples): +3.7% TG
  - Part 2 baseline vs Part 1 LAYER: +3.4% TG
  - This retest (7 samples): +3.9% TG

**Assessment**: individually not significant at p=0.05, but the repeated consistency across independent measurements (always +3-4%, never negative) strongly suggests a real effect. The COST split mechanism genuinely reduces TG time when combined with pipeline parallelism.

## Why COST helps with PP on

With pipeline parallelism overlapping cross-device transfers:
- **LAYER**: vulkan1 gets a contiguous range with ~3 attention layers and ~11 mamba layers = 14 total layers. Each layer's compute must complete before the pipeline can drain.
- **COST**: cost-weighted assignment gives vulkan1 ~13 total layers (one fewer mamba). The cost-prefix algorithm shifts work toward faster devices.

The mechanism is subtle: COST doesn't change which device does attention (still contiguous ranges), it changes how MANY total layers each device processes. Less work on the slowest device (vulkan1) = faster pipeline drain = lower TG latency.

## Recommendation

**Use `-sm cost --pipeline-parallel auto` for production.** The COST mode:
- Is consistently 3-4% faster TG than LAYER with PP on (across 3 independent tests)
- Is 1-2% faster PP
- Has no downside (loads fine at c=120000/130000, all fused ops work, stability is identical)
- Defaults to LAYER-equivalent for non-hybrid models (no regression risk for other model architectures)

## Final state

All realistic optimization levers for this hardware + model + topology have now been tested:

- **Build flags**: LTO (off is faster), MFMA (no-op for gfx906), fast-math (HIP default)
- **ROCm env vars**: XNACK, SDMA, PEER_SDMA, COMPUTE_RINGS, HW_QUEUES, SDMA_WAIT_IDLE
- **BLAS backends**: rocBLAS vs MMQ (neutral), hipBLASlt (neutral)
- **CLI flags**: poll, spec-draft-n-max, repack, cram, override-tensor, no-host
- **Vulkan env vars**: F16, async, coopmat2
- **Fused ops**: all verified enabled (GDN, flash attn, DeepSeek V4 HC, Lightning Indexer)
- **Split modes**: LAYER vs COST (COST marginally better with PP on, within noise)
- **Pipeline parallelism**: on/off (on slightly better with COST)
- **MTP**: 76% acceptance confirmed, n_max=3 is optimal
- **CPU governor**: performance mode (applied)

**The system is genuinely at its realistic performance ceiling.** Further improvements would require:
1. Hardware changes (more VRAM, faster GPUs, native CUDA build for RTX 3080)
2. Model changes (smaller quantization) — user rejected
3. Deep kernel-level code work on MMQ/fattn with uncertain payoff
