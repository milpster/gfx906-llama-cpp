#!/usr/bin/env bash
# Fixed-history TG measurement: identical request sequence from a fresh
# server; drafter (adaptive MTP) state depends only on position in sequence.
# Canonical steady TG = median of rounds 6..10. Usage: tg_fixed_history.sh <port> <rounds=10>
PORT=${1:-8123}; R=${2:-10}; NP=128
P='Write a short story about a lighthouse keeper who discovers something unusual. The story should be complete with a beginning, middle and end.'
OUT=${OUT:-bench/logs/q38speed/tg-harness/results.tsv}
printf 'round\ttps\taccept\tdraft_n\tpredicted_ms\tsha\n' > "$OUT"
for i in $(seq 1 "$R"); do
  response=$(curl -s -m 600 "http://127.0.0.1:$PORT/completion" -d "$(jq -nc --arg p "$P" --argjson np "$NP" '{prompt: $p, n_predict: $np, temperature: 0.0, seed: 42}')")
  sha=$(printf '%s' "$response" | jq -j '.content // ""' | sha256sum | cut -c1-12)
  printf '%s' "$response" | jq -r --argjson i "$i" --arg sha "$sha" '[$i, .timings.predicted_per_second, ((.timings.draft_n_accepted // 0) / (.timings.draft_n // 1)), (.timings.draft_n // 0), .timings.predicted_ms, $sha] | @tsv' >> "$OUT"
done
echo "=== per-round ==="; column -t "$OUT"
echo "=== steady (rounds 6..$R median) ==="
tail -n +2 "$OUT" | awk -F'\t' 'NR>=6 {print $2}' | sort -n | awk '{a[NR]=$1} END {print (NR%2)? a[(NR+1)/2] : (a[NR/2]+a[NR/2+1])/2}'
