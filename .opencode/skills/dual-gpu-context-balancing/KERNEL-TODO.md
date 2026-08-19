# Kernel TODO (post q8-shadow-fix, 2026-08-17)

Ideas that survived the tuning sessions but are NOT yet implemented.
Each entry: what, why, expected gain, cost/risk, kill criteria.

## 1. Split-plane q8_0 KV layout -> vectorized tile loaders

Status: IMPLEMENTED, MEASURED, KILLED (2026-08-18). Do not revisit without
a new microarchitectural insight.

Verdict (matched pairs, clean build, Q6_K_XL + q8/q8 KV @ 262k cap,
-ts 39,21,40 -sm layer, 110k-token fill):

- first 16384-token batch: canonical 323.6 t/s vs split 319.1 (-1.4%)
- 110k whole-fill average: canonical 192.2 t/s vs split 176.6 (-8.1%)
- harness pp1: 322.6 vs 315.3 (-2.3%); tg 19.8 vs 18.9 (-4.5%)

Mixed KV (F16 K + q8 V, V-split only, production q6v config @ 210k,
matched pair 2026-08-18): first batch 341.0 vs 333.5 (-2.2%), 110k
whole-fill avg 205.8 vs 188.9 (-8.2%), tg@110k 20.21 vs 20.24 (neutral).
The earlier "+6.5% mixed" was also a stale-baseline artifact (and was
measured on the broken-stride binary). Same -8% deep-fill pattern as
q8/q8: the 16B-vector split V loader loses to the coalesced scalar-ushort
canonical loader on gfx906 at depth, in every KV combination tested.

The regression grows with depth - opposite of the design hypothesis. On
gfx906 the fork's canonical scalar-ushort q8_0 loader (consecutive threads
read consecutive ushorts -> coalesced) beats 16B vector loads with split
d/qs addressing. The earlier "+18.8% split" session number was measured
against a stale pre-shadow-fix canonical binary (263.5); the real canonical
on the same build is 322.

Correctness work that landed and is kept (env-gated, default OFF):

- GGML_TYPE_Q8_0S (43), type_size = 34 B/block (2 d + 32 qs, NOT 36 -
  virtual strides must match the physical 272 B head-slice layout)
- row/slice layout: per-256-elem head slice = [8 x fp16 d][256 int8 qs]
- writers: cpy_f32_q8_0s, k_set_rows_q8_0s, CPU quantize_row_q8_0s_ref
- readers: fattn tile loaders q8_0s (16B vector qs), vec dot/dequant
- llama-kv-cache remap via GGML_KV_SPLIT_Q8=k|v|kv (ROCm layers only,
  head-dim 256 gate in dispatch)
- verified token-identical vs canonical at 8k ctx, deterministic across runs

Re-enable for experiments with GGML_KV_SPLIT_Q8=kv - but any future attempt
needs a different loader design, not this one.

### Original problem (kept for context)

q8_0 blocks are 34 bytes: fp16 scale `d` then 32 int8 quants (`qs`).
In the KV cache, `qs` therefore sits at offset 2 of a 34-byte row stride,
so `qs` is only guaranteed 2-byte aligned. The tile loaders in
`ggml/src/ggml-cuda/fattn-tile.cuh` (`flash_attn_tile_load_tile_q8_0`,
half2 and float variants) must read `ushort` one at a time:

    const ushort * qs = (const ushort *) blk->qs; // qs is only 2-byte aligned
    for (int l = 0; l < 16; ++l) { const ushort u = qs[l]; ... }

At deep fills (100k+ KV) attention is pure KV-stream bandwidth and the
per-load instruction overhead + narrow bursts cap the kernel. Round-2
notes already flagged this as "BLOCKED structurally" - it is blocked for
the *on-disk/in-cache q8_0 format*, not for a fork-local cache layout.

### Design sketch

Fork-local KV cache layout with two separate planes per K (and V) tensor:

- plane A: the `d` scales, one fp16 per 32-element block, contiguous
  (n_kv x n_blocks_per_head_row fp16);
- plane B: the raw `qs` bytes, 32-byte aligned rows, contiguous
  (n_kv x 32*n_blocks int8), 16-byte aligned by construction.

Loader then issues 16-byte vector loads on plane B and scalar/short loads
on plane A, dequantizing in SRAM exactly as today. Touch points:

- KV cache allocation path (llama-context / ggml-cuda KV views) - write
  planes at cache-fill time (quantization kernel splits its output);
- `fattn-tile.cuh` q8_0 loaders - new addressing, vectorized;
- VEC kernel + any CPU fallback that reads the cache - either keep a
  compatibility branch on layout version or convert them too;
- KV cache IO (state save/load, --cache-reuse) - must serialize in the
  standard q8_0 layout or carry a layout tag.

### Expected gain

+10-20% deep-fill pp (216 -> ~235-260 tok/s @100k). Shallow pp: neutral
(not KV-bound). tg: neutral (VEC path, per-row reads already hidden).

### Cost / risk

Invasive: cache alloc + quant kernels + 2 loaders + VEC fallback + state
serialization. Risk of subtle correctness drift between planes. Must be
A/B-able at runtime (env toggle) so production can fall back.

### Kill criteria

- Prototype loader microbench (synthetic 100k-depth q8 KV stream) shows
  < 8% end-to-end kernel gain, or
- e2e deep-fill pp gain < 5% after integration, or
- any output divergence vs standard layout (token-for-token, greedy).

## 2. Small fish (only if bored, sub-1% each)

- Tail/verify dispatch: Q rows 3..16 now ride the 32-col tile config;
  a cols_per_block = 8 variant for Q->ne[1] <= 8 would cut wasted Q-tile
  compute in prompt tails and MTP verify. ~20 lines in fattn-tile.cuh
  dispatch. Measure across a 180k prefill before keeping.
- tg: nothing kernel-side left (weights-bandwidth-bound; acceptance is a
  model-quality property, not kernel efficiency).

## Context

- q8-shadow dispatch fix (2026-08-17, fattn-tile.cuh) removed the F16
  shadow writes that corrupted pools and capped ctx fits; ceilings were
  re-laddered after (see scripts/trials.md, same date).
- Measured dead, do not revisit: 64-col config (occupancy 1), nbatch_fa 64,
  ub ladder past 384, q4 KV, -sm tensor for 4-KV-head models, HIP graphs
  (already ON in build-vega20), n-max 3.
