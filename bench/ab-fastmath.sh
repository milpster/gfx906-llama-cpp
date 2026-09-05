#!/usr/bin/env bash
# A/B for HIP_FAST_MATH=1 (E71 audit item 1: sole remaining unmeasured
# build opt-in; -ffast-math -fno-math-errno was on through build-vega20/
# build-sync25, dropped since build-dflash with no recorded verdict).
# Two trials, only BIN differs:
#   A = build-dflash-novega (production flags, same source commit)
#   B = build-fastmath      (CMAKE_HIP_FLAGS="-ffast-math -fno-math-errno")
# Gates: pp/tg/acc. sha may move (numerics class, not a bug) - adopting it
# is a user policy call; measurement first. Mirror parity with prod
# (E119.6): both sides LLAMA_DFLASH_MIRROR_OUTPUT=1 + --spec-draft-device.
# Stop the production server first (trials need the full 40 GB).
# ~30-40 min per trial. Results -> journal E120 (JOURNAL-2026-09-05.md).
set -euo pipefail

cd "$(dirname "$0")"
ROOT=$(cd .. && pwd)

BIN_A=${BIN_A:-$ROOT/build-dflash-novega/bin/llama-server}
BIN_B=${BIN_B:-$ROOT/build-fastmath/bin/llama-server}
MODEL=${MODEL:-/home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf}
DRAFT=${DRAFT:-/home/srcds/ai/ai/Qwen3.8-27B-DFlash2-Q4_K_M.gguf}
PORT=${PORT:-8013}

[ -x "$BIN_A" ] || { echo "error: not found: $BIN_A" >&2; exit 1; }
[ -x "$BIN_B" ] || { echo "error: not found: $BIN_B" >&2; exit 1; }

# production parity (2llama-start-iq6v-dflash2.sh incl. E119.6 mirror)
export PP=off
export TS=35,20,45 CTX=250000
export SPEC_TYPE=draft-dflash
export HIP_GRAPH=1 HIP_FORCE_P2P=1 GGML_CUDA_FATTN_PATH=force_convert
export LLAMA_DFLASH_MIRROR_OUTPUT=1

EXTRAS=(
    -md "$DRAFT" --spec-draft-n-max 4
    --spec-draft-override-tensor '.*=ROCm0' --spec-draft-device ROCm0 -ngld 99
    -ctk f16 -ctv q8_0
    -sm layer -ub 384 -cram 28000
)

echo "== A: control ($BIN_A)"
BIN=$BIN_A MODEL=$MODEL PORT=$PORT ./ab-bench.sh fastmath-A "${EXTRAS[@]}"

echo
echo "== B: -ffast-math ($BIN_B)"
BIN=$BIN_B MODEL=$MODEL PORT=$PORT ./ab-bench.sh fastmath-B "${EXTRAS[@]}"

echo
echo "== trial rows:"
grep "fastmath-" trials.md | tail -2
