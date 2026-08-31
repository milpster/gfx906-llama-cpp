# Next lanes to run (2026-08-31, post-E67)

fa1s-geom16 is DONE and WON: native cols-16 = 12.3 t/s vs 9.2
(cols-64 native) vs 12.5 (convert). Committed with the code.

One optional confirming lane left before the 68B pair-loader
experiment (agent-side): geometry at 250k ctx. fa1-lane-120k.sh
hardcodes C=155000, so use the direct runner:

```
cd /home/srcds/dev/uf3_rocm6.1_llama.cpp
GGML_CUDA_FATTN_PATH=force_native LANE=fa1s-geom250 BIN_DIR=$PWD/build-dflash-novega \
C=250000 TS=35,20,45 SM=layer CTV=q8_0 SPEC_TYPE=draft-dflash SPEC_N_MAX=4 \
NGRAM=0 FILL1=120000 FILL2=0 TG_N=256 EXTRA=-v ./bench/lane-dflash.sh
```

Expect ~12-12.5 (b1-native was flat vs KV-length, 9.2 -> 9.3 at
200k; convert decays slightly, 12.5 -> 11.9 over the same span).
Also verifies the compact (~238 MiB-class) reserve sizing holds at
250k on the native path. Check /tmp/opencode/lane-fa1s-geom250.json.

If it confirms: nothing else to run - the 68B pair loader is a
code+build thing, and its validation lane gets written here after
it builds.
