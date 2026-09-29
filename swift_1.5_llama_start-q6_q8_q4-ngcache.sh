#!/usr/bin/env bash
# Duplicate of swift_1.5_llama_start-q6_q8_q4.sh with the ngram-cache
# drafter + file-backed dynamic cache integrated (2026-09-28).
# Differences from the 1.5 launcher:
# - --spec-type chain adds ngram-cache behind ngram-mod (SPEC_TYPE env
#   overrides the chain, e.g. SPEC_TYPE=ngram-cache,draft-dflash).
# - --spec-ngram-cache-strict: request-local confidence gate (validated
#   2026-09-28, bench/logs/promptlookup-dynamic-benefit-20260928-summary.md).
# - -lcd $NGRAM_CACHE_FILE: loads the dynamic cache at startup when
#   present, creates it when missing, saves it on clean shutdown.
# - --spec-ngram-cache-p-min $NGRAM_CACHE_P_MIN (default 0.75, 0 = old
#   behavior): dynamic-cache drafts only when the top continuation holds
#   >= P share of observations; provisional until the GPU sweep lands.
# - Default port 8009 with a separate log file; LOG_DIR/BIN/LD_LIB
#   overrides work as in the original.
# - BIN/LD_LIB default to the build-pr29478 binary: the ngcache 5-PR
#   build plus upstream #29478 gfx906 packed-byte subtraction, adopted
#   2026-09-29 (TG +9-10%, temp-0 SHA identical; rollback binary:
#   build-promptlookup-baseline).
# Production (swift_1.5_llama_start-q6_q8_q4.sh) remains a separate lane.
# The original header (model, drafter, fit E172/E173, LD_LIBRARY_PATH,
# mirror-output, force_convert notes) applies to this copy verbatim.
set -eu

SCRIPT_DIR=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
BIN=${BIN:-$SCRIPT_DIR/build-pr29478/bin/llama-server}
LD_LIB=${LD_LIB:-$SCRIPT_DIR/build-pr29478/bin}
LOG_DIR=${LOG_DIR:-$SCRIPT_DIR/log}
PORT=${PORT:-8009}
NGRAM_CACHE_FILE=${NGRAM_CACHE_FILE:-$LOG_DIR/ngram-cache.bin}
NGRAM_CACHE_P_MIN=${NGRAM_CACHE_P_MIN:-0.75}
SPEC_TYPE=${SPEC_TYPE:-ngram-mod,ngram-cache,draft-dflash}
mkdir -p "$LOG_DIR/prompts"
# A/B knobs (defaults = shipped config): FATTN_PATH, SPEC_N_MAX, PIPELINE, SSM_CM, GRAPHS
[ -n "${SSM_CM:-}" ] && export LLAMA_QWEN4EXP_SSM_CONV_CM=1
[ "${GRAPHS:-1}" = "0" ] && export GGML_CUDA_DISABLE_GRAPHS=1
HIP_GRAPH=1 AMD_LOG_LEVEL=0 \
LLAMA_DFLASH_MIRROR_OUTPUT=1 \
GGML_CUDA_FATTN_PATH="${FATTN_PATH:-force_convert}" \
GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 HIP_FORCE_P2P=1 \
GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \
LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$LD_LIB:/opt/rocm-6.1.0/lib \
exec "$BIN" \
  -m /home/srcds/ai/ai/Swift-Qwen3.8-27B-Q6_K.gguf \
  --mmproj /home/srcds/ai/ai/mmproj-F16.gguf \
  -md /home/srcds/ai/ai/Qwen3.8-27B-DFlash2-Q4_K_M.gguf \
  --spec-type "$SPEC_TYPE" --spec-ngram-cache-strict --spec-ngram-cache-p-min "$NGRAM_CACHE_P_MIN" -lcd "$NGRAM_CACHE_FILE" \
  --spec-draft-n-max "${SPEC_N_MAX:-3}" \
  --spec-ngram-mod-n-match 24 --spec-ngram-mod-n-min 28 --spec-ngram-mod-n-max 64 \
  --spec-draft-override-tensor '.*=ROCm0' --spec-draft-device ROCm0 -ngld 99 \
  --threads-batch 10 --threads 9 --load-mode none -fa on -ngl 333 \
  -b 16384 -ub 384 --ctx-checkpoints 30 \
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  --device rocm0,vulkan1,rocm1 --port "$PORT" -np 2 -mg 0 \
  --reasoning-preserve --reasoning on \
  -ctk q8_0 -ctv q4_0 \
  -cram 28000 --reasoning-format deepseek \
  --chat-template-file "$SCRIPT_DIR/sharp_chat_template.jinja" \
  --pipeline-parallel "${PIPELINE:-off}" \
  -ts 35,23,43 -sm layer -c 398000 \
  --no-mmproj-offload \
  --log-file "$LOG_DIR/llama-server-ngcache-iq6v-f16-f16.log" \
  --log-prompts-dir "$LOG_DIR/prompts"
