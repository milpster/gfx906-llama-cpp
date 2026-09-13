#!/usr/bin/env bash
# A/B: our vega MMQ table (A, prod build-sync0909) vs upstream #27841 GCN table (B).
#
# Purpose: quantify whether PR #27841's per-quant GCN MMQ config changes anything
# for OUR production deployment. Key facts baked in (see JOURNAL-2026-09-12.md):
#   - prod main model is Q6_K; our vega.cuh ALREADY carries the #27841 Q6_K row
#     (256,2,64), byte-identical to the PR -> expect ~0 delta on the Q6_K PP lane.
#   - prod draft is Q4_K_M; our Q4_K row is the UNIFORM (256,1,128), the PR uses
#     (256,2,64/128) -> this is the only lane where a real delta is possible.
#
# This script RUNS llamas (llama-bench) and builds a B-arm worktree. It does NOT
# touch the live server and does NOT kill any process. Run it yourself:
#   ./bench/pr27841/ab-gcn.sh build     # build the B arm (worktree), ~minutes
#   ./bench/pr27841/ab-gcn.sh bench     # interleaved A/B PP benchmark
#   ./bench/pr27841/ab-gcn.sh all
#
# NOTE: the live prod server holds ~98GB across 3 GPUs. For clean numbers stop it
# first (manually, `kill <pid>`); do NOT run this benchmark while it is serving.

set -euo pipefail
ROOT=$(cd "$(dirname "$(readlink -f "$0")")/../.." && pwd)

# ---- pinned state -------------------------------------------------------------
GIT_SHA=$(git -C "$ROOT" rev-parse HEAD)
MODEL_MAIN=${MODEL_MAIN:-/home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf}
MODEL_Q4K=${MODEL_Q4K:-/home/srcds/ai/ai/Qwen3.8-27B-DFlash2-Q4_K_M.gguf}
A_BIN=${A_BIN:-$ROOT/build-sync0909/bin/llama-bench}   # A arm = prod (our vega table)
WT="$ROOT/build-pr27841-gcn"                            # B arm worktree (source)
B_BIN=${B_BIN:-$WT/bin/llama-bench}

# prod device/batch shape (matches live server; -sm layer hits the J<=64 path).
# llama-bench flag names differ from llama-server: --device (not -device), and
# there is NO -c ctx flag (prompt -p sets the KV base for the tg test).
PROD_COMMON=( -fa on -b 16384 -ub 384 -sm layer -ts 35,20,45
              --device rocm0,vulkan1,rocm1 -ctk f16 -ctv f16 -ngl 999 )
# Regime per bench/FINDINGS.md:19 + journal: pp1 = first 16384-token batch (the
# prod calibration metric); TG measured at 120k fill depth. Match those, else the
# A/B is off-regime and the Q6_K vs PR comparison can be masked.
PP_SIZES=(${PP_SIZES:-512 8192 16384})   # 16384 = the pp1 prod metric
TG_N=${TG_N:-1024}      # tg1024 (regime: tg1024@120k)
TG_KV=${TG_KV:-120000}  # fill depth for the tg lane (regime: @120k; lower to save time)
RUNS=${RUNS:-3}   # interleaved A,B,A... ; first pass of the session is warmup

