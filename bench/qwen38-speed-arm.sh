#!/usr/bin/env bash
# Qwen3.8-Flash-Next 200k PP speed-arm benchmark.
# Usage: bench/qwen38-speed-arm.sh <arm> <reps> [extra llama-cli args...]
# Results: /tmp/opencode/qwen38-speed/<arm>/{rN.log,rN.out,summary.txt}

set -uo pipefail

ARM=${1:?arm name required}
REPS=${2:?rep count required}
shift 2

REPO=$(cd "$(dirname "$0")/.." && pwd)
BUILD_DIR=${BUILD_DIR:-$REPO/build-qwen38-mtp}
BIN=$BUILD_DIR/bin/llama-cli
MODEL=/home/srcds/ai/ai/Qwen3.8-Flash-Next-AD-4.27bpw-Q4_K_M-M64.gguf
DRAFT=/home/srcds/ai/ai/MTP/mtp-Qwen3.8-Flash-Next-shared-Q8_0.gguf
MMPROJ=/home/srcds/ai/ai/mmproj-Qwen3.8-Flash-Next-F16.gguf
PROMPT_SOURCE=/tmp/opencode/pp16384-prompt.txt
OUTDIR=/tmp/opencode/qwen38-speed/$ARM
PROMPT=$OUTDIR/prompt-2k.txt

if [ ! -s "$PROMPT_SOURCE" ]; then
    echo "missing prompt source: $PROMPT_SOURCE" >&2
    exit 2
fi

mkdir -p "$OUTDIR"
# PROMPT_BYTES selects the prompt length (default 7200 chars ~ 2684 tok, E147)
dd if="$PROMPT_SOURCE" of="$PROMPT" bs=1 count=${PROMPT_BYTES:-7200} status=none
: > "$OUTDIR/summary.txt"

cleanup() {
    jobs -pr | xargs -r kill 2>/dev/null || true
}
trap cleanup INT TERM EXIT

BASE_ARGS=(
    -m "$MODEL"
    --threads 16 --threads-batch 16 --poll 0 --poll-batch 0
    -lm mmap -lzm on -fit off -fa on -ngl all -ncmoe 29
    -b 16384 -ub 128 -cram 0 --ctx-checkpoints 0
    --device rocm0,vulkan1,rocm1 -np 1 -mg 0
    --pipeline-parallel off -sm layer -ts 66,10,24
    -c 204800 -ctk f16 -ctv f16
    --temp 0 --seed 42 -n 0 --no-warmup
)

# FULL_STACK=0 drops the MTP draft + mmproj sidecars for pure-PP probing
# (E147): the draft bundle wastes 2647 MiB VRAM and never runs at -n 0.
if [ "${FULL_STACK:-1}" = "1" ]; then
    BASE_ARGS+=(
        -md "$DRAFT" --spec-type draft-mtp-adaptive
        --spec-draft-n-max 10 --spec-draft-n-min-adaptive 3
        -ngld all -ctkd f16 -ctvd f16 -otd '.*=ROCm0'
        -mm "$MMPROJ" -mmdev none
    )
fi

BASE_ARGS+=(
    --single-turn --simple-io --no-display-prompt --log-verbosity 3
    -f "$PROMPT"
)

echo "== arm $ARM reps=$REPS extra: $* =="
for i in $(seq 1 "$REPS"); do
    LOG=$OUTDIR/r$i.log
    OUT=$OUTDIR/r$i.out
    START=$(date +%s)
    env -u USE_MLOCK \
        HIP_GRAPH=1 \
        AMD_LOG_LEVEL=0 \
        GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 \
        HSA_OVERRIDE_GFX_VERSION=9.0.6 \
        HIP_VISIBLE_DEVICES=0,1 \
        HSA_XNACK=0 \
        GPU_SINGLE_ALLOC_PERCENT=100 \
        HSA_ENABLE_SDMA=1 \
        HSA_DISABLE_FRAGMENT_ALLOCATOR=0 \
        GPU_MAX_ALLOC_PERCENT=100 \
        LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$BUILD_DIR/bin:/opt/rocm-6.1.0/lib \
        timeout 30m "$BIN" "${BASE_ARGS[@]}" "$@" -o "$OUT" \
        < /dev/null 2>&1 | tee "$LOG"
    EXIT=${PIPESTATUS[0]}
    WALL=$(($(date +%s) - START))
    PP=$(grep -m1 "prompt eval time" "$LOG" || true)
    SHA=$(sha256sum "$OUT" 2>/dev/null | cut -d' ' -f1)
    printf 'run=%s exit=%s wall_s=%s sha=%s | %s\n' \
        "$i" "$EXIT" "$WALL" "${SHA:-NA}" "$PP" \
        | tee -a "$OUTDIR/summary.txt"
    sleep 2
done

echo "== summary $ARM =="
cat "$OUTDIR/summary.txt"
