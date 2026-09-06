#!/usr/bin/env python3
"""Full KLD/error stats between two llama-perplexity --save-all-logits dumps.

Dump record per position (nv = 2*((n_vocab+1)/2)+4 uint16):
  [0:2] scale (f32), [2:4] min_log_prob (f32), [4:4+n_vocab] u16 entries
  log_prob[i] = scale*u[i] + min_log_prob; writer clamps the window to
  16 nats below the max logit (entries below -> 0, u step ~2.44e-4 nats).

Error metrics are over log-PROB differences = shift-normalized logit
differences (per-position softmax shift removed; this is the error that
matters for sampling). KL(base||Q) mimics the tool (base terms with
log_prob > -16 only, no renormalization) so the mean cross-checks the
perplexity tool's own number.

Usage: kld-fullstats.py BASE_dump Q_dump
"""
import struct
import sys
import numpy as np

def read_header(f, path):
    magic = f.read(8)
    assert magic == b"_logits_", f"{path}: bad magic {magic!r}"
    n_ctx, n_vocab, n_chunk = struct.unpack("<Iii", f.read(12))
    tokens = np.frombuffer(f.read(4 * n_ctx * n_chunk), dtype=np.int32)
    return n_ctx, n_vocab, n_chunk, tokens

def stats(name, vals):
    v = np.asarray(vals, dtype=np.float64)
    print(f"  {name:14s} mean={v.mean():+.6g}  median={np.median(v):+.6g}  "
          f"p95={np.percentile(v,95):+.6g}  p99={np.percentile(v,99):+.6g}  "
          f"max={v.max():+.6g}")

def main():
    base_p, q_p = sys.argv[1], sys.argv[2]
    fa, fb = open(base_p, "rb"), open(q_p, "rb")
    ca = read_header(fa, base_p); cb = read_header(fb, q_p)
    assert ca[:3] == cb[:3], f"header mismatch {ca[:3]} vs {cb[:3]}"
    n_ctx, n_vocab, n_chunk = ca[:3]
    assert np.array_equal(ca[3], cb[3]), "token streams differ"
    tokens = ca[3]
    nv = 2 * ((n_vocab + 1) // 2) + 4
    first = n_ctx // 2
    n_eval = n_ctx - 1 - first
    n_pos = n_eval * n_chunk
    print(f"n_vocab={n_vocab} n_chunk={n_chunk} n_eval_tok/chunk={n_eval} "
          f"positions={n_pos}")

    def rec(f):
        r = np.frombuffer(f.read(2 * nv), dtype=np.uint16)
        scale = r[:2].view(np.float32)[0]
        min_lp = r[2:4].view(np.float32)[0]
        return scale * r[4:4 + n_vocab].astype(np.float64) + min_lp

    kld_bq, kld_qb = [], []
    d_top1 = d_top5 = d_top1_in5 = 0
    dp_next = []
    rmse_ss = rmse_n = 0.0
    emax = 0.0
    rmse_ss_100 = rmse_n_100 = 0.0
    emax_100 = 0.0
    pos_maxerr = []

    for pos in range(n_pos):
        tgt = int(tokens[(pos // n_eval) * n_ctx + first + 1 + pos % n_eval])
        la, lb = rec(fa), rec(fb)
        pa, pb = np.exp(la), np.exp(lb)
        m = la > -16.0
        kld_bq.append(float(np.sum(pa[m] * (la[m] - lb[m]))))
        m2 = lb > -16.0
        kld_qb.append(float(np.sum(pb[m2] * (lb[m2] - la[m2]))))
        ia, ib = int(la.argmax()), int(lb.argmax())
        topa = set(np.argpartition(-la, 5)[:5].tolist())
        topb = set(np.argpartition(-lb, 5)[:5].tolist())
        d_top1 += int(ia == ib)
        d_top5 += int(topa == topb)
        d_top1_in5 += int(ia in topb)
        dp_next.append(abs(pb[tgt] - pa[tgt]))
        d = la - lb
        rmse_ss += float(np.dot(d, d)); rmse_n += d.size
        emax = max(emax, float(np.max(np.abs(d))))
        pos_maxerr.append(float(np.max(np.abs(d))))
        u100 = np.union1d(np.argpartition(-la, 100)[:100],
                          np.argpartition(-lb, 100)[:100])
        d1 = d[u100]
        rmse_ss_100 += float(np.dot(d1, d1)); rmse_n_100 += d1.size
        emax_100 = max(emax_100, float(np.max(np.abs(d1))))

    n = n_pos
    print(f"\n== KL divergence (nats per position, base=mainline Q=fork)")
    stats("KL(base||Q)", kld_bq)
    stats("KL(Q||base)", kld_qb)
    print(f"\n== agreement")
    print(f"  top-1 identical      : {d_top1 / n:.4%}")
    print(f"  top-5 sets identical : {d_top5 / n:.4%}")
    print(f"  base top-1 in Q top5 : {d_top1_in5 / n:.4%}")
    print(f"\n== next-token (ground truth) probability")
    stats("|dp_next|", dp_next)
    print(f"\n== logit error (shift-normalized = log-prob diff; u16 quant floor ~2.4e-4/entry)")
    print(f"  full vocab   : RMSE={np.sqrt(rmse_ss / rmse_n):.6g}  max|e|={emax:.6g}  "
          f"median per-pos max|e|={np.median(pos_maxerr):.6g}")
    print(f"  union top-100: RMSE={np.sqrt(rmse_ss_100 / rmse_n_100):.6g}  max|e|={emax_100:.6g}")

if __name__ == "__main__":
    main()
