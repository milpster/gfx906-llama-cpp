#!/usr/bin/env bash
# Mainline control for E132: PPL @120k ctx on upstream mainline
# (~/dev/llama.cpp build-stock, mainline-cmp @ c5a5535e6, pre-#28068).
# Same protocol as bench/perplexity-gdnnorm.sh COMMON args so the
# fork-stock / fork-gdn-norm / mainline trio is directly comparable.
# Self-gating: waits until no llama-perplexity is running (patch side
# of the e132 window still owns the GPUs). Logs -> logs/ppl-gdn-mainline.log,
# markers /tmp/opencode/ppl-mainline.{OK,FAIL}.
set -u
cd "$(dirname "$0")"
ML=${ML:-/home/srcds/dev/llama.cpp/build-stock}
BIN=$ML/bin/llama-perplexity
LOG=logs/ppl-gdn-mainline.log

[ -x "$BIN" ] || { echo "error: missing $BIN" >&2; exit 1; }

while pgrep -f llama-perplexity > /dev/null 2>&1; do sleep 30; done
sleep 15

export HSA_OVERRIDE_GFX_VERSION=9.0.6 HSA_XNACK=0 HIP_VISIBLE_DEVICES=0,1
export HIP_FORCE_P2P=1 GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1
export HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100
export AMD_LOG_LEVEL=0

if LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$ML/bin:/opt/rocm-6.1.0/lib \
    "$BIN" \
    -m /home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf \
    -f /home/srcds/ai/ai/log.txt \
    --device rocm0,vulkan1,rocm1 -ngl 99 \
    -sm layer -ts 35,20,45 \
    -c 120000 -b 1024 -ub 384 \
    --threads 9 --threads-batch 10 --no-mmap -fa on \
    > "$LOG" 2>&1; then
    touch /tmp/opencode/ppl-mainline.OK
else
    touch /tmp/opencode/ppl-mainline.FAIL
fi
