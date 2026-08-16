# Who profits from our kernel changes

## Short version

Anyone running llama.cpp on **AMD GCN GPUs via ROCm/HIP** with a
**q8_0 KV cache** (`-ctk q8_0 -ctv q8_0`) and flash attention on.

## The winning hardware

| GPU | Arch | Benefits? | Notes |
|---|---|---|---|
| Radeon VII | gfx906 (GCN) | **Yes** | our test rig |
| MI50 / MI60 32GB | gfx906 (GCN) | **Yes** | cheap on eBay, popular for home LLM servers |
| MI50 16GB | gfx906 (GCN) | **Yes** | same chip as Radeon VII |
| Vega 56 / 64 | gfx903/906 (GCN) | **Yes** | same code path |
| MI25 / Vega FE | gfx900 (GCN) | Likely | older, FP16 slower, untested |

## Who does NOT benefit

| GPU / platform | Why not |
|---|---|
| MI250 / MI300 (CDNA) | Has MFMA tensor cores, own kernel paths; excluded by our gate |
| RX 7000 / 9000 (RDNA3/4) | Has WMMA paths; keeps the VEC route |
| All NVIDIA | Different code path entirely; already uses tensor cores for this |
| Vulkan backend users | Change is in the HIP/ROCm backend only |
| CPU backend | Not affected |
| F16 / BF16 KV users | The kernel only targets q8_0 K and V |
| macOS / Metal | Not affected |

## What the win looks like

Depends on how full your context is when processing prompts:

| Cache fill when prompt arrives | Speedup |
|---|---|
| Short chats (few k tokens) | ~+10% |
| 32k filled | ~+50% |
| 64k filled | ~2x |
| 100k+ filled (RAG, long docs, agent loops) | **2x+** |

Why: the old path re-read the whole cache once per prompt token. The
fuller the cache, the more waste. Our kernel reads it in tiles shared
across many prompt tokens at once.

## Requirements

- Build with the HIP backend (ROCm), `GGML_HIP=ON`
- Run with `-ctk q8_0 -ctv q8_0 -fa on`
- Head size of the model must be <= 256 and divisible by 32 (all common
  Qwen/Llama/Mistral sizes qualify: 64, 80, 96, 128, 256)
- Batched prompt processing (the win is in pp, not generation)

## tl;dr for announcements

"2x prompt processing on 100k+ filled contexts for Radeon VII / MI50 /
MI60 users with q8_0 KV cache, free otherwise."
