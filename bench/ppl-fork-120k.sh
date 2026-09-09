#!/usr/bin/env bash
# Fork rerun for the E132 anomaly: PPL @120k ctx on build-dflash-novega
# (production binary + model of 2llama-start-iq6v_f16_f16.sh). Protocol
# = ppl-mainline-120k.sh / perplexity-gdnnorm.sh COMMON, so E132 stock
# / gdn-norm / mainline / this rerun are directly comparable.
# Self-gating: waits until no llama-perplexity is running. Logs ->
# logs/ppl-fork-120k.log, markers /tmp/opencode/ppl-fork-120k.{OK,FAIL}.
set -u
cd "$(dirname "$0")"
ROOT=$(cd .. && pwd)
BIN=$ROOT/build-dflash-novega/bin/llama-perplexity
LOG=logs/ppl-fork-120k.log

[ -x "$BIN" ] || { echo "error: missing $BIN" >&2; exit 1; }

while pgrep -f llama-perplexity > /dev/null 2>&1; do sleep 30; done
sleep 15

export HSA_OVERRIDE_GFX_VERSION=9.0.6 HSA_XNACK=0 HIP_VISIBLE_DEVICES=0,1
export HIP_FORCE_P2P=1 GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1
export HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100
export AMD_LOG_LEVEL=0

if LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$ROOT/build-dflash-novega/bin:/opt/rocm-6.1.0/lib \
    "$BIN" \
    -m /home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf \
    -f /home/srcds/ai/ai/log.txt \
    --device rocm0,vulkan1,rocm1 -ngl 99 \
    -sm layer -ts 35,20,45 \
    -c 120000 -b 1024 -ub 384 \
    --threads 9 --threads-batch 10 --no-mmap -fa on \
    > "$LOG" 2>&1; then
    touch /tmp/opencode/ppl-fork-120k.OK
else
    touch /tmp/opencode/ppl-fork-120k.FAIL
fi
