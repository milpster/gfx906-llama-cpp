---
name: qwen38-flash-next-llamacpp-perf
description: Qwen3.8 Flash Next and llama.cpp performance tuning for long-context mixed ROCm/Vulkan systems. Use when tuning Qwen3.8-Flash-Next, sparse QSA, 200k context, per_layer_token_embd or the ngram/PLE table, -lzm on-direct, mmap+mlock, CPU expert residency, MoE staging, NCMOE, tensor split, gfx906, Radeon VII, Vulkan RTX 3080, PP/TG throughput, or when deciding whether a measured bottleneck requires a llama.cpp code change.
---

# Qwen3.8 Flash Next llama.cpp Performance

## Purpose

Use this skill to tune Qwen3.8 Flash Next as a complete system rather than as
an isolated kernel benchmark. It joins four constraints that must remain
consistent:

1. architecture-specific QSA and recurrent execution;
2. MoE weight residency and host-to-device staging;
3. per-device VRAM fit at long context;
4. llama.cpp scheduler, loader, and backend behavior.

Apply it to the reference topology when relevant:

```text
ROCm0: Radeon VII / gfx906, 16 GiB
Vulkan1: RTX 3080 Laptop, 8 GiB
ROCm1: Radeon VII / gfx906, 16 GiB
device order: rocm0,vulkan1,rocm1
```

Do not transfer a placement or optimization to another quant, context, GPU
order, llama.cpp commit, or backend version without repeating the fit and
performance gates.

## Hard invariants

### The ngram table stays on backing storage

`per_layer_token_embd.weight` is the 26.8 GiB, 1.6G-element IQ4_NL ngram/PLE
table. It must remain file-backed on HDD/NVMe. Never mlock it, pre-populate it,
copy it into anonymous RAM, or place it in VRAM.

Use:

```text
-lzm on-direct
```

The direct lazy reader must fetch only the selected rows with `pread`, sorted
and deduplicated where supported. A healthy idle process should show almost no
resident memory for this mapping. The reference observation was 4 KiB.

This table is not part of the CPU expert residency budget. If it becomes
resident, a 62 GiB machine cannot also hold the locked expert set and normal
process overhead without reclaim or swap pressure.

### CPU and GPU expert residency

- CPU-assigned experts must be resident and locked before performance is
  accepted.
- GPU-assigned experts must remain in their intended device buffers.
- Do not infer residency from `VmLck` alone. With `MLOCK_ONFAULT`, a range can
  be marked locked while its pages remain absent.
- Compare `/proc/<pid>/status`, `/proc/<pid>/smaps_rollup`, process I/O counters,
  and the model placement map.
- Device expert placement and compute placement must agree. A tensor override
  that moves weights without moving the operation can add per-token
  cross-device copies and collapse throughput while preserving correct output.

### Runtime configuration

For the established 200k lane, preserve unless a trial explicitly isolates
one variable:

```text
FA: on
target KV: q8_0 K / q4_0 V
devices: rocm0,vulkan1,rocm1
split mode: layer
pipeline parallel: off
QSA sparse FA: enabled
QSA chunk: 1024 baseline
lazy mode: on-direct
```

Never disable flash attention to manufacture a fit. Do not silently reduce
context, ubatch, KV precision, or the number of selected GPUs.

## Relevant implementation map

Start with these paths and symbols:

```text
src/models/qwen4exp.cpp
  build_qsa_top_k
  build_inp_ple
  QSA generated-mask and sparse-bias construction

src/llama-lazy-reader.h
  sparse pread reader for the ngram/PLE table

src/llama-model-loader.cpp
  init_mappings
  load_all_data
  lazy tensor exclusion from mlock
  placement and selective lock ranges

src/llama-model.cpp
  load_tensors
  mapped versus allocated host buffers
  multi-buffer host allocation and mlock ownership

src/llama-mmap.cpp
  llama_mlock::impl::raw_lock
  lock_range / lock_ranges
  MLOCK_ONFAULT behavior

ggml/src/ggml-backend.cpp
  scheduler backend selection
  split input copies
  weight-affinity and offload_op decisions

ggml/src/ggml-cuda/ggml-cuda.cu
  host buffer allocation
  GGML_MOE_CPU_COMPUTE_MIN_BATCH routing
  ROCm host staging and copy behavior

ggml/src/ggml-vulkan/ggml-vulkan.cpp
  host-resident MUL_MAT_ID streaming
  staging ring and full-copy chunks
  Vulkan allocation limits

run-qwen38f-fast.sh
  production arguments and env-gated trial knobs
```

