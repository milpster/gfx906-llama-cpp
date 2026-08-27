#!/usr/bin/env python3
"""Manual placement fitter for the 3-GPU (ROCm0/Vulkan1/ROCm1) layer-split rig.

Implements the dual-gpu-context-balancing skill math offline: reads exact tensor
sizes from the target GGUF, simulates -sm layer placement from --tensor-split,
adds KV/recurrent/compute/drafter/mmproj per device, and solves max -c per split
at a chosen min per-device margin.

Constants calibrated from measured logs (sources in comments); override not
needed for routine use. Run BEFORE a fitting trial to pick -ts/-c; verify the
prediction against the run's own -lv 4 memory breakdown table.

Usage:
  python3 bench/manual-fit.py <model.gguf> [--ts 40,20,40] [--margin 250]
                              [--ctx N] [--grid] [--dflash/--mtp]
                              [--drafter path.gguf] [--mmproj MiB]
"""
import argparse
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "gguf-py"))
from gguf import GGUFReader  # noqa: E402

MiB = 1024 * 1024

# Device geometry (calib/tests/fixtures/reftext_210k.log breakdown table):
#   total / free-before-load per device
DEVS = [
    {"name": "ROCm0", "total": 16368, "free": 16012},
    {"name": "Vulkan1", "total": 8192, "free": 7612},
    {"name": "ROCm1", "total": 16368, "free": 16030},
]

# Per-token KV bytes for one full-attention layer, F16: 4 kv-heads * 256 * 2(KV) * 2B
KV_PER_ATTN_LAYER_F16 = 4 * 256 * 2 * 2
# Compute buffers at -b 16384 -ub 384 (calib table: 245/253/245 MiB)
COMPUTE_MIB = [245, 253, 245]
# Fixed "context" overhead not scaling with C, folded from the calib table:
# context row 7426 MiB total @ q8 KV 210k (=6554) -> ~870 MiB fixed (recurrent
# state of GDN layers + KV padding + misc). Scales 2x KV part for f16 not applied
# here: recurrent state is per-seq fixed. Split proportional to layer share.
CONTEXT_FIXED_MIB_PER_LAYER = 870.0 / 64.0
# DFlash2 drafter (z-lab Q4_K_M): weights all on ROCm0 via
# --spec-draft-override-tensor '.*=ROCm0' -ngld 99; draft KV flat (window 2048)
# + draft compute estimated on ROCm0 (verify vs run log).
DRAFT_W_MIB_ROCM0 = 1090
DRAFT_KVCOMPUTE_MIB_ROCM0 = 230  # estimate; verify from -lv 4 table
# mmproj-F16 vision tower ~927 MB, lands with the mtmd context on dev 0
MMPROJ_MIB_DEV0 = 930


def load_model_tensors(path):
    r = GGUFReader(path)
    blocks = {}  # il -> {"attn": bool, "bytes": int}
    other = {}   # name -> bytes (token_embd, output, norms)
    for t in r.tensors:
        n = t.name
        if n.startswith("blk."):
            il = int(n.split(".")[1])
            b = blocks.setdefault(il, {"attn": False, "gdn": False, "bytes": 0})
            b["bytes"] += t.n_bytes
            if ".attn_k." in n:
                b["attn"] = True
            if ".ssm_" in n or ".attn_qkv." in n:
                b["gdn"] = True
        else:
            other[n] = other.get(n, 0) + t.n_bytes
    return blocks, other


def place(blocks, other, ts, use_nextn):
    """Simulate -sm layer placement. Returns per-device weights + attn/gdn layer lists.

    Skill formula: N = min(n_gpu_layers, n_layer_all+1) positions; position p goes
    to the first device whose cumulative normalized split exceeds p/N.
    token_embd rides with position 0 (dev 0); output head with the last (dev -1).
    nextn (highest il) is dropped entirely when use_nextn=False (draft-dflash).
    """
    ts = [x / sum(ts) for x in ts]
    layers = sorted(il for il, b in blocks.items() if use_nextn or il < max(blocks))
    n_main = len([il for il in layers if not blocks[il].get("nextn", False)]) if False else len(layers)
    # main blocks = all il except the nextn one (il == max); nextn excluded when unused
    nextn_il = max(blocks)
    main = [il for il in layers if il != nextn_il]
    pos_layers = main if not use_nextn else main + [nextn_il]
    N = len(pos_layers) + 1  # + output head position
    cum = []
    s = 0.0
    for x in ts:
        s += x
        cum.append(s)

    def dev_of_pos(p):
        f = (p + 1) / N
        for j, c in enumerate(cum[:-1]):
            if f <= c + 1e-9:
                return j
        return len(ts) - 1

    W = [0] * len(ts)
    attn_layers = [[] for _ in ts]
    gdn_layers = [[] for _ in ts]
    emb_bytes = sum(v for k, v in other.items() if "token_embd" in k or "token_embd" in k)
    out_bytes = sum(v for k, v in other.items() if k.startswith("output"))
    norm_bytes = sum(v for k, v in other.items() if "norm" in k and not k.startswith("output"))
    d0 = dev_of_pos(0)
    dl = dev_of_pos(N - 1)
    W[d0] += emb_bytes
    W[dl] += out_bytes + norm_bytes
    for p, il in enumerate(pos_layers):
        j = dev_of_pos(p)
        W[j] += blocks[il]["bytes"]
        if blocks[il]["attn"]:
            attn_layers[j].append(il)
        elif blocks[il]["gdn"]:
            gdn_layers[j].append(il)
    return W, attn_layers, gdn_layers


