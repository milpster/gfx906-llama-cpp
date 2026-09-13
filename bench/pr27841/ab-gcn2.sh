#!/usr/bin/env bash
# A/B upstream #27841 (GCN MMQ table) vs our prod build, using the EXISTING
# server-level harness (../ab-bench.sh) - real prod config, pp1 / deep-fill /
# tg / acceptance / output sha. NOT llama-bench (can't run the draft or pp1).
#
# A = build-sync0909 (prod, our vega table)
# B = build-pr27841-gcn (B arm, PR #27841 gcn table)   [build first: ../pr27841/ab-gcn.sh build]
#
# Expect: Q6_K main-model lanes ~parity (our Q6_K rows == PR's). The dflash draft
# lane (Q4_K_M) is the only place a #27841 delta can show.
#
# Requires the prod server STOPPED (ab-bench.sh checks port 8013 and owns the GPUs).
# Run: ./ab-gcn2.sh            (both models, interleaved)
#       ./ab-gcn2.sh main       (main Q6_K model only, faster)
#       ./ab-gcn2.sh draft      (dflash draft lane only)

set -euo pipefail
HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
BENCH="$HERE/.."
cd "$BENCH"

A_BIN="$HERE/../../build-sync0909/bin/llama-server"
B_BIN="$HERE/../../build-pr27841-gcn/bin/llama-server"
MODEL=${MODEL:-/home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf}
export MODEL
DRAFT=/home/srcds/ai/ai/Qwen3.8-27B-DFlash2-Q4_K_M.gguf

# prod config (live server): -sm layer -ts 35,20,45 -ub 384 -c 235000 f16 kv.
# Draft lanes default to CTX=130000: the 235k fit is knife-edge under the bench
# env (PP reserve fails) - see journal E167 run log.
export CTX=${CTX:-235000} TS=${TS:-35,20,45} UB=${UB:-384} SM=layer
export TG_FILL=${TG_FILL:-120000}   # deep-fill tg lane (regime: tg@120k)
export PP=on
# required for the dflash draft (prod launcher env): without MIRROR_OUTPUT the
# draft graph references main output.weight on ROCm1 and aborts at sched_reserve
export LLAMA_DFLASH_MIRROR_OUTPUT=1 HIP_GRAPH=1 GGML_CUDA_FATTN_PATH=force_convert VK_F16=1
SPEC_DEFAULT=ngram-mod,draft-dflash
DRAFT_ARGS=( -md "$DRAFT" --spec-draft-n-max 4 --spec-ngram-mod-n-match 24
             --spec-ngram-mod-n-min 28 --spec-ngram-mod-n-max 64
             --spec-draft-override-tensor '.*=ROCm0' --spec-draft-device ROCm0 -ngld 99 )

run() {  # $1=label  $2=bin  rest = extra server args
  local label=$1 bin=$2; shift 2
  echo "=== trial $label (BIN=$bin)"; echo
  BIN=$bin ./ab-bench.sh "$label" "$@"
}

which_mode=${1:-all}

main_lanes() {
  export SPEC_TYPE=none
  run A-main-1 "$A_BIN"; run B-main-1 "$B_BIN"
  run A-main-2 "$A_BIN"; run B-main-2 "$B_BIN"
}

draft_lanes() {
  export SPEC_TYPE=draft-dflash
  run A-draft-1 "$A_BIN" "${DRAFT_ARGS[@]}"
  run B-draft-1 "$B_BIN" "${DRAFT_ARGS[@]}"
  run A-draft-2 "$A_BIN" "${DRAFT_ARGS[@]}"
  run B-draft-2 "$B_BIN" "${DRAFT_ARGS[@]}"
}

echo "A=$A_BIN"; echo "B=$B_BIN"; echo "ctx=$CTX ts=$TS ub=$UB sm=$SM tg_fill=$TG_FILL"; echo
case "$which_mode" in
  main)  main_lanes ;;
  draft) draft_lanes ;;
  all)   main_lanes; echo; draft_lanes ;;
  *) echo "usage: $0 [all|main|draft]"; exit 1 ;;
esac

echo
echo "== compare rows (pp1_tps, tg_tps, acc, sha) in $BENCH/trials.md =="
echo "Parity expected on Q6_K main lanes; dflash (Q4_K_M) is the delta candidate."
echo "Any sha mismatch A vs B = correctness issue, not a perf win (abort the claim)."
