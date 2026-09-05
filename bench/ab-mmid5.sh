#!/usr/bin/env bash
# A/B for exp/mmid-q6k5: GCN MMVQ-for-MUL_MAT_ID batch table Q6_K 4 -> 5
# (mmvq.cu get_mmvq_mmid_max_batch_gcn). At --spec-draft-n-max 4 the
# verify batch is 5 rows: every MoE verify pass crosses into the heavier
# MMQ-for-ids path today. RDNA2/RDNA4 tables allow 5 for Q6_K.
# Verify-pass-only lever: PP (batch 384 >> 8) and single-token decode
# (batch 1 <= 4, already MMVQ) are unaffected - tg is the metric, pp
# expected flat. Gates: tg/acc; sha may stay (E93 dualacc reassociation
# precedent) or move (kernel-family swap) - record either way.
# Two trials, only BIN differs:
#   A = build-dflash-novega              (table 4, production)
#   B = ../uf3-wt-mmid5/build-mmid5      (table 5, worktree exp/mmid-q6k5)
# Mirror parity with prod (E119.6). Stop the production server first.
# ~30-40 min per trial. Results -> journal E120 (JOURNAL-2026-09-05.md).
set -euo pipefail

cd "$(dirname "$0")"
ROOT=$(cd .. && pwd)

BIN_A=${BIN_A:-$ROOT/build-dflash-novega/bin/llama-server}
BIN_B=${BIN_B:-$ROOT/../uf3-wt-mmid5/build-mmid5/bin/llama-server}
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

echo "== A: control, table 4 ($BIN_A)"
BIN=$BIN_A MODEL=$MODEL PORT=$PORT ./ab-bench.sh mmid5-A "${EXTRAS[@]}"

echo
echo "== B: table 5 ($BIN_B)"
BIN=$BIN_B MODEL=$MODEL PORT=$PORT ./ab-bench.sh mmid5-B "${EXTRAS[@]}"

echo
echo "== trial rows:"
grep "mmid5-" trials.md | tail -2
