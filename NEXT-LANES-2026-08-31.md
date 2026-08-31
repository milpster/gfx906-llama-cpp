# Next lanes to run (2026-08-31, post-E69 - release state)

Release build: build-dflash-novega (source == HEAD 832deab2c +
docs; relinked after the E69 revert, BUILD_EXIT=0). All lane
runners point at it (lane-dflash.sh default fixed).

State of the kernel work:
- geometry (cols-16 small-Q native): IN, committed (832deab2c).
  12.3 t/s vs 9.2 pre-geometry native, fill unchanged.
- 68B pair q8_0 loader: REVERTED (E69) - tg neutral (12.2),
  same-kernel fill -2.7%. Dequant-staging line closed.

Lane pending (release verification at 250k, AUTO path): re-run
fa1s-auto250 on the final binary. Expect AUTO to stay convert
(~12.5-12.6 tg, ~228 fill, .672) as in the pre-geometry run; the
geometry change cannot affect it (AUTO picks convert, native path
untaken):

```
cd /home/srcds/dev/uf3_rocm6.1_llama.cpp
LANE=fa1s-auto250b C=250000 TS=35,20,45 SM=layer CTV=q8_0 \
SPEC_TYPE=draft-dflash SPEC_N_MAX=4 NGRAM=0 FILL1=120000 FILL2=0 \
TG_N=256 EXTRA=-v ./bench/lane-dflash.sh
```

Check /tmp/opencode/lane-fa1s-auto250b.json, sha e54019ff6b42,
repro_ok true.

Optional: native250 (fa1s-geom250) - FORCE_NATIVE at C=250000,
confirms geometry + compact reserve at 250k (expect ~12.3 flat,
b1-native was flat vs KV-length).

After that: Q x KV regression matrix of the small-Q routing
(SPEC_N_MAX 0..7 at c=155k), then push decision (gated,
dflash2:master, explicit user go).
