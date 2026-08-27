#!/usr/bin/env python3
"""Dump GGUF KV metadata relevant to memory fitting (layers, KV shape, attn types).

Usage: python3 bench/gguf-meta.py <model.gguf> [--all]
Reusable: no llama.cpp build needed, reads only the GGUF header.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "gguf-py"))
from gguf import GGUFReader  # noqa: E402


def fmt(v):
    if isinstance(v, bytes):
        return v.decode(errors="replace")
    if isinstance(v, list):
        return [fmt(x) for x in v]
    return v


def main():
    path = sys.argv[1]
    show_all = "--all" in sys.argv
    r = GGUFReader(path)
    arch = None
    kv = {}
    for f in r.fields.values():
        try:
            val = fmt(f.contents() if f.types == [0] * len(f.parts) else f.contents())
        except Exception:
            val = f"<{f.types}>"
        kv[f.name] = val
        if f.name == "general.architecture":
            arch = val
    keys = sorted(kv) if show_all else [k for k in sorted(kv) if any(
        s in k for s in ("architecture", "block_count", "head_count", "key_length",
                         "value_length", "attn", "sliding", "context", "embedding_length",
                         "expert", "feed_forward", "spec", "dflash", "window"))]
    for k in keys:
        v = kv[k]
        if isinstance(v, list) and len(v) > 24:
            print(f"{k} = [len {len(v)}] {v[:24]}...")
        else:
            print(f"{k} = {v}")
    # tensor name summary per block (one line per distinct suffix pattern)
    if show_all and arch:
        import re
        pats = {}
        for t in r.tensors:
            p = re.sub(r"blk\.(\d+)\.", "blk.N.", t.name)
            pats.setdefault(p, [0, 0])
            pats[p][0] += 1
            pats[p][1] += t.n_bytes
        for p, (n, b) in sorted(pats.items()):
            print(f"tensor {p:64s} x{n:3d} {b/2**20:10.1f} MiB")


if __name__ == "__main__":
    main()
