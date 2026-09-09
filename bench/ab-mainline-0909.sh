#!/usr/bin/env bash
# Comprehensive fork-vs-mainline A/B (E139+): speeds (naked prod-shape lanes),
# PPL, cross-KLD. Fork = build-sync0909 (master c84835a69-class binary),
# mainline = ~/dev/llama.cpp build-0909 @ upstream 434ddbbc0.
# PPL + KLD both at -c 10000 wikitext (user directive: KLD ctx like PPL).
# KLD CHUNKS=6 (disk: ~1.24 GB/chunk logits dumps x2 sides).
# Naked lanes = identical common-subset args (no fork-only spec/reasoning/
# cram flags) so the delta is pure fork kernels/tunes.
# Usage: setsid bench/ab-mainline-0909.sh (detached); markers /tmp/opencode/ab0909-*.OK
set -uo pipefail
ROOT=/home/srcds/dev/uf3_rocm6.1_llama.cpp
UP=/home/srcds/dev/llama.cpp
FORK_BIN=$ROOT/build-sync0909/bin
MAIN_BIN=$UP/build-0909/bin
MODEL=/home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf
TEXT=/home/srcds/ai/ai/wikitext-2-raw/wiki.test.raw
MMPROJ=/home/srcds/ai/ai/mmproj-F16.gguf
OUT=$ROOT/bench/logs
CHUNKS=${CHUNKS:-6}
cd "$ROOT"
export HSA_OVERRIDE_GFX_VERSION=9.0.6 HSA_XNACK=0 HIP_VISIBLE_DEVICES=0,1
export HIP_FORCE_P2P=1 GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1
export HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 AMD_LOG_LEVEL=0

ppl() { # $1 label, $2 bin, $3 libdir
  echo "== PPL $1"
  LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$3:/opt/rocm-6.1.0/lib \
    "$2" -m "$MODEL" -f "$TEXT" --device rocm0,vulkan1,rocm1 -ngl 99 \
    -sm layer -ts 35,20,45 -c 10000 -b 1024 -ub 384 \
    --threads 9 --threads-batch 10 --load-mode none -fa on \
    > "$OUT/ppl-ab0909-$1.log" 2>&1
  grep -E 'Final estimate' "$OUT/ppl-ab0909-$1.log"
}

kld() { # $1 label, $2 bin, $3 libdir, extra args...
  local label=$1 bin=$2 lib=$3; shift 3
  LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$lib:/opt/rocm-6.1.0/lib \
    "$bin" -m "$MODEL" -f "$TEXT" --device rocm0,vulkan1,rocm1 -ngl 99 \
    -sm layer -ts 35,20,45 -c 10000 -b 1024 -ub 384 \
    --threads 9 --threads-batch 10 --load-mode none -fa on --chunks "$CHUNKS" "$@" \
    > "$OUT/kld-ab0909-$label.log" 2>&1
}

naked_lane() { # $1 side, $2 bindir, $3 port
  local side=$1 bindir=$2 port=$3
  local log=$OUT/naked-$side.log
  pkill -9 -f "llama-server.*--port $port" 2>/dev/null || true; sleep 2
  env LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:$bindir/bin:/opt/rocm-6.1.0/lib \
    setsid "$bindir/bin/llama-server" \
    -m "$MODEL" --mmproj "$MMPROJ" \
    -b 16384 -ub 384 --ctx-checkpoints 30 \
    --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
    --device rocm0,vulkan1,rocm1 --port "$port" -np 1 -mg 0 \
    -ctk f16 -ctv f16 -fa on -ngl 333 \
    -ts 35,20,45 -sm layer -c 250000 --load-mode none \
    > "$log" 2>&1 < /dev/null &
  disown
  for _ in $(seq 1 150); do
    grep -q "listening on" "$log" 2>/dev/null && break
    grep -qE "GGML_ASSERT|failed to allocate|error while loading|invalid argument" "$log" 2>/dev/null && { echo "$side FAILED"; tail -8 "$log"; return 1; }
    sleep 2
  done
  FILL1=120000 TG_N=1024 python3 bench/cmp-client.py "$port" | tee /tmp/opencode/naked-$side.json
  pkill -9 -f "llama-server.*--port $port" 2>/dev/null || true
}

# Phase 1: PPL
ppl mainline "$MAIN_BIN/llama-perplexity" "$MAIN_BIN" && touch /tmp/opencode/ab0909-ppl-mainline.OK || touch /tmp/opencode/ab0909-ppl-mainline.FAIL

# Phase 2: cross-KLD
rm -f "$OUT"/kld-ab0909-*.bin
kld mainline-dump "$MAIN_BIN/llama-perplexity" "$MAIN_BIN" --save-all-logits "$OUT/kld-ab0909-logits-mainline.bin"
kld fork-kld    "$FORK_BIN/llama-perplexity"  "$FORK_BIN"  --kl-divergence --kl-divergence-base "$OUT/kld-ab0909-logits-mainline.bin"
kld fork-dump   "$FORK_BIN/llama-perplexity"  "$FORK_BIN"  --save-all-logits "$OUT/kld-ab0909-logits-fork.bin"
kld mainline-kld "$MAIN_BIN/llama-perplexity" "$MAIN_BIN" --kl-divergence --kl-divergence-base "$OUT/kld-ab0909-logits-fork.bin"
rtk echo KLD_PHASE_DONE

# Phase 3: naked speed lanes
naked_lane mainline "$UP/build-0909" 8031 && touch /tmp/opencode/ab0909-naked-mainline.OK || touch /tmp/opencode/ab0909-naked-mainline.FAIL
naked_lane fork "$ROOT/build-sync0909" 8031 && touch /tmp/opencode/ab0909-naked-fork.OK || touch /tmp/opencode/ab0909-naked-fork.FAIL
rm -f "$OUT"/kld-ab0909-*.bin
rtk echo AB0909_ALL_DONE
