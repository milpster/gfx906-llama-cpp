#!/usr/bin/env python3
"""Lane client: full protocol per journal/JOURNAL-2026-08-26.md C1.

health -> temp0-repro-BEFORE -> PP16384 (first-batch SSE) -> fill to 120k ->
fill to 180k (cached extend) -> TG1024 @ temp 1.0 (seeded) -> temp0-repro-AFTER.

Prints one JSON line on stdout; exits non-zero on failure. PP parsing matches
bench-client.py exactly (first prompt_progress event of a 16392+4 prompt).
"""
import hashlib
import json
import os
import sys
import time
import urllib.request

PORT = sys.argv[1] if len(sys.argv) > 1 else "8014"
BASE = f"http://127.0.0.1:{PORT}"
TG_N = int(os.environ.get("TG_N", "1024"))
FILL1 = int(os.environ.get("FILL1", "120000"))
FILL2 = int(os.environ.get("FILL2", "180000"))
REPRO_PROMPT = "Write a clear technical explanation of why the sky is blue."


def req(path, payload=None, timeout=7200):
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(BASE + path, data=data,
                               headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        return json.loads(resp.read())


t0 = time.time()
for _ in range(900):
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

filler = " ".join(
    f"The {w} archive records event {i:05d} with measure {i*7%997:03d} and note {i*13%89:02d}."
    for i, w in enumerate(["red", "blue", "green", "amber", "slate", "ochre", "teal", "plum"] * 5000)
)
# tokenize the filler ONCE; all stages slice the same token list
all_toks = req("/tokenize", {"content": filler})["tokens"]
if len(all_toks) < FILL2 + 8:
    print(json.dumps({"error": f"filler too small: {len(all_toks)} < {FILL2}"}))
    sys.exit(1)

def repro():
    last = req("/completion", {"prompt": REPRO_PROMPT, "n_predict": 256,
                               "temperature": 0, "cache_prompt": False,
                               "id_slot": 0, "stream": False, "seed": 1})
    return hashlib.sha256(last["content"].encode()).hexdigest()[:12]

# --- repro BEFORE ---
sha_before = repro()

# --- single-pass PP + deep fill: one FILL1-token streamed prompt; first
# prompt_progress event = first-batch PP, last = fill metric ---
def ppfill(n_tokens):
    t = all_toks[:n_tokens] + ["\n\nContinue:"]
    payload = {"prompt": t, "n_predict": 4,
               "temperature": 0, "cache_prompt": False, "id_slot": 0,
               "stream": True, "return_progress": True}
    r = urllib.request.Request(BASE + "/completion", data=json.dumps(payload).encode(),
                               headers={"Content-Type": "application/json"})
    first_batch = None
    last_prog = None
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
            if prog and prog.get("processed", 0) > 0:
                if first_batch is None:
                    first_batch = prog
                last_prog = prog
    if not first_batch or not last_prog:
        print(json.dumps({"error": "no progress in PP stream"}))
        sys.exit(1)
    return {"pp_tps": round(first_batch["processed"] / first_batch["time_ms"] * 1000.0, 1),
            "pp_n": first_batch["processed"],
            "fill_tps": round(last_prog["processed"] / last_prog["time_ms"] * 1000.0, 1),
            "fill_n": last_prog["processed"]}

f1 = ppfill(FILL1)

# --- optional second fill (FILL2=0 disables: protocol is one 120k pass) ---
if FILL2 > 0:
    def fill(n_tokens):
        t = all_toks[:n_tokens] + ["\n\nContinue:"]
        last = req("/completion", {"prompt": t, "n_predict": 4,
                                   "temperature": 0, "cache_prompt": True,
                                   "id_slot": 0, "stream": False})
        tm = last["timings"]
        return {"processed": tm["prompt_n"], "cached": tm.get("cache_n", -1),
                "tps": round(tm["prompt_per_second"], 1)}, t
    f2, fill2_prompt = fill(FILL2)
else:
    f2, fill2_prompt = None, all_toks[:FILL1] + ["\n\nContinue:"]

# --- TG 1024 at production sampling (temp 1.0, seeded for lane comparability) ---
# extends the deepest fill so generation runs at deep KV fill
tg_prompt = fill2_prompt + ["\n\nThe following is a technical essay.\n\n",
                            "Write a clear technical essay on Rayleigh scattering and why the sky is blue. The essay begins:"]
tg_last = req("/completion", {"prompt": tg_prompt, "n_predict": TG_N,
                              "temperature": 1.0, "top_p": 0.95, "top_k": 20,
                              "min_p": 0.0, "seed": 42, "cache_prompt": True,
                              "id_slot": 0, "stream": False})
tg = tg_last["timings"]
if tg.get("predicted_n", 0) < 256:
    print(json.dumps({"error": f"degenerate TG: {tg.get('predicted_n')} tokens"}))
    sys.exit(1)
acc = round(tg.get("draft_n_accepted", 0) / max(tg["predicted_n"], 1), 3)
tg_depth = tg.get("cache_n", -1)

# --- repro AFTER (same fresh-slot conditions -> must match BEFORE) ---
sha_after = repro()

print(json.dumps({
    "load_s": load_s, "n_ctx": n_ctx,
    "pp_n": f1["pp_n"], "pp_tps": f1["pp_tps"],
    "fill1": {"processed": f1["fill_n"], "cached": 0, "tps": f1["fill_tps"]}, "fill2": f2,    "tg_n": tg["predicted_n"], "tg_tps": round(tg["predicted_per_second"], 1),
    "tg_depth_cached": tg_depth,
    "acc": acc,
    "repro_ok": sha_before == sha_after,
    "sha": sha_before,
}))
