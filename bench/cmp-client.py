#!/usr/bin/env python3
"""Cmp client: 2llama-config fork-vs-mainline comparison, ctx 200k.

health -> temp0-repro-BEFORE -> PP16384 + fill (one 120k pass) ->
TG512 temp-0 at 120k depth (t/s + draft acceptance + sha) ->
temp0-repro-AFTER.

Prints one JSON line on stdout; exits non-zero on failure.
"""
import hashlib
import json
import os
import sys
import time
import urllib.request

PORT = sys.argv[1] if len(sys.argv) > 1 else "8021"
BASE = f"http://127.0.0.1:{PORT}"
FILL1 = int(os.environ.get("FILL1", "120000"))
TG_N = int(os.environ.get("TG_N", "512"))
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
all_toks = req("/tokenize", {"content": filler})["tokens"]
if len(all_toks) < FILL1 + 8:
    print(json.dumps({"error": f"filler too small: {len(all_toks)} < {FILL1}"}))
    sys.exit(1)


def repro():
    last = req("/completion", {"prompt": REPRO_PROMPT, "n_predict": 256,
                               "temperature": 0, "top_k": 1, "seed": 1,
                               "cache_prompt": False, "id_slot": 0, "stream": False})
    return hashlib.sha256(last["content"].encode()).hexdigest()[:12]


sha_before = repro()


# single pass to FILL1: first prompt_progress = first-batch PP (16384), last = fill
def ppfill(n_tokens):
    t = all_toks[:n_tokens] + ["\n\nContinue:"]
    payload = {"prompt": t, "n_predict": 4,
               "temperature": 0, "top_k": 1, "cache_prompt": False, "id_slot": 0,
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

# temp-0 greedy TG at fill depth: deterministic cross-build sha + draft acceptance
tg_prompt = all_toks[:FILL1] + ["\n\nContinue:",
                                "\n\nThe following is a technical essay.\n\n",
                                "Write a clear technical essay on Rayleigh scattering and why the sky is blue. The essay begins:"]
tg_last = req("/completion", {"prompt": tg_prompt, "n_predict": TG_N,
                              "temperature": 0, "top_k": 1,
                              "cache_prompt": True, "id_slot": 0, "stream": False})
tg = tg_last["timings"]
if tg.get("predicted_n", 0) < 128:
    print(json.dumps({"error": f"degenerate TG: {tg.get('predicted_n')} tokens"}))
    sys.exit(1)
acc = round(tg.get("draft_n_accepted", 0) / max(tg["predicted_n"], 1), 3)
tg_sha = hashlib.sha256(tg_last["content"].encode()).hexdigest()[:12]

sha_after = repro()

print(json.dumps({
    "load_s": load_s, "n_ctx": n_ctx,
    "pp_n": f1["pp_n"], "pp_tps": f1["pp_tps"],
    "fill1": {"processed": f1["fill_n"], "tps": f1["fill_tps"]},
    "tg_n": tg["predicted_n"], "tg_tps": round(tg["predicted_per_second"], 1),
    "tg_depth_cached": tg.get("cache_n", -1),
    "acc": acc, "tg_sha": tg_sha,
    "repro_ok": sha_before == sha_after, "sha": sha_before,
}))
