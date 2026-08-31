#!/usr/bin/env bash
# Fork vs mainline comparison on the FULL 2llama production config
# (Q6_K + mmproj + DFlash2 Q4_K_M drafter, spec-draft-n-max 4, ts 35,20,45,
# f16 K / q8_0 V, checkpoints 30, reasoning) with -c 200000.
# Per side: temp0 repro BEFORE -> PP16384 first-batch + one 120k fill pass
# -> TG512 temp-0 at 120k depth (t/s, draft acceptance, output sha) ->
# temp0 repro AFTER. Same server args on both sides; only the binary and
# port differ. Runtime ~10-11 min per side.
#
# Usage:  bash bench/cmp-mainline-temp0.sh             # both sides
#         SIDES=mainline bash bench/cmp-mainline-temp0.sh   # one side
# Env: C=200000 TS=35,20,45 FILL1=120000 TG_N=512 PORT_BASE=8021
#      MODEL=... MMPROJ=... DRAFTER=... TEMPLATE=...
#      FORK_BIN=... MAIN_BIN=... EXTRA_FORK=... EXTRA_MAINLINE=...
# Requires: GPUs free; mainline built in MAIN_BIN at current upstream
# master (~/dev/llama.cpp, branch mainline-cmp).
# Output: bench/logs/cmp-2llama-<side>.log (server), /tmp/opencode/cmp-2llama-<side>.json
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
# fork-only flag (removed upstream); fork default is off, explicit for fidelity
EXTRA_FORK=${EXTRA_FORK:---pipeline-parallel off}
mkdir -p bench/logs /tmp/opencode

run_side() {
    local side=$1 bin=$2 port=$3 extra=${4:-}
    local log=bench/logs/cmp-2llama-$side.log
    echo "== side=$side bin=$bin port=$port c=$C ts=$TS"
    pkill -9 -f "llama-server.*--port $port" 2>/dev/null || true
    sleep 1
    env HIP_GRAPH=1 AMD_LOG_LEVEL=0 \
      GGML_CUDA_FATTN_PATH=force_convert \
      GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
      HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 HIP_FORCE_P2P=1 \
      GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
      HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \
      LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$bin/bin:/opt/rocm-6.1.0/lib \
      setsid $bin/bin/llama-server \
        -m "$MODEL" --mmproj "$MMPROJ" \
        -md "$DRAFTER" --spec-type draft-dflash --spec-draft-n-max 4 \
        --spec-draft-override-tensor '.*=ROCm0' -ngld 99 \
        --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
        -b 16384 -ub 384 --ctx-checkpoints 30 \
        --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
        --presence_penalty 0.0 --repeat-penalty 1.0 \
        --device rocm0,vulkan1,rocm1 --port $port -np 1 -mg 0 \
        --reasoning-preserve --reasoning on \
        -ctk f16 -ctv q8_0 \
        -cram 28000 --reasoning-format deepseek \
        --chat-template-file "$TEMPLATE" \
        -ts "$TS" -sm layer -c "$C" \
        $extra \
        >"$log" 2>&1 < /dev/null &
    disown
    local ok=""
    for _ in $(seq 1 150); do
        grep -q "listening on" "$log" 2>/dev/null && { ok=1; break; }
        if grep -qE "GGML_ASSERT|failed to allocate|error while loading|unknown parameter" "$log" 2>/dev/null; then
            echo "SIDE $side: server failed to start; log tail:"; tail -20 "$log"; return 1
        fi
        sleep 2
    done
    [ -n "$ok" ] || { echo "SIDE $side: never listened; log tail:"; tail -20 "$log"; return 1; }
    grep -E "AUTO: .* -> " "$log" | head -4 || true
    FILL1=$FILL1 TG_N=$TG_N python3 bench/cmp-client.py "$port" \
        | tee /tmp/opencode/cmp-2llama-$side.json
    pkill -9 -f "llama-server.*--port $port" 2>/dev/null || true
    sleep 10
}

for side in ${SIDES//,/ }; do
    case $side in
        fork)     run_side fork     "$FORK_BIN" "$PORT_BASE"        "${EXTRA_FORK:-}" ;;
        mainline) run_side mainline "$MAIN_BIN" "$((PORT_BASE + 1))" "${EXTRA_MAINLINE:-}" ;;
        *) echo "unknown side '$side' (fork|mainline)"; exit 1 ;;
    esac
done

python3 - <<'EOF'
import json, os
def load(s):
    p = "/tmp/opencode/cmp-2llama-%s.json" % s
    if not os.path.exists(p):
        return None
    return json.loads(open(p).read().strip().splitlines()[-1])
fork, main = load("fork"), load("mainline")
print("== cmp-2llama summary (pp16384 / fill120k / tg512-t0 / acc / repro / sha)")
for name, d in (("fork", fork), ("mainline", main)):
    if not d:
        print("%-8s (not run)" % name)
        continue
    print("%-8s pp=%6.1f fill=%6.1f tg=%5.1f acc=%.3f repro_ok=%s sha=%s tg_sha=%s" % (
        name, d.get("pp_tps", 0), (d.get("fill1") or {}).get("tps", 0),
        d.get("tg_tps", 0), d.get("acc", -1), d.get("repro_ok"),
        d.get("sha", "?")[:12], d.get("tg_sha", "?")[:12]))
if fork and main:
    print("temp0 repro sha match across builds:", fork.get("sha") == main.get("sha"))
    print("temp0 tg sha match across builds:  ", fork.get("tg_sha") == main.get("tg_sha"))
EOF
