#!/usr/bin/env bash
# Production launcher: Qwen3.8-27B.i1-Q6_K + mmproj-F16 vision
# + DFlash2 external drafter (Q4_K_M), f16 K / q8_0 V.
# drafter Q4_K_M: measured equivalent to Q8_0 (R0 vs R1: identical
# TG/fill/sha), and Q8_0 + -c 250000 crashes the current builds
# (fattn invalid-device-function, journal E80, cause still open).
# --spec-draft-n-max 4: beats 7 at depth (TG 9.0 vs 8.6, X2); acceptance
# rate drops .708 -> .646 but t/s is the metric (journal K3).
# ngram-mod chained ahead of the drafter (F5, 24/28/64): no fill tax,
# idle on novel content, drafts for real on replayed spans (54 gen /
# 45 acc, mean len 46) - insurance for replay-heavy sessions.
# bin/LD_LIB = build-rcfix with the vega MMQ/TOPK/GRAPHS tunes + 0924 sync fixes
# (E82/E83: tuned release lane pp 369 / fill 327 / tg 13.3, canonical
# sha, repro gate passes; ~395+ client-scale PP16384).
# LD_LIBRARY_PATH must carry build-rcfix/bin: RUNPATH lets a
# stale lib path shadow the entire build (E70).
# LLAMA_DFLASH_MIRROR_OUTPUT=1 + --spec-draft-device ROCm0: local copy
# of the borrowed vocab head on the drafter's device -> single-device
# draft graph, draft rounds -42% / TG +11% at depth (E119.3); mirror
# copy adds ~1 GiB host-staged, +2-10 s load time.
# force_convert: keeps the FATTN path convert-native as sessions age
# (selector re-check quirk, E75); costs <=3% on first PP batches.
# Vision + DFlash2 requires the #27408 M-RoPE port (upstream since #27816).
# Fit E171->E173 (2026-09-16, q8_0/q8_0 KV regime): -ts 34,22,44 kept;
# -c 353200 (n_ctx 353280, slots 2 x 176640) + ot3 (blk.24 from VK1,
# blk.37+38 from ROCm1 -> ROCm0, ~627 MiB). E171 first shipped 358750
# (ROCm1 free 108) - REVOKED: the fattn workspace pool alloc
# (ggml-cuda.cu:507) OOMs nondeterministically when an AMD sits under
# ~200 MiB free at ready; ~150 MiB context-checkpoint transients race
# the fill's pool alloc. 353280 (frees ~238/~207 ROCm0/ROCm1) passed
# the crash gate twice (chk-i1-353k-r1/r2: acc .652, TG 975 clean).
# -ot graph cost ~1.5% PP (lot335 vs lplain335: 355.2 vs 360.4).
# TEMP-0 REPRO NOTE: sha before/after deep use can differ (benign KV/
# batch-state drift, same class as lplain335/lot335/lot358 lanes).
# --pipeline-parallel off: forced "on" + -ot crashes at startup
# (1583 MiB pipeline buffer); the server auto-disables pipeline at
# every fit we run anyway (needs 12+ GiB free estimates).
set -eu

SCRIPT_DIR=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
BIN=${BIN:-$SCRIPT_DIR/build-rcfix/bin/llama-server}
LD_LIB=${LD_LIB:-$SCRIPT_DIR/build-rcfix/bin}
# Logging (no -v): --log-file tees normal (non-verbose) output to a file while
# the terminal keeps it; --log-prompts-dir writes one .txt per request with the
# full prompt (tokens in) and, appended at completion, token ids + text (tokens
# out) via the fork's append_prompt_log_completion patch.
LOG_DIR=${LOG_DIR:-$SCRIPT_DIR/log}
mkdir -p "$LOG_DIR/prompts"

HIP_GRAPH=1 AMD_LOG_LEVEL=0 \
LLAMA_DFLASH_MIRROR_OUTPUT=1 \
GGML_CUDA_FATTN_PATH=force_convert \
GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 HIP_FORCE_P2P=1 \
GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \
LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$LD_LIB:/opt/rocm-6.1.0/lib \
exec "$BIN" \
  -m /home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf \
  --mmproj /home/srcds/ai/ai/mmproj-F16.gguf \
  -md /home/srcds/ai/ai/Qwen3.8-27B-DFlash2-Q4_K_M.gguf \
  --spec-type ngram-mod,draft-dflash --spec-draft-n-max 4 \
  --spec-ngram-mod-n-match 24 --spec-ngram-mod-n-min 28 --spec-ngram-mod-n-max 64 \
  --spec-draft-override-tensor '.*=ROCm0' --spec-draft-device ROCm0 -ngld 99 \
  --threads-batch 10 --threads 9 --load-mode none -fa on -ngl 333 \
  -b 16384 -ub 384 --ctx-checkpoints 30 \
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  --device rocm0,vulkan1,rocm1 --port 8009 -np 2 -mg 0 \
  --reasoning-preserve --reasoning on \
  -ctk q8_0 -ctv q8_0 \
  -cram 28000 --reasoning-format deepseek \
  --chat-template-file "$SCRIPT_DIR/sharp_chat_template.jinja" \
  --pipeline-parallel off \
  -ts 34,22,44 -sm layer -c 353200 \
  -ot '^blk\.(24|37|38)\.ffn_(gate|up|down)\.weight$=ROCm0' \
  --no-mmproj-offload \
  --log-file "$LOG_DIR/llama-server-iq6v-f16-f16.log" \
  --log-prompts-dir "$LOG_DIR/prompts" \
