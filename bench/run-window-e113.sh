#!/usr/bin/env bash
# E113 GPU-window runner: waits for a free rig (no llama-server), then runs
# the sync-regression lanes + q6k A/B lane + rd2d shim screen sequentially.
# Never kills anything it did not start; skips remaining steps if a server
# appears between steps (user prod has priority).
# Status: /tmp/opencode/e113-window.status ; log: /tmp/opencode/e113-window.log
set -uo pipefail
cd "$(dirname "$(readlink -f "$0")")/.."
ROOT=$PWD
LOG=/tmp/opencode/e113-window.log
STATUS=/tmp/opencode/e113-window.status
MAX_WAIT_H=${MAX_WAIT_H:-8}

log() { echo "[$(date +%H:%M:%S)] $*" >> "$LOG"; }

rig_free() { ! pgrep -f "bin/llama-server" >/dev/null 2>&1; }

wait_window() {
    log "waiting for GPU window (max ${MAX_WAIT_H}h): no llama-server + q6k build present"
    local deadline=$(( $(date +%s) + MAX_WAIT_H * 3600 ))
    while [ "$(date +%s)" -lt "$deadline" ]; do
        if rig_free && [ -x build-e114-q6k64/bin/llama-server ]; then
            sleep 30  # debounce: prod may be mid-restart
            if rig_free; then log "window open"; return 0; fi
        fi
        sleep 60
    done
    log "TIMEOUT: no window within ${MAX_WAIT_H}h"
    return 1
}

lane() {  # lane <name> <bin_dir>
    local lane=$1 bin=$2
    rig_free || { log "SKIP $lane: server appeared"; return 1; }
    log "LANE $lane start (bin=$bin)"
    if LANE=$lane BIN_DIR=$ROOT/$bin TS=35,20,45 SM=layer C=250000 CTK=f16 CTV=q8_0 \
         SPEC_N_MAX=4 PP=on EXTRA="--no-mmproj-offload" \
         ./bench/lane-dflash.sh >> "$LOG" 2>&1; then
        log "LANE $lane DONE"
    else
        log "LANE $lane FAILED (status: $(cat /tmp/opencode/lane-$lane.status 2>/dev/null))"
        return 1
    fi
    sleep 10
}

rd2d_screen() {
    rig_free || { log "SKIP rd2d: server appeared"; return 1; }
    log "rd2d shim screen start (8k ctx, no drafter, TG-only probe)"
    local port=8021
    AMD_LOG_LEVEL=0 GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16 HSA_OVERRIDE_GFX_VERSION=9.0.6 \
    HIP_VISIBLE_DEVICES=0,1 HSA_XNACK=0 GPU_SINGLE_ALLOC_PERCENT=100 HSA_ENABLE_SDMA=1 \
    HSA_DISABLE_FRAGMENT_ALLOCATOR=0 GPU_MAX_ALLOC_PERCENT=100 USE_MLOCK=true HIP_GRAPH=1 \
    LD_PRELOAD=$ROOT/bench/rd2d-count.so RD2D_OUT=/tmp/opencode/rd2d-tg.txt \
    LD_LIBRARY_PATH=$ROOT/build-dflash-novega/bin:/home/srcds/rocm-gfx906-xnack/lib:/opt/rocm-6.1.0/lib \
    setsid $ROOT/build-dflash-novega/bin/llama-server \
      -m /home/srcds/ai/ai/Qwen3.8-27B.i1-Q6_K.gguf \
      --threads-batch 8 --threads 8 --no-mmap -fa on -ngl 333 \
      -b 2048 -ub 384 --temp 0 --top-p 1.0 --top-k 1 \
      --device rocm0,vulkan1,rocm1 --port $port -np 1 -mg 0 \
      -ctk f16 -ctv q8_0 -ts 35,20,45 -sm layer -c 8192 \
      > /tmp/opencode/rd2d-server.log 2>&1 < /dev/null &
    disown
    local i healthy=0
    for i in $(seq 1 90); do
        curl -sf -m 2 http://127.0.0.1:$port/health >/dev/null 2>&1 && { healthy=1; break; }
        pgrep -f "llama-server.*--port $port" >/dev/null 2>&1 || break
        sleep 5
    done
    if [ "$healthy" != 1 ]; then
        log "rd2d: server never healthy - see /tmp/opencode/rd2d-server.log"
        pkill -9 -f "llama-server.*--port $port" 2>/dev/null || true
        return 1
    fi
    log "rd2d: healthy, TG probe 256 tokens"
    curl -s http://127.0.0.1:$port/completion -H 'Content-Type: application/json' \
      -d '{"prompt":"The quick brown fox jumps over the lazy dog. Understanding recurrent state copy behavior in hybrid transformer architectures requires careful measurement of device to device memory transfers during long token generation loops with many iterations.","n_predict":256,"temperature":0,"stream":false}' \
      > /tmp/opencode/rd2d-completion.json
    pkill -INT -f "llama-server.*--port $port" 2>/dev/null || true
    for i in $(seq 1 24); do [ -s /tmp/opencode/rd2d-tg.txt ] && break; sleep 5; done
    if [ ! -s /tmp/opencode/rd2d-tg.txt ]; then
        pkill -TERM -f "llama-server.*--port $port" 2>/dev/null || true
        for i in $(seq 1 12); do [ -s /tmp/opencode/rd2d-tg.txt ] && break; sleep 5; done
    fi
    pkill -9 -f "llama-server.*--port $port" 2>/dev/null || true
    sleep 5
    if [ -s /tmp/opencode/rd2d-tg.txt ]; then
        log "rd2d histogram:" && cat /tmp/opencode/rd2d-tg.txt >> "$LOG"
        log "rd2d screen DONE"
    else
        log "rd2d: no dump produced (atexit skipped) - treat as inconclusive"
        return 1
    fi
}

echo PENDING > "$STATUS"
: > "$LOG"
log "E113 window runner armed (pid $$)"
wait_window || { echo TIMEOUT > "$STATUS"; exit 1; }
echo RUNNING > "$STATUS"
fail=0
lane e113b0 build-dflash-novega || fail=1
lane e113s0 build-e113-sync     || fail=1
lane e114q0 build-e114-q6k64    || fail=1
rd2d_screen || fail=1
if [ "$fail" = 0 ]; then echo DONE > "$STATUS"; log "ALL DONE"; else echo PARTIAL > "$STATUS"; log "PARTIAL FAILURE (see lanes above)"; fi
