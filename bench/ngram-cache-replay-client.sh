#!/usr/bin/env bash
set -euo pipefail

PORT=${1:-8013}
TOKENS=${REPLAY_TOKENS:-512}
PROMPT=$'Continue the Gettysburg Address exactly, without headings or commentary. Begin after this text:\nFour score and seven years ago our fathers brought forth on this continent, a new nation, conceived in Liberty, and dedicated to the proposition that all men are created equal.\n'

payload=$(jq -cn \
  --arg prompt "$PROMPT" \
  --argjson n_predict "$TOKENS" \
  '{prompt: $prompt, n_predict: $n_predict, temperature: 0, top_k: 1, seed: 1, cache_prompt: false, id_slot: 0, stream: false, ignore_eos: true}')
response=$(curl -fsS --max-time 1200 \
  -H 'Content-Type: application/json' \
  -d "$payload" \
  "http://127.0.0.1:$PORT/completion")

predicted_n=$(jq -er '.timings.predicted_n' <<< "$response")
if [ "$predicted_n" -ne "$TOKENS" ]; then
  printf 'ERROR: incomplete replay completion: %s != %s\n' "$predicted_n" "$TOKENS" >&2
  exit 1
fi

content=$(jq -er '.content' <<< "$response")
output_sha=$(printf '%s' "$content" | sha256sum | cut -d ' ' -f 1)

jq -cn \
  --arg output_sha "${output_sha:0:12}" \
  --argjson response "$response" \
  '{
    requested_n: $response.timings.predicted_n,
    predicted_n: $response.timings.predicted_n,
    tg_tps: ($response.timings.predicted_per_second * 1000 | round / 1000),
    draft_n: ($response.timings.draft_n // 0),
    draft_n_accepted: ($response.timings.draft_n_accepted // 0),
    accepted_per_generated: ((($response.timings.draft_n_accepted // 0) / $response.timings.predicted_n) * 1000000 | round / 1000000),
    accepted_per_draft: (if ($response.timings.draft_n // 0) > 0 then ((($response.timings.draft_n_accepted // 0) / $response.timings.draft_n) * 1000000 | round / 1000000) else 0 end),
    output_sha: $output_sha,
    output_lines: ($response.content | split("\n") | length),
    output_prefix: ($response.content[0:160])
  }'
