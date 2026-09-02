#!/usr/bin/env bash
# Numerics gate for GGML_CUDA_VEGA_TUNE_MMQ_DUALACC (journal E92).
# DUALACC reassociates the mmq sum (two accumulator chains), so temp-0
# sha is expected to move; the acceptance test is perplexity delta
# between the two builds on identical input and flags.
#
# f16 KV (no -ctk/-ctv) isolates the weight-matmul change.
# Stop the production server first. ~10 min per side.
set -euo pipefail

cd "$(dirname "$0")"
ROOT=$(cd .. && pwd)

BIN_A=${BIN_A:-$ROOT/build-dflash-novega/bin/llama-perplexity}
BIN_B=${BIN_B:-$ROOT/build-dualacc/bin/llama-perplexity}
MODEL=${MODEL:-/home/srcds/ai/ai/Qwen3.8-27B-UD-Q6_K_L.gguf}
TEXT=${TEXT:-/home/srcds/ai/ai/log.txt}

for b in "$BIN_A" "$BIN_B"; do
    [ -x "$b" ] || { echo "error: not found: $b" >&2; exit 1; }
done

COMMON=(
    -m "$MODEL" -f "$TEXT"
    --device rocm0,vulkan1,rocm1 -ngl 333
    -sm layer -ts 40,20,40
    -c 4096 -b 1024 -ub 384
    --threads 9 --threads-batch 10 --no-mmap -fa on
)

export HSA_OVERRIDE_GFX_VERSION=9.0.6 HSA_XNACK=0 HIP_VISIBLE_DEVICES=0,1
export HIP_FORCE_P2P=1 GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1
export HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100
export LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$ROOT/build-dflash-novega/bin:/opt/rocm-6.1.0/lib

run() { # $1 label, $2 bin, $3 libdir
    echo "== $1 ($2)"
    LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$3:/opt/rocm-6.1.0/lib \
        "$2" "${COMMON[@]}" 2>&1 | rtk grep -E "perplexity |llama_perf" | tail -4
}

run A "$BIN_A" "$ROOT/build-dflash-novega/bin"
echo
run B "$BIN_B" "$ROOT/build-dualacc/bin"
