#!/usr/bin/env bash
# Interleaved A/B for the fattn tile geometry: stock (build-dflash-novega,
# ncols=32 config) vs cols16 (build-cols16). Alternating invocations share
# thermal drift; per-arm mean +/- sd over N rounds decides whether the
# ~0.5% delta is real or noise.
#
# run:  N=6 ./ab-fattn-geom.sh          (~10 min; KV/TOK/ITERS overridable)
set -euo pipefail
cd "$(dirname "$0")"

N=${N:-6}
KV=${KV:-120000}
TOK=${TOK:-384}
ITERS=${ITERS:-30}

export HIP_VISIBLE_DEVICES=0 HSA_OVERRIDE_GFX_VERSION=9.0.6 HSA_XNACK=0
STOCK=/home/srcds/rocm-gfx906-xnack/lib:$PWD/../build-dflash-novega/bin:/opt/rocm-6.1.0/lib
C16=/home/srcds/rocm-gfx906-xnack/lib:$PWD/../build-cols16/bin:/opt/rocm-6.1.0/lib

run_ms() {
    LD_LIBRARY_PATH="$1" ./bench-fattn-tile "$KV" "$TOK" "$ITERS" 2>/dev/null \
        | grep -oE '[0-9]+\.[0-9]+ ms/op' | grep -oE '^[0-9.]+'
}

rm -f /tmp/fa-stock.txt /tmp/fa-cols16.txt
for i in $(seq 1 "$N"); do
    a=$(run_ms "$STOCK")
    b=$(run_ms "$C16")
    echo "round $i: stock $a ms  cols16 $b ms"
    echo "$a" >> /tmp/fa-stock.txt
    echo "$b" >> /tmp/fa-cols16.txt
done

python3 - <<'EOF'
import statistics as st
s = [float(x) for x in open('/tmp/fa-stock.txt')]
c = [float(x) for x in open('/tmp/fa-cols16.txt')]
print()
print(f"stock  : mean {st.mean(s):7.3f} ms  sd {st.stdev(s):.3f}  n {len(s)}")
print(f"cols16 : mean {st.mean(c):7.3f} ms  sd {st.stdev(c):.3f}  n {len(c)}")
d = st.mean(s) - st.mean(c)
se = (st.stdev(s)/len(s)**0.5 + st.stdev(c)/len(c)**0.5)
print(f"delta  : {d:+.3f} ms ({d/st.mean(s)*100:+.2f}%), rough SE {se:.3f} ms")
print("verdict:", "REAL (delta > 2x SE)" if abs(d) > 2*se else "NOISE-class (delta within 2x SE)")
EOF
