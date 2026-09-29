# Handoff 2026-09-27 (evening): UB campaign + long-context adaptation

Continuation of `HANDOFF-2026-09-27-q38fast-lane.md` (perf campaign close-out) and
`LEDGER-gfx906-rig.md` (master ledger). Everything below happened after those docs.
Model: Swift-1.5-Qwen3.8-Flash-Next IQ4_XS (91.0 GiB = 60.94 experts + 26.84 PLE
disk-resident + 3.19 other). Rig: rocm0+rocm1 (Radeon VII 16 GB) + vulkan1 (RTX 3080
8 GB, ~0.9 GB display), 62 GB RAM, build-rcfix noomp binaries, sha `3cc4e0d1d0dc`.

## 1. Current best configs (measured, smoke-passed)

| lane | env | result |
|---|---|---|
| 20k production (committed defaults) | `UB=5696` (now launcher default), SPEC=none PPFLAG=off THREADS=8 POLL=0 OT=on NCMOE=27 TS=70,10,20 RANGESPLIT=2048 MG=0 | PP 242-244, TG ~10-11, sha-gated |
| 60k / UB=5696 (r5, smoke-passed) | `NCMOE=28 TS=75,1,24 CTX=61440 CTK=q8_0 CTV=q8_0 UB=5696 EXTRA_ARGS='-lv 4 --n-outputs-max 1024'` | GPU weights 17.66 GiB (8262/8500/895), compute 5831/1785/6604, KV 765 MiB; margins rocm0 1.7 GiB / rocm1 1.0 GiB; RAM avail 50/62; RSS ~13 GiB |
| 200k / UB=2048 (designed, NOT yet run clean) | `NCMOE=28 TS=75,1,24 CTX=204800 CTK=q8_0 CTV=q4_0 UB=2048` | r7 launch aborted by user (UB ruling); expected compute ~5.7 GiB/card |

KV quant ruling from user: **K=q8_0, V=q4_0 mandatory** ("KV at q8/q4!!!").

## 2. UB campaign (closed): champion 5696

Gate mechanics (read from `bench/bench-client.py` before trusting any number):
- PP gate prompt = 16393 tokens, `cache_prompt:false`, measures the FIRST ubatch only
  (`prompt_progress` per-ubatch, `pp_n == UB` in every arm).
- Every arm = one full ubatch, identical geometry, NO undersized tail. The 17,136
  (5712x3) resonance theory therefore does NOT apply to our gate; 5712's old win was
  an off-grid point riding the same ridge.
- User ruling: **only UB divisible by 64 permissible**. 5712 = 89.25x64 -> invalid.

Full 64-grid ladder (ab-bench PP, single warm run each, sha `3cc4e0d1d0dc` unless noted):

