#!/usr/bin/env bash
# KLD probe series over archived builds (no rebuilds).
# For each probe: run llama-perplexity --kl-divergence against ONE fixed
# mainline dump (fork-flags-agnostic reference) and record mean KLD +
# same-top. Probes with no archived ppl binary run the current
# build-dflash-novega ppl binary against the archive's libs (numerics
# live in libggml-hip.so; frontend version does not affect kernels).
# Usage: bash bench/kld-probe-archive.sh [label ...]   (default: all)
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$(pwd)

REF_BIN=${REF_BIN:-/home/srcds/dev/llama.cpp/build-stock}
DUMP=bench/logs/kld-logits-A-mainline.bin
PPL=$ROOT/build-dflash-novega/bin/llama-perplexity
# frontend for lib-swap probes; pre-sync archive builds need a pre-sync
# frontend (sonames are identical across the sync, ABI is not)
RELAY_FRONTEND=${RELAY_FRONTEND:-$PPL}
MODEL=${MODEL:-/home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf}
TEXT=${TEXT:-/home/srcds/ai/ai/log.txt}
COMMON=(-m "$MODEL" -f "$TEXT" --device rocm0,vulkan1,rocm1 -ngl 99
    -sm layer -ts 35,20,45 -c 4096 -b 1024 -ub 384
    --threads 9 --threads-batch 10 --no-mmap -fa on --chunks "${CHUNKS:-6}")

export HSA_OVERRIDE_GFX_VERSION=9.0.6 HSA_XNACK=0 HIP_VISIBLE_DEVICES=0,1
export HIP_FORCE_P2P=1 GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1
export HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100
export AMD_LOG_LEVEL=0
ROCM=/home/srcds/rocm-gfx906-xnack/lib:/opt/rocm-6.1.0/lib

# label|bin|libdir  (bin=RELAY means lib-swap via current ppl binary)
PROBES=(
  "B-forkflags|/home/srcds/dev/llama.cpp/build-forkflags/bin/llama-perplexity|/home/srcds/dev/llama.cpp/build-forkflags/bin"
  "old-jul13|$ROOT/build-old-1784294746/bin/llama-perplexity|$ROOT/build-old-1784294746/bin"
  "dflash-aug28|$ROOT/build-dflash/bin/llama-perplexity|$ROOT/build-dflash/bin"
  "ab2-sep1|$ROOT/build-ab2/bin/llama-perplexity|$ROOT/build-ab2/bin"
  "dualacc-sep2|$ROOT/build-dualacc/bin/llama-perplexity|$ROOT/build-dualacc/bin"
  "q8ldr-sep2-lib|RELAY|$ROOT/build-q8ldr/bin"
  "mmvq23685-sep2-lib|RELAY|$ROOT/build-mmvq23685/bin"
  "qpipe-sep2-lib|RELAY|$ROOT/build-qpipe/bin"
  "cols16-sep2-lib|RELAY|$ROOT/build-cols16/bin"
  "occ3-sep2-lib|RELAY|$ROOT/build-occ3/bin"
  "e106a-gdn-lib|RELAY|$ROOT/build-e106a-gdn/bin"
  "e106b-q81-lib|RELAY|$ROOT/build-e106b-q81/bin"
  "e106e-screen-lib|RELAY|$ROOT/build-e106e-screen/bin"
  "e113-sync-lib|RELAY|$ROOT/build-e113-sync/bin"
  "e114-q6k64-lib|RELAY|$ROOT/build-e114-q6k64/bin"
  "mirror-sep4-lib|RELAY|$ROOT/build-mirror/bin"
  "fastmath-sep5-lib|RELAY|$ROOT/build-fastmath/bin"
)

if [ ! -f "$DUMP" ]; then
    echo "== dumping reference A (mainline stock)"
    LD_LIBRARY_PATH=$ROCM:$REF_BIN/bin "$REF_BIN/bin/llama-perplexity" \
        "${COMMON[@]}" --save-all-logits "$DUMP" > bench/logs/kld-A-dump.log 2>&1
fi

want="${*:-}"
for p in "${PROBES[@]}"; do
    IFS='|' read -r label bin lib <<<"$p"
    [ -n "$want" ] && [[ " $want " != *" $label "* ]] && continue
    [ -d "$lib" ] || { echo "== $label: SKIP (no $lib)"; continue; }
    [ "$bin" = RELAY ] && bin=$RELAY_FRONTEND
    [ -x "$bin" ] || { echo "== $label: SKIP (no binary)"; continue; }
    echo "== $label (libs: $lib)"
    loaded=$(LD_LIBRARY_PATH=$lib:$ROCM ldd "$bin" 2>/dev/null | awk '/libggml-hip/{print $3; exit}')
    echo "   ggml-hip -> ${loaded:-UNKNOWN}"
    log=bench/logs/kld-probe-$label.log
    LD_LIBRARY_PATH=$lib:$ROCM "$bin" "${COMMON[@]}" \
        --kl-divergence --kl-divergence-base "$DUMP" > "$log" 2>&1 \
        || { echo "   FAILED (see $log)"; tail -3 "$log"; continue; }
    awk '/Mean    KLD/{k=$3" "$4}/Same top p/{t=$3" "$4}END{printf "   meanKLD=%s same_top=%s\n", k, t}' "$log"
done
