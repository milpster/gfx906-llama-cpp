#!/usr/bin/env bash
# Profiling twin of run-qwen38-155k-fast.sh: identical server args, but
# prepends to LD_LIBRARY_PATH (the production launcher resets it, which
# unloads the rocprof interposer libs). Started under bench/rocprof.sh.
set -eu

export AMD_LOG_LEVEL=0
export GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16
export HSA_OVERRIDE_GFX_VERSION=9.0.6
export HIP_VISIBLE_DEVICES=0,1
export HSA_XNACK=0
export GPU_SINGLE_ALLOC_PERCENT=100
# rocprof's PMU interposer faults on SDMA copies during load - use MMIO path
export HSA_ENABLE_SDMA=0
# graph-replayed dispatches fault the rocprof interposer (CPF page fault);
# disabling graph capture does not change kernel shapes, only the launch path
export GGML_CUDA_DISABLE_GRAPHS=1
export HSA_DISABLE_FRAGMENT_ALLOCATOR=0
export GPU_MAX_ALLOC_PERCENT=100
export USE_MLOCK=true
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH:-}:/home/srcds/rocm-gfx906-xnack/lib:/home/srcds/dev/rocm6.1_llama.cpp/build-vega20/bin:/opt/rocm-6.1.0/lib"

exec /home/srcds/dev/rocm6.1_llama.cpp/build-vega20/bin/llama-server \
  -m ~/ai/ai/Qwen3.8-27B-Q8_0.gguf \
  --threads-batch 8 --threads 8 --no-mmap -fa on -ngl 333 \
  -b 16384 -ub 448 --poll 100 --ctx-checkpoints 30 \
  --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  --device rocm0,vulkan1,rocm1 --port 8009 -np 1 -mg 0 \
  --reasoning-preserve --reasoning on --reasoning-budget -1 \
  --spec-type draft-mtp --spec-draft-n-max 2 \
  -cram 20000 --reasoning-format deepseek \
  --chat-template-file /home/srcds/dev/rocm6.1_llama.cpp/qwen38chat_template.jinja \
  --pipeline-parallel on \
  -sm cost -ts 41,20,39 \
  -c 155000
