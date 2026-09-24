#!/usr/bin/env bash
# Current fork vs upstream master. Server lanes copy
# 2llama-start-iq6v_f16_f16.sh, except c=130000, temp=0, and the
# mainline draft context inherits all devices so it can use output.weight on ROCm1.
# PPL and bidirectional cross-KLD use the E140 c=10000 protocol.
set -euo pipefail

ROOT=/home/srcds/dev/uf3_rocm6.1_llama.cpp
UP=/home/srcds/dev/llama.cpp
FORK_BIN=$ROOT/build-sync0913
MAIN_BIN=$UP/build-0913
MODEL=/home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf
MMPROJ=/home/srcds/ai/ai/mmproj-F16.gguf
DRAFTER=/home/srcds/ai/ai/Qwen3.8-27B-DFlash2-Q4_K_M.gguf
TEXT=/home/srcds/ai/ai/wikitext-2-raw/wiki.test.raw
TEMPLATE=$ROOT/froggeric_chat_templ_v23_cache.jinja
OUT=$ROOT/bench/logs
CTX=${CTX:-130000}
FILL1=${FILL1:-120000}
TG_N=${TG_N:-1024}
CHUNKS=${CHUNKS:-6}
RUN_QUALITY=${RUN_QUALITY:-1}
RUN_SIDE=${RUN_SIDE:-both}

mkdir -p "$OUT" /tmp/opencode
cd "$ROOT"

export HSA_OVERRIDE_GFX_VERSION=9.0.6 HSA_XNACK=0 HIP_VISIBLE_DEVICES=0,1
export HIP_FORCE_P2P=1 GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1
export HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 AMD_LOG_LEVEL=0

run_ppl() {
    local side=$1 bin=$2
    echo "== PPL $side"
    LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$bin/bin:/opt/rocm-6.1.0/lib \
        "$bin/bin/llama-perplexity" -m "$MODEL" -f "$TEXT" \
        --device rocm0,vulkan1,rocm1 -ngl 99 -sm layer -ts 35,20,45 \
        -c 10000 -b 1024 -ub 384 --threads 9 --threads-batch 10 \
        --load-mode none -fa on > "$OUT/ppl-ab0913-$side.log" 2>&1
    grep -E 'Final estimate' "$OUT/ppl-ab0913-$side.log"
    sleep 5
}

run_kld() {
    local label=$1 bin=$2; shift 2
    echo "== KLD $label"
    LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$bin/bin:/opt/rocm-6.1.0/lib \
        "$bin/bin/llama-perplexity" -m "$MODEL" -f "$TEXT" \
        --device rocm0,vulkan1,rocm1 -ngl 99 -sm layer -ts 35,20,45 \
        -c 10000 -b 1024 -ub 384 --threads 9 --threads-batch 10 \
        --load-mode none -fa on --chunks "$CHUNKS" "$@" \
        > "$OUT/kld-ab0913-$label.log" 2>&1
    grep -E 'Final estimate|Mean KLD|same top|KL divergence' "$OUT/kld-ab0913-$label.log" | tail -8 || true
    sleep 5
}

SRV_PID=
cleanup() {
    if [ -n "$SRV_PID" ] && kill -0 "$SRV_PID" 2>/dev/null; then
        kill -9 "$SRV_PID" 2>/dev/null || true
        wait "$SRV_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

run_speed() {
    local side=$1 bin=$2 port=$3
    local log=$OUT/ab0913-$side-server.log
    local extra=()
    local draft_device=()
    if [ "$side" = fork ]; then
        extra=(--pipeline-parallel on)
        draft_device=(--spec-draft-device ROCm0)
    fi
    echo "== SPEED $side (c=$CTX, PP16384, TG$TG_N@${FILL1}, temp=0)"
    env HIP_GRAPH="${HIP_GRAPH:-1}" AMD_LOG_LEVEL=0 LLAMA_DFLASH_MIRROR_OUTPUT=1 \
        GGML_CUDA_FATTN_PATH=force_convert GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 \
        HSA_OVERRIDE_GFX_VERSION=9.0.6 HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 HIP_FORCE_P2P=1 \
        GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 HSA_DISABLE_FRAGMENT_ALLOCATOR=0 \
        GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \
        LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$bin/bin:/opt/rocm-6.1.0/lib \
        setsid "$bin/bin/llama-server" \
        -m "$MODEL" --mmproj "$MMPROJ" -md "$DRAFTER" \
        --spec-type ngram-mod,draft-dflash --spec-draft-n-max 4 \
        --spec-ngram-mod-n-match 24 --spec-ngram-mod-n-min 28 --spec-ngram-mod-n-max 64 \
        --spec-draft-override-tensor '.*=ROCm0' "${draft_device[@]}" -ngld 99 \
        --threads-batch 10 --threads 9 --load-mode none -fa on -ngl 333 \
        -b 16384 -ub 384 --ctx-checkpoints 30 --temp 0 --top-p 0.95 --top-k 20 --min-p 0 \
        --presence_penalty 0 --repeat-penalty 1 --device rocm0,vulkan1,rocm1 \
        --port "$port" -np 1 -mg 0 --reasoning-preserve --reasoning on \
        -ctk f16 -ctv f16 -cram 28000 --reasoning-format deepseek \
        --chat-template-file "$TEMPLATE" -ts 35,20,45 -sm layer -c "$CTX" \
        --no-mmproj-offload "${extra[@]}" > "$log" 2>&1 < /dev/null &
    SRV_PID=$!

    local ready=
    for _ in $(seq 1 180); do
        grep -q 'listening on' "$log" 2>/dev/null && { ready=1; break; }
        if ! kill -0 "$SRV_PID" 2>/dev/null; then
            echo "$side exited before serving"; tail -20 "$log"; return 1
        fi
        sleep 2
    done
    [ -n "$ready" ] || { echo "$side never listened"; tail -20 "$log"; return 1; }

    FILL1=$FILL1 TG_N=$TG_N python3 bench/cmp-client.py "$port" \
        | tee "$OUT/ab0913-$side.json"
    cleanup
    SRV_PID=
    sleep 10
}

if [ "$RUN_QUALITY" = 1 ]; then
    rm -f "$OUT"/kld-ab0913-*.bin
    run_ppl mainline "$MAIN_BIN"
    run_ppl fork "$FORK_BIN"
    run_kld mainline-dump "$MAIN_BIN" --save-all-logits "$OUT/kld-ab0913-logits-mainline.bin"
    run_kld fork-vs-mainline "$FORK_BIN" --kl-divergence --kl-divergence-base "$OUT/kld-ab0913-logits-mainline.bin"
    run_kld fork-dump "$FORK_BIN" --save-all-logits "$OUT/kld-ab0913-logits-fork.bin"
    run_kld mainline-vs-fork "$MAIN_BIN" --kl-divergence --kl-divergence-base "$OUT/kld-ab0913-logits-fork.bin"
    rm -f "$OUT"/kld-ab0913-*.bin
fi

if [ "$RUN_SIDE" != fork ]; then
    run_speed mainline "$MAIN_BIN" 8031
fi
if [ "$RUN_SIDE" != mainline ]; then
    run_speed fork "$FORK_BIN" 8031
fi

echo "== JSON results"
if [ "$RUN_SIDE" = both ]; then
    cat "$OUT/ab0913-mainline.json" "$OUT/ab0913-fork.json"
else
    cat "$OUT/ab0913-$RUN_SIDE.json"
fi
