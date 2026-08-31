#!/usr/bin/env bash
# E50v2 fix stage 0: the AC1 champion command on the build-dflash-novega
# binary built with the FATTN sub-gate on AND the tile batch gate raised
# (Q->ne[1] > 32 instead of > 2) so small-Q ops (spec verify, few rows)
# stay on the shadow-free VEC kernel instead of the in-kernel-dequant tile.
# Same binary config as e50v2-b1 (FATTN on, MMQ/TOPK/GRAPHS off); the only
# diff vs b1 is the dispatch threshold.
# Reading: TG near e50v2's 11.9 with buffer 238.15 = the TG loss was the
# small-Q tile routing; fill1 ~202 = tile dequant cost on the prompt path
# (the part the kernel work must fix).
# Same env + full paths as e50v2-b1-lane-200k.sh.
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")/.."

BIN_DIR="$PWD/build-dflash-novega"
[ -x "$BIN_DIR/bin/llama-server" ] || { echo "missing $BIN_DIR/bin/llama-server" >&2; exit 1; }

export LANE=e50v2-s0
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
