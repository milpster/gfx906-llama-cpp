#!/usr/bin/env bash
# Fork vs latest mainline A/B on the FULL 2llama production config
# (Q6_K + mmproj + DFlash2 Q4_K_M drafter, spec-draft-n-max 4, ts 35,20,45,
# f16 K / q8_0 V, checkpoints 30, reasoning) with -c 200000.
#
# USER-MANAGED SERVER: the script prints the exact server command per side;
# you start it in your own terminal, the script waits for /health, runs the
# cmp-client.py protocol, then asks you to stop the server. ~10-11 min per
# side once the server is up (repro BEFORE -> PP16384 + one 120k fill ->
# TG512 temp-0 at 120k depth -> repro AFTER; same protocol as
# cmp-mainline-temp0.sh / E85).
#
# PRECONDITIONS:
#   - NO llama-server running (prod needs the VRAM freed or the probe
#     instance OOMs, E115): pgrep -fa llama-server must be empty
#   - mainline side: ~/dev/llama.cpp branch mainline-cmp @ upstream/master,
#     built into build-stock with the pinned 6.1 recipe
#
# Usage:  bash bench/cmp-mainline-user.sh             # both sides
#         SIDES=mainline bash bench/cmp-mainline-user.sh   # one side
# Env: C=200000 TS=35,20,45 FILL1=120000 TG_N=512 PORT_BASE=8021
#      MODEL=... MMPROJ=... DRAFTER=... TEMPLATE=...
#      FORK_BIN=... MAIN_BIN=... EXTRA_FORK=... EXTRA_MAINLINE=...
# Output: /tmp/opencode/cmp-2llama-<side>.json + summary (README numbers)
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")/.."

SIDES=${SIDES:-fork,mainline}
C=${C:-200000}
TS=${TS:-35,20,45}
TG_N=${TG_N:-512}
FILL1=${FILL1:-120000}
PORT_BASE=${PORT_BASE:-8021}
MODEL=${MODEL:-/home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf}
MMPROJ=${MMPROJ:-/home/srcds/ai/ai/mmproj-F16.gguf}
DRAFTER=${DRAFTER:-/home/srcds/ai/ai/Qwen3.8-27B-DFlash2-Q4_K_M.gguf}
TEMPLATE=${TEMPLATE:-"$PWD/froggeric_chat_templ.jinja"}
FORK_BIN=${FORK_BIN:-$PWD/build-dflash-novega}
MAIN_BIN=${MAIN_BIN:-/home/srcds/dev/llama.cpp/build-stock}
# fork-only flag; kept off on both A/B generations for row comparability
EXTRA_FORK=${EXTRA_FORK:---pipeline-parallel off}
EXTRA_MAINLINE=${EXTRA_MAINLINE:-}
mkdir -p /tmp/opencode

# --- preflight ---------------------------------------------------------------
for bin in "$FORK_BIN" "$MAIN_BIN"; do
    [ -x "$bin/bin/llama-server" ] || { echo "missing binary: $bin/bin/llama-server"; exit 1; }
done
for f in "$MODEL" "$MMPROJ" "$DRAFTER" "$TEMPLATE"; do
    [ -f "$f" ] || { echo "missing file: $f"; exit 1; }
done
if pgrep -f llama-server >/dev/null 2>&1; then
    echo "ERROR: a llama-server is still running - stop it first (prod holds"
    echo "the VRAM the probe needs; the second instance OOM'd on ROCm0, E115):"
    pgrep -fa llama-server || true
    exit 1
fi
echo "fork bin:     $FORK_BIN/bin/llama-server"
echo "mainline bin: $MAIN_BIN/bin/llama-server"
git -C "$MAIN_BIN/.." log --oneline -1 2>/dev/null || true

server_cmd() { # $1=bin dir  $2=port  $3=extra args
    cat <<EOF
HIP_GRAPH=1 AMD_LOG_LEVEL=0 \\
GGML_CUDA_FATTN_PATH=force_convert \\
GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \\
HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 HIP_FORCE_P2P=1 \\
GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \\
HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \\
LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$1/bin:/opt/rocm-6.1.0/lib \\
$1/bin/llama-server \\
  -m "$MODEL" --mmproj "$MMPROJ" \\
  -md "$DRAFTER" --spec-type draft-dflash --spec-draft-n-max 4 \\
  --spec-draft-override-tensor '.*=ROCm0' -ngld 99 \\
  --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \\
  -b 16384 -ub 384 --ctx-checkpoints 30 \\
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \\
  --presence_penalty 0.0 --repeat-penalty 1.0 \\
  --device rocm0,vulkan1,rocm1 --port $2 -np 1 -mg 0 \\
  --reasoning-preserve --reasoning on \\
  -ctk f16 -ctv q8_0 \\
  -cram 28000 --reasoning-format deepseek \\
  --chat-template-file "$TEMPLATE" \\
  -ts "$TS" -sm layer -c "$C" \\
  $3
EOF
}

