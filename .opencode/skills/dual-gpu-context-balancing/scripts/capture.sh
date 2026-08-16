#!/usr/bin/env bash
# Wait for a trial to finish fitting, then print the per-device breakdown.
# Usage: capture.sh <trial_name> [timeout_sec=900]
set -eu
NAME="${1:?usage: $0 <trial_name> [timeout_sec]}"
TIMEOUT="${2:-900}"
ROOT=/home/srcds/dev/rocm6.1_llama.cpp
LOG="$ROOT/.opencode/skills/dual-gpu-context-balancing/scripts/logs/$NAME.log"

# Done markers: server listening OR fatal alloc failure
DONE_PAT='HTTP server listening|server listening on|all slots are initialized'
FAIL_PAT='FATAL|failed to allocate|Unable to allocate|ggml_gallocr_alloc_tensor|out of memory|LLM error|terminate'

t=0
while [ $t -lt $TIMEOUT ]; do
  [ -s "$LOG" ] && grep -qiE "$DONE_PAT" "$LOG" && { echo "[done at ${t}s]"; break; }
  [ -s "$LOG" ] && grep -qiE "$FAIL_PAT" "$LOG" && { echo "[FAIL at ${t}s]"; break; }
  sleep 3; t=$((t+3))
done
[ $t -ge $TIMEOUT ] && echo "[timeout after ${TIMEOUT}s - log still growing?]"

echo "=== $NAME : fit-relevant lines ==="
grep -inE 'device [0-9]|buffer size|model size|KV |KV buffer|compute buffer|alloc|n_ctx|context|MTP|spec|tensor split|layer [0-9]|free memory|VRAM|MiB|limiting|fit' "$LOG" \
  | grep -viE 'session|cron|ggml-|cvector|embeddings' | tail -150
echo "=== last 8 lines ==="
tail -n 8 "$LOG"
