#!/usr/bin/env bash
# E50v2 fix stage 1a: UNPROFILED verify-regime timing (the authoritative
# timing for the FATTN path comparison; profiled runs serialize kernels).
# Fills to 120k then runs a short TG at fixed ~120k KV depth, where the
# spec verify ops (Q=3-5 rows) are the cost center. EXTRA=-v enables the
# per-round spec debug lines (n_draft / n_accepted) so the Q-mix can be
# compared across the FATTN-on (b1) and FATTN-off builds: if the two Q
# histograms diverge, the end-to-end us/verify delta is acceptance-
# confounded and must be read against stage 1b (PMU), not as a kernel
# ranking.
# Usage: ./fa1-lane-120k.sh [FA1A_B1]   (LANE label; default fa1a-b1)
# Run once per build-dflash-novega variant.
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")/.."

BIN_DIR="$PWD/build-dflash-novega"
[ -x "$BIN_DIR/bin/llama-server" ] || { echo "missing $BIN_DIR/bin/llama-server" >&2; exit 1; }

export LANE=${1:-fa1a-b1}
export BIN_DIR
export C=155000
export TS=35,20,45
export SM=layer
export CTV=q8_0
export SPEC_TYPE=draft-dflash
export SPEC_N_MAX=4
export NGRAM=0
export FILL1=120000
export FILL2=0
export TG_N=256
export EXTRA=-v

exec bash bench/lane-dflash.sh
