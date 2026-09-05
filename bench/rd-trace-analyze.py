#!/usr/bin/env python3
# rd-trace-analyze: post-process rd-trace.bin rings (see bench/rd-trace.c).
# Answers the E119.1 question for the TG campaign: during generation rounds,
# are the VIIs GPU-busy (kernel-chain compute-bound) or idle between bursts
# (pipeline handoff / latency-bound)?
# Usage: rd-trace-analyze.py TRACE.bin [--last SEC] [--t0 NS] [--t1 NS]
#        [--burst-gap MS] [--top N]
import argparse, struct, sys, collections

REC = struct.Struct('<QQQQQIB3x')  # 48 bytes, matches rec_t
K_KERNEL, K_MEMCPY, K_MEMSET, K_GRAPH, K_BUSY, K_MARKER, K_SYNC = range(7)

def load(path):
    recs = []
    with open(path, 'rb') as f:
        while True:
            b = f.read(REC.size)
            if len(b) < REC.size:
                break
            ts, stream, a0, a1, a2, shm, kind = REC.unpack(b)
            if ts == 0 or kind > K_SYNC:
                continue  # unwritten slot
            recs.append((ts, kind, stream, a0, a1, a2, shm))
    recs.sort(key=lambda r: r[0])  # ring wrap: order by timestamp, not slot
    return recs

def busy_map(recs):
    m = collections.defaultdict(list)  # card -> [(ts, pct)]
    for ts, kind, _, a0, a1, _, _ in recs:
        if kind == K_BUSY:
            m[a0].append((ts, a1))
    return m

def gap_hist(gaps_ns):
    h = collections.Counter()
    for g in gaps_ns:
        b = 0
        while (1 << b) <= g and b < 40:
            b += 1
        h[b] += 1
    return h

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('trace')
    ap.add_argument('--last', type=float, default=60.0, help='analyze last N seconds')
    ap.add_argument('--burst-gap', type=float, default=5.0, help='ms quiet gap splitting bursts')
    ap.add_argument('--top', type=int, default=15)
    args = ap.parse_args()

    recs = load(args.trace)
    if not recs:
        sys.exit('no valid records')
    t_end = recs[-1][0]
    t0 = t_end - int(args.last * 1e9)
    win = [r for r in recs if r[0] >= t0]
    span_s = (win[-1][0] - win[0][0]) / 1e9 if len(win) > 1 else 0.0

    kinds = collections.Counter(r[1] for r in win)
    print(f'window: {span_s:.1f}s, {len(win)} recs: ' +
          ', '.join(f'{k}={v}' for k, v in sorted(kinds.items())))

    kernels = [r for r in win if r[1] == K_KERNEL]
    if kernels:
        print(f'kernel launches: {len(kernels)} ({len(kernels)/max(span_s,1e-9):.0f}/s)')
        fp = collections.Counter(
            (r[3], r[4] >> 32, r[5] >> 32, r[4] & 0xffffffff, r[5] & 0xffffffff, r[6])
            for r in kernels)
        print('top grids (gx,gy,gz,bx,by,shm):')
        for fp_, n in fp.most_common(args.top):
            print(f'  {n:8d}  {fp_}')
        streams = collections.Counter(r[2] for r in kernels)
        print(f'streams: {len(streams)}, busiest share '
              f'{max(streams.values())/max(len(kernels),1)*100:.0f}%')

    cpy = [r for r in win if r[1] == K_MEMCPY]
    if cpy:
        tot = sum(r[3] for r in cpy) / 1e9
        dur = sum(r[4] for r in cpy) / 1e9
        print(f'memcpys: {len(cpy)}, {tot:.2f} GB, {dur:.2f}s blocking')

    sync = [r for r in win if r[1] == K_SYNC]
    if sync:
        tot_s = sum(r[3] for r in sync) / 1e9
        med_ms = sorted(r[3] for r in sync)[len(sync)//2] / 1e6
        print(f'sync calls: {len(sync)}, total {tot_s:.2f}s, med {med_ms:.3f}ms, '
              f'share of window {tot_s/max(span_s,1e-9)*100:.0f}%')

    bm = busy_map(win)
    for card, samples in sorted(bm.items()):
        avg = sum(p for _, p in samples) / max(len(samples), 1)
        print(f'card{card} busy: avg {avg:.0f}% over {len(samples)} samples')

    # burst segmentation on kernel launches (TG rounds = dense bursts)
    if len(kernels) > 10:
        ts = [r[0] for r in kernels]
        gap_ns = int(args.burst_gap * 1e6)
        bursts, cur = [], [ts[0]]
        for a, b in zip(ts, ts[1:]):
            if b - a > gap_ns:
                bursts.append(cur)
                cur = []
            cur.append(b)
        bursts.append(cur)
        big = [x for x in bursts if len(x) >= 8]  # drop stragglers
        if len(big) >= 3:
            durs = [(x[-1] - x[0]) / 1e6 for x in big]
            quiet = [(b[0] - a[-1]) / 1e6 for a, b in zip(big, big[1:])]
            lens = [len(x) for x in big]
            med = lambda v: sorted(v)[len(v)//2]
            print(f'bursts (>=8 launches, gap>{args.burst_gap:.0f}ms): {len(big)}')
            print(f'  launches/burst med {med(lens)}, burst span med {med(durs):.1f}ms, '
                  f'quiet between med {med(quiet):.1f}ms')
            # busy% inside vs between bursts, every sampled card
            import bisect
            for card in sorted(bm):
                s = sorted(bm[card])
                sts = [x[0] for x in s]
                def q(lo, hi):
                    i0, i1 = bisect.bisect_left(sts, lo), bisect.bisect_right(sts, hi)
                    vals = [p for _, p in s[i0:i1]]
                    return (sum(vals)/len(vals), len(vals)) if vals else (0.0, 0)
                inb, nb = [], []
                for x in big:
                    v, n = q(x[0], x[-1])
                    if n: inb.append(v)
                for a, b in zip(big, big[1:]):
                    v, n = q(a[-1], b[0])
                    if n: nb.append(v)
                if inb and nb:
                    print(f'  card{card} busy inside bursts {sum(inb)/len(inb):.0f}% '
                          f'vs quiet {sum(nb)/len(nb):.0f}%')
        hg = gap_hist([b - a for a, b in zip(ts, ts[1:])])
        print('host inter-launch gap histogram (2^n ns): ' +
              ', '.join(f'{k}:{v}' for k, v in sorted(hg.items()) if k >= 15))

if __name__ == '__main__':
    main()
