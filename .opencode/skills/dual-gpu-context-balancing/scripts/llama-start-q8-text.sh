#!/usr/bin/env bash
# Text-only max-context launcher: same calibration but no --mmproj.
# -c 218000 is the listening cliff (220000 fails: ROCm1 MTP context alloc).
# ROCm0 free ~946 MiB is fine without CLIP. Add --mmproj back => use -c 197000.
# No GGML_VK_DISABLE_F16: it cripples the 3080 (pp 238 -> 285 tok/s).
set -eu

HIP_GRAPH=1 AMD_LOG_LEVEL=0 \
GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 HIP_FORCE_P2P=1 \
GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \
LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:/home/srcds/dev/rocm6.1_llama.cpp/build-vega20/bin:/opt/rocm-6.1.0/lib \
exec /home/srcds/dev/rocm6.1_llama.cpp/build-vega20/bin/llama-server \
  -m /home/srcds/ai/ai/Qwen3.6-27B-Fable-Fus-711-UnHeretic-NM-DAU-NEO-MAX-NEO-MTP-Q8_0.gguf \
  --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
  -b 16384 -ub 384 --ctx-checkpoints 30 \
  --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  --device rocm0,vulkan1,rocm1 --port 8009 -np 1 -mg 0 \
  --reasoning-preserve --reasoning on \
  --spec-type draft-mtp --spec-draft-n-max 3 \
  -ctk q8_0 -ctv q8_0 -ctkd q8_0 -ctvd q8_0 \
  -cram 20000 --reasoning-format deepseek \
  --chat-template-file /home/srcds/dev/llama.cpp/q36chat_template.jinja \
  --pipeline-parallel on \
  -ts 42,19,39 -sm cost -c 218000
