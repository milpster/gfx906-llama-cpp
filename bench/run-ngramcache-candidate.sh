#!/usr/bin/env bash
# fork-local: candidate chain lane - adds ngram-cache behind ngram-mod.
# Everything else stays identical to the production launcher and the
# sync0924 validation gate. Usage:
#   OUT=$PWD/bench/logs/<tag> [BUILD=...] bench/run-ngramcache-candidate.sh
set -euo pipefail

ROOT=$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)
OUT=${OUT:?OUT must be set}
SPEC_CHAIN=${SPEC_CHAIN:-ngram-mod,ngram-cache,draft-dflash}
mkdir -p "$OUT"

cache_arg=
if [ -n "${DYNAMIC_CACHE:-}" ]; then
    cache_arg="-lcd \"$DYNAMIC_CACHE\""
fi

sed -e "s|--spec-type ngram-mod,draft-dflash|--spec-type $SPEC_CHAIN --spec-ngram-cache-strict $cache_arg|" \
    -e "s|--spec-draft-n-max \"\${SPEC_N_MAX:-3}\"|--spec-draft-n-max \"\${SPEC_N_MAX:-3}\" --spec-draft-n-min \"\${SPEC_N_MIN:-3}\"|" \
    -e "s|exec \"\$BIN\" \\\\|exec \"\$BIN\" ${TRACE:+-v} \\\\|" \
    "$ROOT/swift_llama_start-q6_q8_q4.sh" > "$OUT/launcher-candidate.sh"
cp "$ROOT/sharp_chat_template.jinja" "$OUT/sharp_chat_template.jinja"
chmod +x "$OUT/launcher-candidate.sh"

if [ "$(grep -F -c -- "--spec-type $SPEC_CHAIN" "$OUT/launcher-candidate.sh")" -ne 1 ]; then
    echo "ERROR: launcher substitution failed"
    exit 1
fi

export LAUNCHER="$OUT/launcher-candidate.sh"
export BUILD=${BUILD:-$ROOT/build-promptlookup-baseline}
export OUT

exec bash "$ROOT/bench/run-sync0924-validation.sh"
