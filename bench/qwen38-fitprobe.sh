#!/usr/bin/env bash
# Load-only placement probe for the Qwen3.8-Flash-Next lane.
# Prints the per-device fit table (weights + KV + compute) without generating.
# Usage: bench/qwen38-fitprobe.sh <tag> [ncmoe] [ts] [ctx]
#   tag   - label used for the log dir /tmp/opencode/fitprobe/<tag>/
#   ncmoe - CPU MoE layer count (default 24)
#   ts    - tensor split (default 70,13,17)
#   ctx   - context size (default 4096)
set -euo pipefail
TAG=${1:?tag}
NCMOE=${2:-24}
TS=${3:-70,13,17}
CTX=${4:-4096}
SRC=${SRC:-/home/srcds/dev/uf3_rocm6.1_llama.cpp}
BUILD_DIR=${BUILD_DIR:-$SRC/build-qwen38-mtp}
MODEL=${MODEL:-/home/srcds/ai/ai/Qwen3.8-Flash-Next-AD-4.27bpw-Q4_K_M-M64.gguf}
OUT=/tmp/opencode/fitprobe/$TAG
mkdir -p "$OUT"

cd "$SRC"
env -u USE_MLOCK HIP_GRAPH=1 AMD_LOG_LEVEL=0 \
  GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
  HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 GPU_SINGLE_ALLOC_PERCENT=100 \
  HSA_ENABLE_SDMA=1 HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 \
  LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$BUILD_DIR/bin:/opt/rocm-6.1.0/lib \
  timeout 10m "$BUILD_DIR/bin/llama-cli" \
  -m "$MODEL" -lm mmap -lzm on -fit off -fa on \
  -ngl all -ncmoe "$NCMOE" -b 512 -ub 128 \
  --device rocm0,vulkan1,rocm1 -np 1 -mg 0 \
  -sm layer -ts "$TS" -c "$CTX" -ctk f16 -ctv f16 \
  --temp 0 --seed 42 -n 0 --no-warmup --single-turn --simple-io \
  --no-display-prompt --log-verbosity 3 -p '' >"$OUT/out.txt" 2>"$OUT/err.txt" || true

echo "=== $TAG ncmoe=$NCMOE ts=$TS ctx=$CTX ==="
grep -E "layers on CPU|offloaded.*layers|KV buffer|Compute buffer|CUDA0 buffer|CUDA1 buffer|CUDA2 buffer|Vulkan|buffer of size" "$OUT/err.txt" | tail -30
grep -E "MiB|GiB" "$OUT/err.txt" | tail -30
