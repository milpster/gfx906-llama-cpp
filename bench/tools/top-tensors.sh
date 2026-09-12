#!/usr/bin/env bash
# top-tensors.sh <logfile> [backend-filter] [top-n]
# Sum ggml sched debug node sizes per tensor name (aggregate across graph
# reserve passes) from a GGML_SCHED_DEBUG=2 dump. Sizes are 5-char truncated
# by ggml (e.g. "40K", "1.2M") so sums are approximate.
set -euo pipefail
LOG="${1:?usage: top-tensors.sh <log> [backend] [n]}"
BE="${2:-}"
N="${3:-15}"
grep -aE 'node #' "$LOG" | grep -a ${BE:+"$BE"} | awk -v n="$N" '
{
    # strip timestamp+level prefix up to "node #"
    idx = index($0, "node #")
    if (idx == 0) next
    line = substr($0, idx)
    # split at first "): " -> "<node # N ( OP):" | "name (size) [backend ..."
    pos = index(line, "):")
    if (pos == 0) next
    rest = substr(line, pos + 2)
    gsub(/^ +/, "", rest)
    # name = first token; size = next "( SIZE )" possibly spaced
    m = match(rest, /^([^ ]+) +\(([ 0-9.]+[KMGT]?)\)/, cap)
    if (m == 0) next
    name = cap[1]; sz = cap[2]; gsub(/ /, "", sz)
    u = substr(sz, length(sz)); v = substr(sz, 1, length(sz) - 1) + 0
    mb = (u == "G") ? v * 1024 : (u == "M") ? v : (u == "K") ? v / 1024 : (u == "T") ? v * 1048576 : 0
    sum[name] += mb; cnt[name]++
}
END {
    for (k in sum) printf "%10.1f MB x%-4d %s\n", sum[k], cnt[k], k
}' | sort -rn | head -"$N"
