#!/usr/bin/env bash
# Logit-level A/B: fork vs upstream (~/dev/llama.cpp/build-stock).
# Two-phase KLD protocol (perplexity tool semantics):
#   dump:   --save-all-logits FILE       writes per-token uint16 log-probs
#   kld:    --kl-divergence --kl-divergence-base FILE
# Cross direction: mainline dumps -> fork computes KLD(fork||mainline),
# then fork dumps -> mainline computes KLD(mainline||fork).
# Same COMMON args as perplexity-upstream-fork.sh so chunking/token
# alignment matches the PPL lane. Logits files ~1.24 GB/chunk on disk
# (NOT tmpfs). --chunks 6 -> ~7.5 GB per dump, ~1.5 min GPU per phase.
set -euo pipefail

cd "$(dirname "$0")"
ROOT=$(cd .. && pwd)

UP_ROOT=${UP_ROOT:-/home/srcds/dev/llama.cpp}
BIN_A=${BIN_A:-$ROOT/build-dflash-novega/bin/llama-perplexity}
BIN_B=${BIN_B:-$UP_ROOT/build-stock/bin/llama-perplexity}
MODEL=${MODEL:-/home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf}
TEXT=${TEXT:-/home/srcds/ai/ai/log.txt}
CHUNKS=${CHUNKS:-6}
OUTDIR=${OUTDIR:-$ROOT/bench/logs}

for b in "$BIN_A" "$BIN_B"; do
    [ -x "$b" ] || { echo "error: not found: $b" >&2; exit 1; }
done

COMMON=(
    -m "$MODEL" -f "$TEXT"
    --device rocm0,vulkan1,rocm1 -ngl 99
    -sm layer -ts 35,20,45
    -c 4096 -b 1024 -ub 384
    --threads 9 --threads-batch 10 --no-mmap -fa on
    --chunks "$CHUNKS"
)

export HSA_OVERRIDE_GFX_VERSION=9.0.6 HSA_XNACK=0 HIP_VISIBLE_DEVICES=0,1
export HIP_FORCE_P2P=1 GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1
export HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100
export AMD_LOG_LEVEL=0

run() { # $1 label, $2 bin, $3 libdir, extra args...
    local label=$1 bin=$2 lib=$3; shift 3
    echo "== $label"
    LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$lib:/opt/rocm-6.1.0/lib \
        "$bin" "${COMMON[@]}" "$@" 2>&1 \
        | tee "$OUTDIR/kld-$label.log" \
        | grep -E "perplexity:|Final estimate|Perplexity statistics" | tail -6
}

mkdir -p "$OUTDIR"
run mainline-dump "$BIN_B" "$UP_ROOT/build-stock/bin" \
    --save-all-logits "$OUTDIR/kld-logits-mainline.bin"
run fork-kld "$BIN_A" "$ROOT/build-dflash-novega/bin" \
    --kl-divergence --kl-divergence-base "$OUTDIR/kld-logits-mainline.bin"
run fork-dump "$BIN_A" "$ROOT/build-dflash-novega/bin" \
    --save-all-logits "$OUTDIR/kld-logits-fork.bin"
run mainline-kld "$BIN_B" "$UP_ROOT/build-stock/bin" \
    --kl-divergence --kl-divergence-base "$OUTDIR/kld-logits-fork.bin"

echo "== KLD tables"
grep -h -E "^chunk|same top|Perplexity statistics" -A10 "$OUTDIR/kld-fork-kld.log" | tail -12
grep -h -E "^chunk|same top|Perplexity statistics" -A10 "$OUTDIR/kld-mainline-kld.log" | tail -12
