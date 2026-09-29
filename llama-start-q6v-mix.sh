#!/usr/bin/env bash
# Production launcher: Qwen3.8-27B-UD-Q6_K_XL + mmproj-F16 vision, mixed KV
# K=f16 V=q8_0 (target only; draft/MTP KV stays F16). Max-ctx performer:
# 210k ctx @ first-batch pp 310.7, tg 18.4.
# Calibrated 2026-08-20, see .opencode/skills/dual-gpu-context-balancing/scripts/trials.md
# "V-q8_0 mixed KV push". Key: V-q8 frees VRAM so 14 VK1 layers fit at 210k
# (26/14/26); split gain (+10 pp) beats mixed-kernel tax (-6). pp is
# split-bound not ctx-bound here. Supersedes llama-start-q6v.sh.
# Deep-validated: 180k fill 151.4 avg, tg 18.42 @depth, vision @depth OK,
# VK1 floor 171 MiB (no sysmem spill). 220k startup-only; 230k dead
# (VK1 compute OOM). pipeline/cost matrix all equal at ~311 -> off/layer.
# Full-F16 alternative (V stays f16): llama-start-q6v-f16.sh = 165k @ 311.9.
set -eu

SCRIPT_DIR=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
BIN=${BIN:-$SCRIPT_DIR/build-dedup/bin/llama-server}
LD_LIB=${LD_LIB:-$SCRIPT_DIR/build-dedup/bin}

HIP_GRAPH=1 AMD_LOG_LEVEL=0 \
GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 HIP_FORCE_P2P=1 \
GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \
LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$LD_LIB:/opt/rocm-6.1.0/lib \
exec "$BIN" \
  -m /home/srcds/ai/ai/Qwen3.8-27B-UD-Q6_K_XL.gguf \
  --mmproj /home/srcds/ai/ai/mmproj-F16.gguf \
  --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
  -b 16384 -ub 384 --ctx-checkpoints 30 \
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  --device rocm0,vulkan1,rocm1 --port 8009 -np 1 -mg 0 \
  --reasoning-preserve --reasoning on \
  --spec-type draft-mtp-adaptive --spec-draft-n-max 10 --spec-draft-n-min-adaptive 3 \
  --cache-reuse 256 \
  -ctk f16 -ctv q8_0 \
  -cram 24000 --reasoning-format deepseek \
  --chat-template-file /home/srcds/dev/uf2_rocm6.1_llama.cpp/froggeric_chat_templ.jinja \
  --pipeline-parallel off \
  -ts 39,21,40 -sm layer -c 210000 \
  --override-tensor '^blk\.64\.nextn\..*=ROCm0'
