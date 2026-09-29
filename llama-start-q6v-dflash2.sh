#!/usr/bin/env bash
# Production launcher: Qwen3.8-27B-UD-Q6_K_XL + mmproj-F16 vision
# + DFlash2 external drafter (z-lab Q4_K_M, 08-24 format).
# Based on llama-start-q6v.sh + validated lane L6 (2026-08-26/27):
#   PP16384 335.3 (+3.1% vs adaptive), 120k fill 193.5 (+10.4%),
#   TG@120k 8.4 (parity), acc 0.686 mean len 3.15.
# Vision + DFlash2 requires the #27408 M-RoPE port (commit db64a4f58);
# do NOT point BIN at a build without it.
# Drafter must be Q4_K_M: Q8_0/BF16 do not fit on any device at 210k
# (ROCm0 927MB / Vulkan1 1.04GB / ROCm1 2.05GB alloc failures measured).
# -c 200000: the validated fit; 210k untested with the drafter.
# Temp-0 note: DFlash2 output diverges from no-spec on near-ties
# (sampler path, single flip + cascade, coherent); fine at temp 1.0.
set -eu

SCRIPT_DIR=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
BIN=${BIN:-$SCRIPT_DIR/build-dedup/bin/llama-server}
LD_LIB=${LD_LIB:-$SCRIPT_DIR/build-dedup/bin}

HIP_GRAPH=1 AMD_LOG_LEVEL=0 \
GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 HIP_FORCE_P2P=1 \
GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \
LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$LD_LIB:/opt/rocm-6.1.0/lib \
exec "$BIN" \
  -m /home/srcds/ai/ai/Qwen3.8-27B-UD-Q6_K_XL.gguf \
  --mmproj /home/srcds/ai/ai/mmproj-F16.gguf \
  -md /home/srcds/ai/ai/Qwen3.8-27B-DFlash2-Q4_K_M.gguf \
  --spec-type draft-dflash --spec-draft-n-max 7 \
  --spec-draft-override-tensor '.*=ROCm0' -ngld 99 \
  --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
  -b 16384 -ub 384 --ctx-checkpoints 30 \
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  --device rocm0,vulkan1,rocm1 --port 8009 -np 1 -mg 0 \
  --reasoning-preserve --reasoning on \
  -ctk f16 -ctv q8_0 \
  -cram 28000 --reasoning-format deepseek \
  --chat-template-file "$SCRIPT_DIR/froggeric_chat_templ.jinja" \
  --pipeline-parallel off \
  -ts 40,20,40 -sm layer -c 200000
