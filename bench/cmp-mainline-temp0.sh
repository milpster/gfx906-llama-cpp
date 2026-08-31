#!/usr/bin/env bash
# Temp-0 speed + reproducibility comparison: fork build vs mainline build.
# Same base-model config on both sides (no spec drafter, no vision, no
# fork-only flags): greedy PP16384 first-batch -> 120k fill -> TG@depth,
# sha256 of the temp-0 token stream per side, then side-by-side summary.
#
# Usage:  bash bench/cmp-mainline-temp0.sh            # both sides
#         SIDES=fork bash bench/cmp-mainline-temp0.sh # one side only
# Env: C=155000 TS=35,20,45 TG_N=256 FILL1=120000 PORT_BASE=8021
#      MODEL=... FORK_BIN=... MAIN_BIN=... EXTRA_FORK=... EXTRA_MAINLINE=...
# Requires: GPUs free; mainline built in MAIN_BIN (see ~/dev/llama.cpp,
# branch mainline-cmp; configure flags in /tmp/opencode/mainline-build.log).
# Output: bench/logs/cmp-temp0-<side>.log (server), /tmp/opencode/cmp-temp0-<side>.json
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")/.."

SIDES=${SIDES:-fork,mainline}
C=${C:-155000}
TS=${TS:-35,20,45}
TG_N=${TG_N:-256}
FILL1=${FILL1:-120000}
PORT_BASE=${PORT_BASE:-8021}
MODEL=${MODEL:-/home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf}
FORK_BIN=${FORK_BIN:-$PWD/build-dflash-novega}
MAIN_BIN=${MAIN_BIN:-/home/srcds/dev/llama.cpp/build-stock}
mkdir -p bench/logs /tmp/opencode

run_side() {
    local side=$1 bin=$2 port=$3 extra=${4:-}
    local log=bench/logs/cmp-temp0-$side.log
    echo "== side=$side bin=$bin port=$port c=$C ts=$TS"
    pkill -9 -f "llama-server.*--port $port" 2>/dev/null || true
    sleep 1
    env HIP_GRAPH=1 AMD_LOG_LEVEL=0 \
      GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
      HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 HIP_FORCE_P2P=1 \
      GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
      HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \
      LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$bin/bin:/opt/rocm-6.1.0/lib \
      setsid $bin/bin/llama-server \
        -m "$MODEL" \
        --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
        -b 16384 -ub 384 \
        --device rocm0,vulkan1,rocm1 --port $port -np 1 -mg 0 \
        -ctk f16 -ctv q8_0 \
        -ts "$TS" -sm layer -c "$C" \
        $extra \
        >"$log" 2>&1 < /dev/null &
    disown
    local ok=""
    for _ in $(seq 1 150); do
        grep -q "listening on" "$log" 2>/dev/null && { ok=1; break; }
        if grep -qE "GGML_ASSERT|failed to allocate|error while loading" "$log" 2>/dev/null; then
            echo "SIDE $side: server failed to start; log tail:"; tail -20 "$log"; return 1
        fi
        sleep 2
    done
    [ -n "$ok" ] || { echo "SIDE $side: never listened; log tail:"; tail -20 "$log"; return 1; }
    grep -E "AUTO: .* -> " "$log" | head -4 || true
    FILL2=0 FILL1=$FILL1 TG_N=$TG_N python3 bench/lane-client.py "$port" \
        | tee /tmp/opencode/cmp-temp0-$side.json
    pkill -9 -f "llama-server.*--port $port" 2>/dev/null || true
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
    p = "/tmp/opencode/cmp-temp0-%s.json" % s
    if not os.path.exists(p):
        return None
    return json.loads(open(p).read().strip().splitlines()[-1])
fork, main = load("fork"), load("mainline")
print("== cmp-temp0 summary (pp16384 / fill120k / tg / repro / sha)")
for name, d in (("fork", fork), ("mainline", main)):
    if not d:
        print("%-8s (not run)" % name)
        continue
    print("%-8s pp=%6.1f fill=%6.1f tg=%5.2f repro_ok=%s sha=%s" % (
        name, d.get("pp_tps", 0), (d.get("fill1") or {}).get("tps", 0),
        d.get("tg_tps", 0), d.get("repro_ok"), d.get("sha", "?")[:12]))
if fork and main:
    print("temp0 sha match across builds:", fork.get("sha") == main.get("sha"))
EOF
