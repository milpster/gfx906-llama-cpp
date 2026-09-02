#!/usr/bin/env bash
# A/B for GGML_CUDA_VEGA_TUNE_MMQ_Q8LDR (q8_0 load_tiles GCN5 remap, #21698,
# journal E94). Two trials, only BIN differs:
#   A = build-dflash-novega  (production, DUALACC off)
#   B = build-dualacc        (Q8LDR on, #21698 port)
# Lane = current UD production shape (E89): UD-Q6_K_L @ 256k, ts 40,20,40.
#
# Expectation: pp up ~7-8% (E91 pro-rate: Q8_0 = 25.5% of GPU cycles,
# PR claims +28-36% on pure-Q8_0 MI50); sha IDENTICAL (remap stores the
# same values, different thread ownership - verified in E94 ISA check);
# tg/acc within noise. Perplexity gate not required.
#
# Stop the production server first (trials need the full 40 GB).
# ~30-40 min per trial. Fallback if it does not fit: CTX=250112.
# Results -> journal E94 (journal/JOURNAL-2026-09-02.md).
set -euo pipefail

cd "$(dirname "$0")"
ROOT=$(cd .. && pwd)

BIN_A=${BIN_A:-$ROOT/build-dflash-novega/bin/llama-server}
BIN_B=${BIN_B:-$ROOT/build-q8ldr/bin/llama-server}
MODEL=${MODEL:-/home/srcds/ai/ai/Qwen3.8-27B-UD-Q6_K_L.gguf}
DRAFT=${DRAFT:-/home/srcds/ai/ai/Qwen3.8-27B-DFlash2-Q4_K_M.gguf}
PORT=${PORT:-8013}

[ -x "$BIN_A" ] || { echo "error: not found: $BIN_A" >&2; exit 1; }
[ -x "$BIN_B" ] || { echo "error: not found: $BIN_B" >&2; exit 1; }

# production parity (2UDllama-start-iq6v-dflash2.sh)
export PP=off
export TS=40,20,40 CTX=256000
export SPEC_TYPE=draft-dflash
export HIP_GRAPH=1 HIP_FORCE_P2P=1 GGML_CUDA_FATTN_PATH=force_convert

EXTRAS=(
    -md "$DRAFT" --spec-draft-n-max 4
    --spec-draft-override-tensor '.*=ROCm0' -ngld 99
    -ctk f16 -ctv q8_0
    -sm layer -ub 384 -cram 28000
)

echo "== A: control ($BIN_A)"
BIN=$BIN_A MODEL=$MODEL PORT=$PORT ./ab-bench.sh q8ldr-A "${EXTRAS[@]}"

echo
echo "== B: dual accumulator chains ($BIN_B)"
BIN=$BIN_B MODEL=$MODEL PORT=$PORT ./ab-bench.sh q8ldr-B "${EXTRAS[@]}"

echo
echo "== trial rows:"
grep "q8ldr-" trials.md | tail -2
