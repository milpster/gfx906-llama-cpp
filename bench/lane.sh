#!/usr/bin/env bash
# Lane runner: full-protocol config lane per journal/JOURNAL-2026-08-26.md.
# Usage: LANE=L0a SPEC_ARGS="--spec-type draft-mtp-adaptive --spec-draft-n-max 10 --spec-draft-n-min-adaptive 3" EXTRA_ARGS="" ./lane.sh
# Server log: bench/logs/lane-<LANE>.log ; result line appended to bench/logs/lane-results.jsonl
set -eu
cd "$(dirname "$(readlink -f "$0")")/.."
LANE=${LANE:?set LANE}
SPEC_ARGS=${SPEC_ARGS:?set SPEC_ARGS}
EXTRA_ARGS=${EXTRA_ARGS:-}
PORT=${PORT:-8014}
BIN_DIR=${BIN_DIR:-$PWD/build-sync25}

LOG="bench/logs/lane-$LANE.log"
RES="bench/logs/lane-results.jsonl"
STATUS="/tmp/opencode/lane-$LANE.status"
mkdir -p bench/logs
rm -f "$LOG" "$STATUS"
echo RUNNING > "$STATUS"
trap 'echo FAILED > "$STATUS" 2>/dev/null || true' ERR

pkill -9 -f "llama-server.*--port $PORT" 2>/dev/null || true
sleep 1

env HIP_GRAPH=1 AMD_LOG_LEVEL=0 \
GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 HIP_FORCE_P2P=1 \
GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \
LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$BIN_DIR/bin:/opt/rocm-6.1.0/lib \
setsid $BIN_DIR/bin/llama-server \
  -m /home/srcds/ai/ai/Qwen3.8-27B-UD-Q6_K_XL.gguf \
  --mmproj /home/srcds/ai/ai/mmproj-F16.gguf \
  --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
  -b 16384 -ub 384 --ctx-checkpoints 30 \
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  --device rocm0,vulkan1,rocm1 --port "$PORT" -np 1 -mg 0 \
  --reasoning-preserve --reasoning on \
  --cache-reuse 256 \
  -ctk f16 -ctv q8_0 \
  -cram 28000 --reasoning-format deepseek \
  --chat-template-file froggeric_chat_templ.jinja \
  --pipeline-parallel off \
  -ts 40,20,40 -sm layer -c 210000 \
  --override-tensor '^blk\.64\.nextn\..*=ROCm0' \
  $SPEC_ARGS $EXTRA_ARGS \
  >"$LOG" 2>&1 < /dev/null &
SRV_PID=$!
disown

if ! python3 bench/lane-client.py "$PORT" | tee /tmp/opencode/lane-$LANE.json; then
  echo "LANE $LANE FAILED - server log tail:" >&2
  tail -30 "$LOG" >&2
  pkill -9 -f "llama-server.*--port $PORT" 2>/dev/null || true
  exit 1
fi

python3 - "$LANE" "$SPEC_ARGS" "$EXTRA_ARGS" <<'EOF' >> "$RES"
import json, sys
lane, spec, extra = sys.argv[1:4]
line = open("/tmp/opencode/lane-%s.json" % lane).read().strip().splitlines()[-1]
d = json.loads(line)
d.update({"lane": lane, "spec": spec, "extra": extra})
print(json.dumps(d))
EOF

pkill -9 -f "llama-server.*--port $PORT" 2>/dev/null || true
echo DONE > "$STATUS"
echo "LANE $LANE DONE"
