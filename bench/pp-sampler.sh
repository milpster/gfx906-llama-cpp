#!/usr/bin/env bash
# Sample llama-server threads and GPU use for N seconds while a PP pass runs.
set -u
D=$1
PID=$2
N=${3:-24}
: > "$D/gpu_sample.txt"
: > "$D/thread_deltas.txt"
for i in $(seq 1 $((N / 4))); do
    for t in /proc/$PID/task/*; do
        u=$(awk '{print $14+$15}' "$t/stat" 2>/dev/null)
        echo "${t##*/} $u"
    done > /tmp/opencode/pp_before.txt
    rocm-smi --showuse --showmemuse 2>/dev/null | grep -E '^GPU' >> "$D/gpu_sample.txt"
    echo '---' >> "$D/gpu_sample.txt"
    sleep 4
    while read -r tid u1; do
        u2=$(awk '{print $14+$15}' "/proc/$PID/task/$tid/stat" 2>/dev/null)
        [ -n "$u2" ] && echo "$tid $((u2 - u1))" >> "$D/thread_deltas.txt"
    done < /tmp/opencode/pp_before.txt
    echo '---' >> "$D/thread_deltas.txt"
done
