#!/usr/bin/env bash
# Standalone fattn-selector probe (PP350 follow-up, 2026-08-31).
# Production-matched server at c=250000, then a 1-token warmup request
# to force the real shadow-fit AUTO decision (the lane-dflash PROBE
# kills too early and only the shadow-0.00 first-round decision logs).
# Runs TWO variants to isolate the flip trigger:
#   A) lane-equivalent  (no --ctx-checkpoints)
#   B) production-exact (--ctx-checkpoints 30)
# Usage: bash bench/probe-fattn.sh        (GPUs free; ~6 min total)
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")/.."

BIN_DIR=${BIN_DIR:-$PWD/build-dflash-novega}
MODEL=${MODEL:-/home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf}
MD=${MD:-/home/srcds/ai/ai/Qwen3.8-27B-DFlash2-Q4_K_M.gguf}
PORT=${PORT:-8017}
C=${C:-250000}
TS=${TS:-35,20,45}

probe_variant() {
    local tag=$1; shift
    local log=bench/logs/probe-fattn-$tag.log
    echo "== variant $tag ($*)"
    pkill -9 -f "llama-server.*--port $PORT" 2>/dev/null || true
    sleep 1
    env HIP_GRAPH=1 AMD_LOG_LEVEL=0 \
      GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
      HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 HIP_FORCE_P2P=1 \
      GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
      HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \
      LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$BIN_DIR/bin:/opt/rocm-6.1.0/lib \
      setsid $BIN_DIR/bin/llama-server \
        -m "$MODEL" \
        --mmproj /home/srcds/ai/ai/mmproj-F16.gguf \
        -md "$MD" \
        --spec-type draft-dflash --spec-draft-n-max 4 \
        --spec-draft-override-tensor '.*=ROCm0' -ngld 99 \
        --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
        -b 16384 -ub 384 \
        --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
        --presence_penalty 0.0 --repeat-penalty 1.0 \
        --device rocm0,vulkan1,rocm1 --port $PORT -np 1 -mg 0 \
        --reasoning-preserve --reasoning on \
        -ctk f16 -ctv q8_0 \
        -cram 28000 --reasoning-format deepseek \
        -lv 4 \
        -ts "$TS" -sm layer -c "$C" \
        "$@" \
        >"$log" 2>&1 < /dev/null &
    disown
    for _ in $(seq 1 150); do
        grep -q "listening on" "$log" 2>/dev/null && break
        grep -qE "GGML_ASSERT|failed to allocate" "$log" 2>/dev/null && {
            echo "  START FAILED:"; grep -E "GGML_ASSERT|failed to allocate|ROCm error" "$log" | head -3; return 1; }
        sleep 2
    done
    grep -q "listening on" "$log" || { echo "  never listened"; return 1; }
    # ~3.6k-token warmup: the shadow-fit AUTO decision only fires on a
    # large-Q (prefill-sized) graph; a 1-token warmup never triggers it
    local payload
    payload=$(python3 -c "import json; print(json.dumps({'prompt': 'the quick brown fox jumps over the lazy dog. ' * 400, 'n_predict': 1, 'temperature': 0}))")
    curl -s -m 300 http://127.0.0.1:$PORT/completion \
        -H 'Content-Type: application/json' \
        -d "$payload" > /dev/null || true
    sleep 3
    echo "  selector decisions:"
    grep -E "ggml_cuda_fattn: device .* AUTO:" "$log" | sed 's/^.*I /  /'
    echo "  KV buffers:"
    grep -E "KV buffer size" "$log" | sed 's/^.*I /  /' | head -3
    pkill -9 -f "llama-server.*--port $PORT" 2>/dev/null || true
}

probe_variant lane-nockpt
probe_variant prod-ckpt30 --ctx-checkpoints 30

echo
echo "verdict guide: '-> f16 convert' = convert fits; '-> native' = flipped."
echo "If prod-ckpt30 says native and lane-nockpt says convert,"
echo "the ctx-checkpoints reserve is the trigger -> set GGML_CUDA_FATTN_PATH=force_convert"
echo "in 2llama-start-iq6v-dflash2.sh."
