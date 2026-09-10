#!/usr/bin/env bash
# Load-only placement probe for the Qwen3.8-Flash-Next lane.
# Loads the model, waits for the load marker, samples per-device VRAM, kills.
# Usage: bench/qwen38-fitprobe.sh <tag> [ncmoe] [ts] [ctx] [extra args...]
#   tag   - label used for the log dir /tmp/opencode/fitprobe/<tag>/
#   ncmoe - CPU MoE layer count (default 24)
#   ts    - tensor split (default 70,13,17)
#   ctx   - context size (default 4096)
set -uo pipefail
TAG=${1:?tag}
NCMOE=${2:-24}
TS=${3:-70,13,17}
CTX=${4:-4096}
shift 4 2>/dev/null || shift $#
EXTRA="$*"
SRC=${SRC:-/home/srcds/dev/uf3_rocm6.1_llama.cpp}
BUILD_DIR=${BUILD_DIR:-$SRC/build-qwen38-mtp}
MODEL=${MODEL:-/home/srcds/ai/ai/Qwen3.8-Flash-Next-AD-4.27bpw-Q4_K_M-M64.gguf}
SM=${SM:-layer}
OUT=/tmp/opencode/fitprobe/$TAG
mkdir -p "$OUT"
rm -f "$OUT"/vram.txt "$OUT"/err.txt

cd "$SRC"
env -u USE_MLOCK HIP_GRAPH=1 AMD_LOG_LEVEL=0 \
  GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
  HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 GPU_SINGLE_ALLOC_PERCENT=100 \
  HSA_ENABLE_SDMA=1 HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 \
  LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$BUILD_DIR/bin:/opt/rocm-6.1.0/lib \
  "$BUILD_DIR/bin/llama-cli" \
  -m "$MODEL" -lm mmap -lzm on -fit off -fa on \
  -ngl all -ncmoe "$NCMOE" -b 512 -ub 128 \
  --device rocm0,vulkan1,rocm1 -np 1 -mg 0 \
  -sm "$SM" -ts "$TS" -c "$CTX" -ctk f16 -ctv f16 \
  --temp 0 --seed 42 -n 0 --no-warmup --single-turn --simple-io \
  --no-display-prompt --log-verbosity 3 -p 'The capital of France is' $EXTRA >"$OUT/out.txt" 2>"$OUT/err.txt" &
PID=$!
trap 'kill "$PID" 2>/dev/null' INT TERM EXIT

# wait for load to finish (or exit), then sample VRAM
for _ in $(seq 1 240); do
  if ! kill -0 "$PID" 2>/dev/null; then break; fi
  if grep -q "model loaded\|encode: tokenized" "$OUT/err.txt" 2>/dev/null; then
    sleep 1
    { rocm-smi --showmeminfo vram --csv 2>/dev/null | grep -E "card[01]";
      nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader 2>/dev/null; } >"$OUT/vram.txt"
    break
  fi
  sleep 2
done
kill "$PID" 2>/dev/null
wait "$PID" 2>/dev/null

echo "=== $TAG ncmoe=$NCMOE ts=$TS ctx=$CTX ==="
grep -E "offloaded [0-9]+/[0-9]+|layers on CPU|pipeline parallelism disabled|failed to allocate|out of memory" "$OUT/err.txt" | head -6
cat "$OUT/vram.txt" 2>/dev/null || echo "NO VRAM SAMPLE (load failed?)"
