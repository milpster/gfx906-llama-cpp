#!/usr/bin/env bash
# PPL lane: production launcher config (2llama-start-iq6v_f16_f16.sh)
# at 80k ctx. Base model only (no mmproj / drafter, per the canonical
# PPL protocol in perplexity-upstream-fork.sh: PPL does not exercise
# spec decoding). Launcher deltas vs the 120k mainline control:
# -ctk/-ctv f16, GGML_CUDA_FATTN_PATH=force_convert,
# GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16, -b 16384, -ngl 333.
# Self-gating: waits while another llama-perplexity holds the GPUs.
# Logs -> logs/ppl-prod80k.log, markers /tmp/opencode/ppl-prod80k.{OK,FAIL}.
set -u
cd "$(dirname "$0")"
ROOT=$(cd .. && pwd)
BIN=${BIN:-$ROOT/build-dflash-novega/bin/llama-perplexity}
LOG=logs/ppl-prod80k.log

[ -x "$BIN" ] || { echo "error: missing $BIN" >&2; exit 1; }

while pgrep -f llama-perplexity > /dev/null 2>&1; do sleep 30; done
sleep 15

export HSA_OVERRIDE_GFX_VERSION=9.0.6 HSA_XNACK=0 HIP_VISIBLE_DEVICES=0,1
export HIP_FORCE_P2P=1 GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1
export HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100
export AMD_LOG_LEVEL=0
# launcher numerics env (2llama-start-iq6v_f16_f16.sh)
export GGML_CUDA_FATTN_PATH=force_convert GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16
export USE_MLOCK=true

if LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$ROOT/build-dflash-novega/bin:/opt/rocm-6.1.0/lib \
    "$BIN" \
    -m /home/srcds/ai/ai/Qwen3.8-27B-UD-Q6_K_L.gguf \
    -f /home/srcds/ai/ai/log.txt \
    --device rocm0,rocm1 -mg 0 -ngl 333 \
    -sm layer \
    -c 10000 -b 16384 -ub 2048 \
    -ctk f16 -ctv f16 \
    --threads 9 --threads-batch 10 --no-mmap -fa on \
    > "$LOG" 2>&1; then
    touch /tmp/opencode/ppl-prod80k.OK
else
    touch /tmp/opencode/ppl-prod80k.FAIL
fi
