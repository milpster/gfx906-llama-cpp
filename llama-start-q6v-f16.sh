#!/usr/bin/env bash
# Production launcher: Qwen3.8-27B-UD-Q6_K_XL + mmproj-F16 vision, FULL F16 KV.
# No KV quantization: target AND draft/MTP KV stay at default F16
# (no -ctk/-ctv flags). pp-max config: 165k @ first-batch pp 311.9,
# tg 18.8. Deep-validated: 110k fill 215.6 avg, tg 18.35 @depth, vision OK.
# Alternatives measured 2026-08-20 (trials.md "Q6_K_XL full-F16-KV ladder"):
#   max-ctx-safe: -ts 42,21,37 -c 190000 (28/13/25) = pp 301.5, tg 19.1
#     @depth, margins 285/913/531 MiB, DEEP-VALIDATED (160k fill 169.8 avg,
#     vision @depth OK);
#   200k = startup-only (R0 28 MiB at 42,21,37; -ot VK1 fixes kill pp).
# Split/placement: -sm layer -ts 39,21,40 (26/14/26; Q6 per-layer is fastest
# on the 3080 - each layer moved VK1->Vega costs ~4.5 tok/s pp), nextn -ot,
# pipeline off (3rd confirmation: no single-request pp gain), ub 384 optimal,
# n-max 2. Rejected: token_embd->ROCm0 offload (pp 203.6!), ub 352 (294),
# cost mode (= layer at same placement), 26/14/26 @170k+.
# Alternatives measured: mixed K=f16 V=q8_0 = 210k, full q8_0 = 295k
# (both quantized - excluded here by requirement).
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
  --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
  -b 16384 -ub 384 --ctx-checkpoints 30 \
  --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  --device rocm0,vulkan1,rocm1 --port 8009 -np 1 -mg 0 \
  --reasoning-preserve --reasoning on \
  --spec-type draft-mtp,ngram-mod --spec-draft-n-max 2 \
  --spec-ngram-mod-n-match 24 --spec-ngram-mod-n-min 28 --spec-ngram-mod-n-max 64 \
  --cache-reuse 256 \
  -cram 24000 --reasoning-format deepseek \
  --chat-template-file /home/srcds/dev/uf2_rocm6.1_llama.cpp/froggeric_chat_templ.jinja \
  --pipeline-parallel off \
  -ts 39,21,40 -sm layer -c 165000 \
  --override-tensor '^blk\.64\.nextn\..*=ROCm0'
