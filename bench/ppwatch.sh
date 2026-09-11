#!/usr/bin/env bash
# bench/ppwatch.sh — live status dashboard for qwen38f PP benchmark runs.
# Start (detached):  tmux new-session -d -s ppwatch 'exec bash bench/ppwatch.sh'
# Attach:            tmux attach -t ppwatch        (detach: Ctrl-b d)
# Stop:              tmux kill-session -t ppwatch
# Env: PPWATCH_REFRESH (seconds, default 2)
#
# Shows: running llama processes, kernel-truth GPU busy%/VRAM (card2/card3 =
# Radeon VII ROCm0/ROCm1, card4 = RTX 3080 Vulkan), CPU load, the 8 most
# recent bench arms with their newest "prompt eval time" line, and a tail
# of the newest run log. Journal: journal/JOURNAL-2026-09-*.md (E147+).

REFRESH=${PPWATCH_REFRESH:-2}
BASE=/tmp/opencode/qwen38-speed

while true; do
    clear
    printf '== qwen38f PP watch  %s ==\n' "$(date '+%H:%M:%S')"

    printf '\n[llama processes]\n'
    ps -eo pid,etime,args | grep -E 'llama-(cli|server|bench)' | grep -v grep | cut -c1-150 || true
    ps -eo pid,etime,args | grep -E 'llama-(cli|server|bench)' | grep -v grep | grep -q . || echo '  (none running)'

    printf '\n[GPU busy%% / VRAM]   '
    for c in 2 3 4; do
        b=$(cat /sys/class/drm/card$c/device/gpu_busy_percent 2>/dev/null || echo NA)
        v=$(awk '{printf "%.1fG", $1/1073741824}' /sys/class/drm/card$c/device/mem_info_vram_used 2>/dev/null || echo NA)
        printf 'card%s: %s%% %s   ' "$c" "$b" "$v"
    done
    printf '\n[CPU load] %s\n' "$(cut -d' ' -f1-3 /proc/loadavg)"

    printf '\n[latest speed arms (newest first)]\n'
    ls -t $BASE/*/summary.txt 2>/dev/null | head -8 | while read -r f; do
        arm=$(basename "$(dirname "$f")")
        line=$(grep 'prompt eval time' "$f" | tail -1 | sed -E 's/^[^|]*\|[^|]*prompt eval time =//; s/\(.*tokens per second\)//')
        printf '  %-26s %s\n' "$arm" "$line"
    done

    newest=$(ls -t $BASE/*/r*.log 2>/dev/null | head -1)
    if [ -n "$newest" ]; then
        printf '\n[tail %s/%s]\n' "$(basename "$(dirname "$newest")")" "$(basename "$newest")"
        tail -n 4 "$newest" | cut -c1-150
    fi

    sleep "$REFRESH"
done
