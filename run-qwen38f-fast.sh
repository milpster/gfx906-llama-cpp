#!/usr/bin/env bash
set -eu

# Qwen3.8-Flash-Next speed lane: 20k ctx, PP + MTP draft in one server.
# 2026-09-26: CPU-computed MoE experts at prefill (GGML_MOE_CPU_COMPUTE_MIN_BATCH)
# + capped/chunked draft catch-up -> PP5132 130 t/s warm, TG 8.95 t/s @5k-deep,
# draft live (bench/logs/q38speed/draft-cap). Staged baseline: 17-21 PP.
# PP-off variant: 141 PP / 6.28 TG (pipeline overlaps draft round-trips at
# decode: -7% PP buys +42% TG). No-draft: 148.5 / 4.31.
#
# Load-bearing:
#   - GGML_MOE_CPU_COMPUTE_MIN_BATCH=128 REQUIRED for the PP win; 0 = old staged
#     behavior.
#   - Draft batch is capped to n_max+1 in-code (upstream #27569 adapted): its
#     fattn pool never sizes for the 5712 prefill width. -otd '.*=ROCm0' keeps
#     the draft bundle on ROCm0.
#   - GGML_RANGE_SPLIT_MB=2048 REQUIRED with -lzm on-direct (contiguous ROCm1
#     range regression on the 0920 sync); harmless without it.
#   - Projection-level CPU hosting keeps 602/361/476 MiB free on
#     ROCm0/Vulkan1/ROCm1 (bench/logs/q38speed/tenancy-recovery-n27-vk2p2-r1p2).
#   - threads MUST stay <= 8 (E141); ncmoe 27; mmproj CPU.

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
GGML_MOE_CPU_COMPUTE_MIN_BATCH=128 \
LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:/home/srcds/dev/uf3_rocm6.1_llama.cpp/build-rcfix/bin:/opt/rocm-6.1.0/lib \
exec /home/srcds/dev/uf3_rocm6.1_llama.cpp/build-rcfix/bin/llama-server \
  -m /home/srcds/ai/ai/Swift-1.5-Qwen3.8-Flash-Next-IQ4_XS.gguf \
  --threads 8 --threads-batch 8 --poll 0 --poll-batch 0 \
  -lm mmap -lzm on -fit off -fa on -ngl all -ncmoe 27 \
  -b 5712 -ub 5712 -cram 0 --ctx-checkpoints 0 \
  --device rocm0,vulkan1,rocm1 --port 8009 -np 1 -mg 0 \
  --pipeline-parallel on -sm layer -ts 70,10,20 \
  -c 20480 -ctk f16 -ctv f16 \
  -ot '(blk\.(3[1-4]|3[89])\.ffn_(up|gate|down)_exps\.|blk\.37\.ffn_down_exps\.|blk\.41\.ffn_down_exps\.)=CPU' \
  -md /home/srcds/ai/ai/MTP/mtp-Qwen3.8-Flash-Next-shared-Q8_0.gguf \
  --spec-type draft-mtp-adaptive --spec-draft-n-max 10 --spec-draft-n-min-adaptive 3 \
  -ngld all -ctkd f16 -ctvd f16 -otd '.*=ROCm0' \
  -mm /home/srcds/ai/ai/mmproj-Qwen3.8-Flash-Next-F16.gguf -mmdev none \
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  --chat-template-file "./sharp_chat_template.jinja" \
  --reasoning on --reasoning-budget -1
