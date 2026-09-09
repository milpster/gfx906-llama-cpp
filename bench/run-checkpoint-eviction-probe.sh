#!/usr/bin/env bash
# Reproduce the short-turn checkpoint eviction behavior fixed by upstream #28302.
set -euo pipefail

ROOT=$(dirname "$(readlink -f "$0")")/..
cd "$ROOT"

LABEL=${1:?usage: $0 LABEL BIN_DIR}
BIN_DIR=${2:?usage: $0 LABEL BIN_DIR}
PORT=${PORT:-8018}
MODEL=${MODEL:-/home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf}
TS=${TS:-35,20,45}
C=${C:-16384}
CHECKPOINTS=${CHECKPOINTS:-30}
CHECKPOINT_MIN_STEP=${CHECKPOINT_MIN_STEP:-8192}

if [[ ! "$LABEL" =~ ^[A-Za-z0-9._-]+$ ]]; then
    printf 'invalid label: %s\n' "$LABEL" >&2
    exit 2
fi
if [[ ! -x "$BIN_DIR/bin/llama-server" ]]; then
    printf 'missing executable: %s/bin/llama-server\n' "$BIN_DIR" >&2
    exit 2
fi
if [[ ! -f "$MODEL" ]]; then
    printf 'missing model: %s\n' "$MODEL" >&2
    exit 2
fi
if fuser "$PORT/tcp" >/dev/null 2>&1; then
    printf 'port %s is already in use\n' "$PORT" >&2
    exit 2
fi

LOG="bench/logs/checkpoint-eviction-$LABEL.log"
RESULT="bench/logs/checkpoint-eviction-$LABEL.json"
STATUS="/tmp/opencode/checkpoint-eviction-$LABEL.status"
mkdir -p bench/logs /tmp/opencode
rm -f "$LOG" "$RESULT" "$STATUS"
printf 'RUNNING\n' > "$STATUS"

server_pid=
cleanup() {
    rc=$?
    trap - EXIT
    set +e
    if [[ -n "$server_pid" ]] && kill -0 "$server_pid" 2>/dev/null; then
        kill -TERM -- "-$server_pid" 2>/dev/null
        for _ in {1..20}; do
            kill -0 "$server_pid" 2>/dev/null || break
            sleep 0.5
        done
        kill -KILL -- "-$server_pid" 2>/dev/null || true
        wait "$server_pid" 2>/dev/null || true
    fi
    if (( rc == 0 )); then
        printf 'DONE\n' > "$STATUS"
    else
        printf 'FAILED\n' > "$STATUS"
        printf 'probe failed; inspect %s\n' "$LOG" >&2
    fi
    exit "$rc"
}
trap cleanup EXIT INT TERM

env HIP_GRAPH=${HIP_GRAPH:-1} AMD_LOG_LEVEL=0 \
    GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
    HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 HIP_FORCE_P2P=1 \
    GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
    HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \
    LD_LIBRARY_PATH="/home/srcds/rocm-gfx906-xnack/lib:$BIN_DIR/bin:/opt/rocm-6.1.0/lib" \
    setsid "$BIN_DIR/bin/llama-server" \
    -m "$MODEL" \
    --no-mmproj \
    --threads-batch 10 --threads 9 --load-mode none -fa on -ngl 333 \
    -b 2048 -ub 384 \
    --device rocm0,vulkan1,rocm1 --port "$PORT" -np 1 -mg 0 \
    --pipeline-parallel on \
    --reasoning off \
    -ctk f16 -ctv q8_0 \
    -cram 28000 \
    --chat-template-file "$ROOT/froggeric_chat_templ.jinja" \
    --ctx-checkpoints "$CHECKPOINTS" \
    --checkpoint-min-step "$CHECKPOINT_MIN_STEP" \
    -lv 4 \
    -ts "$TS" -sm layer -c "$C" \
    > "$LOG" 2>&1 < /dev/null &
server_pid=$!

ready=0
for _ in {1..300}; do
    if curl --fail --silent --show-error "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
        ready=1
        break
    fi
    if ! kill -0 "$server_pid" 2>/dev/null; then
        break
    fi
    sleep 2
done
if (( ready == 0 )); then
    printf 'server did not become ready\n' >&2
    exit 1
fi

uv run --script "$ROOT/bench/checkpoint-eviction-probe.py" "$PORT" | tee "$RESULT"
printf 'checkpoint probe %s complete\n' "$LABEL"
