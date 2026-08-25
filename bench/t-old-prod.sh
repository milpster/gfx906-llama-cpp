#!/usr/bin/env bash
# Triage launcher for eaman-rs binary: same as llama-start-q6v.sh but takes
# extra ARGS (spec overrides etc) and PORT/LOG from env. Usage:
#   PORT=8013 TRIAL=n3 ./triage-start.sh --spec-draft-n-max 3
set -eu
cd "$(dirname "$(readlink -f "$0")")/.."
PORT=${PORT:-8013}
TRIAL=${TRIAL:-triage}
: ${SPEC_ARGS:?set SPEC_ARGS (e.g. "--spec-type none" or "--spec-type draft-mtp,ngram-mod --spec-draft-n-max 3")}

HIP_GRAPH=1 AMD_LOG_LEVEL=0 \
GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 HIP_FORCE_P2P=1 \
GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \
LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:/home/srcds/dev/uf2_rocm6.1_llama.cpp/build-vega20/bin:/opt/rocm-6.1.0/lib \
exec /home/srcds/dev/uf2_rocm6.1_llama.cpp/build-vega20/bin/llama-server \
  -m /home/srcds/ai/ai/Qwen3.8-27B-UD-Q6_K_XL.gguf \
  --mmproj /home/srcds/ai/ai/mmproj-F16.gguf \
  --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
  -b 16384 -ub 384 --ctx-checkpoints 30 \
  --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  --device rocm0,vulkan1,rocm1 --port "$PORT" -np 1 -mg 0 \
  --reasoning-preserve --reasoning on \
  --cache-reuse 256 \
  -ctk f16 -ctv q8_0 \
  -cram 28000 --reasoning-format deepseek \
  --chat-template-file froggeric_chat_templ.jinja \
  --pipeline-parallel off \
  -ts 40,20,40 -sm layer -c 210000 \
  --override-tensor '^blk\.64\.nextn\..*=ROCm0' \
  $SPEC_ARGS