run_side() {
    local side=$1 bin=$2 port=$3 extra=${4:-}
    echo
    echo "=============================================================== SIDE"
    echo "  $side  |  --port $port  |  verify the command below names:"
    echo "  $(readlink -f "$bin")"
    echo "==============================================================="
    server_cmd "$bin" "$port" "$extra"
    echo "-------------------------------------------------------------------"
    echo "Paste that into your terminal. When it prints"
    echo "'listening on http://127.0.0.1:$port' the script proceeds."
    echo "(If it fails to start, read the error in YOUR terminal and restart -"
    echo "the wait below keeps polling.)"
    local t0=$(date +%s)
    while :; do
        if curl -sf "http://127.0.0.1:$port/health" >/dev/null 2>&1; then
            echo "side $side: health OK (waited $(( ($(date +%s) - t0) / 60 )) min)"
            break
        fi
        if [ $(( $(date +%s) - t0 )) -gt 2400 ]; then
            echo "side $side: /health never came up in 40 min; aborting this side"
            return 1
        fi
        sleep 3
    done
    FILL1=$FILL1 TG_N=$TG_N python3 bench/cmp-client.py "$port" \
        | tee "/tmp/opencode/cmp-2llama-$side.json"
    echo
    echo "SIDE $side DONE. Stop its server now (Ctrl-C in that terminal)."
    read -r -p "Server stopped? [y/N] " ans
    case ${ans:-n} in
        y|Y) ;;
        *) echo "continuing without that side's teardown; make sure no server"
           echo "remains before the next side (the preflight re-checks)";
           pgrep -f llama-server >/dev/null 2>&1 && { echo "still running:"; pgrep -fa llama-server; exit 1; } ;;
    esac
    sleep 20  # let VRAM release before the next side
}

LAST=
for side in ${SIDES//,/ }; do
    case $side in
        fork)     run_side fork     "$FORK_BIN" "$PORT_BASE"        "$EXTRA_FORK" ;;
        mainline) run_side mainline "$MAIN_BIN" "$((PORT_BASE + 1))" "$EXTRA_MAINLINE" ;;
        *) echo "unknown side '$side' (fork|mainline)"; exit 1 ;;
    esac
    LAST=$side
done

python3 - "$SIDES" <<'EOF'
import json, os, sys
sides = sys.argv[1].split(",")
def load(s):
    p = "/tmp/opencode/cmp-2llama-%s.json" % s
    if not os.path.exists(p):
        return None
    return json.loads(open(p).read().strip().splitlines()[-1])
print()
print("== cmp-2llama summary (pp16384 / fill120k / tg512-t0 / acc / repro / sha) ==")
rows = {}
for s in sides:
    d = load(s)
    rows[s] = d
    if not d:
        print("%-8s (not run)" % s)
        continue
    print("%-8s pp=%6.1f fill=%6.1f tg=%5.1f acc=%.3f repro_ok=%s sha=%s tg_sha=%s" % (
        s, d.get("pp_tps", 0), (d.get("fill1") or {}).get("tps", 0),
        d.get("tg_tps", 0), d.get("acc", -1), d.get("repro_ok"),
        d.get("sha", "?")[:12], d.get("tg_sha", "?")[:12]))
f, m = rows.get("fork"), rows.get("mainline")
if f and m:
    ok = (f.get("sha") == m.get("sha")) and (f.get("tg_sha") == m.get("tg_sha"))
    pf = lambda a, b: round((a / b - 1) * 100, 1) if b else None
    print()
    print("fork vs mainline:  pp %+.1f pct   fill %+.1f pct   tg %+.1f pct" % (
        pf(f.get("pp_tps", 0), m.get("pp_tps", 0)),
        pf((f.get("fill1") or {}).get("tps", 0), (m.get("fill1") or {}).get("tps", 0)),
        pf(f.get("tg_tps", 0), m.get("tg_tps", 0))))
    print("temp0 sha parity across builds (README gate):", ok)
    if not ok:
        print("SHA MOVED - treat run as a regression, halt and bisect before README edits")
EOF
