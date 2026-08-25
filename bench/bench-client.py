#!/usr/bin/env python3
"""Benchmark client: health wait, single-batch PP, one 256-token TG pass.

PP: prompt is sized just above n_batch (16384+8) so the first server batch is
exactly 16384 tokens; the first prompt_progress SSE event IS that batch.
TG: one greedy 256-token completion, streamed live to stderr when LIVE=1.

Prints one JSON line on stdout; exits non-zero on failure.
"""
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request

PORT = sys.argv[1] if len(sys.argv) > 1 else "8013"
BASE = f"http://127.0.0.1:{PORT}"
LIVE = os.environ.get("LIVE", "1") != "0"
TG_N = int(os.environ.get("TG_N", "256"))
PP_ABORT = os.environ.get("PP_ABORT", "1") != "0"


def req(path, payload=None, timeout=3600):
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(BASE + path, data=data,
                               headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        return json.loads(resp.read())


t0 = time.time()
for _ in range(600):
    try:
        urllib.request.urlopen(BASE + "/health", timeout=5)
        break
    except Exception:
        time.sleep(2)
else:
    print(json.dumps({"error": "health timeout"}))
    sys.exit(1)
load_s = round(time.time() - t0, 1)

n_ctx = req("/slots")[0]["n_ctx"]

# --- PP: one full 16384-token batch, then stop reading ---
filler = " ".join(
    f"The {w} archive records event {i:05d} with measure {i*7%997:03d} and note {i*13%89:02d}."
    for i, w in enumerate(["red", "blue", "green", "amber", "slate", "ochre", "teal", "plum"] * 6000)
)
toks = req("/tokenize", {"content": filler})["tokens"][:16392]

pp_payload = {
    "prompt": toks + ["\n\nSummary:"],
    "n_predict": 4,
    "temperature": 0,
    "cache_prompt": False,
    "id_slot": 0,
    "stream": True,
    "return_progress": True,
}
first_batch = None
r = urllib.request.Request(BASE + "/completion", data=json.dumps(pp_payload).encode(),
                           headers={"Content-Type": "application/json"})
with urllib.request.urlopen(r, timeout=3600) as resp:
    for raw in resp:
        line = raw.decode().strip()
        if not line.startswith("data: "):
            continue
        body = line[len("data: "):]
        if body == "[DONE]":
            break
        ev = json.loads(body)
        prog = ev.get("prompt_progress")
        if prog and first_batch is None and prog.get("processed", 0) > 0:
            first_batch = prog
            if PP_ABORT:
                break

if not first_batch:
    print(json.dumps({"error": "no progress in PP stream"}))
    sys.exit(1)
pp_tps = round(first_batch["processed"] / first_batch["time_ms"] * 1000.0, 1)
pp_n = first_batch["processed"]

TG_FILL = int(os.environ.get("TG_FILL", "0"))

# --- TG: one greedy 256-token pass, streamed live to stderr ---
# TG_FILL > 0 prepends that many filler tokens so generation runs at deep
# KV fill, measuring the ctx -> TG cost (attention reads scale with fill).
# The prompt is cut mid-sentence because greedy decoding after long repetitive
# filler tends to emit EOS immediately when asked a fresh question.
tg_prompt = "Write a clear technical explanation of why the sky is blue."
if TG_FILL > 0:
    toks_fill = req("/tokenize", {"content": filler})["tokens"][:TG_FILL]
    tg_prompt = (toks_fill + ["\n\nThe following is a technical essay.\n\n"]
                 + [tg_prompt + " The sky appears blue because"])

def stream_completion(payload):
    parts = []
    last_event = {}
    r = urllib.request.Request(BASE + "/completion", data=json.dumps(payload).encode(),
                               headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=3600) as resp:
        for raw in resp:
            line = raw.decode().strip()
            if not line.startswith("data: "):
                continue
            body = line[len("data: "):]
            if body == "[DONE]":
                break
            ev = json.loads(body)
            last_event = ev
            delta = ev.get("content")
            if delta:
                parts.append(delta)
                if LIVE:
                    print(delta, end="", file=sys.stderr, flush=True)
    return last_event, "".join(parts)

if LIVE:
    print("--- TG output (live) ---", file=sys.stderr, flush=True)
tg_last, tg_content = stream_completion({"prompt": tg_prompt, "n_predict": TG_N,
                                          "temperature": 0, "cache_prompt": False,
                                          "id_slot": 0, "stream": True})
if LIVE:
    print("\n--- end TG output ---", file=sys.stderr, flush=True)
tg = tg_last.get("timings")
if tg is None or tg.get("predicted_n", 0) < 32:
    print(json.dumps({"error": f"degenerate TG completion: {tg and tg.get('predicted_n')} tokens"}))
    sys.exit(1)

acc = round(tg.get("draft_n_accepted", 0) / max(tg["predicted_n"], 1), 3)

print(json.dumps({
    "load_s": load_s,
    "n_ctx": n_ctx,
    "pp_n": pp_n,
    "pp_tps": pp_tps,
    "tg_n": tg["predicted_n"],
    "tg_tps": round(tg["predicted_per_second"], 1),
    "acc": acc,
    "sha": hashlib.sha256(tg_content.encode()).hexdigest()[:12],
}))