| UB | pp_tps | note |
|---|---|---|
| 4096 | 191.2 | |
| 4608 | 191.3 | |
| 5120 | 224.9 | |
| 5376 | 231.9 | |
| 5504 | 231.0 | |
| 5568 | 232.7 | |
| 5632 | 221.5 | first run VOID: sha `785250dfbe73` anomaly; redo clean, dip real |
| 5648 | 234.6 | off-grid (+16), kept for reference |
| 5696 | 242.4 / 215.2* / 244.0 | *wobble-contaminated run (tg 3.1); CHAMPION = 89x64 |
| 5712 | 242.0 | off-grid, historical reference, disqualified |
| 5760 | 236.4 / 242.2 | statistically tied, never ahead |
| 5776 | 238.4 | off-grid |
| 5824 | 168.3 | crater |
| 5888 | 214.8 | dip |
| 6016 | OOM | vulkan reserve fail |
| 6144 | OOM | vulkan compute 4.40 GiB demand + 0.47 staging fail |
| 6400 | 234.5 | fits while 6144 doesn't - buffer shape quantizes |
| 6656 | 230.2 | |
| 7168 | OOM | 3.97 GiB demand fail (SMALLER than 6144's - non-monotone) |

Lessons: cliffs are graph/split/buffer-shape quantization, not kernel geometry
(adjacent grid points differ by 68 t/s); vulkan fit is UB-shape-dependent and
non-monotone. Method: coarse ~512-stride first, then 64-grid zero-in, NO repeat
runs (user: "you dont need to measure it twice"). Launcher default flipped
5712 -> 5696 (uncommitted with the other knob edits).

## 3. Long-context: the walls, measured

- **Vulkan compute wall (60k)**: UB=5712 @ CTX=61440 -> vulkan compute pp buffer
  8.47 GiB > 8 GB card (server-kv60k-q8-r1.log). UB=2048 fits.
- **Runtime-margin wall**: trial r1 (ts=75,1,24, NCMOE=27): startup HEALTHY, then
  runtime `ROCm error: out of memory` on first 16k PP. rocm0 = 9562 weights +
  5831 compute + 573 KV = 15,966/16,368 MiB -> 400 MiB margin is NOT enough.
  Safe margin >= ~1 GiB. Rule: startup fit is capacity evidence only.
- **Vulkan per-layer workspace (UB=5696)**: 895 MiB weights -> 1785 MiB compute;
  2692 MiB weights -> 7724 MiB compute (r2, dead). Vulkan must stay starved
  (middle ts ~1%) at high UB.
- **NCMOE stops binding downward**: NCMOE=31 placed IDENTICALLY to 32 (4363/8500/895).
  The walk's own margin rule caps; NCMOE=28 re-binds (rocm0 -> 8262).
- **RAM ceiling**: NCMOE=32 -> 43.6 GiB CPU experts -> RAM "too full" (user halt).
  NCMOE=28 -> 38.2 GiB -> healthy (50-55 GiB available, RSS ~13 GiB, mapped weights
  live in buff/cache). User directive: RAM is a first-class constraint; smoke tests
  only until tenancy settled.
- **KV is tiny on this arch (correction of old belief)**: only 12 full-attn layers
  (rest is sparse QSA). 60k q8/q8 = 765 MiB total; 200k q8/q4 = 1950 MiB
  (1300/325/325). KV was never the VRAM constraint. My earlier "4.18 GiB at 60k"
  arithmetic assumed 43 KV layers - WRONG, do not reuse.
- **Compute-buffer slope (the UB ceiling equation)**: rocm0 compute(UB=5696) =
  1613 MiB fixed + 70.3 KiB/token x ctx. Measured: 5831 @ 60k, 15,912 @ 200k
  (cudaMalloc fail, r6 log). Both terms ~linear in UB. Therefore:
  - UB ceiling at 200k ~ 2200 -> use 2048 (64-aligned)
  - UB=5696 maxes out at ~64k ctx
  - ctx x UB ~ 460M tok^2 const on this rig
  - 5696 @ 200k is impossible without code changes (15.9 GiB/card demand)

## 4. 200k status (user target: 200k, UB=5696 demanded, then "only winning UB")

CONFLICT: 5696 and 200k are mutually exclusive by measured arithmetic (section 3).
Three routes offered, user decision PENDING:
1. 60k @ 5696 (r5 config, alive and smoke-passed)
2. 200k @ 2048 (r7 designed; launch aborted by user mid-wait; not yet run clean)
3. Fork-level buffer project: attack the attention workspace itself (chunked/trimmed
   causal mask, extend frugal-buffer machinery to attn view tensors) to move the
   UB ceiling at 200k. Real effort, uncertain payoff.

Reference point: user's 27B 200k launcher (`run-qwen38f-200k.sh`, read-only, never
touch/stage) solved the same wall with `-b 512 -ub 128`, f16/f16 KV mandatory,
`-ncmoe 31 -ts 66,10,24 -sm layer -fit off`, `-lm mmap -lzm on` (no mlock).

## 5. Flag survey findings (llama-server --help of this build)

