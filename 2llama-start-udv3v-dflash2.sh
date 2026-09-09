#!/usr/bin/env bash
# Trial launcher: Qwen3.8-27B-UD-Q6_K_L-v2 (quality lane, E96/E97)
# + mmproj-F16 vision on CPU + DFlash2 external drafter (Q4_K_M),
# f16 K / q8_0 V. Quality-strictly->= stock UD-Q6_K_L (38 Q5_K
# tensors promoted to imatrix Q6_K, 828/866 tensors byte-identical;
# PP measured neutral vs L: 345.8 vs 346.0, E97). v2 IS the unsloth
# Dynamic 3.0 generation (final imatrix; E125 - repo unchanged since).
# Mix: Q6_K 62.2% / Q8_0 37.5% / Q4_K 0.2%; 22.81 GiB. Expect the
# 346-351 client pp class, ~-11% vs the i1 v23 lane (393) - that is
# the byte cost of the quality lane, not a regression.
# E119.3 upgrades ported from the v23 i1 launcher (model-agnostic):
# ngram-mod chain (F5), v23 cache chat template. NOT ported: draft-head
# mirror + --spec-draft-device - L0p probe (E128): mirror needs 1288 MiB
# on ROCm0, only ~1130 free after the drafter at this fit; the failed
# alloc is NOT a graceful skip - sched_reserve GGML_ASSERT-aborts
# (ggml-backend.cpp:941, pre-allocated output.weight, buffer ROCm1).
# Mirror stays an i1-lane luxury until that fallback bug is fixed or
# the fit frees ~160 MiB more on ROCm0.
# -ts 40,20,40 -c 256000: E89 rebalance for L-class bytes (+0.3 GiB
# v2 over L: VK1 razor +74 MiB is L's number, v2 keeps the same
# fallback rule). Do NOT raise to 262144 (VK1 +3 MiB, PP cliff ~335).
# Conservative fallback if delayed OOM: -c 250112 (+156 VK1).
# --no-mmproj-offload: mmproj on CPU (~40 s per Full HD image);
# GPU mmproj OOM-crashes clip_encode at this ctx (E89).
# --pipeline-parallel off: 4-copy pipeline buffers never fit VK1 at
# this ctx (E30); no single-request PP gain at -np 1 (D1).
set -eu

SCRIPT_DIR=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
BIN=${BIN:-$SCRIPT_DIR/build-sync0909/bin/llama-server}
LD_LIB=${LD_LIB:-$SCRIPT_DIR/build-sync0909/bin}

HIP_GRAPH=1 AMD_LOG_LEVEL=0 \
LLAMA_DFLASH_MIRROR_OUTPUT=1 \
GGML_CUDA_FATTN_PATH=force_convert \
GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 HIP_FORCE_P2P=1 \
GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \
LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$LD_LIB:/opt/rocm-6.1.0/lib \
exec "$BIN" \
  -m /home/srcds/ai/ai/Qwen3.8-27B-UD-Q6_K_L-v2.gguf \
  --mmproj /home/srcds/ai/ai/mmproj-F16.gguf --no-mmproj-offload \
  -md /home/srcds/ai/ai/Qwen3.8-27B-DFlash2-Q4_K_M.gguf \
  --spec-type ngram-mod,draft-dflash --spec-draft-n-max 4 \
  --spec-ngram-mod-n-match 24 --spec-ngram-mod-n-min 28 --spec-ngram-mod-n-max 64 \
  --spec-draft-override-tensor '.*=ROCm0' --spec-draft-device ROCm0 -ngld 99 \
  --threads-batch 10 --threads 9 --load-mode none -fa on -ngl 333 \
  -b 16384 -ub 384 --ctx-checkpoints 30 \
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  --device rocm0,vulkan1,rocm1 --port 8009 -np 1 -mg 0 \
  --reasoning-preserve --reasoning on \
  -ctk f16 -ctv q8_0 \
  -cram 28000 --reasoning-format deepseek \
  --chat-template-file "$SCRIPT_DIR/froggeric_chat_templ_v23_cache.jinja" \
  --pipeline-parallel off \
  -ts 40,20,40 -sm layer -c 256000
