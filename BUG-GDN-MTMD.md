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

## Mechanism (decoded from the position arithmetic)

- Warned batches end at pos 105954 while the recurrent cell already holds
  105953/105954 -> ubatches spanning `[105571..105954]` were re-submitted
  over already-processed ground (~383-token overlap). Two warnings per
  ubatch = target + draft contexts both run recurrent memory.
- The following batch starts at 105994 and ends 106377: positions
  **105955..105993 (39 tokens) are never seen** by the recurrent memory.
- A 39-token invisible span with text re-crossing the boundary is the
  signature of an **image chunk decoded through the separate mtmd path**
  (`server-context.cpp: process_mtmd_chunk`) while the recurrent memory's
  one-pos-per-sequence cell tracking does not account for the
  placeholder->image-token expansion.
- Ruled out: `--cache-reuse 256` (force-disabled at startup by `--mmproj`,
  see `server-context.cpp:1277`); MTP catch-up seq_rm (single-head chain);
  checkpoints (pure state snapshots, no re-decode); PP scheduler (off in
  this config).

## Impact

- PP speed decay in the same log (319 -> 196 t/s cumulative) is separately
  explained by KV-fill attention cost on the full-attention layers; that
  part is normal for deep fill.
- Quality: each overlap re-folds ~hundreds of text tokens into the GDN
  running state (double-counted), and image spans are never folded. Bounded
  drift near image boundaries, no crash. Severity of output degradation
  unverified.

## Confirmation (cheap, when convenient)

1. Same conversation with images removed -> warnings should vanish.
2. Count warning bursts vs number of images crossing a ubatch boundary
   (expect roughly one burst per boundary-crossing image).
3. Server-side log lines at the burst timestamps (they carry slot/task
   context the libllama warning lacks) should show mtmd chunk processing.

## Fix direction (upstream)

Either `find_slot` in the recurrent memory must tolerate mtmd chunk
decodes (advance cells through image spans, accept position re-entry), or
the mtmd path must keep the recurrent cell positions in sync with the
token-position frontier across image expansion. Related latent bug found
while auditing: `seq_rm` partial rollback returns false when the rollback
depth exceeds `n_rs_seq` and callers (e.g. cache-reuse path) ignore the
return value, leaving a stale `cell.pos`.
