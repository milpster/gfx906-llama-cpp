# Master ledger: gfx906 rig + Flash-Next lane (through 2026-09-27)

Everything tried on this rig (2x Radeon VII gfx906 + RTX 3080 Laptop,
ROCm 6.1 fork `~/dev/uf3_rocm6.1_llama.cpp`, build-rcfix noomp), what
helped, what did not, what is open, what is dead, and every upstream
item we know. Sources: journal/, bench/trials.md, bench/FINDINGS.md,
README "What did not work", session records. Session-scoped handoff:
`journal/HANDOFF-2026-09-27-q38fast-lane.md`.

Current production: Swift-1.5-Qwen3.8-Flash-Next 20k lane = TG 10.89 /
PP 242 / sha `3cc4e0d1d0dc` (plain decode, PPFLAG off, noomp t8 p0,
NCMOE=27 TS=70,10,20 RANGESPLIT=2048). 27B reference lane: README.

=====================================================================
1. HELPED (landed, in production)
=====================================================================

Fork core vs upstream (banked, README E140 naked pair):
+37% prefill, +16% 120k deep fill, 250k ctx on 40 GB, DFlash2 +43% TG
(27B lane), KLD ~5e-4 / same-top 99.14%.

Components:
- wave64 kernel tables (MMQ tiles Q6_K I=64, top-k, fattn dispatch;
  occupancy 1->2 waves) -> +20% PP
- draft head mirror (LLAMA_DFLASH_MIRROR_OUTPUT=1 + --spec-draft-device)
  -> draft rounds -42%, TG +11% @120k
- pipeline parallelism on/off switch + safe fallback + draft-ctx
  exclusion (eaman patch store adoption)
- tight fits: f16-K/q8_0-V KV, fattn path selector, frugal compute
  buffers (4.7x smaller), HIP graph robustness
- robustness ports from mx-llama.cpp (fattn-vec stride, pipeline drain,
  HIP graph exec reinstantiation) - bit-exact
