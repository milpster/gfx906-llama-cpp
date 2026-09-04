#!/usr/bin/env bash
# TG/verify-regime profiling twin of 2llama-start-iq6v-dflash2.sh.
# Same shape as rocprof-server-i1.sh (250k, ts 35,20,45, f16K/q8_0V, dflash n4)
# but: prod parity extras (ngram-mod chain, --pipeline-parallel on,
# --no-mmproj-offload), port 8017. The two rocprof deviations stay
# (HSA_ENABLE_SDMA=0, GGML_CUDA_DISABLE_GRAPHS=1 - see bench/rocprof-server.sh).
# E119 use: profile the TG round structure (draft split, verify, copies, gaps).
set -eu

export AMD_LOG_LEVEL=0
export GGML_CUDA_FATTN_PATH=force_convert
export GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16
export HSA_OVERRIDE_GFX_VERSION=9.0.6
export HIP_VISIBLE_DEVICES=0,1
export HSA_XNACK=0
export HIP_FORCE_P2P=1
export GPU_SINGLE_ALLOC_PERCENT=100
export HSA_ENABLE_SDMA=0
export GGML_CUDA_DISABLE_GRAPHS=1
export HSA_DISABLE_FRAGMENT_ALLOCATOR=0
export GPU_MAX_ALLOC_PERCENT=100
export USE_MLOCK=true

ROOT=$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH:-}:/home/srcds/rocm-gfx906-xnack/lib:$ROOT/build-dflash-novega/bin:/opt/rocm-6.1.0/lib"

exec "$ROOT/build-dflash-novega/bin/llama-server" \
  -m /home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf \
  --mmproj /home/srcds/ai/ai/mmproj-F16.gguf \
  -md /home/srcds/ai/ai/Qwen3.8-27B-DFlash2-Q4_K_M.gguf \
  --spec-type ngram-mod,draft-dflash --spec-draft-n-max 4 \
  --spec-ngram-mod-n-match 24 --spec-ngram-mod-n-min 28 --spec-ngram-mod-n-max 64 \
  --spec-draft-override-tensor '.*=ROCm0' -ngld 99 \
  --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
  -b 16384 -ub 384 --ctx-checkpoints 30 \
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  --device rocm0,vulkan1,rocm1 --port 8017 -np 1 -mg 0 \
  --reasoning-preserve --reasoning on \
  -ctk f16 -ctv q8_0 \
  -cram 28000 --reasoning-format deepseek \
  --chat-template-file "$ROOT/froggeric_chat_templ.jinja" \
  --no-mmproj-offload \
  --pipeline-parallel on \
  -ts 35,20,45 -sm layer -c 250000
