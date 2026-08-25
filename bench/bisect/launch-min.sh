#!/usr/bin/env bash
# Minimal upstream-compatible launcher for bisect PP tests (no fork-only flags).
set -eu
cd "$(dirname "$(readlink -f "$0")")/../.."
PORT=${PORT:-8015}
BIN=${BIN:-$PWD/build-bisect/bin/llama-server}
HIP_GRAPH=1 AMD_LOG_LEVEL=0 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 HIP_FORCE_P2P=1 \
GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \
LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$(dirname "$BIN"):/opt/rocm-6.1.0/lib \
exec "$BIN" \
  -m /home/srcds/ai/ai/Qwen3.8-27B-UD-Q6_K_XL.gguf \
  --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
  -b 16384 -ub 384 \
  --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --device rocm0,vulkan1,rocm1 --port "$PORT" -np 1 -mg 0 \
  -ctk f16 -ctv q8_0 \
  -ts 40,20,40 -sm layer -c 210000 \
  --override-tensor '^blk\.64\.nextn\..*=ROCm0'
