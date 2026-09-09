#!/usr/bin/env bash
# Kernel-duration profiler lane: prod-shaped llama-server under rocprofv3.
# Purpose (E138): per-kernel GPU time shares for fill/TG phases to rank opt
# candidates. rocprof-attach cannot inject (6.1 runtime), so we launch under
# rocprofv3 and SIGINT to flush.
#
# Usage:
#   PHASE=fill ./prof-kernels.sh            # one ~16k-token wiki fill, n_predict 1
#   PHASE=tg   ./prof-kernels.sh            # warm 2k, then n_predict 384 spec TG
# Vars: PHASE FILL_TOKENS(16000) TG_N(384) WARM_TOKENS(2048) PORT(8021)
#       OUT(/tmp/opencode/prof-$PHASE) BIN_DIR MODEL MD TS SM C SPEC_N_MAX PP EXTRA
# Output: $OUT/*.csv (rocprofv3), server log /tmp/opencode/prof-server-$PHASE.log
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")/.."

PHASE=${PHASE:?set PHASE=fill|tg}
PORT=${PORT:-8021}
BIN_DIR=${BIN_DIR:-$PWD/build-dflash-novega}
MODEL=${MODEL:-/home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf}
MD=${MD:-/home/srcds/ai/ai/Qwen3.8-27B-DFlash2-Q4_K_M.gguf}
TS=${TS:-35,20,45}
SM=${SM:-layer}
C=${C:-250000}
SPEC_N_MAX=${SPEC_N_MAX:-4}
PP=${PP:-on}
EXTRA=${EXTRA:-}
FILL_TOKENS=${FILL_TOKENS:-16000}
WARM_TOKENS=${WARM_TOKENS:-2048}
TG_N=${TG_N:-384}
OUT=${OUT:-/tmp/opencode/prof-$PHASE}
ROCPROF=${ROCPROF:-/opt/rocm/bin/rocprofv3}

WIKI=/home/srcds/ai/ai/wikitext-2-raw/wiki.test.raw
[ -f "$WIKI" ] || { echo "missing $WIKI" >&2; exit 2; }
[ -x "$ROCPROF" ] || { echo "missing $ROCPROF" >&2; exit 2; }

mkdir -p "$OUT"
SLOG=/tmp/opencode/prof-server-$PHASE.log
pkill -9 -f "llama-server.*--port $PORT" 2>/dev/null || true
sleep 1

# ~4 chars/token: FILL_TOKENS of wiki text, JSON-escaped via python
PROMPT_FILE=/tmp/opencode/prof-prompt-$PHASE.json
python3 - "$WIKI" "$FILL_TOKENS" "$PROMPT_FILE" <<'PYEOF'
import json, sys
wiki, ntok, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
with open(wiki, encoding='utf-8') as f:
    text = f.read(4 * ntok)
text = ' '.join(text.split())  # collapse newlines
with open(out, 'w', encoding='utf-8') as f:
    json.dump({'prompt': text, 'n_predict': 1, 'temperature': 0.0}, f)
PYEOF

env HIP_GRAPH=1 AMD_LOG_LEVEL=0 \
  GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
  HIP_VISIBLE_DEVICES=${HIP_VIS:-0,1} HSA_XNACK=0 HIP_FORCE_P2P=1 \
  GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
  HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \
  GGML_CUDA_FATTN_PATH=force_convert LLAMA_DFLASH_MIRROR_OUTPUT=1 \
  LD_LIBRARY_PATH=${XNACK_LIB_DIR:-/home/srcds/rocm-gfx906-xnack/lib}:$BIN_DIR/bin:/opt/rocm-6.1.0/lib \
  setsid "$ROCPROF" -d "$OUT" -f csv -- "$BIN_DIR/bin/llama-server" \
  -m "$MODEL" \
  --mmproj /home/srcds/ai/ai/mmproj-F16.gguf \
  -md "$MD" \
  --spec-type draft-dflash --spec-draft-n-max "$SPEC_N_MAX" \
  --spec-draft-override-tensor '.*=ROCm0' -ngld 99 \
  --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
  -b 16384 -ub 384 --ctx-checkpoints 30 \
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  --device ${DEVICES:-rocm0,vulkan1,rocm1} --port "$PORT" -np 1 -mg 0 \
  --reasoning-preserve --reasoning on \
  -ctv q8_0 \
  -cram 28000 --reasoning-format deepseek \
  --chat-template-file "$PWD/froggeric_chat_templ.jinja" \
  --pipeline-parallel "$PP" \
  -lv 4 \
  -ts "$TS" -sm "$SM" -c "$C" \
  ${SPECDEV:+--spec-draft-device $SPECDEV} --no-mmproj-offload \
  ${EXTRA} \
  > "$SLOG" 2>&1 < /dev/null &
disown

# wait for listen
ok=""
for _ in $(seq 1 150); do
  if grep -q "listening on" "$SLOG" 2>/dev/null; then ok=1; break; fi
  if grep -qE "GGML_ASSERT|failed to allocate" "$SLOG" 2>/dev/null; then break; fi
  sleep 2
done
[ -n "$ok" ] || { echo "server did not start; tail:" >&2; tail -20 "$SLOG" >&2; pkill -9 -f "llama-server.*--port $PORT" || true; exit 1; }
SPID=$(pgrep -f "llama-serve[r].*--port $PORT" | head -1)
echo "server pid $SPID up; phase=$PHASE"

req() { # $1 = json file, $2 = timeout
  curl -sS --max-time "$2" -H 'Content-Type: application/json' \
       -d @"$1" "http://127.0.0.1:$PORT/v1/completions" -o /dev/null
}

case "$PHASE" in
  fill)
    req "$PROMPT_FILE" 600
    ;;
  tg)
    python3 - "$WIKI" "$WARM_TOKENS" /tmp/opencode/prof-warm.json <<'PYEOF'
import json, sys
wiki, ntok, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
with open(wiki, encoding='utf-8') as f:
    text = ' '.join(f.read(4 * ntok).split())
with open(out, 'w', encoding='utf-8') as f:
    json.dump({'prompt': text, 'n_predict': 16, 'temperature': 1.0}, f)
PYEOF
    req /tmp/opencode/prof-warm.json 300   # warm KV + drafter
    python3 - "$WIKI" "$TG_N" /tmp/opencode/prof-tg.json <<'PYEOF'
import json, sys
wiki, npred, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
with open(wiki, encoding='utf-8') as f:
    text = ' '.join(f.read(120).split())
with open(out, 'w', encoding='utf-8') as f:
    json.dump({'prompt': text, 'n_predict': npred, 'temperature': 1.0}, f)
PYEOF
    req /tmp/opencode/prof-tg.json 600
    ;;
  *) echo "bad PHASE" >&2; exit 2;;
esac

sleep 2
# graceful stop -> rocprofv3 flushes csv on app exit
pkill -INT -f "llama-server.*--port $PORT" 2>/dev/null || true
for _ in $(seq 1 30); do pgrep -f "llama-serve[r].*--port $PORT" >/dev/null || break; sleep 2; done
pkill -9 -f "llama-server.*--port $PORT" 2>/dev/null || true
sleep 3
echo "profile artifacts:"
ls -la "$OUT" | head -10
