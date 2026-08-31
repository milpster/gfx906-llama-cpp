#!/usr/bin/env bash
# Reproduce the pp393b/c fattn "invalid device function" crash.
# Starts one server (lane env), sends a small greedy completion (the
# 12-token task that crashed the lanes), prints CRASH/CLEAN plus the
# fattn selector decisions, kills the server.
# Env: BIN_DIR, MD, C, PORT, TOKENS, FATTN_PATH (unset = AUTO)
set -uo pipefail
cd "$(dirname "$(readlink -f "$0")")/.."
BIN_DIR=${BIN_DIR:-$PWD/build-dflash-novega}
MD=${MD:-/home/srcds/ai/ai/Qwen3.8-27B-DFlash2-Q8_0.gguf}
C=${C:-250000}
PORT=${PORT:-8017}
TOKENS=${TOKENS:-12}
LOG=/tmp/opencode/repro-crash-$PORT.log

pkill -9 -f "llama-server.*--port $PORT" 2>/dev/null
sleep 1
FPENV=()
[ -n "${FATTN_PATH:-}" ] && FPENV=(GGML_CUDA_FATTN_PATH="$FATTN_PATH")

env HIP_GRAPH=1 AMD_LOG_LEVEL=0 ${FPENV[@]+"${FPENV[@]}"} \
  GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
  HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 HIP_FORCE_P2P=1 \
  GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
  HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \
  LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$BIN_DIR/bin:/opt/rocm-6.1.0/lib \
  setsid $BIN_DIR/bin/llama-server \
    -m /home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf \
    --mmproj /home/srcds/ai/ai/mmproj-F16.gguf \
    -md "$MD" \
    --spec-type draft-dflash --spec-draft-n-max 4 \
    --spec-draft-override-tensor '.*=ROCm0' -ngld 99 \
    --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
    -b 16384 -ub 384 \
    --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
    --device rocm0,vulkan1,rocm1 --port $PORT -np 1 -mg 0 \
    -ctk f16 -ctv q8_0 -lv 4 \
    -ts 35,20,45 -sm layer -c "$C" \
    >"$LOG" 2>&1 < /dev/null &
disown

for _ in $(seq 1 120); do
    grep -q "listening on" "$LOG" 2>/dev/null && break
    grep -qE "GGML_ASSERT|failed to allocate|ROCm error" "$LOG" 2>/dev/null && break
    sleep 2
done
grep -q "listening on" "$LOG" || {
    echo "START-FAIL:"; tail -5 "$LOG"; pkill -9 -f "llama-server.*--port $PORT" 2>/dev/null; exit 1; }

python3 - "$PORT" "$TOKENS" <<'EOF'
import json, sys, urllib.request
port, n = sys.argv[1], int(sys.argv[2])
req = urllib.request.Request(
    "http://127.0.0.1:%s/completion" % port,
    data=json.dumps({"prompt": "Write a clear technical explanation of why the sky is blue."[:n],
                     "n_predict": 1, "temperature": 0}).encode(),
    headers={"Content-Type": "application/json"})
try:
    urllib.request.urlopen(req, timeout=180).read()
    print("REQUEST-OK")
except Exception as e:
    print("REQUEST-ERR:", str(e)[:120])
EOF

sleep 3
echo "== fattn decisions:"
grep -E "ggml_cuda_fattn: device .* AUTO:" "$LOG" | sed 's/^.*I /  /' | head -4
if grep -q "ROCm error" "$LOG"; then
    echo "VERDICT: CRASH"
    grep -m1 -A2 "ROCm error" "$LOG" | head -3
else
    echo "VERDICT: CLEAN"
fi
pkill -9 -f "llama-server.*--port $PORT" 2>/dev/null
sleep 2
