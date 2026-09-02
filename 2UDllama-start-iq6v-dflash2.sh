#!/usr/bin/env bash
# Production launcher: Qwen3.8-27B-UD-Q6_K_L + mmproj-F16 vision
# + DFlash2 external drafter (Q4_K_M), f16 K / q8_0 V.
# UD model note: "Q6_K_L" is a dynamic mix (55% Q4_K, 38% Q8_0, 7% Q3_K
# bytes). It reads ~13% more weight bytes than i1-Q6_K, so first-batch
# PP16384 is ~375 tok/s server-scale / ~351 client here; the 393-408
# client class belongs to the i1 launcher, not this model (E89).
# drafter Q4_K_M: measured equivalent to Q8_0 (R0 vs R1: identical
# TG/fill/sha), and Q8_0 + -c 250000 crashes the current builds
# (fattn invalid-device-function, journal E80, cause still open).
# --spec-draft-n-max 4: beats 7 at depth (TG 9.0 vs 8.6, X2); acceptance
# rate drops .708 -> .646 but t/s is the metric (journal K3). ngram-mod
# measured a no-op (X1).
# bin/LD_LIB = build-dflash-novega with the vega MMQ/TOPK/GRAPHS tunes
# (E82/E83). LD_LIBRARY_PATH must carry build-dflash-novega/bin: RUNPATH
# lets a stale lib path shadow the entire build (E70).
# force_convert: keeps the FATTN path convert-native as sessions age
# (selector re-check quirk, E75); costs <=3% on first PP batches.
# Vision + DFlash2 requires the #27408 M-RoPE port (upstream since #27816).
# -ts 40,20,40 -c 256000 (E89 rebalance; attn 6/4/6, KV 4704/3136/4704
# MiB at 256k; fit-free vs target: ROCm0 +1926 / VK1 +74 / ROCm1 +937).
# 256k is the flat-PP plateau edge: 375 t/s first batch, fill 236.8,
# TG1024@120k 12.8, acc .676, sha 6b38a21df2bf, repro gate passes.
# Do NOT raise to 262144 (model metadata cap): VK1 drops to +3 MiB fit
# margin and first-batch PP cliffs to ~335 (Vulkan low-VRAM degrade).
# Conservative fallback if delayed OOM ever shows: -c 250112 (+156 VK1).
# The old W6 -ot blk.37/38 + 260k opt-in is obsolete on this build/model.
# -sm layer: cost mode is byte-identical placement on this stack (E15).
# --pipeline-parallel off: pipeline 4-copy buffers never fit VK1 at this
# ctx (E30); no single-request PP gain at -np 1 (D1).
# --no-mmproj-offload: mmproj runs on CPU. Vision costs ~40 s per Full HD
# image (~2086 image tokens, ~52 tok/s encode, 9 threads); GPU mmproj
# OOM-crashes clip_encode at this ctx (needs ~1.2 GiB free on ROCm0, E89).
set -eu

SCRIPT_DIR=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
BIN=${BIN:-$SCRIPT_DIR/build-dflash-novega/bin/llama-server}
LD_LIB=${LD_LIB:-$SCRIPT_DIR/build-dflash-novega/bin}

HIP_GRAPH=1 AMD_LOG_LEVEL=0 \
GGML_CUDA_FATTN_PATH=force_convert \
GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 HIP_FORCE_P2P=1 \
GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \
LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$LD_LIB:/opt/rocm-6.1.0/lib \
exec "$BIN" \
  -m /home/srcds/ai/ai/Qwen3.8-27B-UD-Q6_K_L.gguf \
  --mmproj /home/srcds/ai/ai/mmproj-F16.gguf --no-mmproj-offload \
  -md /home/srcds/ai/ai/Qwen3.8-27B-DFlash2-Q4_K_M.gguf \
  --spec-type draft-dflash --spec-draft-n-max 4 \
  --spec-draft-override-tensor '.*=ROCm0' -ngld 99 \
  --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
  -b 16384 -ub 384 --ctx-checkpoints 30 \
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  --device rocm0,vulkan1,rocm1 --port 8009 -np 1 -mg 0 \
  --reasoning-preserve --reasoning on \
  -ctk f16 -ctv q8_0 \
  -cram 28000 --reasoning-format deepseek \
  --chat-template-file "$SCRIPT_DIR/froggeric_chat_templ.jinja" \
  --pipeline-parallel off \
  -ts 40,20,40 -sm layer -c 256000
