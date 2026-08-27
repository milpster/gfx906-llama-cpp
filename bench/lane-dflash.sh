#!/usr/bin/env bash
# Lane runner for the DFlash2 production config (llama-start-q6v-dflash2.sh)
# with manually fitted parameters. Reusable: only placement/ctx/model/KV vary
# via env; all other production knobs stay fixed so a lane cannot silently
# regress them (same contract as bench/lane.sh + skill run.sh).
#
# Defaults = 2026-08-27 F16-KV campaign: i1-Q6_K model, NO KV quantization
# (no -ctk/-ctv -> f16/f16), -ts 40,20,40 -sm layer, -c via env.
# Keep fit ENABLED: params are pinned so it adjusts nothing, but the -lv 4
# breakdown tables only print from the fit pass (--fit off = no tables).
#
# Usage: LANE=F1 [TS=.. SM=.. C=.. MODEL=.. CTK=.. CTV=.. PORT=.. TG_N=..
#                FILL1=.. FILL2=.. EXTRA=..] ./lane-dflash.sh
# Protocol: PP16384 first-batch -> fill FILL1 (120k) -> TG1024 @depth
#           (FILL2=0 default: one fill pass, user protocol D16).
# Server log: bench/logs/lane-$LANE.log ; result -> bench/logs/lane-results.jsonl
# Status markers: /tmp/opencode/lane-$LANE.status (RUNNING/DONE/FAILED).
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")/.."
LANE=${LANE:?set LANE}
PORT=${PORT:-8014}
BIN_DIR=${BIN_DIR:-$PWD/build-dflash}
MODEL=${MODEL:-/home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf}
MD=${MD:-/home/srcds/ai/ai/Qwen3.8-27B-DFlash2-Q4_K_M.gguf}
TS=${TS:-40,20,40}
SM=${SM:-layer}
C=${C:-195000}
OT=${OT:-}
CTK=${CTK:-}
CTV=${CTV:-}
CTKV=${CTK:+-ctk $CTK}   # empty = f16 (unquantized)
CTVV=${CTV:+-ctv $CTV}
OTARG=()
[ -n "$OT" ] && OTARG=(--override-tensor "$OT")
# NGRAM=1 chains ngram-mod ahead of the drafter (priority order set in speculative.cpp)
SPEC_TYPE=${SPEC_TYPE:-draft-dflash}
SPEC_N_MAX=${SPEC_N_MAX:-7}
NGRAMARGS=()
if [ "${NGRAM:-0}" = "1" ]; then
  SPEC_TYPE="ngram-mod,$SPEC_TYPE"
  NGRAMARGS=(--spec-ngram-mod-n-match "${NGRAM_MATCH:-24}" \
             --spec-ngram-mod-n-min "${NGRAM_MIN:-28}" \
             --spec-ngram-mod-n-max "${NGRAM_MAX:-64}")
fi
SPECARGS=(--spec-type "$SPEC_TYPE" --spec-draft-n-max "$SPEC_N_MAX" "${NGRAMARGS[@]}")

LOG="bench/logs/lane-$LANE.log"
RES="bench/logs/lane-results.jsonl"
STATUS="/tmp/opencode/lane-$LANE.status"
mkdir -p bench/logs /tmp/opencode
rm -f "$LOG" "$STATUS"
echo RUNNING > "$STATUS"
trap 'echo FAILED > "$STATUS" 2>/dev/null || true' ERR

pkill -9 -f "llama-server.*--port $PORT" 2>/dev/null || true
sleep 1

env HIP_GRAPH=${HIP_GRAPH:-1} AMD_LOG_LEVEL=0 \
  GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
  HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 HIP_FORCE_P2P=1 \
  GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
  HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \
  LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$BIN_DIR/bin:/opt/rocm-6.1.0/lib \
  setsid $BIN_DIR/bin/llama-server \
  -m "$MODEL" \
  --mmproj /home/srcds/ai/ai/mmproj-F16.gguf \
  -md "$MD" \
  "${SPECARGS[@]}" \
  --spec-draft-override-tensor '.*=ROCm0' -ngld 99 \
  --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
  -b 16384 -ub 384 --ctx-checkpoints 30 \
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  --device rocm0,vulkan1,rocm1 --port "$PORT" -np 1 -mg 0 \
  --reasoning-preserve --reasoning on \
  $CTKV $CTVV \
  -cram 28000 --reasoning-format deepseek \
  --chat-template-file "$PWD/froggeric_chat_templ.jinja" \
  --pipeline-parallel ${PP:-off} \
  -lv 4 \
  -ts "$TS" -sm "$SM" -c "$C" \
  "${OTARG[@]}" \
  ${EXTRA:-} \
  >"$LOG" 2>&1 < /dev/null &
disown

# PROBE=1: fit evidence only (wait for listen/fail, print buffers, kill, no client)
if [ "${PROBE:-0}" = "1" ]; then
  ok=""
  for _ in $(seq 1 120); do
    if grep -q "listening on" "$LOG" 2>/dev/null; then ok=1; break; fi
    if grep -qE "GGML_ASSERT|failed to allocate" "$LOG" 2>/dev/null; then break; fi
    sleep 2
  done
  grep -E "model buffer size = |KV buffer size|RS buffer size|memory breakdown|ROCm0 \(|Vulkan1 \(|ROCm1 \(|n_ctx_slot|failed to allocate|GGML_ASSERT|ROCm error" "$LOG" | head -30
  pkill -9 -f "llama-server.*--port $PORT" 2>/dev/null || true
  echo "${ok:+DONE}${ok:-FAILED}" > "$STATUS"
  exit 0
fi

if ! FILL2="$FILL2" FILL1="${FILL1:-120000}" TG_N="${TG_N:-1024}" \
     python3 bench/lane-client.py "$PORT" | tee /tmp/opencode/lane-$LANE.json; then
  echo "LANE $LANE FAILED - server log tail:" >&2
  tail -30 "$LOG" >&2
  pkill -9 -f "llama-server.*--port $PORT" 2>/dev/null || true
  exit 1
fi

python3 - "$LANE" "$MODEL" "$TS" "$SM" "$C" "$CTK" "$CTV" "$OT" "${EXTRA:-}" <<'EOF' >> "$RES"
import json, sys
lane, model, ts, sm, c, ctk, ctv, ot, extra = sys.argv[1:10]
line = open("/tmp/opencode/lane-%s.json" % lane).read().strip().splitlines()[-1]
d = json.loads(line)
d.update({"lane": lane, "model": model.rsplit("/",1)[-1], "ts": ts, "sm": sm,
          "c": int(c), "kv": (ctk or "f16") + "/" + (ctv or "f16"),
          "ot": ot or "none", "extra": extra})
print(json.dumps(d))
EOF

pkill -9 -f "llama-server.*--port $PORT" 2>/dev/null || true
echo DONE > "$STATUS"
echo "LANE $LANE DONE"
