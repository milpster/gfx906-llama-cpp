# Handoff: Swift-1.5-Qwen3.8-Flash-Next fast-lane campaign (2026-09-27)

Written at campaign close. Operational state, full lever ledger, and the
remaining path. Companion record: `journal/JOURNAL-2026-09-26.md` (dated
sections, 09-26/09-27) and `bench/trials.md` (every row).

## Objective

Own the perf envelope of the Swift-1.5-Qwen3.8-Flash-Next 20k fast lane
(gfx906 x2 + 3080, ROCm 6.1 fork at `~/dev/uf3_rocm6.1_llama.cpp`,
build-rcfix): root-cause TG underperformance, map every lever, land what
wins, document the rest. Arc: wobble -> plain promotion -> noomp ->
bottleneck anatomy -> residency frontier -> quant-path closure.
**Campaign is CLOSED**: default lane = TG 10.89 / PP 242, everything else
measured and banked.

## Constraints

- "no delegate!!" - never spawn subagents. Commits only on explicit
  request, `Assisted-by: Sisyphus`, never push/PR. Never touch/stage
  `run-qwen38f-200k.sh` (user's, always `M` in tree).
- Round economy ("fewer test rounds"), one variable per arm,
  `PP_ABORT=0` only (GPU hang), `pgrep -x llama-server` guard +
  `pkill -9` + sleep 5 around every launch.
- Journal = `journal/JOURNAL-2026-09-26.md` (append-only dated sections).
  Trials = `bench/trials.md` (commits include ONLY it, not raw logs).
- Env-prefix collision lesson: never pass one var twice in a prefix
  (made mislabeled row q38plain-pp-r1). Launcher env-chain: a blank line
  after a `\` continuation severs the whole env prefix (caused a
  "no ROCm-capable device" false alarm).
- `rtk grep -h` conflicts with real grep -h (use the Grep tool).
  llama-bench segfaults in this build after backend enumeration - use
  `llama-cli -f <prompt> -n 16 -st -lv 5` timing lines instead.

## Work State

### Completed (all committed, tree clean except user's file)

- Commits this arc: `e2d0c8057` plain-decode default, `4da47f36d` bench
  rows, `ac345e5f2` journal, `2eb48f94c` cuda pinned-bounce+allocdbg
  (env-gated off), `2da1c32be` launcher knobs, `20a6edd30`/`dc2593534`
  frontier+ledger, `c92dba67b`/`45134e9d1` decision correction (242
  point kept).
- Production lane: `run-qwen38f-fast.sh` defaults = SPEC=none PPFLAG=off
  THREADS=8 POLL=0 OT=on NCMOE=27 TS=70,10,20 RANGESPLIT=2048 MG=0,
  noomp binaries (GGML_OPENMP:BOOL=OFF; OMP restore cmd in journal).
  TG 10.89 / PP 242 / sha gate `3cc4e0d1d0dc`.
- Fast-TG hatch (env only): `NCMOE=21 TS=56,6,38 RANGESPLIT=1024` ->
  TG 11.88 / PP 201, same sha. User chose the 242 point as default.
- MODEL CENSUS (fact of record): GGUF = 91.0 GiB = experts 60.94
  (43 layers x 1.363 GiB) + PLE n-gram tables 26.84
  (per_layer_token_embd, disk-resident via -lzm on-direct) + 3.19 other.
  Walls: VRAM ~40 GB usable, RAM 62 GB (57 avail), PCIe 6 GB/s. Full GPU
  residency, PLE-in-RAM (needs 88), per-token device streaming
  (~115 ms) all impossible by arithmetic.

### Closed levers (measured, do not re-try)

1. Spec decode: net-negative (verify(4) ~3.5x cost vs acceptance ~0.5);
   caused the TG wobble.
2. PPFLAG on no-draft lane: -47% PP.
3. OMP=OFF: WON (+6-11% TG, in production); POLL=50 neutral-worse;
   THREADS=11 regresses under native pool (9.61).
4. Expert cache 48 slots: 4x TG regression despite 52.9% hit-rate
   (gfx906 batch-1 MMQ + ~182 MB/step inserts).
5. Residency frontier: 10 GPU layers = TG +9.1% / PP -17%; mid-points
   regress (placement topology dominates); frontier mapped.
6. Pinned-bounce copies (`GGML_CUDA_PINNED_D2H`): implemented, NEUTRAL
   (10.34 vs 10.46) - the ~0.45 ms/copy is stream-sync WAIT, not
   pageable staging.
7. Quant path for PP: closed by local probe (Qwen3-0.6B vehicle on
   rocm0): Q4_0 cost/byte = 0.86x IQ4_XS (not cheap-class); IQ4_XS
   matches Q8_0 per pass at half the bytes - already near-optimal for
   its size class. No helpful type near 4.25 bpw; composed imatrix mix
   has nothing to compose toward; best case <= +5% PP. Q6_K small-shape
   tile pathology noted (fork tables; real-lane Q6_K fine per E91).
8. MUL_MAT_ID: PP at silicon (96.9% cycles in optimal tiles, dp4a
   ~41%); decode batch-1 reads only routed slices (~21 MB/layer) -
   kernel is not the wall anywhere.

### Bottleneck anatomy (final, instrumented)

- Decode ~92-100 ms/step: CPU splits ~77 ms (= ~40 ms protocol: ~35
  serialized GPU-CPU layer round-trips x ~70 stream-sync'd copies +
  ~36 ms RAM streaming ~750-900 MB/token at 20-25 GB/s) + ~31 ms
  serialized GPU-side staging (GPU compute ~2-3 ms - GPUs idle).
  PP 242 compute-bound at MMQ ceiling.
- Loader/fit knowledge (12-attempt fit war): walk is capacity-driven -
  largest-ts device fills to ~16.3 GB; slots map nominally (slot0 ->
  rocm0, 1 -> vulkan, 2 -> rocm1); runtime reservations rocm0 = KV
  2.78 + ~1 compute, rocm1 = ~3.1 compute, vulkan = 3.6 compute pp +
  display (=> vulkan weights <= ~1.4 GiB); real single-range ceiling
  below 2048 -> RANGESPLIT=1024. `GGML_CUDA_ALLOC_DEBUG=1` (committed)
  prints per-range device free.

## Key Decisions

- User's calls: plain+PPFLAG=off default; 242-PP residency point over
  11.88-TG point; no-requant standing rule (quant path now closed by
  measurement anyway).
- Designed-but-unbuilt (the ONLY remaining path past 10.89/242):
  cross-stream/event input copies (attacks the ~40 ms wait;
  scheduler-level rewrite) and expert prefetch pipelining (attacks the
  ~36 ms stream); combined ceiling ~16-18 t/s. Deferred by design -
  large surgery, do with fresh context.
- rocprof link/CPU/MMQ attribution on the real lane: never run; best
  case now prices at <= +5% PP - low priority.
- #27530 = robustness fix (failed-restore K/V cleanup), no perf
  content; "sync-class" items are correctness rides.

## Files & Symbols

- `run-qwen38f-fast.sh` - all knobs (OT/NCMOE/TS/MG/RANGESPLIT/SPEC/
  PPFLAG/THREADS/POLL), header = dated decision log incl. the escape
  hatch.
- `journal/JOURNAL-2026-09-26.md` - complete record; final sections:
  residency frontier, pinned-bounce, MUL_MAT_ID analysis, default
  correction, per-type MMQ probe.
- `bench/trials.md` - all rows (q38plain-pp r1-r3, cache48,
  noomp-{plain,poll50,t11}, gpuexp r19/r20/pp, pind2h pair).
- Evidence: `bench/logs/q38speed/tg-harness/{server,results}-*`
  (cache48, noomp arms, splitiming-noomp, gpuexp*-r1..r20, pind2h*),
  `bench/logs/noomp-pp-r1.log`.
- Fork code touched: `ggml/src/ggml-cuda/ggml-cuda.cu` (allocdbg ~950,
  pinned_bounce_copy ~800); split print
  `ggml/src/ggml-backend.cpp` ~2053 (`GGML_SCHED_SPLIT_TIMING=1`).
- HF: `ukisai/Swift-1.5-Qwen3.8-Flash-Next-GGUF` (full quant zoo;
  Q4_0 93.7 GiB, Q3_K_L 86.8 - both now known-not-worth-it).
- Tensor dump regenerable: `llama-gguf <file> r n` (~5 min warm cache).

## Next Moves (if ever resumed)

1. Cross-stream/event copy rewrite + prefetch pipelining - fresh
   session, ~16-18 t/s ceiling.
2. Optional: rocprof attribution pass (<= +5% best case).
3. Next upstream gated sync: #27530 rides along (correctness only).

## Open Questions

- (none pending user input) - all decisions taken; remaining items are
  explicitly deferred-by-design.
