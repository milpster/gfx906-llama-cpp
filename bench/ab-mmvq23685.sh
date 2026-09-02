#!/usr/bin/env bash
# A/B for the upstream #23685 merge (4x packed Q8_1 MMVQ, Q4_K/Q5_K/Q6_K).
# Two trials, only BIN differs:
#   A = build-dflash-novega (production binary, no PR)
#   B = build-mmvq23685     (merge, commit 7dc25a9f5)
# ab-bench.sh starts one server per trial, runs the client, kills it,
# appends a row to bench/trials.md.
#
# First attempt (harness env only) OOMed on ROCm1 at compute-buffer
# reserve: the 250k ctx needs the production fit (-ctv q8_0, -sm layer,
# -ub 384, drafter args). The harness defaults (f16 KV, -sm cost, no
# drafter) do not fit. EXTRAS below carry the production-fit set (same
# as repro-crash.sh, proven to load C=250000, minus mmproj); appended
# args win over the harness's own -sm cost / -ub 448 / -cram 20000.
# Q4_K_M drafter, not Q8_0: Q8_0 + 250k is the E80 crash window.
#
# Stop the production server first (trials need the full 40 GB).
# ~30-40 min per trial. Fallback if it still does not fit:
#   CTX=200000 ./ab-mmvq23685.sh
# Results -> journal E88 (journal/JOURNAL-2026-09-02.md).
set -euo pipefail

cd "$(dirname "$0")"
ROOT=$(cd .. && pwd)

BIN_A=${BIN_A:-$ROOT/build-dflash-novega/bin/llama-server}
BIN_B=${BIN_B:-$ROOT/build-mmvq23685/bin/llama-server}
MODEL=${MODEL:-/home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf}
DRAFT=${DRAFT:-/home/srcds/ai/ai/Qwen3.8-27B-DFlash2-Q4_K_M.gguf}
PORT=${PORT:-8013}

[ -x "$BIN_A" ] || { echo "error: not found: $BIN_A" >&2; exit 1; }
[ -x "$BIN_B" ] || { echo "error: not found: $BIN_B" >&2; exit 1; }

# production parity (2llama-start-iq6v-dflash2.sh)
export PP=off
export TS=35,20,45 CTX=250000
export SPEC_TYPE=draft-dflash
export HIP_GRAPH=1 HIP_FORCE_P2P=1 GGML_CUDA_FATTN_PATH=force_convert

EXTRAS=(
    -md "$DRAFT" --spec-draft-n-max 4
    --spec-draft-override-tensor '.*=ROCm0' -ngld 99
    -ctk f16 -ctv q8_0
    -sm layer -ub 384 -cram 28000
)

echo "== A: control ($BIN_A)"
BIN=$BIN_A MODEL=$MODEL PORT=$PORT ./ab-bench.sh mmvq23685-A "${EXTRAS[@]}"

echo
echo "== B: #23685 merge ($BIN_B)"
BIN=$BIN_B MODEL=$MODEL PORT=$PORT ./ab-bench.sh mmvq23685-B "${EXTRAS[@]}"

echo
echo "== trial rows:"
grep "mmvq23685-" trials.md | tail -2
