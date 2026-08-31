#!/usr/bin/env bash
# Profiling twin of bench/lane-dflash.sh for the E50v2 FATTN fix, VERIFY
# REGIME (not 16k-PP): KV pre-filled to ~120k, then a short TG, so the
# sampled FA ops are the spec verify ops (Q=3-5 rows) at fixed KV depth.
# Runs the current dflash2 lane config (i1-Q6_K + DFlash2 draft, q8_0 V
# cache, ts 35,20,45, sm layer) on build-dflash-novega.
#
# Counter-only pass: profiling serializes kernels, so NEVER read wall
# clock or us/verify from this run (that is stage 1a, the unprofiled
# bench/fa1-lane-120k.sh).
#
# Interposer requirements (verified 2026-08-15, same as rocprof-server.sh):
#   - LD_LIBRARY_PATH is PREPENDED, not reset (else the interposer libs
#     unload)
#   - HSA_ENABLE_SDMA=0 (interposer faults on SDMA copies during load)
#   - GGML_CUDA_DISABLE_GRAPHS=1 (graph-replayed dispatches fault the
#     interposer; kernel shapes unchanged, only the launch path)
#
# Two passes, one per build of build-dflash-novega (FATTN-on b1, then the
# all-OFF variant):
#   ./bench/rocprof.sh -i bench/rocprof-pmc-a.txt --plugin file \
#       -d /tmp/opencode/fa1b-passA bash bench/rocprof-server-fa.sh
#   # second shell, once the server is up:
#   FILL1=120000 FILL2=0 TG_N=256 python3 bench/lane-client.py 8009
#
# Q-mix caveat (E58): the two passes draft different token streams, so the
# Q=3/4/5 mix can drift between them. Run stage 1a (unprofiled, -v) on
# both builds first and compare the per-round n_draft/n_accepted
# histograms before reading the PMU totals as a kernel ranking; if the
# CSV carries per-invoke grid/time columns, filter to the identical
# Q-shape invocations instead.
set -eu

export AMD_LOG_LEVEL=0
export GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16
export HSA_OVERRIDE_GFX_VERSION=9.0.6
export HIP_VISIBLE_DEVICES=0,1
export HSA_XNACK=0
export GPU_SINGLE_ALLOC_PERCENT=100
export HSA_ENABLE_SDMA=0
export GGML_CUDA_DISABLE_GRAPHS=1
export HSA_DISABLE_FRAGMENT_ALLOCATOR=0
export GPU_MAX_ALLOC_PERCENT=100
export USE_MLOCK=true
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH:-}:/home/srcds/rocm-gfx906-xnack/lib:/home/srcds/dev/uf3_rocm6.1_llama.cpp/build-dflash-novega/bin:/opt/rocm-6.1.0/lib"

cd /home/srcds/dev/uf3_rocm6.1_llama.cpp

exec build-dflash-novega/bin/llama-server \
  -m /home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf \
  --mmproj /home/srcds/ai/ai/mmproj-F16.gguf \
  -md /home/srcds/ai/ai/Qwen3.8-27B-DFlash2-Q4_K_M.gguf \
  --spec-type draft-dflash --spec-draft-n-max 4 \
  --spec-draft-override-tensor '.*=ROCm0' -ngld 99 \
  --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
  -b 16384 -ub 384 --ctx-checkpoints 30 \
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  -device rocm0,vulkan1,rocm1 --port 8009 -np 1 -mg 0 \
  --reasoning-preserve --reasoning on \
  -ctv q8_0 \
  -cram 28000 --reasoning-format deepseek \
  --chat-template-file "$PWD/froggeric_chat_templ.jinja" \
  -ts 35,20,45 -sm layer -c 155000
