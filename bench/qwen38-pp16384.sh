#!/usr/bin/env bash
# qwen4exp PP16384 benchmark runner.
# Runs one llama-cli pass over a >=16384-token prompt with -n 0 and prints
# the prompt-eval line. Same placement/env as qwen38-nondet-arm.sh baseline.
#
# usage: bench/qwen38-pp16384.sh <run-name> [extra llama-cli args...]
# env overrides: HIP_GRAPH(1), POLL_ARGS (default: --poll 0 --poll-batch 0)
# results: /tmp/opencode/pp16384/<run>/{run.log,out.txt} + parsed summary line

set -u
set -o pipefail

RUN=${1:?run name required}
shift

REPO=$(cd "$(dirname "$0")/.." && pwd)
BIN=$REPO/build-qwen38-mtp/bin/llama-cli
MODEL=/home/srcds/ai/ai/Qwen3.8-Flash-Next-AD-4.27bpw-Q4_K_M-M64.gguf
PROMPT=/tmp/opencode/pp16384-prompt.txt
OUTDIR=/tmp/opencode/pp16384/$RUN
mkdir -p "$OUTDIR"

HIP_GRAPH=${HIP_GRAPH:-1}

BASE_ARGS=(
  -m "$MODEL"
  --threads-batch 8 --threads 8 --poll 0 --poll-batch 0
  -lm mmap -lzm on -fit off -fa on -ngl all -ncmoe 24
  -b 512 -ub 128 -cram 0 --ctx-checkpoints 0
  --device rocm0,vulkan1,rocm1 -np 1 -mg 0
  --pipeline-parallel off -ts 70,13,17 -sm layer
  -c 20480 -ctk f16 -ctv f16
  --temp 0 --seed 42 -n 0 --no-warmup
  --single-turn --simple-io --no-display-prompt --log-verbosity 3
  -f "$PROMPT"
)

echo "== pp16384 run $RUN extra: $* =="
env -u USE_MLOCK \
  HIP_GRAPH=$HIP_GRAPH \
  AMD_LOG_LEVEL=0 \
  GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 \
  HSA_OVERRIDE_GFX_VERSION=9.0.6 \
  HIP_VISIBLE_DEVICES=0,1 \
  HSA_XNACK=0 \
  GPU_SINGLE_ALLOC_PERCENT=100 \
  HSA_ENABLE_SDMA=1 \
  HSA_DISABLE_FRAGMENT_ALLOCATOR=0 \
  GPU_MAX_ALLOC_PERCENT=100 \
  LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$REPO/build-qwen38-mtp/bin:/opt/rocm-6.1.0/lib \
  timeout 40m "$BIN" "${BASE_ARGS[@]}" "$@" -o "$OUTDIR/out.txt" \
  < /dev/null 2>&1 | tee "$OUTDIR/run.log"
EXIT=${PIPESTATUS[0]}

PE=$(grep -m1 "prompt eval time" "$OUTDIR/run.log" || true)
echo "RUN=$RUN exit=$EXIT | $PE" | tee -a /tmp/opencode/pp16384/summary.txt
