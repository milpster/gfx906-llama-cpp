#!/usr/bin/env bash
set -eu

# Qwen3.8-Flash-Next speed lane (E175): 20k ctx PP-optimized serve config.
# 2.0-2.9x the 200k launcher's PP (75.1 t/s vs 20.8-25, bench/logs/q38speed/
# sp-e165-0920build) at the cost of 180k context. Context dropped per user.
#
# GATE PENDING (do NOT treat as production until passed):
#   bench/qwen38-nondet-arm.sh x3 + TG/acceptance lane at THIS geometry.
#   New geometry vs E142 (ts 70,10,20 + L42 -ot + ub5712): determinism NOT
#   yet proven; E158's sibling geometry was 3/3 unique on the pre-sync build.
#
# Load-bearing (see journal/JOURNAL-2026-09-21.md E175):
#   - GGML_RANGE_SPLIT_MB=2048 REQUIRED with -lzm on-direct on the 0920 sync
#     (contiguous ROCm1 range regression); harmless without it.
#   - -ot 'blk\.(3[1-9]|4[01])=CPU' hosts expert layers 31-41: required for
#     the ub5712 fit; deeper hosting (L43+) hits the E166b RAM wall.
#   - threads MUST stay <= 8 (E141); ncmoe 31; mmproj CPU; -otd '.*=ROCm0'.

AMD_LOG_LEVEL=0 \
GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 \
HSA_OVERRIDE_GFX_VERSION=9.0.6 \
HIP_VISIBLE_DEVICES=0,1 \
HSA_XNACK=0 \
GPU_SINGLE_ALLOC_PERCENT=100 \
HSA_ENABLE_SDMA=1 \
HSA_DISABLE_FRAGMENT_ALLOCATOR=0 \
GPU_MAX_ALLOC_PERCENT=100 \
GGML_RANGE_SPLIT_MB=2048 \
GGML_EXPS_RING=1 \
LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:/home/srcds/dev/uf3_rocm6.1_llama.cpp/build-sync0920/bin:/opt/rocm-6.1.0/lib \
exec /home/srcds/dev/uf3_rocm6.1_llama.cpp/build-rcfix/bin/llama-server \
  -m /home/srcds/ai/ai/Swift-1.5-Qwen3.8-Flash-Next-IQ4_XS.gguf \
  --threads 8 --threads-batch 8 --poll 0 --poll-batch 0 \
  -lm mmap -lzm on -fit off -fa on -ngl all -ncmoe 31 \
  -b 5712 -ub 5712 -cram 0 --ctx-checkpoints 0 \
  --device rocm0,vulkan1,rocm1 --port 8009 -np 1 -mg 0 \
  --pipeline-parallel off -sm layer -ts 70,10,20 \
  -c 20480 -ctk f16 -ctv f16 \
  -ot 'blk\.(3[1-9]|4[01])=CPU' \
  -md /home/srcds/ai/ai/MTP/mtp-Qwen3.8-Flash-Next-shared-Q8_0.gguf \
  --spec-type draft-mtp-adaptive --spec-draft-n-max 10 --spec-draft-n-min-adaptive 3 \
  -ngld all -ctkd f16 -ctvd f16 -otd '.*=ROCm0' \
  -mm /home/srcds/ai/ai/mmproj-Qwen3.8-Flash-Next-F16.gguf -mmdev none \
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  --chat-template-file "./sharp_chat_template.jinja" \
  --reasoning on --reasoning-budget -1