- checkpoint rewind (#26004 + #28302): re-prefill 455 s -> <1 s
- MoE MMQ OOB fix (host-side padding) - PPL tie, perf-neutral
- lane-gated upstream syncs (last: 0924 merge 7887b8887)

Flash-Next PP arc (137 -> 248.4 era peak, now 242 at prod UB):
- PLE on-direct preads (-lzm on-direct) -> 185.5
- fenced pinned staging ring -> 212.5
- chunked full-tensor expert staging (E147.6 + GGML_MOE_FULLCOPY_CHUNK)
  -> 248.4
- GGML_MOE_CPU_COMPUTE_MIN_BATCH=128 (rocm rejects host-expert compute
  at PP batches; REQUIRED for the PP win)
- GGML_RANGE_SPLIT_MB range cap (0920-sync regression fix)

Flash-Next TG arc (this session):
- plain decode promotion (SPEC=none): killed the 6-10 t/s wobble,
  spec machinery was the cause; 9.8-10.3 stable
- PPFLAG=off on no-draft lane: PP 158.8 -> 233.2 (flag fallback state
  cost ~47% PP without a draft)
- GGML_OPENMP=OFF (native pool), t8 poll0: TG 10.0 -> 10.89 (+6-11%;
  the 72% libgomp barrier share converted)
- residency escape hatch documented: NCMOE=21 TS=56,6,38 RANGESPLIT=
  1024 -> TG 11.88 / PP 201 (not default; user kept 242 point)

27B lane, earlier:
- #28118 spec ckpts on-device: TG 10.2 -> ~12 full mode
- #29274 NVIDIA 4-row rm_id: opt-in, TG neutral-to-positive

=====================================================================
2. TRIED AND DEAD (measured, never re-run)
=====================================================================

Flash-Next lane, this session:
- spec/MTP decode (Flash): net-negative. verify(4) ~3.5x plain cost,
  acceptance 0.42-0.67, CPU-expert cost scales with distinct experts
  touched; also the TG wobble source
- expert cache 48 slots (LLAMA_ARG_MOE_EXPERT_CACHE): 2.50 t/s = 4x
  REGRESSION despite healthy 52.9% hit-rate; hits move expert matmul
  into gfx906 batch-1 MMQ (worst regime) + ~182 MB/step insert traffic
- THREADS=11 under native pool: 9.61 (OMP-era value does not transfer)
- POLL=50/100: neutral-worse
- pinned-bounce D2H copies (GGML_CUDA_PINNED_D2H, implemented+gated
  off): 10.34 vs 10.46 = neutral; per-copy ~0.45 ms is stream-sync
  WAIT (queued GPU work), not pageable staging
- mid-frontier residency NCMOE=24: 10.48 - worse than both endpoints;
  placement topology dominates layer count (frontier non-monotonic)
- quant path for PP (probe-closed, Qwen3-0.6B vehicle on rocm0):
  Q4_0 cost/byte = 0.86x IQ4_XS (NOT cheap class); IQ4_XS == Q8_0 per
  pass at half the bytes - already near-optimal at its size class;
  no helpful type near 4.25 bpw; stock Q4_0/Q3_K_L downloads and any
  composed imatrix mix price <= +5% PP best case
- MUL_MAT_ID kernel work: PP at silicon (96.9% cycles in optimal
  tiles J=64 fb=0, dp4a ~41% issue); decode batch-1 reads only routed
  slices (~21 MB/layer) - kernel is not the wall in either regime

Earlier eras (README / FINDINGS):
- MMQ inner-loop restructures, 5 variants: ~41% issue ceiling structural
- fattn scheduling/geometry probes: -0.5 to -5.8% (compiler schedule
  is a local optimum)
- draft n_max=5: 6-row verify kernel-shape cliff, -28% TG
- K quantization beyond q8_0-V: -2.6 t/s
- native q8_0-K/q4_0-V fattn tile as default: slower at every depth
  (16k -3%, 160k fill -15%, 160k TG -9%); kept as certified fallback
- ts rebalance / drafter relocation sweeps: decode is overhead-bound,
  not bandwidth-bound
- checkpoint sparsify: neutral; checkpoint off: breaks prompt restore
- WY-chunked GDN prefill (software tiles): x0.5 - gfx906 has no matrix
  units, latency-bound at 2.6% FP32 peak
- GDN chain-shortening family: wall shares too small (7.6% fill, 2% TG)
- 27B Q5_K class removal: modeled +3.8%, delivered 0.0% - attribution
  is an upper bound, only a lane A/B decides (STANDING LESSON)
- transfer-queue overlap probe (#28414-adjacent): 222 vs 248.4 -
  in-order queue caps device overlap
- #27851 tiled k-quant CPU mulmat, true-CPU mode: 74 vs 248 t/s

=====================================================================
3. CLOSED BY ARITHMETIC (impossible on this rig, no run needed)
=====================================================================

Model facts: GGUF 91.0 GiB = experts 60.94 (43 layers x 1.363 GiB) +
PLE n-gram tables 26.84 (disk-resident by -lzm on-direct) + 3.19 other.
Rig: ~40 GB usable VRAM, 62 GB RAM (57 avail), PCIe Gen3 x8 6 GB/s.

- full GPU-resident experts: 61 GiB > 40 GB VRAM
- PLE tables in RAM: needs 88 GiB > 62 GB
- per-token expert streaming to a device: ~700-900 MB/token over
  6 GB/s = ~115 ms - link wall
- Q4_K_S/M, Q3_K_XL, Q4_K_L, Q5/Q6/Q8 expert swaps: streamed-expert
  RAM 68-104 GiB - dead (skill units model + sizes from the HF repo)
- #27861-style cache widening to the Flash lane: mooted by the cache
  measurement above (same mechanism, same wall)

=====================================================================
4. OPEN (designed or deferred, with ceilings) - reordered 2026-09-27
=====================================================================

P0 - Qwen4exp sparse-QSA audit (#28734): RESOLVED ALREADY-PRESENT.
  src/llama-graph.cpp:3259 passes kq_mask_top_k + top_k->ne[0] as
  n_kv_max (the patched form). The dense 0-form at :3338 is a different,
  non-QSA builder. BUT the deeper #28734 levers are NOT present:
  src/llama-memory-hybrid-idx.cpp runs block selection HOST-side per
  step (std::fill + pointer writes into blk_cells, then set_input_qsa
  feeds cell_blk/blk_cells/blk_pos/bias as graph inputs) and caches
  RAW indexer keys, re-pooling + rope-ing at read time (file comment
  line 54). That is exactly the per-token host work + H2D/G2D traffic
  (#28734 measured 3.1 MB/tok H2D + 13.2 MB/tok G2G at depth) that
  E148b/c/d remove.
P1 - E148 mini-project (only if depth workloads matter): E148b
  graph-side block-granular top-k, E148c persistent pooled block-key
  cache (update dirty blocks only), E148d device-resident membership.
  Measure set_input_qsa cost first (attribute the ROCm1 1-node 3-4 ms
  receipt splits). Win zone is the 250k 27B lane, not 20k Flash.
P2 - rocprof trace: separate QSA depth cost from MoE protocol cost.
P3 - cross-stream/event MoE handoff: mine GenerelSchwerz moe-cache fork
  (--backend-sampling, --decode-overlap, --decode-boundary-overlap,
  --moe-early-router; CUDA/cache-oriented, do not merge, mine the
  lifecycle/graph-capture solutions) and the AMD moe-hotcache fork
  (gfx1200 but the ROCm lessons transfer: capture-safe per-token
  counters must live in captured kernels, adaptive policy on a host
  thread, side-stream creation copies - syncing the capture stream
  breaks capture, slot quarantine, atomic pointer publication; their
  slow-link GPU deemed useless as cache tier = our topology lesson).
P4 - expert prefetch: fold into P3 (thecodacus fable5/prefetch-experts
  branch as comparison: pinned mmap + second-stream prefetch + ring;
  +64% PP on THEIR machine, ours already has ring+chunked staging;
  3 portable commits preserved as format-patches - check if they avoid
  a sync our ring still pays).
P5 - RTX 3080 expert-cache experiment: below everything else.

Also parked: 60k-ctx KV experiment (user stopped). Facts gathered:
vulkan compute pp buffer scales with ctx (3.6 GiB @20k -> 8.47 GiB
@60k at UB 5712 -> OOM on the 8 GB card); UB knob added to launcher
(UB=2048 should fit, untested - r2 aborted by user). Launcher now has
CTX/CTK/CTV/KVO/UB knobs (defaults unchanged, uncommitted).

Minor: llama-bench segfault in this build (use llama-cli -lv 5 timing);
Q6_K small-shape tile pathology (fork tables, tiny models only); nvidia
clock lock offered/never run (~2%); lookup-spec arm never run (gaming
confound + adverse economics).

Upstream watchlist additions: #29428 CUDA TOP_K heuristic (we measured
top-k worth <= 0.4 t/s here), #29326 radix TOP_K ~20% PP on NVIDIA
(not ours to relearn), #29355 speculative draft reuse (Flash MTP
economics already bad). #28734 sparse256 CUDA-MMA whitelist (DKQ=256,
DV=256, ncols1=1, ncols2=8): do NOT port to gfx906 - no Ampere matrix
path; the graph-level QSA sparsity is the transferable part.

=====================================================================
5. UPSTREAM (ggml-org/llama.cpp), every item we tracked
=====================================================================

Adopted (in fork):
- #26004 + #28302 checkpoint rewind
- #28118 spec ckpts on-device (+ eviction fix) - promoted to fast lane
- #27841 wave64 GCN row (converges with our vega tables)
- #29274 NVIDIA 4-row rm_id (opt-in)
- mx-llama.cpp: 3 robustness ports (bit-exact); GDN chunk + q8_1 cache
  carried but perf-neutral here
- eaman patch store: pipeline-parallel controls + fit refinements

Rejected after measurement/triage:
- #27173 draft-chain perf: launch overhead TG-neutral; took the output
  head mirror instead
- #21698 q8_0 loader remap: +1.0% noise
- #23685 packed Q8_1 MMVQ: no gain on target path; parked as reference
- #24546 MoE expert-width N-tiles: 96.9% of cycles already J=64 fb=0
- #28313 ROCm top-k resolve: top-k worth <= 0.4 t/s
- #28178 small-D2D copy kernel: no per-layer-per-token small copies
  on our path
- #25635 fattn XOR swizzle: -0.5 to -5.8%
- #28102 fattn tuning (gfx1201): wrong arch, same local-optimum result
- #27694 probabilistic drafter: sha-breaking rejection-sampling verify
- #28305 static sampling subgraph: dflash2 walks lattice on CPU
- #28390 drafter meta-backend: VRAM saving only under -sm tensor
- #28391 default spec config: perf-neutral; re-verify additive flag
  semantics at next sync
- #28333 zero MTP carrier: MTP-family; dflash carrier separate
- #27692 speculative prefill: lossy prefill; watch
- #21170 ROCm multi-GPU IMA fix: hand-applied for crash tests
- #21849 per-arch MMQ tiles: converges with our table; drop our gate
  only after it merges
- #26592 hipCUB top-k: no hot sort on our path
- #29191 streaming load-mode: UMA-only + 24G swap requirement
- #28414 prefetch-experts-slots: ring already frees host timeline;
  in-order queue caps overlap (222 vs 248.4)
- #27851 tiled k-quant CPU mulmat: not bit-exact; Q6_K GEMV
  regression; true-CPU mode loses to vk streaming
- #29353 GDN chunked kernel (hip): wall share too small on flash lane
- #27861 expert cache widening: same n==1 gate; +31% was CUDA with
  GPU-resident experts - our cache arm measured 4x regression
- #29280 vulkan descriptor-set reuse: applied clean, sha-clean,
  TG neutral -> reverted to zero diff (PLE precedent)
- #26631 MUL_MAT_ID -1 skip: 7 commits, reference only

Riding at next gated sync:
- #27530 K/V + recurrent state cleanup after failed restores
  (correctness only, merged 2026-09-26 upstream)
- re-verify #28391 additive flag semantics
- #21849: drop our vega gate if it merges

=====================================================================
6. Standing lessons (do not relearn)
=====================================================================

- Attribution is an upper bound; only a lane A/B decides (Q5_K 0.0%).
- An expert's cost is dominated by where it COMPUTES, not where it is
  stored: RAM+CPU vec_dot beats gfx906 batch-1 MMQ on this rig.
- -ts ratios are weak hints in this fork's capacity-driven walk; the
  largest-slot device fills to ~16.3 GB; per-device runtime reserves
  (KV 2.78 rocm0, ~3.1 compute rocm1, 3.6 compute pp + display vulkan)
  and RANGESPLIT=1024 are the real fit constraints.
- A blank line after a `\` continuation severs the launcher env chain.
- Never pass the same env var twice in one prefix.
- Costs/byte constants are per model family: re-derive with a probe
  before believing any units model on a new model.
