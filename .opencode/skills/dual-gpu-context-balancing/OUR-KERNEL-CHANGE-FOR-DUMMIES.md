# Our kernel change, for dummies

## The setup: what happens when the model reads

A language model keeps a diary of everything it has seen: the **KV cache**.
Every time you send a prompt, the model's attention step has to read that
diary to figure out which earlier words matter right now.

We shrank that diary to half size using q8_0 (8-bit) storage instead of
F16 (16-bit). Great for memory - but it created a slow path, which is
what we fixed.

## The problem: reading the diary once per word

Imagine checking a 100-page diary. The old code did this:

- Take the first word of your prompt
- Read ALL 100 pages to see what matters for that word
- Take the second word
- Read ALL 100 pages again
- ... repeat for every word of the prompt

That is what the old kernel (called **VEC**) did. Each prompt word got
its own full pass over the diary. On top of that, it had to "translate"
the q8 shorthand back into normal numbers on the fly, every single time.

A 5,000-word prompt into a 100,000-word diary meant the same pages were
read thousands of times per model layer. That is why our prompt
processing collapsed from ~300 words/sec down to ~106 as chats got long.

## The fix: read once, share with the neighbors

Our new kernel path (a variant of the existing **tile** kernel) does this:

- Take a group of 32 prompt words at once
- Read each diary page ONCE for the whole group
- Translate the q8 shorthand to normal numbers right there in the
  chip's fast scratch memory, as the tile is loaded
- Use it for all 32 words, throw it away, move to the next page

Same math, same answers - just no redundant reading and no separate
translation step.

## Why it is 2x on long chats, only +10% on short ones

- Short diary (few pages): reading it was never the bottleneck, so
  sharing saves little. ~+10%.
- Long diary (100k+ pages): reading dominated everything. Cutting the
  reads by ~32x per group turns 106 words/sec into 216. **2x.**

## The technical version (3 sentences, for when people ask)

llama.cpp's HIP path routed all quantized-KV flash attention to the VEC
kernel, which iterates the KV cache per query row - no amortization
across the GQA group. We added q8_0 tile loaders that dequantize
block-aligned 32-element groups into shared memory during tile load,
templated the existing tile kernel on a `kv_q8_0` flag, and dispatch to
it on GCN when K and V are both q8_0 and block-aligned. It is gated to
GCN only (Vega 10/20, MI50/MI60) because CDNA/RDNA have their own
tensor-core paths we did not touch.

## What we did NOT change

- Generation speed (tg): the model reads its own weights for every
  generated word - that is memory-bandwidth-bound, not diary-bound.
- Output quality: bit-identical math, just scheduled differently.
- Any other quant or format: only q8_0 K + V, nothing else.

## The file locations, if someone asks

- `ggml/src/ggml-cuda/fattn-tile.cuh` - the tile loaders + kernel variant
- `ggml/src/ggml-cuda/fattn.cu` - the routing decision + memory sizing
- Commits: `d14628d04` (the kernel), `5471c58d7` (GCN-only gate)
