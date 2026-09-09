# Quant perplexity comparisons (Qwen3.8-27B and friends)

One row per quant file, one fixed protocol, so rows are comparable.
Started 2026-09-06 (E130). Numbers are only valid against rows run
with the same protocol - do not mix with ab-bench or server PPL
endpoints.

## Protocol

- Binary: build-dflash-novega/bin/llama-perplexity (fork, current)
- Text: /home/srcds/ai/ai/log.txt, full file, 65 chunks
- Args: --device rocm0,vulkan1,rocm1 -ngl 99 -sm layer -ts 35,20,45
  -c 4096 -b 1024 -ub 384 --threads 9 --threads-batch 10 --no-mmap
  -fa on
- Default f16 KV (no -ctk/-ctv): isolates weight-matmul numerics
- Env: HSA_OVERRIDE_GFX_VERSION=9.0.6 HSA_XNACK=0 HIP_VISIBLE_DEVICES=0,1
  HIP_FORCE_P2P=1 GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1
  HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100
  AMD_LOG_LEVEL=0, LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:
  <builddir>/bin:/opt/rocm-6.1.0/lib
- Metric: "Final estimate: PPL = X +/- sigma" from the log tail
- Wall: ~15-18 min per 27B model; log kept at bench/logs/ppl-<name>.log

Template (run from repo root):

```bash
export HSA_OVERRIDE_GFX_VERSION=9.0.6 HSA_XNACK=0 HIP_VISIBLE_DEVICES=0,1 \
  HIP_FORCE_P2P=1 GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
  HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 AMD_LOG_LEVEL=0
LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$PWD/build-dflash-novega/bin:/opt/rocm-6.1.0/lib \
  build-dflash-novega/bin/llama-perplexity \
  -m <MODEL.gguf> -f /home/srcds/ai/ai/log.txt \
  --device rocm0,vulkan1,rocm1 -ngl 99 -sm layer -ts 35,20,45 \
  -c 4096 -b 1024 -ub 384 --threads 9 --threads-batch 10 --no-mmap -fa on \
  > bench/logs/ppl-<name>.log 2>&1
grep "Final estimate" bench/logs/ppl-<name>.log
```

## Results

| date | quant | GiB | mix | PPL | sigma | log | journal |
|---|---|---:|---|---:|---:|---|---|
| 2026-09-06 | Qwen3.8-27B.i1-Q6_K (prod) | 20.88 | 100% Q6_K | 1.3043 | 0.00561 | ppl lane E122 | E122 |
| 2026-09-06 | Qwen3.8-27B-UD-Q6_K_L (stock unsloth Dynamic 3.0) | 22.52 | Q6_K 55 / Q8_0 38 / Q5_K 6.6 / Q4_K 0.2 | 1.3035 | 0.00556 | bench/logs/ppl-L-fork.log | E130 |

Reading: i1 vs L = 0.0008 apart on sigma 0.0056 over the SAME 65
chunks (chunk-correlated, so the raw delta overstates independence):
statistically indistinguishable. The UD 38% Q8_0 mass shows no
measurable PPL gain over uniform Q6_K on this text. Combined with
the -16 to -20% PP cost (E129), the UD-L lane is rejected on this
rig (E130).

## Caveats

- One text, one domain (log.txt). A quant tuned for agentic/chat
  (unsloth's claim: Divergence-300 @32, top-1% accuracy) can differ
  where PPL on generic text does not. PPL here is the accepted
  project quality gate, not a universal ranking.
- Lower sigma-bound crossings do not exist here: deltas under ~0.005
  on this protocol are noise; call ties instead of ranking them.
- Build-dependent numerics (vega MMQ tune, E123) shift PPL in the
  3rd decimal - compare quants only within the same binary.
