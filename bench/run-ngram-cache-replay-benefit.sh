#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)
OUT=${OUT:?OUT must name a new result directory}
BUILD=${BUILD:-$ROOT/build-promptlookup-baseline}
LAUNCHER=${LAUNCHER:-$ROOT/swift_1.5_llama_start-q6_q8_q4-ngcache.sh}
PORT=${PORT:-8013}
RUNS=${RUNS:-3}
TOKENS=${TOKENS:-256}
COOLDOWN_SECONDS=${COOLDOWN_SECONDS:-5}
CLIENT=$ROOT/bench/ngram-cache-replay-client.sh
HARNESS=$ROOT/bench/run-sync0924-validation.sh
SNAPSHOT=$OUT/snapshot-training.bin
MASTER=$OUT/snapshot-master.bin

if [ -e "$OUT" ]; then
    printf 'ERROR: OUT already exists: %s\n' "$OUT" >&2
    exit 1
fi
mkdir -p "$OUT"

run_lane() {
    label=$1
    spec_type=$2
    cache_file=$3
    GIT_MASTER=1 \
    OUT="$OUT/$label" \
    BUILD="$BUILD" \
    LAUNCHER="$LAUNCHER" \
    CLIENT="$CLIENT" \
    PORT="$PORT" \
    SPEC_TYPE="$spec_type" \
    NGRAM_CACHE_FILE="$cache_file" \
    REPLAY_TOKENS="$TOKENS" \
    SPEC_N_MAX=3 \
    bash "$HARNESS"
    sleep "$COOLDOWN_SECONDS"
}

run_lane train-1 ngram-mod,ngram-cache,draft-dflash "$SNAPSHOT"
run_lane train-2 ngram-mod,ngram-cache,draft-dflash "$SNAPSHOT"
cp "$SNAPSHOT" "$MASTER"

run_lane baseline-warmup ngram-mod,draft-dflash "$OUT/baseline-unused.bin"
cp "$MASTER" "$OUT/candidate-warmup.bin"
run_lane candidate-warmup ngram-mod,ngram-cache,draft-dflash "$OUT/candidate-warmup.bin"

for run in $(seq 1 "$RUNS"); do
    run_lane "baseline-r$run" ngram-mod,draft-dflash "$OUT/baseline-unused.bin"
    cp "$MASTER" "$OUT/candidate-r$run.bin"
    run_lane "candidate-r$run" ngram-mod,ngram-cache,draft-dflash "$OUT/candidate-r$run.bin"
done

baseline_tps=$(jq -s 'map(.tg_tps)' "$OUT"/baseline-r*/result.json)
candidate_tps=$(jq -s 'map(.tg_tps)' "$OUT"/candidate-r*/result.json)
sha_count=$(jq -r '.output_sha' "$OUT"/baseline-r*/result.json "$OUT"/candidate-r*/result.json | sort -u | wc -l)
if [ "$sha_count" -ne 1 ]; then
    printf 'ERROR: temp-0 output SHA differs across retained lanes\n' >&2
    exit 1
fi
output_sha=$(jq -r '.output_sha' "$OUT"/baseline-r1/result.json)

jq -n \
    --argjson baseline "$baseline_tps" \
    --argjson candidate "$candidate_tps" \
    --arg output_sha "$output_sha" \
    '($baseline | add / length) as $baseline_mean |
     ($candidate | add / length) as $candidate_mean |
     {
       baseline_tps: $baseline,
       candidate_tps: $candidate,
       baseline_mean: $baseline_mean,
       candidate_mean: $candidate_mean,
       speedup_percent: (($candidate_mean / $baseline_mean - 1) * 100),
       ratio: ($candidate_mean / $baseline_mean),
       output_sha: $output_sha
     }' | tee "$OUT/summary.json"