- `--n-outputs-max N`: parsed (2 log mentions) but did NOT shrink rocm1's compute
  reserve at our shape - dud for placement. (Logits intermediate theory: the pp
  graph reserve doesn't honor it.)
- `-fit on -fitt MiB0,MiB1,...`: fork's margin-aware fitter. ABORTS with
  "n_gpu_layers already set by user to -2" because launcher hardcodes `-ngl all`.
  Needs ngl/ts/ncmoe all unset + `-fit on` override. When ts/ncmoe dropped, default
  walk gave vulkan 3.7 GiB -> its compute explodes -> dead anyway. Fitter route
  requires launcher surgery (add NGL/FIT knobs); manual placement is the proven path.
- `-sm {none,layer,row,tensor,cost}`: row/tensor exist; campaign settled layer;
  untested at 60k/200k (reserve tier).
- `-dt` defrag, `--moe-expert-cache*` (measured dead: 2.50 t/s, 52.9% hits),
  `-cram`, `--kv-unified-per-slot`: reviewed, not levers for us.
- EXTRA_ARGS passthrough added to launcher (uncommitted): scalars get word-split
  (`${EXTRA_ARGS:-}` unquoted). Gotcha that burned once: quoted-array expansion of
  a scalar env var passes "-lv 4" as ONE argument -> "invalid argument".

## 6. Pipeline parallel (asked twice, answered)

- `--pipeline-parallel off` is ALREADY production (PPFLAG default off).
- ON was measured early: **-47% PP**. Mechanism: PP-on overlaps device compute
  across stages; our pipeline is host-bound (RAM expert streaming + serialized
  staging, GPUs ~90% idle), so overlap buys nothing and the pipeline buffers +
  finer splits cost. PP-on is used by the 27B MTP cost-split lane (different
  bottleneck). Closed lever.
- Pending offer: drop the 3080 as a pipeline stage entirely
  (`EXTRA_ARGS='--device rocm0,rocm1'`, TS=75,25, NCMOE=28): lose ~1.2 GiB
  placement, gain one fewer backend hop + two fewer split boundaries per pass.
  Smoke trial designed, NOT run - awaiting user go.

## 7. Constraints & conduct (standing + new this arc)

- no subagents ("no delegate!!"); commits only on request, `Assisted-by: Sisyphus`;
  never push/PR; never touch/stage `run-qwen38f-200k.sh`.
- `pkill -9 -x llama-server; sleep 5-8` between launches; `PP_ABORT=0` only;
  evidence to `bench/logs/`; one variable per arm (skill discipline) though forced
  combos (ctx+UB+CTV) happened during 200k push.
- NO benchmarks until tenancy settled - smoke tests only (tiny completion + RAM
  readout). Smoke = `curl /completion {"prompt":"The quick brown fox","n_predict":8}`,
  print timings (NOTE: response key is `predicted_n`/`predicted_ms`, not eval_n).
- Round economy: no repeat arms, coarse-then-fine, user hates wasted loads.
- KV: q8_0/q4_0. UB: 64-aligned only, 5696 champion at <=64k.

## 8. Launcher state (run-qwen38f-fast.sh, uncommitted diff)

Knobs (all with production defaults): SPEC/PPFLAG/THREADS/POLL (committed earlier)
+ NEW: CTX (20480), CTK/CTV (f16), KVO (on; off -> -nkvo), UB (**5696** now),
EXTRA_ARGS (passthrough, appended last, overrides possible via last-wins).
NCMOE= empty drops -ncmoe; TS= empty drops -ts (lines 60/68).
Hardcoded: `-fit off -ngl all --device rocm0,vulkan1,rocm1 -sm layer -lm mmap+mlock
-lzm on-direct -fa on` and `--pipeline-parallel ${PPFLAG:-off}`.

## 9. Evidence index (this arc)

- UB ladder arms: `bench/logs/ub-*.log` + ab-bench JSON lines (in shell history +
  trials missing - ADD trials.md rows when journaling)
- 60k: `bench/logs/q38speed/tg-harness/server-kv60k-q8-r1.log` (8.47 GiB vulkan),
  `server-kv60k-q8-ub2k-r2.log` (UB=2048 fit), `server-kv60k-5696-ts75124-r1.log`
  (runtime OOM corpse + first -lv 4 breakdown), `server-kv60k-5696-ts70525-r2.log`
  (vulkan 7.7 GiB), `server-kv60k-5696-ncmoe32-r3.log`, `...-ncmoe31-r4.log`
  (identical placement proof), `...-nom1024-r5.log` (BEST 60k config)
- 200k: `server-kv200k-fit-r6.log` (fitter abort + default-walk placement + 15.9
  GiB rocm0 demand + KV q8/q4 1950 MiB)
- Flag survey dump: `/tmp/opencode/srv-help.txt` (754 lines, may be gone on reboot;
  regenerate: `llama-server --help` with LD_LIBRARY_PATH)
- Depth sweep at 60k: NEVER completed (aborted twice). Method documented in
  HANDOFF-2026-09-27-q38fast-lane.md section "Depth sweep method".

## 10. Immediate next moves (on user go)

1. Resolve the route decision: 60k@5696 bank / 200k@2048 clean run / fork buffer
   project / vulkan-drop smoke.
2. Journal this arc (journal/JOURNAL-2026-09-26.md append) + trials.md rows for UB
   ladder + 60k/200k trials; both still un-journaled.
3. Offer commit: launcher diff (UB 5696 default, EXTRA_ARGS, CTX/CTK/CTV/KVO/UB
   knobs) + journal md files (LEDGER, both HANDOFFs). HEAD = 45134e9d1; tree also
   has user's always-M `run-qwen38f-200k.sh` (leave alone).
4. Whenever benchmarks un-freeze: PP gate on r5 config, then depth sweep, then
   60k-side UB mini-sweep (2048..2300) if route 2 chosen.