build_arm() {
  [ -x "$B_BIN" ] && { echo "B arm already built: $B_BIN"; return; }
  echo "== B arm: worktree from HEAD $GIT_SHA"
  git -C "$ROOT" worktree add -f "$WT" HEAD
  local d="$WT/ggml/src/ggml-cuda"
  cp "$ROOT/bench/pr27841/mmq-config-gcn.cuh" "$d/mmq-config-gcn.cuh"
  # Route gfx906 (both host cc==VEGA20 and device __gfx906__) to the PR gcn table,
  # swapping ONLY the config selector. Everything else in mmq.cuh stays identical,
  # so A vs B differ in NOTHING except the MMQ tile table.
  sed -i 's/ggml_cuda_mmq_get_config_vega/ggml_cuda_mmq_get_config_gcn/g' "$d/mmq.cuh"
  grep -q '#include "mmq-config-gcn.cuh"' "$d/mmq.cuh" \
    || sed -i 's|#include "mmq-config-vega.cuh"|#include "mmq-config-gcn.cuh"\n#include "mmq-config-vega.cuh"|' "$d/mmq.cuh"
  echo "== B arm: build (same flags as build-dflash-novega.sh)"
  export PATH=/opt/rocm-6.1.0/bin:$PATH
  export HSA_OVERRIDE_GFX_VERSION=9.0.6
  cmake -B "$WT" -S "$ROOT" \
    -DCMAKE_HIP_COMPILER=/opt/rocm-6.1.0/lib/llvm/bin/clang \
    -Dhip_DIR=/opt/rocm-6.1.0/lib/cmake/hip \
    -Dhipblas_DIR=/opt/rocm-6.1.0/lib/cmake/hipblas \
    -Drocblas_DIR=/opt/rocm-6.1.0/lib/cmake/rocblas \
    -Dhsa-runtime64_DIR=/opt/rocm-6.1.0/lib/cmake/hsa-runtime64 \
    -Damd_comgr_DIR=/opt/rocm-6.1.0/lib/cmake/amd_comgr \
    -DAMDDeviceLibs_DIR=/opt/rocm-6.1.0/lib/cmake/AMDDeviceLibs \
    -DGGML_CUDA_FA_ALL_QUANTS=ON -DCMAKE_BUILD_TYPE=Release -DGGML_HIP=ON \
    -DAMDGPU_TARGETS=gfx906 -DGGML_VULKAN=ON \
    -DGGML_CUDA_VEGA_TUNE=ON \
    -DGGML_CUDA_VEGA_TUNE_FATTN=ON -DGGML_CUDA_VEGA_TUNE_FATTN_QPIPE=OFF \
    -DGGML_CUDA_VEGA_TUNE_FATTN_COLS16=OFF -DGGML_CUDA_VEGA_TUNE_FATTN_OCC3=OFF \
    -DGGML_CUDA_VEGA_TUNE_MMQ=ON -DGGML_CUDA_VEGA_TUNE_MMQ_DUALACC=OFF \
    -DGGML_CUDA_VEGA_TUNE_MMQ_Q8LDR=OFF -DGGML_CUDA_VEGA_TUNE_TOPK=ON \
    -DGGML_CUDA_VEGA_TUNE_GRAPHS=ON \
    -DGGML_HIP_NO_VMM=ON -DGGML_HIP_MMQ_MFMA=ON \
    -DCMAKE_HIP_FLAGS="" >/dev/null
  cmake --build "$WT" --target llama-server llama-bench -j"$(nproc)"
  echo "== B arm ready: $WT/bin/llama-server"
}

run_pp() {  # $1=label $2=bin $3=model $4=psize
  "$2" -m "$3" "${PROD_COMMON[@]}" -p "$4" -n 0 -r 1 --no-warmup \
    2>&1 | rtk grep -E "pp$4|test|t/s|error|Error|out of memory" | rtk tail -3
}

# run_metric <bin> <model> <base> <tag> <prefix> <num> <extra llama-bench args...>
# prints "<prefix><num>  t/s" or, on failure/no-match, the last real error line
# so a VRAM/device failure is visible instead of killing the run (set -e safe).
run_metric() {
  local bin="$1" model="$2" base="$3" tag="$4" pre="$5" num="$6"; shift 6
  local log="$logd/${base%.*}-${tag}.log"
  "$bin" -m "$model" "${PROD_COMMON[@]}" "$@" -r 1 --no-warmup >"$log" 2>&1
  local rc=$?
  local m
  # real output is pipe-delimited: | pp512 | 123.45 ± 0.00 | -> pull the t/s pair
  m=$(rtk grep -E "${pre}${num}[ ]*\|" "$log" \
    | rtk grep -oE "[0-9.]+ ?± ?[0-9.]+" | rtk head -1 || true)
  if [ -n "$m" ]; then
    echo "${pre}${num}  $m"
  else
    # surface the real reason: OOM / device busy / missing arg / crash
    local err; err=$(rtk grep -iE "error|fail|out of memory|cannot|abort|hip|hipError|no devices|exception" "$log" | rtk tail -1 || true)
    echo "NO_MATCH rc=$rc [${err:-see $log}]"
  fi
}

