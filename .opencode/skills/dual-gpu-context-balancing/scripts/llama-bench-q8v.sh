#!/usr/bin/env bash
# Benchmark the running q8v server: tg (1024 out), pp (~7.5k in @ ub 384), vision sanity.
# Usage: llama-bench-q8v.sh [port]   (default 8009)
set -eu
PORT="${1:-8009}"
URL="http://127.0.0.1:$PORT"
LOG="$(ls -t /home/srcds/dev/rocm6.1_llama.cpp/.opencode/skills/dual-gpu-context-balancing/scripts/logs/*.log 2>/dev/null | head -1)"

echo "== tg: 1024 tokens out =="
curl -s "$URL/completion" -H "Content-Type: application/json" \
  -d '{"prompt":"Write a detailed technical essay about GPU memory architecture.","n_predict":1024,"temperature":0.6,"top_p":0.95,"stream":false}' \
  -o /dev/null -w "wall=%{time_total}s\n"

echo "== pp: ~7.5k tokens in (first run only; rerun hits prompt cache) =="
python3 - <<'EOF' > /tmp/pp_req.json
import json
para = 'The Radeon VII graphics card uses HBM2 memory with a 4096-bit interface, delivering approximately 1 TB/s of memory bandwidth, which remains relevant for large language model inference where KV cache bandwidth often dominates token generation. '
json.dump({'prompt': para * 160, 'n_predict': 1, 'temperature': 0.1}, open('/dev/stdout','w'))
EOF
curl -s "$URL/completion" -H "Content-Type: application/json" -d @/tmp/pp_req.json -o /dev/null -w "wall=%{time_total}s\n"

echo "== vision sanity =="
python3 - <<'EOF' > /tmp/vision_req.json
import base64, struct, zlib, json
W = H = 64
rows = []
for y in range(H):
    row = bytearray([0])
    for x in range(W):
        row += b'\xff\x00\x00' if (8 <= x < 56 and 8 <= y < 56) else b'\x00\x00\xff'
    rows.append(bytes(row))
def chunk(t, d):
    c = t + d
    return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c))
png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
       + chunk(b'IDAT', zlib.compress(b''.join(rows))) + chunk(b'IEND', b''))
b64 = base64.b64encode(png).decode()
json.dump({'model': 'q', 'messages': [{'role': 'user', 'content': [
    {'type': 'text', 'text': 'Describe this image in one sentence.'},
    {'type': 'image_url', 'image_url': {'url': 'data:image/png;base64,' + b64}}]}],
    'max_tokens': 200}, open('/dev/stdout', 'w'))
EOF
curl -s "$URL/v1/chat/completions" -H "Content-Type: application/json" -d @/tmp/vision_req.json \
  | python3 -c "import json,sys; r=json.load(sys.stdin); m=r['choices'][0]['message']; print('VISION OK:', (m.get('content') or m.get('reasoning_content') or '?')[:150])"

echo "== server-side timings (from newest trial log) =="
[ -n "${LOG:-}" ] && grep -E "prompt eval time|eval time|acc rate/pos" "$LOG" | tail -3 || true
