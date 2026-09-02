#!/usr/bin/env bash
# Start one llama-server trial, benchmark it, stop it, record the result.
# See README.md for knobs and output fields.
set -euo pipefail

NAME=${1:?usage: ab-bench.sh trial_name [extra server args...]}
shift

cd "$(dirname "$0")"
ROOT=$(cd .. && pwd)
BIN=${BIN:-$ROOT/build-dflash-novega/bin/llama-server}
PORT=${PORT:-8013}
CTX=${CTX:-155000}
SPEC=${SPEC:-2}
TS=${TS:-41,20,39}
UB=${UB:-448}
MODEL=${MODEL:-$HOME/ai/ai/Qwen3.8-27B-Q8_0.gguf}
LOG=logs/$NAME.log
mkdir -p logs

if curl -sf "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
    echo "error: port $PORT already answers /health - stop the running server first" >&2
    exit 1
fi
if [ ! -x "$BIN" ]; then
    echo "error: binary not found or not executable: $BIN" >&2
    exit 1
fi

export AMD_LOG_LEVEL=0
export GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16
export HSA_OVERRIDE_GFX_VERSION=9.0.6
export HIP_VISIBLE_DEVICES=0,1
export HSA_XNACK=0
export GPU_SINGLE_ALLOC_PERCENT=100
export HSA_ENABLE_SDMA=1
export HSA_DISABLE_FRAGMENT_ALLOCATOR=0
export GPU_MAX_ALLOC_PERCENT=100
export USE_MLOCK=true
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH_OVERRIDE:-$(dirname "$BIN"):/home/srcds/rocm-gfx906-xnack/lib:/opt/rocm-6.1.0/lib}
if [ "${VK_F16:-0}" = "1" ]; then
    unset GGML_VK_DISABLE_F16
else
    export GGML_VK_DISABLE_F16=1
fi

SRV_PID=""
cleanup() {
    if [ -n "$SRV_PID" ] && kill -0 "$SRV_PID" 2>/dev/null; then
        kill -9 "$SRV_PID" 2>/dev/null || true
        wait "$SRV_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

SRV_PID=""
PP=${PP:-on}
SPEC_ARGS=(--spec-type draft-mtp --spec-draft-n-max "$SPEC")
if [ "${SPEC_TYPE:-draft-mtp}" = "none" ]; then
    SPEC_ARGS=()
elif [ "${SPEC_TYPE:-draft-mtp}" != "draft-mtp" ]; then
    SPEC_ARGS=(--spec-type "$SPEC_TYPE")
fi

"$BIN" \
    -m "$MODEL" \
    --threads-batch 8 --threads 8 --no-mmap -fa on -ngl 333 \
    -b 16384 -ub "$UB" --poll 100 --ctx-checkpoints 30 \
    --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0.0 \
    --presence_penalty 0.0 --repeat-penalty 1.0 \
    --device rocm0,vulkan1,rocm1 --port "$PORT" -np 1 -mg 0 \
    --reasoning-preserve --reasoning on --reasoning-budget -1 \
    "${SPEC_ARGS[@]}" \
    -cram 20000 --reasoning-format deepseek \
    --chat-template-file "$ROOT/qwen38chat_template.jinja" \
    --pipeline-parallel "$PP" \
    -sm cost -ts "$TS" \
    -c "$CTX" \
    "$@" >"$LOG" 2>&1 &
SRV_PID=$!

# watchdog: if the server process dies (OOM, config error), fail fast instead
# of letting the client's health-wait run its full 20-minute timeout
( while kill -0 "$SRV_PID" 2>/dev/null; do sleep 2; done
  echo "trial $NAME: server process exited before serving - see $LOG" >&2
  pkill -9 -f "bench-client.py $PORT" 2>/dev/null || true ) &
WD_PID=$!

RESULT=$(python3 bench-client.py "$PORT") || {
    kill "$WD_PID" 2>/dev/null || true
    echo "client failed for trial $NAME - server log: $LOG" >&2
    exit 1
}
kill "$WD_PID" 2>/dev/null || true

# SIGKILL immediately: graceful teardown can hang on Vulkan transfer queues,
# and we do not care about llama.cpp's own cleanup
kill -9 "$SRV_PID" 2>/dev/null || true
wait "$SRV_PID" 2>/dev/null || true
SRV_PID=""
# driver VRAM reclaim after SIGKILL
sleep 5

DATE=$(date +%F)
EXTRA=$(printf '%q ' "$@")
PP="-"
PPF=$(printf '%s' "$RESULT" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["pp_tps"])')
TG=$(printf '%s' "$RESULT" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["tg_tps"])')
ACC=$(printf '%s' "$RESULT" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("acc","-"))')
NCTX=$(printf '%s' "$RESULT" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["n_ctx"])')
LOAD=$(printf '%s' "$RESULT" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["load_s"])')
SHA=$(printf '%s' "$RESULT" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("sha","-"))')
OK="-"

if [ ! -f trials.md ] || ! grep -q '^| date' trials.md; then
    printf '| date | trial | bin | ctx | n_ctx | spec | ts | vk_f16 | extra | pp1_tps | pp_tps | tg_tps | acc | load_s | sha | ok | log |\n' > trials.md
    printf '|---|---|---|---|---|---|---|---|---|---:|---:|---:|---:|---:|---|---|---|\n' >> trials.md
fi
printf '| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |\n' \
    "$DATE" "$NAME" "$BIN" "$CTX" "$NCTX" "$SPEC" "$TS" "${VK_F16:-0}" "${EXTRA:- }" \
    "$PPF" "$PP" "$TG" "$ACC" "$LOAD" "$SHA" "$OK" "$LOG" >> trials.md

echo "$RESULT"