bench() {
  # Runtime env mirrors the prod launcher (2llama-start-*.sh): without the
  # rocm-gfx906-xnack LD_LIBRARY_PATH + HSA_XNACK=0, rocm0/rocm1 don't resolve
  # and ROCm init fails. FATTN/compute-type vars keep A and B on the same path.
  export HSA_OVERRIDE_GFX_VERSION=9.0.6 HSA_XNACK=0 HIP_FORCE_P2P=1
  export HIP_VISIBLE_DEVICES=0,1 AMD_LOG_LEVEL=0
  export GGML_CUDA_FATTN_PATH=force_convert GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16
  export LD_LIBRARY_PATH="/home/srcds/rocm-gfx906-xnack/lib:$(dirname "$A_BIN"):/opt/rocm-6.1.0/lib:$LD_LIBRARY_PATH"
  [ -x "$A_BIN" ] || { echo "missing A bin $A_BIN"; exit 1; }
  [ -x "$B_BIN" ] || { echo "missing B bin - run: $0 build"; exit 1; }
  echo "GIT_SHA=$GIT_SHA"; echo "A=$A_BIN"; echo "B=$B_BIN"
  rocminfo 2>/dev/null | rtk grep -i " ROCm " | rtk head -1 || true
  local out="$ROOT/bench/pr27841/results-$(date +%H%M%S).txt"; : > "$out"
  {
    echo "### pinned: git=$GIT_SHA  A=build-sync0909  B=build-pr27841-gcn"
    echo "### prod shape: -b16384 -ub384 -sm layer -ts 35,20,45 f16 kv rocm0,vulkan1,rocm1"
  } >> "$out"
  local logd="$ROOT/bench/pr27841/runs"; mkdir -p "$logd"
  for model in "$MODEL_MAIN" "$MODEL_Q4K"; do
    local base; base=$(basename "$model")
    echo; echo "########## MODEL $base ##########"; echo >> "$out"
    for r in $(seq 1 $RUNS); do
      for arm in A B; do
        local bin; [ "$arm" = A ] && bin=$A_BIN || bin=$B_BIN
        # PP lane: prompt-only, prod batch shape (MMQ prefill)
        for p in "${PP_SIZES[@]}"; do
          echo "arm=$arm p=$p  $(run_metric "$bin" "$model" "$base" "$arm$r" "pp" "$p" -p "$p" -n 0)" | tee -a "$out"
        done
        # TG lane: fixed-KV decode (Q4_K draft path lives here)
        echo "arm=$arm tg=$TG_N kv=$TG_KV  $(run_metric "$bin" "$model" "$base" "$arm${r}tg" "tg" "$TG_N" -p "$TG_KV" -n "$TG_N")" | tee -a "$out"
      done
    done
  done
  echo; echo "== results: $out"
  echo "Read pp16384 as the primary metric (prod regime). Q6_K should be ~parity (rows"
  echo "identical); the Q4_K_M lane is the only place a #27841 delta can show. Discard"
  echo "the first pass (warmup) when reading."
}

case "${1:-}" in
  build) build_arm ;;
  bench) bench ;;
  all)   build_arm; bench ;;
  *) echo "usage: $0 {build|bench|all}"; exit 1 ;;
esac
