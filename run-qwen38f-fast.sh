#!/usr/bin/env bash
set -eu

ROOT=$(cd "$(dirname "$0")" && pwd)
DRAFT_N_MAX=${DRAFT_N_MAX:-10}
DRAFT_N_MIN_ADAPTIVE=${DRAFT_N_MIN_ADAPTIVE:-3}
SPEC=${SPEC:-none}
SPEC_ARGS=()
if [ "$SPEC" != "none" ]; then
    SPEC_ARGS=(-md /home/srcds/ai/ai/MTP/mtp-Qwen3.8-Flash-Next-shared-Q8_0.gguf
        --spec-type draft-mtp-adaptive --spec-draft-n-max "$DRAFT_N_MAX" --spec-draft-n-min-adaptive "$DRAFT_N_MIN_ADAPTIVE"
        -devd rocm1 -ngld all -ctkd f16 -ctvd f16 -otd '.*=ROCm1')
fi

# Qwen3.8-Flash-Next speed lane: 20k ctx, PP + MTP draft in one server.
# 2026-09-26 (E164-E166): fenced vk staging ring + chunked full-tensor expert
# staging (no ids round-trip) on top of -lzm on-direct. -> PP5132 248.4 t/s,
# PP16384 204.7/201.3, TG 9.5 @5k / 11.07 @16k (bench/logs/q38speed/
# draft-r1-complete/server-ringlane+chunk, pp16384/results-ringchunk).
# 2026-09-26 (evict fix): GGML_SPEC_CKPT_ON_DEVICE=1 - spec recurrent ckpts
# stay on-device (steady TG 10.2 -> ~12); llama_state_seq_evict at big-prompt
# start frees them so PP-after-TG stays clean (237/257/250 vs 199-217 before).
# Staged baseline: 17-21 PP. Arc today: 137 -> 185.5 (PLE on-direct) ->
# 212.5 (ring) -> 248.4 (chunked staging).
# 2026-09-27 (2): residency frontier mapped. KEPT the 242 PP point as
# default (TG 10.89). Fast-TG escape hatch: NCMOE=21 TS=56,6,38
# RANGESPLIT=1024 -> TG 11.88 / PP 201 (sha-gated 3cc4e0d1d0dc).
# 2026-09-27: spec decode net-negative here (CPU-expert cost scales with
# distinct experts touched per step; acceptance ~0.5) and drove the TG
# wobble. Defaults now SPEC=none PPFLAG=off: PP 233.2 agg, TG 9.8-10.3
# stable, sha identical to the spec lane. SPEC=on restores the draft.
#
# Load-bearing:
#   - GGML_MOE_CPU_COMPUTE_MIN_BATCH=128 REQUIRED for the PP win; 0 = old staged
#     behavior.
#   - -lzm on-direct REQUIRED: the 27.46 GiB per-layer embedding table cannot
#     stay resident (43 GiB locked + 27.5 lazy > 62 GB RAM); anything else
#     re-faults it every pass.
#   - Draft batch is capped to n_max+1 in-code (upstream #27569 adapted);
#     GGML_SPEC_DRAFT_UBATCH=128 widens it for the catch-up. Draft bundle on
#     ROCm1 single-device (needs output.weight=ROCm1 + blk.40/42 CPU groups
#     for the fit; keeps the catch-up unfragmented).
#   - GGML_RANGE_SPLIT_MB=2048 REQUIRED (contiguous ROCm1 range regression on
#     the 0920 sync); harmless without it.
#   - threads default 8 (E141 determinism); THREADS=env trial override, 11
#     is the historical sweet spot per user; ncmoe 27; mmproj CPU.
#   - Post-reboot GPU state can wedge the first task (dma fence hang / GPU
#     page fault, cleared by relaunch or reboot).

