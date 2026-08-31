#!/usr/bin/env bash
# Fork-vs-mainline comparison launcher (full 2llama config, -c 200000).
# Fork side completed 2026-08-31 (json kept); default runs the pending
# mainline side only (~11 min). ALL=1 reruns both sides (~22 min).
# GPUs must be free. Requires build-stock at current upstream master
# (~/dev/llama.cpp, branch mainline-cmp).
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"

if [ "${ALL:-0}" = "1" ]; then
    exec bash bench/cmp-mainline-temp0.sh
fi
exec env SIDES=mainline bash bench/cmp-mainline-temp0.sh
