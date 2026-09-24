#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)
BUILD=${BUILD:-$ROOT/build-sync0924}
OUT=${OUT:-$ROOT/bench/logs/sync0924-swift-q6q8q4}
PORT=${PORT:-8013}
SERVER_PID=

cleanup() {
    if [ -n "$SERVER_PID" ] && kill -0 "$SERVER_PID" 2>/dev/null; then
        kill -TERM -- "-$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

while read -r pid command; do
    if [[ "$command" != *"--embedding"* || "$command" != *"-ngl 0"* ]]; then
        echo "ERROR: GPU-backed llama-server is running; validation requires exclusive GPU access"
        echo "$pid $command"
        exit 1
    fi
done < <(pgrep -fa '[l]lama-server' || true)

if ss -ltn "sport = :$PORT" | grep -q LISTEN; then
    echo "ERROR: port $PORT is already in use"
    exit 1
fi

mkdir -p "$OUT/runtime/prompts"
git -C "$ROOT" rev-parse HEAD > "$OUT/git-sha.txt"
uname -a > "$OUT/system.txt"
rocminfo > "$OUT/rocminfo.txt"

BIN="$BUILD/bin/llama-server" \
LD_LIB="$BUILD/bin" \
LOG_DIR="$OUT/runtime" \
PORT="$PORT" \
setsid "$ROOT/swift_llama_start-q6_q8_q4.sh" > "$OUT/launcher.log" 2>&1 < /dev/null &
SERVER_PID=$!

ready=
for _ in $(seq 1 450); do
    if grep -q "listening on" "$OUT/launcher.log" 2>/dev/null; then
        ready=1
        break
    fi
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
        echo "ERROR: validation server exited before listening"
        exit 1
    fi
    sleep 2
done
[ -n "$ready" ] || { echo "ERROR: validation server did not listen within 15 minutes"; exit 1; }

FILL1=16384 TG_N=1024 python3 "$ROOT/bench/cmp-client.py" "$PORT" | tee "$OUT/result.json"
