#!/usr/bin/env bash
# E50v2 lane: the AC1 champion command on the GGML_CUDA_VEGA_TUNE=OFF build
# (build-dflash-novega). One variable vs AC1: the binary. Env cloned from the
# AC1 record: bench/logs/lane-AC1.log (argv facts: ts 35,20,45, sm layer,
# c 200000, ctv q8_0, draft Q4_K_M, n_max=4, ckpt 30) and the AC1 row in
# bench/logs/lane-results.jsonl. Gate thresholds: TG >= 10.5 -> tuning is the
# cause; TG < 9.5 or repro fail -> sched/rocprof path. See HANDOFF-E50-V2.
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")/.."

BIN_DIR="$PWD/build-dflash-novega"
[ -x "$BIN_DIR/bin/llama-server" ] || { echo "missing $BIN_DIR/bin/llama-server" >&2; exit 1; }

export LANE=e50v2
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
