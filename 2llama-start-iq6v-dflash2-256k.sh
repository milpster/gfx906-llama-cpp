#!/usr/bin/env bash
# VARIANT of 2llama-start-iq6v-dflash2.sh: same shape (35,20,45, sm layer,
# mmproj on CPU), only -c raised 250000 -> 256000. Fits only because
# --no-mmproj-offload freed ~1.2 GiB on ROCm0; pre-E89 the 250k shape was
# already ROCm1-limited (fit-free -25, real ~840 MiB) so +6k ctx lands at
# fit-free -177, real ~690 MiB, VK1 386 (far from the E89 +3 cliff).
# Trial lane 2026-09-02 (E105, lane-dflash.sh, build-dflash-novega):
#   pp16384 346.2 / fill120k 237.7 / TG1024@120k 12.2 / acc .658
#   sha e54019ff6b42 (identical greedy stream to the 250k lane)
# vs same-day 250k lane: pp 322.5 / fill 229.9 / tg 11.6 - the +7% pp
# looked run-order-suspicious, L1 control between them did not trend, so
# user validation pending before this replaces production.
# Everything else copied verbatim from 2llama-start-iq6v-dflash2.sh.
set -eu

SCRIPT_DIR=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
BIN=${BIN:-$SCRIPT_DIR/build-dflash-novega/bin/llama-server}
LD_LIB=${LD_LIB:-$SCRIPT_DIR/build-dflash-novega/bin}

HIP_GRAPH=1 AMD_LOG_LEVEL=0 \
GGML_CUDA_FATTN_PATH=force_convert \
GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 HIP_FORCE_P2P=1 \
GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true \
LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$LD_LIB:/opt/rocm-6.1.0/lib \
exec "$BIN" \
  -m /home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf \
  --mmproj /home/srcds/ai/ai/mmproj-F16.gguf \
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
  --chat-template-file "$SCRIPT_DIR/froggeric_chat_templ.jinja" \
  --pipeline-parallel on \
  -ts 35,20,45 -sm layer -c 256000 \
  --no-mmproj-offload
