#!/usr/bin/env bash
# Self-managed A/B lane: starts its own llama-server (own log), runs the
# cmp-client.py protocol, stops the server, prints the JSON and the
# cross-side delta when the other side's JSON exists.
#
# Protocol (unchanged since E85): temp0 repro BEFORE -> PP16384 first-batch
# + one 120k fill pass -> TG512 temp-0 at 120k depth (t/s, draft acceptance,
# sha) -> temp0 repro AFTER. Full 2llama production config, -c 200000,
# identical args on both sides (only binary/port differ); ~10-11 min + load.
#
# SIDE=mainline (default, lane 2): build-stock @ upstream master c5a5535e6,
#   port 8022, no fork flags.
# SIDE=fork     (lane 1):          build-dflash-novega @ d4419ace9, port 8021,
#   --pipeline-parallel off (kept for comparability with the 08-31 row).
#
# PRECONDITION: NO other llama-server running - stop the prod server first
# (port 8009) or the probe instance OOMs while prod holds the VRAM (E115).
#
# Usage:  bash bench/cmp-lane.sh                 # lane 2 (mainline)
#         SIDE=fork bash bench/cmp-lane.sh       # lane 1 (fork)
# Output: bench/logs/cmp-lane-<side>.log, /tmp/opencode/cmp-2llama-<side>.json
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")/.."

SIDE=${SIDE:-mainline}
C=${C:-200000}
TS=${TS:-35,20,45}
TG_N=${TG_N:-512}
FILL1=${FILL1:-120000}
MODEL=${MODEL:-/home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf}
MMPROJ=${MMPROJ:-/home/srcds/ai/ai/mmproj-F16.gguf}
DRAFTER=${DRAFTER:-/home/srcds/ai/ai/Qwen3.8-27B-DFlash2-Q4_K_M.gguf}
TEMPLATE=${TEMPLATE:-"$PWD/froggeric_chat_templ.jinja"}
FORK_BIN=${FORK_BIN:-$PWD/build-dflash-novega}
MAIN_BIN=${MAIN_BIN:-/home/srcds/dev/llama.cpp/build-stock}

case $SIDE in
    fork)     PORT=8021; BIN=$FORK_BIN; EXTRA="--pipeline-parallel off ${FORK_EXTRA:-}" ;;
    mainline) PORT=8022; BIN=$MAIN_BIN; EXTRA="" ;;
    *) echo "unknown SIDE '$SIDE' (fork|mainline)"; exit 1 ;;
esac
LOG=bench/logs/cmp-lane-$SIDE.log
JSON=/tmp/opencode/cmp-2llama-$SIDE.json
OTHER=$([ "$SIDE" = fork ] && echo mainline || echo fork)
mkdir -p bench/logs /tmp/opencode

# --- preflight ---------------------------------------------------------------
[ -x "$BIN/bin/llama-server" ] || { echo "missing binary: $BIN/bin/llama-server"; exit 1; }
for f in "$MODEL" "$MMPROJ" "$DRAFTER" "$TEMPLATE"; do
    [ -f "$f" ] || { echo "missing file: $f"; exit 1; }
done
if pgrep -f llama-server >/dev/null 2>&1; then
    echo "ERROR: a llama-server is still running - stop it first (it holds"
    echo "the VRAM the probe needs; the second instance OOM'd on ROCm0, E115):"
    pgrep -fa llama-server || true
    echo "then re-run: bash bench/cmp-lane.sh"
    exit 1
fi

# --- start server (own log) ---------------------------------------------------
pkill -9 -f "llama-server.*--port $PORT" 2>/dev/null || true
sleep 1
env HIP_GRAPH=1 AMD_LOG_LEVEL=0 \
  GGML_CUDA_FATTN_PATH=force_convert \
  GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
  HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 HIP_FORCE_P2P=1 \
  GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
  HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \
  LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$BIN/bin:/opt/rocm-6.1.0/lib \
  setsid $BIN/bin/llama-server \
    -m "$MODEL" --mmproj "$MMPROJ" \
    -md "$DRAFTER" --spec-type draft-dflash --spec-draft-n-max 4 \
    --spec-draft-override-tensor '.*=ROCm0' -ngld 99 \
    --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
    -b 16384 -ub 384 --ctx-checkpoints 30 \
    --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
    --presence_penalty 0.0 --repeat-penalty 1.0 \
    --device rocm0,vulkan1,rocm1 --port $PORT -np 1 -mg 0 \
    --reasoning-preserve --reasoning on \
    -ctk f16 -ctv q8_0 \
    -cram 28000 --reasoning-format deepseek \
    --chat-template-file "$TEMPLATE" \
    -ts "$TS" -sm layer -c "$C" \
    $EXTRA \
    >"$LOG" 2>&1 < /dev/null &
