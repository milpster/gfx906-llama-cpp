#!/usr/bin/env bash
# Production launcher: Qwen3.8-27B.i1-Q6_K + mmproj-F16 vision
# + DFlash2 external drafter (z-lab Q8_0, 08-24 format), f16 K / q8_0 V.
# Re-validated 2026-08-28 on the upstream-synced build (DFlash2 #27816 +
# Vulkan view-alias fix from PR #27812, lanes W3/X1/X2 in
# JOURNAL-2026-08-27.md):
#   PP16384 363.0, 120k single-pass fill 218.4, TG@120k 9.0 (1024 tok),
#   temp-0 repro gate PASSES (was false on the pre-fix build).
# --spec-draft-n-max 4: beats 7 at depth (TG 9.0 vs 8.6, X2); acceptance
# rate drops .708 -> .646 but t/s is the metric (journal K3). ngram-mod
# and the Q8 drafter measured as no-ops (X1).
# Q4_K_M drafter measured equivalent (R0 vs R1: identical TG/fill/sha).
# Vision + DFlash2 requires the #27408 M-RoPE port (upstream since #27816).
# -ts 35,20,45 -c 250000: attn 6/3/7 with 4 extra GDN layers on ROCm1;
# the shape trades TG (-0.6 t/s vs 40,19,41) for the 250k fit.
# Opt-in +10k ctx (W6, costs ~10% PP / ~8% fill, TG unchanged): add
#   -ot '^blk\.(37|38)\.ffn_(gate|up|down)\.weight$=ROCm0'
#   and raise -c to 260000.
# Temp-0 note: pre-fix builds diverged from no-spec on near-ties; the
# Vulkan fix removed the known corruption source (repro gate now passes).
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
  -m /home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf \
  --mmproj /home/srcds/ai/ai/mmproj-F16.gguf \
  -md /home/srcds/ai/ai/Qwen3.8-27B-DFlash2-Q8_0.gguf \
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
  --pipeline-parallel off \
  -ts 35,20,45 -sm layer -c 250000
