#!/usr/bin/env bash
# E50v2 bisect b1: the AC1 champion command on the build-dflash-novega binary
# built with ONLY the FATTN sub-gate on (GGML_CUDA_VEGA_TUNE + _FATTN on;
# _MMQ/_TOPK/_GRAPHS off). One variable vs the e50v2 all-off lane: the binary.
# Reading: TG near e50v2's 11.9 = fattn tuning innocent; TG collapses toward
# AC1's 8.9 = the flash-attention tile tuning is implicated (stop, report).
# Same env + full paths as e50v2-lane-200k.sh (cloned env; lane-dflash.sh
# carries the MODEL/MD/mmproj/LD_LIBRARY_PATH full-path defaults).
# See PROGRESS-E50-V2-2026-08-30.md + HANDOFF-E50-V2 (Phase 5).
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")/.."

BIN_DIR="$PWD/build-dflash-novega"
[ -x "$BIN_DIR/bin/llama-server" ] || { echo "missing $BIN_DIR/bin/llama-server" >&2; exit 1; }

export LANE=e50v2-b1
export BIN_DIR
export C=200000
export TS=35,20,45
export SM=layer
export CTV=q8_0
export SPEC_TYPE=draft-dflash
export SPEC_N_MAX=4
export NGRAM=0
# lane-dflash.sh reads $FILL2 unguarded (set -u); 0 = single fill pass (D16)
export FILL2=0

exec bash bench/lane-dflash.sh