def margins(blocks, other, ts, C, margin, use_nextn=True, mmproj=True):
    W, attn, gdn = place(blocks, other, ts, use_nextn)
    res = []
    for j, d in enumerate(DEVS):
        used = W[j] / MiB
        used += COMPUTE_MIB[j]
        used += len(attn[j]) * KV_PER_ATTN_LAYER_F16 * C / MiB
        used += (len(attn[j]) + len(gdn[j])) * CONTEXT_FIXED_MIB_PER_LAYER
        if j == 0:
            if use_nextn is False:  # dflash drafter mode
                used += DRAFT_W_MIB_ROCM0 + DRAFT_KVCOMPUTE_MIB_ROCM0
            if mmproj:
                used += MMPROJ_MIB_DEV0
        res.append({"dev": d["name"], "model_MiB": W[j] / MiB, "used": used,
                    "free_after": d["free"] - used, "attn_layers": len(attn[j]),
                    "gdn_layers": len(gdn[j])})
    return res


def solve_ctx(blocks, other, ts, margin, **kw):
    lo, hi = 4096, 262144
    if min(m["free_after"] for m in margins(blocks, other, ts, lo, margin, **kw)) < margin:
        return None
    while hi - lo > 256:
        mid = (lo + hi) // 2 // 256 * 256
        if min(m["free_after"] for m in margins(blocks, other, ts, mid, margin, **kw)) >= margin:
            lo = mid
        else:
            hi = mid
    return lo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--ts", default="40,20,40")
    ap.add_argument("--margin", type=int, default=250)
    ap.add_argument("--ctx", type=int, default=0)
    ap.add_argument("--grid", action="store_true")
    ap.add_argument("--mtp", action="store_true",
                    help="keep nextn/MTP tensors (default: drop them, draft-dflash)")
    ap.add_argument("--no-mmproj", action="store_true")
    args = ap.parse_args()

    blocks, other = load_model_tensors(args.model)
    nextn_il = max(blocks)
    attn_all = [il for il, b in blocks.items() if b["attn"]]
    gdn_all = [il for il, b in blocks.items() if b["gdn"]]
    print(f"blocks: {len(blocks)} (nextn il={nextn_il}, dropped={not args.mtp})")
    print(f"attn layers: {len(attn_all)} {attn_all}")
    print(f"gdn layers: {len(gdn_all)}")
    print(f"total file weights: {sum(b['bytes'] for b in blocks.values()) / MiB:.0f} MiB + "
          f"{sum(other.values()) / MiB:.0f} MiB emb/out")
    use_nextn = args.mtp

    def show(ts, C=None):
        s = solve_ctx(blocks, other, ts, args.margin, use_nextn=use_nextn,
                      mmproj=not args.no_mmproj) if not C else C
        ms = margins(blocks, other, ts, s or 0, args.margin, use_nextn=use_nextn,
                     mmproj=not args.no_mmproj)
        tag = "solved-max" if not C else "requested"
        print(f"\n-ts {','.join(map(str, ts))} margin>={args.margin} ctx={s} ({tag}):")
        for m in ms:
            print(f"  {m['dev']:8s} model {m['model_MiB']:7.0f} attn {m['attn_layers']:2d} "
                  f"gdn {m['gdn_layers']:2d} used {m['used']:7.0f} free-after {m['free_after']:6.0f}")

    if args.grid:
        for ts in [(40, 20, 40), (42, 21, 37), (39, 21, 40), (38, 21, 41), (41, 21, 38),
                   (42, 22, 36), (37, 22, 41), (40, 21, 39), (43, 20, 37), (38, 22, 40),
                   (41, 20, 39), (39, 22, 39), (44, 19, 37)]:
            show(list(ts))
    else:
        show(list(map(float, args.ts.split(","))), args.ctx or None)


if __name__ == "__main__":
    main()
