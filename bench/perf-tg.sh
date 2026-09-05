#!/usr/bin/env bash
# Usage: LANE=.. [DELAY=120] [DUR=25] [FILL1=16000] [TG_N=512] [PORT=8014] ./bench/perf-tg.sh
# Runs bench/lane-dflash.sh (no tracer preload), attaches perf to the server
# during the TG phase, writes bench/logs/perf-$LANE.report.txt
set -u
cd "$(dirname "$0")/.."
LANE=${LANE:?set LANE}
DELAY=${DELAY:-120}
DUR=${DUR:-25}
PORT=${PORT:-8014}
OUT=/tmp/opencode/perf-$LANE.data
LOG=/tmp/opencode/perf-$LANE.log

LANE=$LANE FILL1=${FILL1:-16000} TG_N=${TG_N:-512} PORT=$PORT ./bench/lane-dflash.sh > /tmp/opencode/lane-$LANE.log 2>&1 &
LANE_PID=$!

sleep "$DELAY"
SPID=$(pgrep -f "llama-serve[r].*--port $PORT" | head -1)
if [ -z "$SPID" ]; then
  echo "FAIL: no server pid at +${DELAY}s" >> "$LOG"
  kill $LANE_PID 2>/dev/null
  exit 1
fi
echo "server pid $SPID, perf ${DUR}s @ +${DELAY}s" >> "$LOG"
perf record -F 399 -e cycles:u -p "$SPID" -o "$OUT" -- sleep "$DUR" >> "$LOG" 2>&1

wait $LANE_PID
perf report --stdio -i "$OUT" --sort symbol,dso --percent-limit 0.3 > bench/logs/perf-$LANE.report.txt 2>>"$LOG"
echo "report: bench/logs/perf-$LANE.report.txt ($(date +%H:%M:%S))" >> "$LOG"