Use `journal/JOURNAL-2026-09-26.md` and
`journal/JOURNAL-2026-09-28.md` as the primary decision record. Do not repeat a
rejected experiment without identifying what changed.

## Tuning workflow

### 1. Record a reproducible baseline

Capture:

```text
git commit and build directory
model filename and quant composition
device order
CTX, UB, TS, NCMOE, OT and MG
FA and QSA mode/chunk
target KV types
lazy mode and load mode
pipeline setting
threads and batch threads
speculative configuration
```

Before launching:

1. Confirm no stale server owns the port.
2. Confirm the binary and shared libraries come from the same build.
3. Record system memory, swap, and per-device VRAM.
4. Use a unique log path.

### 2. Separate fit, residency, and performance

Treat these as three independent gates.

**Fit gate**

- Server reaches listening state.
- `/slots` reports the requested `n_ctx_slot`.
- All three intended GPUs have allocations.
- No hidden fallback, reduced context, or backend disappearance occurred.

**Residency gate**

- CPU expert bytes match locked bytes.
- Expert mappings remain resident across a prompt.
- The ngram table remains sparse and file-backed.
- Prompt disk reads match sparse ngram rows, not tens of GiB of expert weights.

**Performance gate**

- A bounded first ubatch completes.
- A second same-server run distinguishes cold faults from steady state.
- PP, TG, scheduler wait, disk reads, GPU utilization, and swap are recorded.

Never call a fit-only trial a performance win.

### 3. Establish placement truth

Enable the placement dump when needed and account separately for:

```text
model weights
target KV
recurrent state
compute buffers
host staging
draft/MTP buffers
```

Total free VRAM is not interchangeable across devices. The limiting device is
the one that cannot satisfy its next contiguous allocation, not necessarily
the device showing the highest total use.

For the reference 200k lane, a typical safe placement used:

```text
TS=75,1,24
NCMOE=28
UB=5696
```

This is a baseline, not a universal optimum.

### 4. Tune expert residency before kernels

The host expert set is approximately 43-47 GiB depending on placement. A wide
PP pass can touch about 45.7 GB of expert data. If these pages are absent,
kernel tuning is irrelevant.

Check in this order:

1. Is the expert range selected for locking?
2. Does `Locked` match the selected byte count?
3. Does a first PP pass read tens of GiB from storage?
4. Does the second pass become much faster?
5. Are pages lost to reclaim between passes?

On Linux, `mlock2(MLOCK_ONFAULT)` avoids load-time populate storms but defers
the first-touch cost. Plain bulk `mlock()` can wedge in `__mm_populate` when
reclaim races a 40+ GiB cursor. Do not reintroduce bulk population as a default.

When `GGML_RANGE_SPLIT_MB` creates a multi-buffer, the wrapper has no base
pointer. Lock each unique child allocation referenced by the context tensors;
never pass the wrapper to `llama_mlock` as one contiguous buffer.

### 5. Protect the ngram direct-read path

For every residency or loader change, verify all of the following:

```text
per_layer_token_embd.weight remains lazy
idle residency remains near zero
the direct reader serves selected rows through pread
no full-table mlock or memcpy appears
output remains equivalent
```

If a load-mode change allocates the ngram table as a real host buffer, reject
the change immediately even if startup succeeds.

### 6. Tune VRAM placement conservatively

Change one variable per startup probe:

```text
NCMOE frontier
then tensor split
then one coherent tensor override
then ubatch
```

Prefer `NCMOE` and coarse layer placement before regex overrides. When testing
an override, verify actual model-buffer movement.

Known reference constraints:

- NCMOE=28 is proven at 200k; 27 is the next fit frontier.
- NCMOE=26 previously exhausted ROCm0.
- Vulkan can show several GiB free while still failing an expert-bearing graph
  because it requests one 3.2-3.7 GiB compute allocation.
- Moving expert tensors alone previously collapsed TG to 0.07-0.19 t/s due to
  cross-backend execution and fencing.
- Use spare Vulkan memory first for compute-coherent dense/attention layers,
  not arbitrary expert tensors.

Stop at the first allocation failure, throughput collapse, or unexpected graph
split increase.

### 7. Diagnose the active bottleneck

Use the signature table:

