#!/usr/bin/env bash
# Production launcher: Qwen3.8-27B Q8_0 + mmproj-F16 vision, q8_0 target KV.
# Calibrated 2026-08-17, see .opencode/skills/dual-gpu-context-balancing/scripts/trials.md
# Winner: -sm layer -ts 39,21,40 (26/14/26 layers) -c 202000, pipeline off, F16
# draft KV, n-max 2, no GGML_VK_DISABLE_F16 (it crippled the 3080).
# Includes fork commit d14628d04 (q8_0-native FA tile kernel) + q8 dispatch fix
# (fattn-tile.cuh small-Q shadow mismatch, 2026-08-17 - required for >197k):
# pp 315/s first batch, 193/s 110k-fill avg, tg 18.4/s, vision OK (2026-08-17
# 110k-prefill validation run).
# Vision ceiling: 202k validated with 110k single prefill + tg 1024 (2026-08-17).
# The nextn -ot below is REQUIRED at 202k: bare 202k dies on ROCm1
# hipblasCreate ALLOC_FAILED ~104k into a deep prefill (rocBLAS workspace
# vs fill-consumed headroom); with it, 110k fill passes (pp 193 avg, tg 17.0).
set -eu

HIP_GRAPH=1 AMD_LOG_LEVEL=0 \
GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 HIP_FORCE_P2P=1 \
GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \
LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:/home/srcds/dev/uf2_rocm6.1_llama.cpp/build-vega20/bin:/opt/rocm-6.1.0/lib \
exec /home/srcds/dev/uf2_rocm6.1_llama.cpp/build-sync25/bin/llama-server \
  -m /home/srcds/ai/ai/Qwen3.8-27B-Q8_0.gguf \
  --mmproj /home/srcds/ai/ai/mmproj-F16.gguf \
  --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
  -b 16384 -ub 384 --ctx-checkpoints 30 \
  --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  --device rocm0,vulkan1,rocm1 --port 8009 -np 1 -mg 0 \
  --reasoning-preserve --reasoning on \
  --spec-type draft-mtp-adaptive --spec-draft-n-max 10 --spec-draft-n-min-adaptive 3 \
  --cache-reuse 256 \
  -ctk q8_0 -ctv q8_0 \
  -cram 20000 --reasoning-format deepseek \
  --chat-template-file /home/srcds/dev/uf2_rocm6.1_llama.cpp/froggeric_chat_templ.jinja \
  --pipeline-parallel off \
  -ts 39,21,40 -sm layer -c 202000 \
  --override-tensor '^blk\.64\.nextn\..*=ROCm0'
