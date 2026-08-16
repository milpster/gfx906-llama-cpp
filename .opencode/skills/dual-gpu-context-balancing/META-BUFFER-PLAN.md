# Plan: fix meta backend multi-buffer abort (enables -sm tensor)

VERDICT (2026-08-16, after execution): **KILLED - not a bug worth fixing
for this model.** Findings below supersede the plan.

## What actually happened

- The "multi buffers are not supported" abort from the first attempt was
  never reproduced: both observed crashes (meta.cpp:1576 and :1520) were
  plain OOM from splits that over-assigned the small devices. With a
  fit-able split (-ts 45,20,35) tensor mode STARTS AND LISTENS.
- With 3 devices the model runs but produces garbage ("////////" for any
  prompt) and pp is 132 tok/s (4x SLOWER than layer mode).
  Cause: qwen35 has only 4 KV heads. A 3-way tensor split misaligns the
  head->device mapping; the 20% VK1 slice gets a fractional head.
- 2 devices (clean 2+2 head split) cannot hold the weights.

## Conclusion

- The multi-buffer limitation is real but was NOT the blocker.
- The blocker is model topology (4 KV heads) + 3 unequal GPUs.
- Even if it ran correctly, measured pp 132 with PCIe-staged copies
  (no ROCm<->Vulkan P2P) suggests tensor mode would lose to layer mode's
  333 on this rig regardless.
- Models with 8+ KV heads on matched GPUs could still benefit from the
  multi-buffer fix; the plan below is kept for that scenario only.

## Original plan (kept for reference)

Goal: let `-sm tensor` (all GPUs work on every matmul in parallel) run on the
ROCm+Vulkan rig, breaking the 66-layer serial-sum pp ceiling (~333 tok/s).

## Root cause (verified in code)

Crash: `ggml-backend-meta.cpp:1154` in `init_tensor_impl`:
`multi buffers are not supported by the meta backend` (upstream #22197).

Chain:
1. `-sm tensor` wraps every weight tensor in a *meta* buffer with one
   segment per device (`llama-model.cpp` tensor-split path).
2. Each segment points at a per-device buffer allocated by
   `ggml_backend_alloc_ctx_tensors_from_buft` (`ggml-alloc.c:1185-1224`).
3. When a device's assigned tensors do NOT fit into one physical
   allocation, the allocator returns a *multi-buffer* (wrapper over
   several real buffers) - `ggml-alloc.c:1223`.
4. On this rig (memory-tight by design), that is the norm -> every
   segment buffer is multi-buffer -> meta aborts on the first tensor.

So tensor split is not fundamentally incompatible; the meta backend just
refuses buffers that wrap >1 allocation.

## Fix options

### Option A (preferred): unwrap multi-buffers in meta

In `ggml_backend_meta_buffer_init_tensor_impl` (meta.cpp ~line 1137):
- When `simple_buf` is multi-buffer, do not abort.
- A multi-buffer exposes its children via its context
  (`ggml-backend.cpp:669+`, `ggml_backend_multi_buffer_context`).
- The tensor's per-device segment (`t_ij`) is allocated inside ONE child.
  Find it by matching the tensor's data range (or by walking
  `alloc_tensor_range` bookkeeping in ggml-alloc.c - it knows which
  tensors landed in which physical buffer).
- Needs a small accessor added to ggml-backend.cpp:
  `ggml_backend_multi_buffer_get_buffers(buffer, &n)` (trivial, context
  is right there).
- Watch: `view_src` handling at meta.cpp:1167+ must unwrap the same way
  for views (qwen35 uses views on output/embd).
- Watch: `set_usage`/`clear`/`free` paths already handle multi buffers
  elsewhere; meta only needs the *lookup*, not ownership.

Estimated: ~60-100 lines, all in meta + a 5-line accessor.

### Option B (fallback): force single-buffer per device at alloc

In `alloc_tensor_range` (ggml-alloc.c), when the caller is the tensor
split loader, cap `max_size` at SIZE_MAX so one physical buffer per
device is always attempted; if that fails (true OOM), fall back to
option A behavior anyway. Less clean: tight devices may genuinely need
fragmented buffers, and forcing one allocation can fail where A succeeds.

## Risks / open questions

1. Cross-backend compute: after buffers are fixed, ggml_backend_sched
   must still route partial results between ROCm and Vulkan devices.
   No ROCm<->Vulkan P2P -> copies stage through host over PCIe.
   This may eat the parallelism win (the reason this was ranked
   "uncertain payoff"). Mitigation: give each device a -ts fraction
   that minimizes boundary exchanges; measure.
2. MTP/nextn tensors in tensor mode are untested on this fork
   (the `llm_arch_supports_sm_tensor` gate passes for qwen35, but the
   draft context must also fit).
3. KV cache in tensor mode is split across devices (per -ts); the q8
   tile kernel reads local segments only - should be transparent, but
   verify dispatch conditions still hold for split K/V tensors
   (n_batch_fa alignment per segment).
4. Upstream #22197 may already have a fix in flight - check before
   writing code to avoid divergence.

## Validation plan (kill criteria included)

1. Reproduce: `-sm tensor -ts 33,33,33 -c 130000` (small ctx) ->
   expect the abort. Save log.
2. Apply option A; rebuild ggml only; same command must reach listening.
3. Correctness: same prompts + seeds vs `-sm layer`; compare outputs
   token-for-token (greedy, temp 0) and perplexity on a fixed file.
4. Bench: pp 5k/30k-fill, tg 1024. Compare vs layer-mode numbers
   (333 / ~300 / 18).
   KILL if pp <= 350 (gain < ~5% for this complexity) or tg drops >10%.
5. Only then: refit ctx ceiling in tensor mode (KV layout differs;
   all previous fits are invalid for -sm tensor).

## Payoff estimate

Best case: pp approaches sum-of-slowest-matmul instead of
sum-of-all-66-layers -> rough ceiling 450-550 tok/s if host-staged
copies do not dominate. Realistic (PCIe staging): 350-420.
Worst case: no gain, revert, keep layer mode. Either way the #22197
class of crash gets fixed for all tensor-mode users.
