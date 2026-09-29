#!/usr/bin/env bash
# Production launcher: Qwen3.8-27B.i1-Q6_K + mmproj-F16 vision
# + DFlash2 external drafter (z-lab Q4_K_M, 08-24 format), FULL F16 KV
# (no -ctk/-ctv -> f16/f16). Validated 2026-08-27/28 on the upstream-synced
# build (DFlash2 #27816 + Vulkan view-alias fix from PR #27812, lanes
# V2/W2 in JOURNAL-2026-08-27.md):
#   PP16384 348-349, 120k single-pass fill 238.4-238.5, TG@120k 10.5
#   (1024 tok), acc .718, temp-0 repro gate PASSES (was false on the
# pre-fix build - Vulkan graph-optimize corruption, see journal).
# -ts 40,19,41: blk.38+39 (incl attn KV) live on ROCm1 - deep KV reads run
# on a 1 TB/s VII instead of the 448 GB/s 3080. Do NOT go back to 40,20,40
# with F16 KV: VK1 oversubscribes (~1 GB) and dies mid-run.
# -c 190000: validated fit + full protocol at 190208 (W2); 195k untested.
#   34,20,46 @ 200k does NOT fit (W4 probe: VK1 -263 / ROCm1 -279 MiB
#   post-drafter, startup never listens).
# CAUTION: GPU OC experiments hung this split 5x on 2026-08-27; stock
# clocks completed 3/3. Re-validate after any clock change.
# Optional (measured free, wins on replayed content, idle on novel):
#   add to --spec-type: ngram-mod,draft-dflash plus
#   --spec-ngram-mod-n-match 24 --spec-ngram-mod-n-min 28
#   --spec-ngram-mod-n-max 64
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
  --spec-type draft-dflash --spec-draft-n-max 7 \
  --spec-draft-override-tensor '.*=ROCm0' -ngld 99 \
  --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
  -b 16384 -ub 384 --ctx-checkpoints 30 \
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  --device rocm0,vulkan1,rocm1 --port 8009 -np 1 -mg 0 \
  --reasoning-preserve --reasoning on \
  -cram 28000 --reasoning-format deepseek \
  --chat-template-file "$SCRIPT_DIR/froggeric_chat_templ.jinja" \
  --pipeline-parallel off \
  -ts 40,19,41 -sm layer -c 190000