| Observation | Likely bottleneck | Next evidence |
|---|---|---|
| Tens of GiB disk reads during PP | Expert page faults | `smaps_rollup`, `read_bytes`, second pass |
| Ngram mapping grows resident | Lazy-path regression | tensor mapping, `-lzm on-direct`, reader trace |
| GPUs idle, one copy thread blocked | Split input or staging copy | scheduler copy trace, gdb stack |
| Vulkan busy, PP scales with staging knobs | MoE host-to-device streaming | staging slots/chunk timing |
| PP near 74-83 t/s | True CPU MoE compute | backend assignment and `offload_op` trace |
| PP unchanged cold to warm | Compute/copy bottleneck, not faults | GPU utilization and split timings |
| Large free VRAM but allocation fails | Contiguous allocation cliff | requested allocation size and device heap |
| Correct output but TG near zero | Cross-device expert movement | node backend versus weight buffer |

Do not diagnose a deadlock from an idle HSA waiter thread. Keep the request
alive, capture the active compute thread, and correlate it with GPU utilization
and process I/O.

### 8. Decide whether llama.cpp code should change

Change code only after a controlled trial proves a structural bottleneck that
launcher knobs cannot solve.

Good code-change targets:

- eliminate an oversized temporary or lifetime;
- preserve sparse QSA bias/mask representation;
- keep ngram reads sparse and direct;
- align expert weight and operation backends;
- remove per-tensor synchronization from a measured hot copy path;
- correct buffer ownership, such as split multi-buffer mlock;
- expose env-gated diagnostics for a specific hypothesis.

Bad code-change targets:

- speculative fallbacks for unobserved failures;
- permanent logging in hot loops;
- broad scheduler rewrites before backend assignment is measured;
- making the ngram table resident;
- disabling FA, reducing context, or degrading KV precision to hide a fit bug.

Keep experimental behavior env-gated and default-safe. Remove temporary traces
after collecting the evidence unless they form a small reusable diagnostic.

### 9. Validate a code improvement

Required gates:

1. Build `llama-server` with the production build directory.
2. Run diagnostics when the language server has valid compile flags; otherwise
   record the LSP limitation and rely on the authoritative CMake build.
3. Reach health at the requested 200k context.
4. Confirm all three GPUs and expected per-device memory.
5. Confirm CPU expert `Locked` bytes and sparse ngram residency.
6. Run a tiny output-equivalence smoke.
7. Run one bounded PP ubatch.
8. Run a second same-server ubatch only if the first is viable.
9. Run full PP16384 only after PP5696 clears the performance gate.
10. Record TG and output hash when the change can affect scheduling or numerics.

Abort a lane early when PP5696 is already clearly below the retained baseline.
Do not spend a full PP16384 run proving an obvious loss.

## QSA and 200k context rules

The indexed QSA path must avoid materializing full
`[n_kv, n_tokens, n_stream]` F32 bias tensors. A valid generated-mask
`mask_col/mask_nvis` pair must retain per-block bias selection.

Reference 200k settings:

```text
LLAMA_QSA_SPARSE_FA=1
LLAMA_QSA_CHUNK=1024
CTX=204800
CTK=q8_0
CTV=q4_0
UB=5696
```

Chunking trades graph fanout for peak allocation. Before increasing the chunk,
calculate the ROCm0 temporary growth and preserve allocation margin. A chunk
that fits startup can still regress scheduler copies or kernel selection.

## Benchmark discipline

For each accepted candidate record:

```text
date and commit
full command and environment
load time
n_ctx_slot
model/KV/recurrent/compute buffers per device
peak VRAM and free VRAM
VmRSS, VmLck, Locked, VmSwap
process read_bytes delta
PP token count and t/s
TG token count and t/s
output hash/equivalence
graph splits and copy count
cold versus warm classification
```

Use the existing benchmark client and logs rather than disposable scripts.
Keep trials bounded and print heartbeats for operations longer than 30 seconds.
After aborting a load, confirm that the server process and GPU allocations are
gone before starting another trial.

## Stop rules

Stop and journal the result when any of these occurs:

- PP5696 is already below the retained baseline;
- experts are not locked or reread from storage;
- the ngram table becomes resident;
- any intended GPU disappears;
- Vulkan requests an impossible contiguous allocation;
- output changes without an understood numerical cause;
- two materially different fixes fail to improve the same bottleneck.

The journal entry must distinguish measured facts, leading hypotheses,
rejected paths, unfinished leads, and the exact clean starting point for the
next session.

## Result template

```markdown
## Qwen3.8 Flash Next trial

- Commit/build:
- Model/quant:
- Goal:
- Configuration:
- Placement and VRAM:
- Host residency:
- Ngram/PLE table residency and reads:
- PP cold/warm:
- TG:
- Output check:
- Bottleneck attribution:
- Verdict: keep / reject / unfinished
- Evidence logs:
- Next smallest discriminator:
```
