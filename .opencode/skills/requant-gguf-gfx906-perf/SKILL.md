---
name: requant-gguf-gfx906-perf
description: Procedure for picking and building GGUF quant mixes that maximize llama.cpp prompt-processing speed on gfx906 (Vega 20 / MI50 / Radeon VII) multi-GPU rigs. Use when choosing between UD/stock quant variants for a model; when a GGUF mix underperforms per-byte expectations on ROCm; when planning a per-tensor requant (swap Q5_K/IQ tails to Q6_K/Q8_0); when building a donor+splice variant that keeps production tensors byte-identical; when sizing a mix change against per-device VRAM fit margins; when validating a new mix (composition, byte-identity, perplexity, PP lane). Front-loads keywords: requant, GGUF mix, imatrix, tensor swap, per-byte MMQ cost, Q5_K tail, UD Q6_K, gfx906, Radeon VII, prompt processing, llama.cpp.
---

# Requantize GGUF for gfx906 Performance

## Purpose

On gfx906, prompt processing (PP) cost is dominated by dp4a MMQ GEMM
cycles, and the quant MIX - not the file size - decides them. This skill
converts that fact into a repeatable procedure: survey candidate quants
without downloading them, model their PP cost, and build a surgical
variant that fixes a bad mix while keeping the rest of the production
model byte-identical.

Ground truth measurements (rocprof per-type attribution, journal E91,
2026-09-02, Qwen3.8-27B UD lane, 2x Radeon VII):

| type | share of MMQ cycles | share of bytes | relative cycles/byte |
|---|---|---|---|
| Q6_K | 40.5% | 55.1% | 0.74 |
| Q8_0 | 25.5% | 38.0% | 0.67 (cheapest) |
| Q5_K | 8.6% | 6.6% | **1.30 (worst, ~1.8x Q6_K)** |

Rules that follow:

- K-quants with single-level or simple scales (Q8_0, Q6_K) are the
  efficient classes on gfx906. Q5_K pays extra for 5th-bit extraction
  plus two-level scale handling in every vec_dot.
- Smaller file != faster. A 20.5 GiB mix with 22% Q5_K measured ~5%
  slower than a 22.5 GiB mix with 6.6% Q5_K (journal E96).
- Model a candidate: `units = sum over types(bytes_GiB * cost)`,
  `est_pp = baseline_pp * baseline_units / units`.
  Costs: Q8_0 0.67, Q6_K 0.74, Q5_K 1.30; IQ types and Q4_K worse
  (bit/grid unpacking); estimate IQ3/Q2 at 1.8-2.5. These constants
  were measured on one model family - re-derive from a rocprof pass
  (see bench/FINDINGS.md "PMU profiling verdict") when the model
  family changes.

## Survey stock variants without downloading

GGUF tensor directories sit in the header; 32 MB covers large
tokenizers. Fetch prefixes and parse:

```bash
curl -sL -r 0-32000000 "<hf-url>/resolve/main/<file>.gguf" -o hdr.bin
python3 - <<'EOF'
# parse magic/counts, walk KV (mind arrays), walk tensor dir,
# accumulate ne*bpw/8 per type; bpw: Q8_0 8.5, Q6_K 6.5625,
# Q5_K 5.5, Q4_K 4.5, IQ4_XS 4.25, BF16 16
EOF
```

Type ids from the local tree (ggml/include/ggml.h): Q8_0=8, Q2_K=10,
Q3_K=11, Q4_K=12, Q5_K=13, Q6_K=14, IQ4_NL=20, IQ3_S=21, IQ4_XS=23,
BF16=30. Do not trust memory - re-check the enum.

## Build a surgical variant (donor + splice)

Goal: keep >=90% of tensors byte-identical to production so A/B deltas
and repro shas attribute cleanly to the swapped tensors.

1. Get the model author's imatrix if it exists (e.g.
   `imatrix_unsloth.gguf` in unsloth GGUF repos). It keeps the new
   tensors consistent with the original quant methodology.
2. Quantize a full donor from the highest-bpw source on disk (F16/BF16
   ideal; Q8_0 is a near-transparent intermediate):

   ```bash
   llama-quantize --allow-requantize --imatrix imatrix.gguf \
       SOURCE-Q8_0.gguf /path/on/DISK/donor.gguf Q6_K
   ```

   27B takes ~2 min on 16 cores. Never place multi-GB donors on tmpfs
   (/tmp) - they eat RAM next to the running server (cram!). Delete
   the donor after splicing; it rebuilds in minutes.

3. Splice with bench/mk-gguf-tensor-swap.py (rebuilds the tensor
   directory: new types + recomputed offsets, KV verbatim, data
   byte-exact from base or donor):

   ```bash
   python3 bench/mk-gguf-tensor-swap.py \
       BASE.gguf DONOR.gguf OUT.gguf q5_k=q6_k [--dry-run]
   ```

   Use --dry-run first: it lists every swapped tensor and the output
   size without writing.

4. Verify before any GPU run:

   ```python
   import gguf, collections, hashlib
   r = gguf.GGUFReader('OUT.gguf')          # parses clean
   # per-type composition; n_tensors matches base
   # swapped tensor sha == donor tensor sha
   # kept tensor sha == base tensor sha
   # first-4KB probe across all tensors: expect n_tensors - n_swapped
   ```

## Quality rules

- Only move tensors UP the bpw ladder (Q5_K -> Q6_K) from a
  near-transparent source. Quality then can only improve; the v2
  splice (E96) kept 828/866 tensors byte-identical and raised 38.
- Transcoding existing quantized data to a bigger type is worthless:
  it keeps the old quantization error and grows the file.
- Requantizing from Q8_0 instead of F16 adds a small second-stage
  penalty; Q8_0 error is negligible against the target type's own.
- Acceptance gates for a perf splice: PP lane A/B (expected from the
  units model), perplexity <= baseline, draft-acc within noise.
  The repro sha WILL move - weights changed by design; do not chase it.

## Fit accounting

A mix change shifts bytes on every device that hosts swapped layers.
Check against per-device fit margins from the production launcher
notes (LISTENS free line or E-entries). Rough split for a layer split
ts a,b,c: swapped-layer bytes distribute a/(a+b+c) etc. VK1-class 8 GB
devices with <100 MiB margins can reject changes that fit everywhere
else; fallback is the next ctx step down (e.g. 256000 -> 250112).

## Worked example

Qwen3.8-27B-UD-Q6_K_L v2 (journal E96, 2026-09-02): 38 Q5_K tensors
(6.6% of bytes, 8.6% of cycles) promoted to imatrix Q6_K from a Q8_0
donor. Output 22.81 GiB, Q6_K 62.2 / Q8_0 37.5 / Q4_K 0.2. Units model
predicted +3.8% pp. Survey first: no stock unsloth variant beat the
production L (XL repo copy identical to local; Q6_K_M/Q6_K smaller but
Q5_K-heavier = slower; Q8_K_L/XL blow the context fit).

## Failure modes seen

- Header corruption from hand-rolled writers: compare the output's
  first bytes against the base file (hex) before deeper debugging -
  an n_kv/n_tensors prologue swap is invisible until gguf-py parses.
- Donor tensor offsets are relative to the DONOR's data section start;
  forgetting the donor's own header size reads plausible garbage.
- Pseudo-code in run instructions: expand every variable before
  handing a command to the harness - ab-bench passes extras verbatim
  to llama-server, one bad arg hangs the health wait (E96 followup).
