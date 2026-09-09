#!/usr/bin/env bash
# PPL A/B @ deep ctx (E132): fork stock vs GDN-norm port (exp/gdn-norm).
# Protocol = perplexity-upstream-fork.sh, but both sides are fork builds so
# ONLY the build_gdn_l2_norm port differs. CTX env (default 120000, user
# regime). f16 KV (no -ctk/-ctv) isolates weight-matmul numerics (E92/E122).
# Full corpus both sides; CHUNKS=16 narrows if runtime matters (sigma rises).
# Logs -> bench/logs/ppl-gdn-{stock,gdn-norm}.log
set -euo pipefail
cd "$(dirname "$0")"
ROOT=$(cd .. && pwd)
WT=${WT:-/home/srcds/dev/uf3-wt-gdn}
BIN_A=${BIN_A:-$ROOT/build-dflash-novega/bin/llama-perplexity}
BIN_B=${BIN_B:-$WT/build-gdnnorm/bin/llama-perplexity}
MODEL=${MODEL:-/home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf}
TEXT=${TEXT:-/home/srcds/ai/ai/log.txt}
CTX=${CTX:-120000}

for b in "$BIN_A" "$BIN_B"; do
    [ -x "$b" ] || { echo "error: not found: $b" >&2; exit 1; }
done

CHUNKARGS=()
[ -n "${CHUNKS:-}" ] && CHUNKARGS=(--chunks "$CHUNKS")

COMMON=(
    -m "$MODEL" -f "$TEXT"
    --device rocm0,vulkan1,rocm1 -ngl 99
    -sm layer -ts 35,20,45
    -c "$CTX" -b 1024 -ub 384
    --threads 9 --threads-batch 10 --no-mmap -fa on
    "${CHUNKARGS[@]}"
)

export HSA_OVERRIDE_GFX_VERSION=9.0.6 HSA_XNACK=0 HIP_VISIBLE_DEVICES=0,1
export HIP_FORCE_P2P=1 GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1
export HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100
export AMD_LOG_LEVEL=0

run() { # $1 label, $2 bin, $3 bindir
    echo "== $1 ($2)"
    LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$3:/opt/rocm-6.1.0/lib \
        "$2" "${COMMON[@]}" 2>&1 | tee "logs/ppl-gdn-$1.log" \
        | grep -E "perplexity:|llama_perf|Final estimate" | tail -6
}

run stock    "$BIN_A" "$ROOT/build-dflash-novega/bin"
echo
run gdn-norm "$BIN_B" "$WT/build-gdnnorm/bin"
