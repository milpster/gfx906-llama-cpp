#!/usr/bin/env bash
set -eu

GGML_VK_DISABLE_F16=1 \
HIP_GRAPH=1 \
AMD_LOG_LEVEL=0 \
GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 \
HSA_OVERRIDE_GFX_VERSION=9.0.6 \
HIP_VISIBLE_DEVICES=0,1 \
HSA_XNACK=0 \
HIP_FORCE_P2P=1 \
GPU_SINGLE_ALLOC_PERCENT=100 \
HSA_ENABLE_SDMA=1 \
HSA_DISABLE_FRAGMENT_ALLOCATOR=0 \
GPU_MAX_ALLOC_PERCENT=100 \
USE_MLOCK=true \
LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:/home/srcds/dev/uf2_rocm6.1_llama.cpp/build-vega20/bin:/opt/rocm-6.1.0/lib \
exec /home/srcds/dev/uf2_rocm6.1_llama.cpp/build-vega20/bin/llama-server \
  -m ~/ai/ai/Qwen3.6-27B-Fable-Fus-711-UnHeretic-NM-DAU-NEO-MAX-NEO-MTP-Q8_0.gguf \
  --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
  -b 16384 -ub 384 --ctx-checkpoints 30 \
  --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  --device rocm0,vulkan1,rocm1 --port 8009 -np 1 -mg 0 \
  --reasoning-preserve --reasoning on \
  --spec-type draft-mtp --spec-draft-n-max 2 \
  -cram 20000 --reasoning-format deepseek \
  --chat-template-file ~/dev/llama.cpp/q36chat_template.jinja \
  --pipeline-parallel on \
  -sm cost -ts 42,19,39 \
  -ot '^blk\.64\.nextn\..*=ROCm0' \
  -ot '^blk\.63\..*=ROCm0' \
  -c 155000
