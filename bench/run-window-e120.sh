#!/usr/bin/env bash
# E120 GPU-window runner: waits for a free rig + green builds, then runs
# the TG campaign: tracer validation -> deep decomposition -> n5 cliff
# diff -> mmid5 A/B -> fastmath A/B.
# Never kills anything it did not start; skips remaining steps if a
# server appears between steps (user prod has priority).
# Status: /tmp/opencode/e120-window.status ; log: /tmp/opencode/e120-window.log
# Arm AFTER the user greenlights the window:
#   setsid nohup ./bench/run-window-e120.sh > /dev/null 2>&1 < /dev/null &
set -uo pipefail
cd "$(dirname "$(readlink -f "$0")")/.."
ROOT=$PWD
LOG=/tmp/opencode/e120-window.log
STATUS=/tmp/opencode/e120-window.status
MAX_WAIT_H=${MAX_WAIT_H:-8}

log() { echo "[$(date +%H:%M:%S)] $*" >> "$LOG"; }

rig_free() { ! pgrep -f "bin/llama-server" >/dev/null 2>&1; }

builds_green() {
    [ -f /tmp/opencode/build-fastmath.OK ] && [ -f /tmp/opencode/build-mmid5.OK ]
}

wait_window() {
    local deadline=$(( $(date +%s) + MAX_WAIT_H * 3600 ))
    while [ "$(date +%s)" -lt "$deadline" ]; do
        if [ -f /tmp/opencode/build-fastmath.FAIL ] || [ -f /tmp/opencode/build-mmid5.FAIL ]; then
            log "ABORT: a build FAILED - window will not run"
            return 2
        fi
        if rig_free && builds_green; then
            sleep 30  # debounce: prod may be mid-restart
            if rig_free && builds_green; then
                log "window open (builds green, rig free)"
                return 0
            fi
        fi
        sleep 60
    done
    log "TIMEOUT: no window within ${MAX_WAIT_H}h"
    return 1
}

trace_lane() {  # trace_lane <name> [VAR=VAL ...]
    local lane=$1; shift
    rig_free || { log "SKIP $lane: server appeared"; return 1; }
    log "TRACER LANE $lane start"
    if env "$@" LANE=$lane ./bench/rd-trace-lane.sh >> "$LOG" 2>&1; then
        log "TRACER LANE $lane DONE"
    else
        log "TRACER LANE $lane FAILED (status: $(cat /tmp/opencode/lane-$lane.status 2>/dev/null))"
        return 1
    fi
    if python3 bench/rd-trace-analyze.py /tmp/opencode/rd-trace-$lane.bin --last 120 \
            > bench/logs/rd-trace-$lane.analysis.txt 2>&1; then
        log "analysis: bench/logs/rd-trace-$lane.analysis.txt"
        tail -5 bench/logs/rd-trace-$lane.analysis.txt >> "$LOG"
    else
        log "analyzer failed for $lane (trace still on disk)"
    fi
    sleep 10
}

ab() {  # ab <script>
    local script=$1
    rig_free || { log "SKIP $script: server appeared"; return 1; }
    log "A/B $script start"
    if ./"$script" >> "$LOG" 2>&1; then
        log "A/B $script DONE"
    else
        log "A/B $script FAILED"
        return 1
    fi
    sleep 10
}

[ -x bench/rd-trace.so ] || { echo "ABORT: bench/rd-trace.so missing" > "$STATUS"; exit 1; }

echo PENDING > "$STATUS"
: > "$LOG"
log "E120 window runner armed (pid $$)"
wait_window
rc=$?
if [ "$rc" != 0 ]; then
    [ "$rc" = 2 ] && echo ABORT > "$STATUS" || echo TIMEOUT > "$STATUS"
    exit 1
fi
echo RUNNING > "$STATUS"
fail=0
trace_lane e120t0                        || fail=1
trace_lane e120t1 FILL1=120000           || fail=1
trace_lane e120t2 SPEC_N_MAX=5           || fail=1
ab bench/ab-mmid5.sh                     || fail=1
ab bench/ab-fastmath.sh                  || fail=1
log "lane rows:"
grep -h "e120t" bench/logs/lane-results.jsonl | tail -3 >> "$LOG" 2>/dev/null || true
log "trial rows:"
grep -E "mmid5-|fastmath-" bench/trials.md | tail -4 >> "$LOG" 2>/dev/null || true
if [ "$fail" = 0 ]; then echo DONE > "$STATUS"; log "ALL DONE"; else echo PARTIAL > "$STATUS"; log "PARTIAL FAILURE (see steps above)"; fi
