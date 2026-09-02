#!/usr/bin/env bash
# Profiling twin of 2UDllama-start-iq6v-dflash2.sh (UD-Q6_K_L @ 256k, dflash
# drafter, ts 40,20,40, pipeline off). Identical server args, but:
# - prepends to LD_LIBRARY_PATH (the production launcher resets it, which
#   unloads the rocprof interposer libs)
# - HSA_ENABLE_SDMA=0: rocprof's PMU interposer faults on SDMA copies during
#   load - MMIO path instead (launcher uses =1)
# - GGML_CUDA_DISABLE_GRAPHS=1: graph-replayed dispatches fault the interposer
#   (CPF page fault); disabling capture does not change kernel shapes, only
#   the launch path (launcher uses HIP_GRAPH=1)
# Started under bench/rocprof.sh. 2026-09-02: rewritten from the 155k-era
# twin (old repo path/build were stale).
set -eu

export AMD_LOG_LEVEL=0
export GGML_CUDA_FATTN_PATH=force_convert
export GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16
export HSA_OVERRIDE_GFX_VERSION=9.0.6
export HIP_VISIBLE_DEVICES=0,1
export HSA_XNACK=0
export HIP_FORCE_P2P=1
export GPU_SINGLE_ALLOC_PERCENT=100
# rocprof's PMU interposer faults on SDMA copies during load - use MMIO path
export HSA_ENABLE_SDMA=0
# graph-replayed dispatches fault the rocprof interposer (CPF page fault)
export GGML_CUDA_DISABLE_GRAPHS=1
export HSA_DISABLE_FRAGMENT_ALLOCATOR=0
export GPU_MAX_ALLOC_PERCENT=100
export USE_MLOCK=true

ROOT=$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH:-}:/home/srcds/rocm-gfx906-xnack/lib:$ROOT/build-dflash-novega/bin:/opt/rocm-6.1.0/lib"

exec "$ROOT/build-dflash-novega/bin/llama-server" \
  -m /home/srcds/ai/ai/Qwen3.8-27B-UD-Q6_K_L.gguf \
  --mmproj /home/srcds/ai/ai/mmproj-F16.gguf --no-mmproj-offload \
  -md /home/srcds/ai/ai/Qwen3.8-27B-DFlash2-Q4_K_M.gguf \
  --spec-type draft-dflash --spec-draft-n-max 4 \
  --spec-draft-override-tensor '.*=ROCm0' -ngld 99 \
  --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
  -b 16384 -ub 384 --ctx-checkpoints 30 \
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  --device rocm0,vulkan1,rocm1 --port 8009 -np 1 -mg 0 \
  --reasoning-preserve --reasoning on \
  -ctk f16 -ctv q8_0 \
  -cram 28000 --reasoning-format deepseek \
  --chat-template-file "$ROOT/froggeric_chat_templ.jinja" \
  --pipeline-parallel off \
  -ts 40,20,40 -sm layer -c 256000
