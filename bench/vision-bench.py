#!/usr/bin/env python3
"""Vision (mmproj) bench: send a Full HD test image, report encode+eval timings.

Usage: vision-bench.py PORT [iterations]

- Generates/reuses bench/vision-test-1080p.png (deterministic 1920x1080 pattern)
- Sends one chat completion with the image, temp 0, short output
- Prints server-side prompt eval (includes image encode) and client wall time
"""
import base64
import json
import struct
import sys
import time
import urllib.request
import zlib

PORT = sys.argv[1] if len(sys.argv) > 1 else "8015"
ITERS = int(sys.argv[2]) if len(sys.argv) > 2 else 3
HERE = "/home/srcds/dev/uf3_rocm6.1_llama.cpp/bench"
PNG = HERE + "/vision-test-1080p.png"
W, H = 1920, 1080


def gen_png():
    # raw RGB scanlines with a deterministic gradient + grid pattern
    rows = []
    for y in range(H):
        row = bytearray()
        for x in range(W):
            r = (x * 255 // W) ^ (y & 0xFF)
            g = (y * 255 // H)
            b = ((x + y) * 127 // (W + H)) | 0x40
            if x % 120 < 2 or y % 120 < 2:  # grid lines: high-contrast detail
                r, g, b = 255 - r, 255 - g, 255 - b
            row += bytes((r, g, b))
        rows.append(b"\x00" + bytes(row))
    raw = b"".join(rows)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))
    with open(PNG, "wb") as f:
        f.write(png)
    return len(png)


def main():
    import os
    if not os.path.exists(PNG):
        n = gen_png()
        print(f"generated {PNG} ({n/1024:.0f} KiB)")
    size = os.path.getsize(PNG)
    b64 = base64.b64encode(open(PNG, "rb").read()).decode()
    print(f"image: {W}x{H} png {size/1024:.0f} KiB, b64 {len(b64)/1024:.0f} KiB")

    body = {
        "messages": [{"role": "user", "content": [
            {"type": "image_url",
             "image_url": {"url": "data:image/png;base64," + b64}},
            {"type": "text", "text": "Describe this image in one short sentence."},
        ]}],
        "max_tokens": 48,
        "temperature": 0,
        "cache_prompt": False,
    }
    url = f"http://127.0.0.1:{PORT}/v1/chat/completions"
    for i in range(ITERS):
        t0 = time.time()
        req = urllib.request.Request(
            url, data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=600) as r:
            d = json.loads(r.read())
        wall = time.time() - t0
        u = d.get("usage", {})
        t = d.get("timings", {})
        pt = u.get("prompt_tokens", -1)
        ct = u.get("completion_tokens", -1)
        pm = t.get("prompt_ms", -1)
        pp_s = t.get("prompt_per_second", -1)
        gen = t.get("generation_ms", -1)
        print(f"iter{i}: wall {wall*1000:8.0f} ms | prompt_tokens {pt} "
              f"(incl. image) | prompt_eval {pm:8.0f} ms | gen {gen:6.0f} ms "
              f"({ct} tok) | pp_t/s {pp_s:.2f}")


if __name__ == "__main__":
    main()
