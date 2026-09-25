#!/usr/bin/env bash
set -eu

# Qwen3.8-Flash-Next-AD-4.27bpw-Q4_K_M-M64.gguf - 3-GPU (2x Radeon VII ROCm + RTX 3080 Laptop Vulkan)
# 200k ctx, F16/F16 KV (mandatory), adaptive MTP (Unsloth shared-Q8_0 sidecar),
# mmproj vision (Unsloth F16, CPU - GPU placement breaks determinism).
# Decision record: journal/JOURNAL-2026-09-11.md E142. Validated: 3/3 deterministic,
# bit-exact vs no-spec clean reference 9d4badea; vision smoke OK; PP16384 lane
# 24.99 t/s @ c20480 (bench/qwen38-pp16384.sh).
#
# DO NOT CHANGE without re-running the determinism gate (bench/qwen38-nondet-arm.sh x3):
#   - ncmoe 29 reintroduces the E141 cross-backend race (B29: 3/3 unique hashes).
#   - mmproj on vulkan1/any GPU breaks determinism (B31M/E200KV); CPU placement
#     verified clean (BM31C). T4 class (DFlash + CPU mmproj) confirmed production-safe.
#   - threads MUST stay <= 8 (8C/16T SMT boundary, E141 root cause).
#   - -otd '.*=ROCm0' is load-bearing: draft bundle (2647 MiB) must land on ROCm0;
#     draft KV then borrows the ROCm1 tail-layer device (freed via ts 66,10,24).
#   - pipeline-parallel at 200k impossible (needs ~8 GiB free on rocm0); PP perf lane
#     is a separate small-ctx config.
# HSA_OVERRIDE_GFX_VERSION=9.0.6 REQUIRED (rms_norm_mul_f32_cuda invalid function
# without it, verified 2026-08-14).

AMD_LOG_LEVEL=0 \
GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 \
HSA_OVERRIDE_GFX_VERSION=9.0.6 \
HIP_VISIBLE_DEVICES=0,1 \
HSA_XNACK=0 \
GPU_SINGLE_ALLOC_PERCENT=100 \
HSA_ENABLE_SDMA=1 \
HSA_DISABLE_FRAGMENT_ALLOCATOR=0 \
GPU_MAX_ALLOC_PERCENT=100 \
LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:/home/srcds/dev/uf3_rocm6.1_llama.cpp/build-qwen38-mtp/bin:/opt/rocm-6.1.0/lib \
exec /home/srcds/dev/uf3_rocm6.1_llama.cpp/build-qwen38-mtp/bin/llama-server \
  -m /home/srcds/ai/ai/Swift-1.5-Qwen3.8-Flash-Next-IQ4_XS.gguf \
  --threads 8 --threads-batch 8 --poll 0 --poll-batch 0 \
  -lm mmap -lzm on -fit off -fa on -ngl all -ncmoe 31 \
  -b 512 -ub 128 -cram 0 --ctx-checkpoints 0 \
  --device rocm0,vulkan1,rocm1 --port 8009 -np 1 -mg 0 \
  --pipeline-parallel off -sm layer -ts 66,10,24 \
  -c 204800 -ctk f16 -ctv f16 \
  -md /home/srcds/ai/ai/MTP/mtp-Qwen3.8-Flash-Next-shared-Q8_0.gguf \
  --spec-type draft-mtp-adaptive --spec-draft-n-max 10 --spec-draft-n-min-adaptive 3 \
  -ngld all -ctkd f16 -ctvd f16 -otd '.*=ROCm0' \
  -mm /home/srcds/ai/ai/mmproj-Qwen3.8-Flash-Next-F16.gguf -mmdev none \
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  --chat-template-file "./sharp_chat_template.jinja" \
  --reasoning on --reasoning-budget -1
