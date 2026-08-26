#!/usr/bin/env bash
# Launch one q8-KV balancing trial. Backgrounds, returns immediately.
# Variant of run.sh: target KV AND MTP draft KV quantized to q8_0.
# Usage: run_q8.sh <trial_name> [-ts <split>] [-ot '<regex>=<DEV>'] [-sm <mode>] [-c <ctx>]
# Defaults: -ts 42,19,39 -sm cost -c 144000 -ot nextn->ROCm0 -ot blk.63->ROCm0
# Logs to logs/<trial_name>.log. Use capture.sh to wait + extract.
set -eu
NAME="${1:?usage: $0 <trial_name> [-ts ..] [-ot ..] [-sm ..] [-c ..]}"
shift || true

ROOT=/home/srcds/dev/uf2_rocm6.1_llama.cpp
LOG="$ROOT/.opencode/skills/dual-gpu-context-balancing/scripts/logs/$NAME.log"

ARGS=("$@")
[ ${#ARGS[@]} -eq 0 ] && ARGS=(-ts 42,19,39 -ot '^blk\.64\.nextn\..*=ROCm0' -ot '^blk\.63\..*=ROCm0')
have_ts=0; have_sm=0; have_c=0
for a in "${ARGS[@]}"; do
  case "$a" in -ts) have_ts=1;; -sm) have_sm=1;; -c) have_c=1;; esac
done
[ $have_ts -eq 0 ] && ARGS+=(-ts 42,19,39)
[ $have_sm -eq 0 ] && ARGS+=(-sm cost)
[ $have_c -eq 0 ] && ARGS+=(-c 144000)

pkill -9 -f llama-server 2>/dev/null || true
sleep 1
mkdir -p "$(dirname "$LOG")"; rm -f "$LOG"

env GGML_VK_DISABLE_F16=1 HIP_GRAPH=1 AMD_LOG_LEVEL=0 \
  GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
  HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 HIP_FORCE_P2P=1 \
  GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
  HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \
  LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$ROOT/build-vega20/bin:/opt/rocm-6.1.0/lib \
  setsid "$ROOT/build-vega20/bin/llama-server" \
    -m /home/srcds/ai/ai/Qwen3.6-27B-Fable-Fus-711-UnHeretic-NM-DAU-NEO-MAX-NEO-MTP-Q8_0.gguf \
    --mmproj /home/srcds/ai/ai/mmproj-F16.gguf \
    --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
    -b 16384 -ub 384 --ctx-checkpoints 30 \
    --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0.0 \
    --presence_penalty 0.0 --repeat-penalty 1.0 \
    --device rocm0,vulkan1,rocm1 --port 8009 -np 1 -mg 0 \
    --reasoning-preserve --reasoning on \
    --spec-type draft-mtp --spec-draft-n-max 3 \
    -ctk q8_0 -ctv q8_0 -ctkd q8_0 -ctvd q8_0 \
    -cram 20000 --reasoning-format deepseek \
    --chat-template-file /home/srcds/dev/llama.cpp/q36chat_template.jinja \
    --pipeline-parallel on -lv 4 \
    "${ARGS[@]}" >"$LOG" 2>&1 < /dev/null &
disown
echo "trial=$NAME pid=$! log=$LOG"
echo "placement: ${ARGS[*]}"