disown
t0=$(date +%s)
ok=""
for _ in $(seq 1 450); do
    grep -q "listening on" "$LOG" 2>/dev/null && { ok=1; break; }
    if grep -qE "GGML_ASSERT|failed to allocate|error while loading|unknown parameter|out of memory" "$LOG" 2>/dev/null; then
        echo "SIDE $SIDE: server failed to start; log tail:"; tail -20 "$LOG"
        pkill -9 -f "llama-server.*--port $PORT" 2>/dev/null || true
        exit 1
    fi
    sleep 2
done
[ -n "$ok" ] || { echo "SIDE $SIDE: never listened in 15 min; log tail:"; tail -20 "$LOG"; pkill -9 -f "llama-server.*--port $PORT" 2>/dev/null || true; exit 1; }
echo "SIDE $SIDE: listening on port $PORT after $(( ($(date +%s) - t0) / 60 )) min"
grep -E "AUTO: .* -> " "$LOG" | head -4 || true

# --- protocol ------------------------------------------------------------------
FILL1=$FILL1 TG_N=$TG_N python3 bench/cmp-client.py "$PORT" | tee "$JSON"
pkill -9 -f "llama-server.*--port $PORT" 2>/dev/null || true
sleep 15  # VRAM release before any next side

# --- cross-side comparison (when the other JSON exists) -------------------------
python3 - "$SIDE" "$OTHER" <<'EOF'
import json, os, sys
side, other = sys.argv[1], sys.argv[2]
def load(s):
    p = "/tmp/opencode/cmp-2llama-%s.json" % s
    return json.loads(open(p).read().strip().splitlines()[-1]) if os.path.exists(p) else None
d, o = load(side), load(other)
print()
print("== side %s: pp=%6.1f fill=%6.1f tg=%5.1f acc=%.3f repro_ok=%s sha=%s tg_sha=%s" % (
    side, d.get("pp_tps", 0), (d.get("fill1") or {}).get("tps", 0), d.get("tg_tps", 0),
    d.get("acc", -1), d.get("repro_ok"), d.get("sha", "?")[:12], d.get("tg_sha", "?")[:12]))
if o:
    pf = lambda a, b: round((a / b - 1) * 100, 1) if b else None
    print("== side %s: pp=%6.1f fill=%6.1f tg=%5.1f acc=%.3f repro_ok=%s sha=%s tg_sha=%s" % (
        other, o.get("pp_tps", 0), (o.get("fill1") or {}).get("tps", 0), o.get("tg_tps", 0),
        o.get("acc", -1), o.get("repro_ok"), o.get("sha", "?")[:12], o.get("tg_sha", "?")[:12]))
    f, m = (d, o) if side == "fork" else (o, d)
    print("fork vs mainline: pp %+.1f pct   fill %+.1f pct   tg %+.1f pct   acc %+.3f" % (
        pf(f.get("pp_tps", 0), m.get("pp_tps", 0)),
        pf((f.get("fill1") or {}).get("tps", 0), (m.get("fill1") or {}).get("tps", 0)),
        pf(f.get("tg_tps", 0), m.get("tg_tps", 0)),
        f.get("acc", -1) - m.get("acc", -1)))
    ok = (f.get("sha") == m.get("sha")) and (f.get("tg_sha") == m.get("tg_sha"))
    print("temp0 sha parity across builds (README gate):", ok)
    if not ok:
        print("SHA MOVED - treat run as a regression, halt and bisect before README edits")
else:
    print("(other side %s not run yet - no cross-side delta)" % other)
EOF
echo "lane $SIDE done; log: $LOG"
