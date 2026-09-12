#!/usr/bin/env bash
# galloc-top.sh <logfile> [buf-id] [top-n]
# Aggregate GGML_GALLOC_DUMP lines (galloc-dump buf=N size=S type=T name=X op=Y)
# by buffer and tensor name; sizes summed per print pass.
set -euo pipefail
LOG="${1:?usage: galloc-top.sh <log> [buf] [n]}"
BUF="${2:-}"
N="${3:-12}"
grep -a 'galloc-dump' "$LOG" | grep -a ${BUF:+"buf=$BUF "} | awk -v n="$N" '
{
    buf = size = ""; name = "?"
    for (i = 1; i <= NF; i++) {
        if ($i ~ /^buf=/)   { buf  = substr($i, 5) }
        if ($i ~ /^size=/)  { size = substr($i, 6) }
        if ($i ~ /^name=/)  { name = substr($i, 6); op = $(i+1); sub(/^op=/, "", op) }
    }
    if (size == "") next
    key = name " (" op ")"
    sum[key] += size/1048576; cnt[key]++
}
END {
    for (k in sum) printf "buf=%s %10.1f MB x%-3d %s\n", buf, sum[k], cnt[k], k
}' | sort -k2 -rn | head -"$N"
