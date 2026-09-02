#!/usr/bin/env bash
# A/B for the UD-Q6_K_L v2 model (journal E96): same binary, only the
# MODEL differs:
#   A = Qwen3.8-27B-UD-Q6_K_L.gguf     (production, known 350.7 class)
#   B = Qwen3.8-27B-UD-Q6_K_L-v2.gguf  (38x Q5_K -> Q6_K imatrix splice)
# Expected: B ~+3.8% pp (client ~364); sha WILL move (weights changed -
# that is the point); tg/acc within noise; B ppl <= A ppl.
#
# Fit warning (E96): B is +300 MiB; VK1 margin at 256k is +74 MiB and
# absorbs ~+60 -> razor. If B OOMs on VK1, retry with CTX=250112.
# Stop the production server first. ~30-40 min per trial.
set -euo pipefail

cd "$(dirname "$0")"
ROOT=$(cd .. && pwd)

BIN=${BIN:-$ROOT/build-dflash-novega/bin/llama-server}
MODEL_A=${MODEL_A:-/home/srcds/ai/ai/Qwen3.8-27B-UD-Q6_K_L.gguf}
MODEL_B=${MODEL_B:-/home/srcds/ai/ai/Qwen3.8-27B-UD-Q6_K_L-v2.gguf}
DRAFT=${DRAFT:-/home/srcds/ai/ai/Qwen3.8-27B-DFlash2-Q4_K_M.gguf}
PORT=${PORT:-8013}

for f in "$BIN" "$MODEL_A" "$MODEL_B"; do
    [ -e "$f" ] || { echo "error: not found: $f" >&2; exit 1; }
done

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

echo "== A: L baseline ($MODEL_A)"
BIN=$BIN MODEL=$MODEL_A PORT=$PORT ./ab-bench.sh udv2-A "${EXTRAS[@]}"

echo
echo "== B: v2 splice ($MODEL_B)"
BIN=$BIN MODEL=$MODEL_B PORT=$PORT ./ab-bench.sh udv2-B "${EXTRAS[@]}"

echo
echo "== trial rows:"
grep "udv2-" trials.md | tail -2
