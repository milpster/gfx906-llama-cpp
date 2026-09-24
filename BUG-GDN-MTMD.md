# GDN "non-consecutive token position" warnings during deep vision prefill

Recorded 2026-08-19. Investigation of the warning burst seen on the live
210k vision server (Q6_K_XL + mmproj, `-ctk f16 -ctv q8_0`, dual spec
`draft-mtp,ngram-mod`, `-ts 40,20,40 -sm layer`, pipeline-parallel off).

## Symptom

During a ~158k-token prefill with images, at each image-boundary ubatch the
log shows bursts of:

    W find_slot: non-consecutive token position 105954 after 105953 for sequence 0 with 384 new tokens
    W find_slot: non-consecutive token position 105954 after 105954 for sequence 0 with 152 new tokens
    ... (repeated, then a jump)
    W find_slot: non-consecutive token position 106377 after 105954 for sequence 0 with 384 new tokens

Source: `src/llama-memory-recurrent.cpp:641` (`llama_memory_recurrent::find_slot`).
This is the **recurrent (GDN) memory** of the hybrid architecture, NOT the
KV cache.

## Evidence: NOT caused by the fork's uncommitted work

1. Live process env (`/proc/<pid>/environ`) contains only
   `GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16`. `GGML_KV_SPLIT_Q8` and
   `GGML_CUDA_MMQ_SCALE_FREE` are unset -> every fork kernel addition is
   dormant (Q8_0S split-plane KV, scale-free MMQ).
2. `git status` clean on every file in the warning's call path:
   `src/llama-memory-recurrent.cpp`, `tools/server/server-context.cpp`,
   `src/llama-context.cpp`, `common/speculative.cpp`, `tools/mtmd/`.
   All fork modifications are GPU-kernel-side (mmq*, fattn*, cpy,
   set-rows, ggml-quants, llama-kv-cache) and never touch positions,
   ubatch splitting, or memory bookkeeping.
3. Running binary is the verified baseline: post-session build whose
   legacy path produced greedy output sha `847d5d35a659` (identical to the
   pre-session baseline) at 330.3 pp1.
4. Binary predates the warnings by 12+ hours of uptime.

## Corrected mechanism (2026-09-24)

The original overlap diagnosis was incorrect. The numbers are M-RoPE temporal coordinates, not one scalar position per decoded row.

- MTMD image embeddings are decoded through the normal target recurrent graph. A 384-row image ubatch can pin every row to one temporal position while its other M-RoPE coordinates vary, so the recurrent state consumes every image row exactly once.
- `llama_memory_recurrent::find_slot` stores only the last temporal coordinate in `cell.pos`, then applies the scalar invariant `last_pos == cell.pos + n_seq_tokens`. That invariant is valid for one-dimensional text positions but not for M-RoPE image rows or the following text jump across an image position span.
- The two copies of each warning come from target and draft recurrent contexts. They do not show duplicate target decoding.
- The 2026-09-24 trace starts with `154802 after 154801`, which proves the LCP-restored recurrent frontier is aligned before the image. The 384-row and 66-row image ubatches then remain at temporal position 154802, and three text rows end at 154829 after the image advances the M-RoPE frontier by 27 positions.
- DFlash intentionally skips position-pinned M-RoPE image rows. Its later `zero-filled 25 draft-cache hole rows` message records catch-up for the scalar positions absent from the draft cache; generation continues normally.

## Impact

- The recurrent and DFlash state transitions observed here are correct. The warning is a false positive and there is no evidence of double-counted text, skipped image state, or output degradation.
- PP speed decay in the original log is separately explained by KV-fill attention cost on full-attention layers and is normal for deep fill.
- Partial recurrent rollback beyond `n_rs_seq` remains a separate behavior worth auditing, but it is not implicated by these traces because the first post-reuse position is consecutive with the restored frontier.

## Fix

`find_slot` now applies the scalar token-count continuity warning only when `llama_ubatch::is_pos_2d()` is false. State updates are unchanged. Scalar-position models retain the existing warning, while M-RoPE batches no longer emit a diagnostic based on an invalid invariant.

Offline verification: `test-batch-alloc` passed all 327 assertions, including the existing M-RoPE layout and allowed-position-jump cases; `llama-server` rebuilt successfully. Live confirmation remains deferred until the prepared validation run is approved.
