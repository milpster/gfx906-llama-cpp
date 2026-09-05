#!/usr/bin/env bash
# TG round-trace lane: bench/lane-dflash.sh wrapped with the rd-trace
# LD_PRELOAD shim. Graphs off so individual hipLaunchKernel calls are
# visible (graphs are TG-neutral, E119.1.1); the shim's amdgpu busy
# sampler rides along (both VIIs, sysfs gpu_busy_percent).
# Usage:
#   LANE=e120t0 [BIN_DIR=.. FILL1=16000|120000 SPEC_N_MAX=4|5 TG_N=..
#                EXTRA=..] ./rd-trace-lane.sh
# Analyze:
#   python3 bench/rd-trace-analyze.py /tmp/opencode/rd-trace-$LANE.bin --last 120
# Defaults = E119 prod shape (35,20,45 @250k, q8_0 V, dflash n4, PP on,
# mirror on). n4-vs-n5 tracer diff finds the 6-row verify cliff kernel.
set -euo pipefail
cd "$(dirname "$0")/.."
LANE=${LANE:?set LANE}

export RD_TRACE_FILE=${RD_TRACE_FILE:-/tmp/opencode/rd-trace-$LANE.bin}
export RD_TRACE_MB=${RD_TRACE_MB:-768}
export LD_PRELOAD=$PWD/bench/rd-trace.so
export GGML_CUDA_DISABLE_GRAPHS=1
export GGML_CUDA_FATTN_PATH=force_convert
export LLAMA_DFLASH_MIRROR_OUTPUT=1

export BIN_DIR=${BIN_DIR:-$PWD/build-dflash-novega}
export TS=${TS:-35,20,45} C=${C:-250000} CTV=${CTV:-q8_0}
export SPEC_TYPE=${SPEC_TYPE:-draft-dflash} SPEC_N_MAX=${SPEC_N_MAX:-4} NGRAM=${NGRAM:-0}
export FILL1=${FILL1:-16000} TG_N=${TG_N:-512}
export PP=${PP:-on}
export EXTRA="--no-mmproj-offload --spec-draft-device ROCm0${EXTRA:+ $EXTRA}"

./bench/lane-dflash.sh

echo "trace: $RD_TRACE_FILE ($(du -h "$RD_TRACE_FILE" | cut -f1))"
