#!/usr/bin/env bash
# qwen4exp no-spec determinism arm runner.
# Runs the fixed Qwen3.8-Flash-Next no-spec lane N times, hashes outputs,
# prints a determinism verdict. One arm = one variable toggle.
#
# usage: bench/qwen38-nondet-arm.sh <arm-name> <reps> [extra llama-cli args...]
#   extra args are appended last so they override base args (llama.cpp last-wins).
# env overrides: HIP_GRAPH (default 1), SRC (source tree with the build, default this repo),
#   BUILD_DIR (default build-qwen38-mtp)
# results: /tmp/opencode/nondet/<arm>/{rN.out,rN.log,hashes.txt,verdict.txt}

set -u
set -o pipefail

ARM=${1:?arm name required}
REPS=${2:?reps required}
shift 2

REPO=$(cd "$(dirname "$0")/.." && pwd)
SRC=${SRC:-$REPO}
BUILD_DIR=${BUILD_DIR:-build-sync0909}
BIN=$SRC/$BUILD_DIR/bin/llama-cli
MODEL=/home/srcds/ai/ai/Qwen3.8-Flash-Next-AD-4.27bpw-Q4_K_M-M64.gguf
OUTDIR=$REPO/bench/logs/q38nondet/$ARM
mkdir -p "$OUTDIR"

HIP_GRAPH=${HIP_GRAPH:-1}

BASE_ARGS=(
  -m "$MODEL"
  --threads-batch 10 --threads 9
  -lm mmap -lzm on -fit off -fa on -ngl all -ncmoe 24
  -b 512 -ub 128 -cram 0 --ctx-checkpoints 0
  --device rocm0,vulkan1,rocm1 -np 1 -mg 0
  -ts 70,13,17 -sm layer
  -c 4096 -ctk f16 -ctv f16
  --temp 0 --seed 42 -n 32 --no-warmup
  --single-turn --simple-io --no-display-prompt --log-verbosity 3
  -p 'The capital of France is'
)
if [ -z "${DROP_PIPELINE_PARALLEL:-}" ]; then
  BASE_ARGS+=(--pipeline-parallel off)
fi

echo "== arm $ARM reps=$REPS HIP_GRAPH=$HIP_GRAPH extra: $* =="
for i in $(seq 1 "$REPS"); do
  echo "== run $i start $(date +%H:%M:%S) =="
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
    LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$SRC/$BUILD_DIR/bin:/opt/rocm-6.1.0/lib \
    timeout 20m "$BIN" "${BASE_ARGS[@]}" "$@" -o "$OUTDIR/r$i.out" \
    < /dev/null 2>&1 | tee "$OUTDIR/r$i.log"
  echo "== run $i exit=${PIPESTATUS[0]} end $(date +%H:%M:%S) =="
  sleep 2
done

sha256sum "$OUTDIR"/r*.out | tee "$OUTDIR/hashes.txt"
NUNIQ=$(sha256sum "$OUTDIR"/r*.out | awk '{print $1}' | sort -u | wc -l)
if [ "$NUNIQ" -eq 1 ]; then V=DETERMINISTIC; else V=NONDETERMINISTIC; fi
echo "ARM=$ARM reps=$REPS unique_outputs=$NUNIQ verdict=$V" | tee "$OUTDIR/verdict.txt"
