#!/usr/bin/env bash
# Production launcher: Qwen3.8-27B-UD-Q6_K_XL + mmproj-F16 vision, K=f16 V=q8_0 KV.
# Calibrated 2026-08-17, see .opencode/skills/dual-gpu-context-balancing/scripts/trials.md
# Winner: -sm layer -ts 39,21,40 -c 210000, pipeline off, n-max 2, nextn -ot.
# Mixed KV via fork fattn tile kernel (k_q8_0/v_q8_0 split, 2026-08-17).
# First-batch pp 297 t/s; 215k+ hits the VK1 sysmem-spill cliff (248 t/s) -
# VK1 context buffer crosses ~2.6 GiB with ~72 MiB free and the NVIDIA Vulkan
# driver backs it with system memory. Do not raise -c without freeing VK1.
# Alternatives measured: full F16 KV = 165k @ 319.5; full q8 KV = 295k @ 263.
set -eu

SCRIPT_DIR=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
# BIN / LD_LIB env vars repoint the server binary and lib dir for A/B trials.
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
  --spec-type draft-dflash --spec-draft-n-max 7 --spec-draft-override-tensor .*=ROCm0 -ngld 99 -md /home/srcds/ai/ai/Qwen3.8-27B-DFlash2-Q4_K_M.gguf \
  --cache-reuse 256 \
  -ctk f16 -ctv q8_0 \
  -cram 28000 --reasoning-format deepseek \
  --chat-template-file "$SCRIPT_DIR/froggeric_chat_templ.jinja" \
  --pipeline-parallel off \
  -ts 40,20,40 -sm layer -c 210000 \
  --override-tensor '^blk\.64\.nextn\..*=ROCm0'
