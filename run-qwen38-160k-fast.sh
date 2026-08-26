#!/usr/bin/env bash
set -eu

# Qwen3.8-27B-Q8_0 - 3-GPU (2x Radeon VII ROCm + RTX 3080 Laptop Vulkan)
# 160k ctx (was 155k), F16 KV, MTP speculative SPEC=2, pipeline parallel ON.
# Calibration 2026-08-15 (604fca587 + fork patches, bench/ harness):
#   PP first-batch 328.5-329.4 tok/s, TG 20.6-20.7 @16k fill (21.3 fresh),
#   SPEC=2 acceptance 0.57. ub sweep in 64-steps: 384 > 448 (+1.6% pp) AND
#   its smaller compute buffer lifts the PP-mode ctx ceiling 155k -> 160k
#   (165k fits but pp1 collapses to 283). Full record: bench/FINDINGS.md
# Full decision record (350-pps quest, env-var audit, rejected ideas):
#   bench/FINDINGS.md - raw trials: bench/trials.md
# Dropped env vars (2026-08-14 audit): HIP_GRAPH (dead - graphs are build-time
#   GGML_HIP_GRAPHS=ON), HIP_FORCE_P2P (dead - code reads GGML_CUDA_P2P, never
#   set; PCIe gfx906 has no P2P anyway). GGML_VK_DISABLE_F16 left out: A/B
#   tested, no throughput or output difference.
# HSA_OVERRIDE_GFX_VERSION=9.0.6 is REQUIRED: without it warmup graph capture
#   dies with "ROCm error: invalid device function" in rms_norm_mul_f32_cuda
#   (empirically verified 2026-08-14) - do not remove.
# -ot no longer disables pipeline parallelism (llama-context.cpp change), but
#   at 155k the MTP -ot costs ~3% PP for no context gain - left out.
# CTX ceiling: 155k is max for pipeline mode - 165k needs ~706 MiB PP compute
#   buffers on ROCm0 (vs 248 without PP); no tested split fits both PP and KV
#   at 165k. 165k remains reachable without PP only.

AMD_LOG_LEVEL=0 \
GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 \
HSA_OVERRIDE_GFX_VERSION=9.0.6 \
HIP_VISIBLE_DEVICES=0,1 \
HSA_XNACK=0 \
GPU_SINGLE_ALLOC_PERCENT=100 \
HSA_ENABLE_SDMA=1 \
HSA_DISABLE_FRAGMENT_ALLOCATOR=0 \
GPU_MAX_ALLOC_PERCENT=100 \
USE_MLOCK=true \
LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:/home/srcds/dev/uf2_rocm6.1_llama.cpp/build-vega20/bin:/opt/rocm-6.1.0/lib \
exec /home/srcds/dev/uf2_rocm6.1_llama.cpp/build-sync25/bin/llama-server \
  -m ~/ai/ai/Qwen3.8-27B-Q8_0.gguf \
  --threads-batch 8 --threads 8 --no-mmap -fa on -ngl 333 \
  -b 16384 -ub 384 --poll 100 --ctx-checkpoints 30 \
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  --device rocm0,vulkan1,rocm1 --port 8009 -np 1 -mg 0 \
  --reasoning-preserve --reasoning on --reasoning-budget -1 \
  --spec-type draft-mtp --spec-draft-n-max "${SPEC:-2}" \
  -cram 20000 \
  --chat-template-file /home/srcds/dev/uf2_rocm6.1_llama.cpp/froggeric_chat_templ.jinja \
  --pipeline-parallel on \
  -sm cost -ts 41,20,39 \
  -c 160000 \
  --reasoning-format deepseek
