# How we made the server faster - a summary

Hardware: 2x AMD Radeon VII (16 GB each, ROCm) + RTX 3080 Laptop (8 GB, Vulkan).
Model: Qwen3.6-27B Q8_0 with MTP (self-drafting) and vision (mmproj).

## Results

| | Before | After |
|---|---|---|
| Context (with vision) | 130k | **197k** |
| Context (text only) | 130k | **226k** |
| pp, short prompts | 238 | **333** |
| pp, 100k-token deep prompt | 106 | **216** |
| tg (generation) | 19 | 17-19 |

## What we changed, in order

- **1. Better layer placement across the 3 GPUs**
  - Moved model layers between cards until memory was balanced
  - Fixed the startup crash (one GPU was 62 MB over-full)
  - Context: 130k -> 144k

- **2. KV cache: F16 -> q8_0**
  - Halves the model's conversation memory
  - Context: 144k -> 197k (vision) / 218k (text)
  - Side effect: draft model guessed worse, tg dropped to 16
  - Fix: keep the *draft* cache at F16 (tiny, ~450 MB) + shorten drafts 3 -> 2
  - tg back to 17-19

- **3. Removed `GGML_VK_DISABLE_F16=1`**
  - Was an AMD RADV workaround that also disabled FP16 on the NVIDIA card
  - pp: 238 -> 285, free win

- **4. Layer split 26/14/26 + pipeline-parallel off**
  - Gave the (now faster) 3080 more layers
  - Pipeline sync cost more than it saved for single requests
  - pp: 285 -> 296

- **5. New attention kernel (code change, commit `d14628d04`)**
  - Problem: old kernel (VEC) read the whole KV cache once per query token
  - Long prompt = hundreds of reads of the same cache per layer
  - That is why pp collapsed to ~106 on deep prompts
  - Fix: tile-based kernel, dequantizes q8 on the fly, shares each tile across 32 queries
  - Same math, same output - just far fewer memory reads
  - Deep prompts: 106 -> 216 (2x), short prompts: 296 -> 333
  - If you cherry-pick one change, pick this one

## What did NOT work (do not retry)

- Bigger tile (64 cols): slower - worse latency hiding on this old GPU
- q4 KV cache: much slower, Vega has no fast decode for it
- Bigger ubatch: OOM or draft-model memory cliff
- "tensor" split mode: crashes, no mixed ROCm+Vulkan support
- Forcing MMQ kernels: already optimal, no change

## Why tg stayed ~the same

- Every generated token reads all 28 GB of weights
- Limited by raw card memory bandwidth, not attention
- Only new hardware or a smaller model changes this

## Hard limits we hit

- **pp ~333**: layer-by-layer math across 3 slow-ish cards
- **tg ~18**: memory bandwidth reading weights
- **Context 226k**: the 8 GB card + draft-model memory cliff; above it the
  server starts but dies on the first big request
- **Vision 197k**: image encoder needs ~1.2 GB free on GPU 0 when a
  picture arrives; 197k keeps that reserve

## Files

- `llama-start-q8v.sh` - daily driver (vision, 197k, 333 tok/s pp)
- `llama-start-q8-text.sh` - max context (226k, no vision)
- `llama-bench-q8v.sh` - quick benchmark (pp, tg, vision)
- `trials.md` - every test we ran, with numbers
- Kernel commit: `d14628d04` (fattn-tile.cuh + fattn.cu)
