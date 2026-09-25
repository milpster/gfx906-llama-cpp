#!/usr/bin/env bash
# rocprof twin of the Swift IQ4_XS 20k PP lane (tenancy-recovery geometry).
# Same interposer constraints as rocprof-server.sh: SDMA off, no HIP graphs.
# Started under bench/rocprof.sh. -lm mmap: kernel shapes are what matters.
set -eu

export AMD_LOG_LEVEL=0
export GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16
export HSA_OVERRIDE_GFX_VERSION=9.0.6
export HIP_VISIBLE_DEVICES=0,1
export HSA_XNACK=0
export GPU_SINGLE_ALLOC_PERCENT=100
export HSA_ENABLE_SDMA=0
export HSA_DISABLE_FRAGMENT_ALLOCATOR=0
export GPU_MAX_ALLOC_PERCENT=100
export GGML_CUDA_DISABLE_GRAPHS=1
export GGML_RANGE_SPLIT_MB=2048
export GGML_EXPS_RING=1

ROOT=$(cd "$(dirname "$0")/.." && pwd)
export LD_LIBRARY_PATH="/home/srcds/rocm-gfx906-xnack/lib:$ROOT/build-rcfix/bin:/opt/rocm-6.1.0/lib"

exec "$ROOT/build-rcfix/bin/llama-server" \
  -m /home/srcds/ai/ai/Swift-1.5-Qwen3.8-Flash-Next-IQ4_XS.gguf \
  --threads 8 --threads-batch 8 --poll 0 --poll-batch 0 \
  -lm mmap -lzm on -fit off -fa on -ngl all -ncmoe 27 \
  -b 5712 -ub 5712 -cram 0 --ctx-checkpoints 0 \
  --device rocm0,vulkan1,rocm1 --port 8124 -np 1 -mg 0 \
  --pipeline-parallel off -sm layer -ts 70,10,20 \
  -c 20480 -ctk f16 -ctv f16 --temp 0 --seed 42 \
  -ot '(blk\.(3[1-4]|3[89])\.ffn_(up|gate|down)_exps\.|blk\.37\.ffn_down_exps\.|blk\.41\.ffn_down_exps\.)=CPU' \
  -md /home/srcds/ai/ai/MTP/mtp-Qwen3.8-Flash-Next-shared-Q8_0.gguf \
  --spec-type draft-mtp-adaptive --spec-draft-n-max 10 --spec-draft-n-min-adaptive 3 \
  -ngld all -ctkd f16 -ctvd f16 -otd '.*=ROCm0' \
  -mm /home/srcds/ai/ai/mmproj-Qwen3.8-Flash-Next-F16.gguf -mmdev none \
  --no-warmup -lv 3