# OT=none: GPU-resident experts (drops -ncmoe and the -ot expert-CPU clauses,
# keeps output.weight=ROCm1). Default keeps the staged CPU-expert lane.
# NCMOE overrides the -ncmoe count (empty with OT=none); TS overrides -ts
# (empty = drop -ts, let the loader balance by free device memory).
OT=${OT:-on}
NCMOE=${NCMOE:-27}
OTARGS=()
NCMOE_ARGS=()
if [ "$OT" = "none" ]; then
  OTARGS+=(-ot 'output\.weight=ROCm1')
  [ -n "$NCMOE" ] && NCMOE_ARGS+=(-ncmoe "$NCMOE")
elif [ "$OT" = "raw" ]; then
  [ -n "$NCMOE" ] && NCMOE_ARGS+=(-ncmoe "$NCMOE")
else
  OTARGS+=(-ot '(blk\.(3[1-4]|3[89]|4[02])\.ffn_(up|gate|down)_exps\.|blk\.37\.ffn_down_exps\.|blk\.41\.ffn_down_exps\.)=CPU,output\.weight=ROCm1')
  NCMOE_ARGS+=(-ncmoe "$NCMOE")
fi
TSARGS=()
[ -n "${TS:-70,10,20}" ] && TSARGS+=(-ts "${TS:-70,10,20}")
# KVO=off adds -nkvo (force KV on GPU); default leaves kv-offload enabled
KVOARGS=()
[ "${KVO:-on}" = "off" ] && KVOARGS+=(-nkvo)
AMD_LOG_LEVEL=0 \
GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 \
HSA_OVERRIDE_GFX_VERSION=9.0.6 \
HIP_VISIBLE_DEVICES=0,1 \
HSA_XNACK=0 \
GPU_SINGLE_ALLOC_PERCENT=100 \
HSA_ENABLE_SDMA=1 \
HSA_DISABLE_FRAGMENT_ALLOCATOR=0 \
GPU_MAX_ALLOC_PERCENT=100 \
GGML_RANGE_SPLIT_MB=${RANGESPLIT:-2048} \
GGML_MOE_CPU_COMPUTE_MIN_BATCH=128 \
GGML_SPEC_DRAFT_UBATCH=128 \
GGML_MOE_FULLCOPY_CHUNK=33554432 \
GGML_SPEC_CKPT_ON_DEVICE=1 \
LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:/home/srcds/dev/uf3_rocm6.1_llama.cpp/build-dedup/bin:/opt/rocm-6.1.0/lib \
exec /home/srcds/dev/uf3_rocm6.1_llama.cpp/build-dedup/bin/llama-server \
  -m /home/srcds/ai/ai/Swift-1.5-Qwen3.8-Flash-Next-IQ4_XS.gguf \
  --threads "${THREADS:-8}" --threads-batch 8 --poll "${POLL:-0}" --poll-batch 0 \
  -lm mmap+mlock -lzm on-direct -fit off -fa on -ngl all ${NCMOE_ARGS[@]+"${NCMOE_ARGS[@]}"} \
  -b "${UB:-5696}" -ub "${UB:-5696}" -cram 0 --ctx-checkpoints 0 \
  --device rocm0,vulkan1,rocm1 --port 8009 -np 1 -mg "${MG:-0}" \
  --pipeline-parallel "${PPFLAG:-off}" -sm layer ${TSARGS[@]+"${TSARGS[@]}"} \
  -c "${CTX:-20480}" -ctk "${CTK:-f16}" -ctv "${CTV:-f16}" ${KVOARGS[@]+"${KVOARGS[@]}"} \
  "${OTARGS[@]}" \
  "${SPEC_ARGS[@]}" \
  -mm /home/srcds/ai/ai/mmproj-Qwen3.8-Flash-Next-F16.gguf -mmdev none \
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence_penalty 0.0 --repeat-penalty 1.0 \
  --chat-template-file "$ROOT/sharp_chat_template.jinja" \
  --reasoning on --reasoning-budget -1 \
  ${EXTRA_ARGS:-}
