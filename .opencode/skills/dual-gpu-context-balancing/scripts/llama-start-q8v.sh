#!/usr/bin/env bash
# Production launcher: Qwen3.6-27B MTP Q8_0 + mmproj-F16 vision, q8_0 target KV.
# Calibrated 2026-08-16, see .opencode/skills/dual-gpu-context-balancing/scripts/trials.md
# Winner: -sm layer -ts 39,21,40 (26/14/26 layers) -c 197000, pipeline off, F16
# draft KV, n-max 2, no GGML_VK_DISABLE_F16 (it crippled the 3080).
# Measured: tg 16.8-19.0/s @1024 out, pp 296 tok/s @5-7.5k in, vision OK.
# pp is a serial sum of all 66 layer-times; ~296 is the config ceiling.
# Tested & rejected: pp on (-4%), ub 416/448/512 (slower/OOM), MMQ force
# (neutral), q4_0 KV (scalar dequant, -20%), cost mode, other splits.
# Vision ceiling: ROCm0 needs >= ~1162 MiB free for CLIP worst-case encode.
# Text-only max ctx: 218k via llama-start-q8-text.sh (cost-mode calibration).
set -eu

HIP_GRAPH=1 AMD_LOG_LEVEL=0 \
GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 HIP_FORCE_P2P=1 \
GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \
LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:/home/srcds/dev/uf2_rocm6.1_llama.cpp/build-vega20/bin:/opt/rocm-6.1.0/lib \
exec /home/srcds/dev/uf2_rocm6.1_llama.cpp/build-sync25/bin/llama-server \
  -m /home/srcds/ai/ai/Qwen3.6-27B-Fable-Fus-711-UnHeretic-NM-DAU-NEO-MAX-NEO-MTP-Q8_0.gguf \
  --mmproj /home/srcds/ai/ai/mmproj-F16.gguf \
  --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
  -b 16384 -ub 384 --ctx-checkpoints 30 \
  --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  --device rocm0,vulkan1,rocm1 --port 8009 -np 1 -mg 0 \
  --reasoning-preserve --reasoning on \
  --spec-type draft-mtp --spec-draft-n-max 2 \
  -ctk q8_0 -ctv q8_0 \
  -cram 20000 --reasoning-format deepseek \
  --chat-template-file /home/srcds/dev/llama.cpp/q36chat_template.jinja \
  --pipeline-parallel off \
  -ts 39,21,40 -sm layer -c 197000
