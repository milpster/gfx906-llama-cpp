#!/usr/bin/env bash
# Tuning trial: q8 target KV fixed; draft KV format, n-max, ub are env-selectable.
# Usage: KV_DRAFT=f16|q8 (default f16) NMAX=3 (default) UB=384 (default) run_tune.sh <name> [-c N]
# Everything else identical to run_q8.sh (mmproj, ts 42,19,39, cost, no -ot).
set -eu
NAME="${1:?usage: run_tune.sh <name> [-c N]}"
shift || true

KV_DRAFT="${KV_DRAFT:-f16}"
NMAX="${NMAX:-2}"
UB="${UB:-384}"
NGRAM="${NGRAM:-0}"
VKF16="${VKF16:-1}"
MMQ="${MMQ:-0}"
SM="${SM:-cost}"
PP="${PP:-on}"
MMPROJ="${MMPROJ:-1}"
DEVS="${DEVS:-rocm0,vulkan1,rocm1}"
CTK="${CTK:-q8_0}"
CTV="${CTV:-q8_0}"

ROOT=/home/srcds/dev/uf2_rocm6.1_llama.cpp
LOG="$ROOT/.opencode/skills/dual-gpu-context-balancing/scripts/logs/$NAME.log"

DRAFT_ARGS=()
[ "$KV_DRAFT" = "q8" ] && DRAFT_ARGS+=(-ctkd q8_0 -ctvd q8_0)
[ "$NGRAM" = "1" ] && DRAFT_ARGS+=(--spec-type ngram-mod --spec-ngram-mod-n-match 24 --spec-ngram-mod-n-min 28 --spec-ngram-mod-n-max 64)

ARGS=("$@")
have_c=0
for a in "${ARGS[@]}"; do case "$a" in -c) have_c=1;; esac; done
[ $have_c -eq 0 ] && ARGS+=(-c 197000)

pkill -9 -f llama-server 2>/dev/null || true
sleep 1
mkdir -p "$(dirname "$LOG")"; rm -f "$LOG"

echo "trial=$NAME kv_draft=$KV_DRAFT nmax=$NMAX ub=$UB c=${ARGS[-1]} vkf16=$VKF16"

VKENV=(GGML_VK_DISABLE_F16=1)
[ "$VKF16" = "1" ] && VKENV=()

MENV=()
[ "$MMQ" = "1" ] && MENV=(GGML_CUDA_FORCE_MMQ=1)

MMARGS=()
[ "$MMPROJ" = "1" ] && MMARGS=(--mmproj /home/srcds/ai/ai/mmproj-F16.gguf)

env "${VKENV[@]}" "${MENV[@]}" HIP_GRAPH=1 AMD_LOG_LEVEL=0 \
  GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
  HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 HIP_FORCE_P2P=1 \
  GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
  HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \
  LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$ROOT/build-vega20/bin:/opt/rocm-6.1.0/lib \
  setsid "$ROOT/build-vega20/bin/llama-server" \
    -m /home/srcds/ai/ai/Qwen3.6-27B-Fable-Fus-711-UnHeretic-NM-DAU-NEO-MAX-NEO-MTP-Q8_0.gguf \
    "${MMARGS[@]}" \
    --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
    -b 16384 -ub "$UB" --ctx-checkpoints 30 \
    --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0.0 \
    --presence_penalty 0.0 --repeat-penalty 1.0 \
    --device "$DEVS" --port 8009 -np 1 -mg 0 \
    --reasoning-preserve --reasoning on \
    --spec-type draft-mtp --spec-draft-n-max "$NMAX" \
    -ctk "$CTK" -ctv "$CTV" "${DRAFT_ARGS[@]}" \
    -cram 20000 --reasoning-format deepseek \
    --chat-template-file /home/srcds/dev/llama.cpp/q36chat_template.jinja \
    --pipeline-parallel "$PP" -lv 4 \
    -ts 42,19,39 -sm "$SM" "${ARGS[@]}" >"$LOG" 2>&1 < /dev/null &
disown
echo "pid=$! log=$LOG"
