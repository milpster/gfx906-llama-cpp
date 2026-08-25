# Eaman patch integration - 2026-08-24

Branch: `eaman-rs` (base `sync/upstream-2026-08-08` fork line, HEAD `a3fbc9321`).
Source: https://store.piffa.net/lm/bug/ (author: eaman). Goal per user: incorporate
all Eaman changes into the fork, fix launcher paths to use this repo's build,
rebuild, measure baseline vs patched (PP = first 16384-token batch, TG = 1024
output tokens), validate output correctness, push to `gfx906` remote.

## What was applied

`latest_rs_cumulative_8144f31.patch` (79K, 2026-08-23) = Eaman production line +
experimental rs line. Applied with `git apply --3way` on top of the fork. The fork
already carried the a3b1eff-era subset (commit `165fc79cb`), so the effective new
content is the delta between the two generations:

- Refined MTP fit: joint target+draft fit via `common_fit_extra_model`
  (draft context fitted together with target in `common/common.cpp`), replacing
  the older server-side standalone estimate + single refinement pass.
- Recurrent-state rollback (`rs` experimental): startup-pinned speculative
  checkpoints for recurrent/hybrid models. New/changed:
  `llama-memory-recurrent.*`, `llama-memory-hybrid*`, `llama-memory.h`,
  `llama-ext.h`, `llama-graph.cpp`, `models/minimax-m3.cpp`,
  `tests/test-recurrent-state-rollback.cpp`, `server-common.*`,
  `tools/server/tests/utils.py`.
- `--hip-fa-force-vec on|off` (default on): op-level flag
  (`ggml_flash_attn_ext_get_force_vec`, plumbed via `ggml.h`/`ggml.c`,
  `llama-cparams.h`) gating VEC dispatch for quantized-KV flash attention.
- Per-device fixed-layout fit updated to upstream's newer `fit.cpp`
  (`n_ctx_min_total`, alignment `256 * n_streams`).

Result: commit `a9a901421`, 29 files, +898/-156.

## Conflict resolutions (7 files, hand triage)

- `common/arg.cpp`, `common/common.cpp`, `common/common.h`,
  `src/llama-context.cpp`, `tools/server/server-context.cpp`: ours-side was the
  older Eaman snapshot; kept theirs (new joint-fit + rs + force-vec). No
  fork-specific content lost (fork additions like `--cost-attn-weight` live
  outside the conflict hunks and are untouched).
- `common/fit.cpp`: kept theirs (newer implementation of the same per-device
  fit feature the fork had from a3b1eff).
- `ggml/src/ggml-cuda/fattn.cu`: hand merge. Fork q8_0 tile kernels
  (`ggml_cuda_fattn_tile_q8_0_native` / `_v_`) keep priority; VEC return is now
  gated by `ggml_flash_attn_ext_get_force_vec(dst)` instead of unconditional.
  Tile check runs even when the flag is off, so `--hip-fa-force-vec off` falls
  back to stock dispatch, never around our kernels.

## Environment findings (2026-08-24)

1. Production launcher was broken since 2026-08-20: it pointed at
   `clean_rocm6.1_llama.cpp/build-vega20-sync`, a botched rebuild containing
   gfx900-only code objects (missing `-DAMDGPU_TARGETS=gfx906`). With
   `HSA_OVERRIDE_GFX_VERSION=9.0.6` the runtime rejects those objects
   ("ROCm error: invalid device function" in rms_norm_mul warmup).
2. System ROCm userspace was upgraded to 6.4.4 (rocm-core 6.4, hip-runtime
   6.4.43484, hsa-rocr 1.15). /opt also holds 7.2.4. The launcher's
   LD_LIBRARY_PATH pins 6.1 + custom gfx906 rocBLAS and still works.
   Builds must pin `-DCMAKE_HIP_COMPILER=/opt/rocm-6.1.0/lib/llvm/bin/clang`
   (CMake 4.2 rejects the hipcc wrapper).
3. Launcher path fixes: `--chat-template-file` and binary now resolve via
   `SCRIPT_DIR` (old tree `rocm6.1_llama.cpp` was renamed to
   `uf2_rocm6.1_llama.cpp`; template path was dead, server refused to start).
   Binary now `$SCRIPT_DIR/build-vega20/bin/llama-server` (Aug-18 gfx906
   build = the binary the 2026-08-17/18 calibration actually measured).
4. Baseline GPU state verified: HIP 0,1 = both Radeon VII (gfx906
   sramecc+:xnack-), APU excluded. Not thermal: 36-41 C between runs.

## Baseline (before eaman-rs binary)

Binary: this repo `build-vega20/bin/llama-server` (build 10543-ish, Aug 18,
gfx906) run via production `llama-start-q6v.sh` (Q6_K_XL, -c 210000, mixed KV
f16 K / q8_0 V, -ts 40,20,40, -sm layer, spec draft-mtp+ngram-mod n-max 10,
pipeline off, nextn on ROCm0). Harness: `bench/bench-client.py` port 8009,
`TG_N=1024` (new knob added 2026-08-24; default 256 unchanged).

| metric | value |
|---|---|
| PP first-batch (16007-token first progress event) | 325.4 tok/s |
| TG 1024 greedy, fresh KV | 9.7 tok/s |
| draft acceptance | 0.669 acc/tok |
| fitted n_ctx | 210176 |
| greedy sha (sky-blue prompt) | 27901297b31a |

Note: historical trials rows showing TG ~20-22 used spec=2 plain MTP with the
Q8_0 model; the production ngram-mod+MTP n=10 combo drafts much deeper and
measures ~9.7 at fresh KV. Same-metric comparisons in this effort use the
production config only.

## Build (eaman-rs)

Fresh dir `build-vega20-eaman` (never overwrote `build-vega20`, the frozen
baseline binary). Working recipe (ROCm 6.1 fully pinned; see Knowledge log for
why each pin exists):

```
ROCM_PATH=/opt/rocm-6.1.0 cmake -S . -B build-vega20-eaman \
    -DCMAKE_BUILD_TYPE=Release \
    -DGGML_HIP=ON -DAMDGPU_TARGETS=gfx906 -DGPU_TARGETS=gfx906 \
    -DGGML_HIP_GRAPHS=ON -DGGML_HIP_NO_VMM=ON -DGGML_CUDA_FORCE_MMQ=ON \
    -DGGML_LTO=OFF -DGGML_VULKAN=ON \
    -DCMAKE_HIP_FLAGS="-ffast-math -fno-math-errno" \
    -DCMAKE_EXE_LINKER_FLAGS="-L/opt/rocm-6.1.0/lib -L/home/srcds/rocm-gfx906-xnack/lib" \
    -DCMAKE_SHARED_LINKER_FLAGS="-L/opt/rocm-6.1.0/lib -L/home/srcds/rocm-gfx906-xnack/lib" \
    -DCMAKE_HIP_COMPILER=/opt/rocm-6.1.0/lib/llvm/bin/clang
cmake --build build-vega20-eaman --target llama-server llama-bench -j16
```

## Knowledge log (chronological)

- K1. `/opt` ROCm tree inventory (verified 2026-08-24):
  `/opt/rocm` = **ROCm 7.15.0 full toolchain** (clang 23.0.0git, default
  rocm-path and default include source); `/opt/rocm-6.1.0` = 6.1.0-82 (our
  pinned stack); `/opt/rocm-6.4.4` = mislabeled second copy of 6.1.0-82;
  `/opt/rocm-7.2.4` = rocBLAS Tensile kernel drop only (`lib/rocblas/library`,
  156 gfx906-xnack hsaco/dat files, no compiler, no host librocblas).
- K2. System dpkg ROCm userspace is 6.4.4 (rocm-core 6.4, hip-runtime 6.4),
  but production never touches it: launcher LD_LIBRARY_PATH pins
  rocm-gfx906-xnack + /opt/rocm-6.1.0/lib first.
- K3. CMake 4.2 rejects the hipcc wrapper as CMAKE_HIP_COMPILER ("use Clang
  directly") -> must pass `/opt/rocm-6.1.0/lib/llvm/bin/clang`.
- K4. ggml-hip CMakeLists reads `$ENV{ROCM_PATH}` for includes/prefix. Neither
  `-DCMAKE_HIP_FLAGS=--rocm-path=...` nor `HIP_PATH` fixes the include path;
  only `ROCM_PATH=/opt/rocm-6.1.0` in the environment does. Symptom when
  wrong: `/opt/rocm/include/hip/...` leaks in and 6.1 clang fails on
  `__builtin_amdgcn_is_invocable` ("builtin functions must be directly
  called").
- K5. rocBLAS 7.2.4-vs-6.1 comparison: **not possible without replacing the
  custom rocBLAS**. The custom gfx906 build embeds Tensile kernels in
  `librocblas.so.4.1` (82MB, only 3 loose library files) and ignores
  `ROCBLAS_TENSILE_LIBPATH`; the 7.2.4 drop has no host lib. Skipped per user
  decision (too much effort). A trial run with the inert override produced a
  full baseline repeat (see R2) - free repeatability evidence.
- K6. Launcher hardening: `BIN` / `LD_LIB` env overrides added to
  `llama-start-q6v.sh`; default stays production `build-vega20`.
- K7. HIP topology stable: HIP 0,1 = both Radeon VII gfx906
  sramecc+:xnack-, APU gfx90c excluded via HIP_VISIBLE_DEVICES.
- K8. Bench client gained `TG_N` env knob (default 256 unchanged); all this
  effort's TG numbers use TG_N=1024 per user metric definition.
- K9. fattn.cu `--hip-fa-force-vec` is op-level: `ggml_flash_attn_ext_get_force_vec`
  in ggml.h/ggml.c, plumbed via llama-cparams; default on.

## Results log

- R1. Baseline (production launcher, uf2 `build-vega20` Aug-18 gfx906 binary,
  Q6_K_XL, -c 210000, mixed KV f16 K/q8_0 V, -ts 40,20,40, -sm layer,
  draft-mtp+ngram-mod n-max 10, pipeline off): PP first-batch **325.4** tok/s
  (16007-token first progress event), TG1024 greedy fresh-KV **9.7** tok/s,
  acc 0.669, fitted n_ctx 210176, greedy sha 27901297b31a.
  log: bench/logs/baseline-prod.log
- R2. Config-identical repeat (R1 + inert ROCBLAS_TENSILE_LIBPATH=7.2.4):
  PP **325.3**, TG **9.7**, acc 0.669, n_ctx 210176, sha 27901297b31a
  (identical) -> run-to-run repeatability ~0.03%, greedy output bit-stable.
  log: bench/logs/rocblas724-tensile.log
- Historical context: trials.md TG ~20-22 rows used spec=2 plain MTP on the
  Q8_0 model; production ngram-mod+MTP n=10 combo drafts deeper -> ~9.7.
  Comparisons in this effort stay within production config.

## Patched results

### rs cumulative build (build-vega20-eaman @ 337d55023) - REJECTED

Binary built and loaded fine (build 10545). Small completions correct and
fast on every spec config tried (no-spec, mtp-only n10, ngram-only n10,
mtp+ngram n3/n5/n8/n10). BUT the server **deadlocks permanently** when a
client aborts a streaming completion mid-prompt-processing (e.g. stops
reading after the first prompt_progress event - exactly what our bench
client and real API clients do):

- Symptom: /health keeps answering, but no new task is ever processed; GPU
  activity 0%; even SIGTERM cannot terminate the wedged process (needs -9).
- Reproduced under gdb (bench/triage-gdb.sh, tmux session): Thread 1 (slot
  loop) blocked forever in `ggml_vk_wait_for_fence` -> `ggml_backend_vk_synchronize`
  mid-decode on the Vulkan device (fence never signals, GPU idle). Thread 21
  (httplib response writer) blocked in `send()` on the dead client socket.
  Full stacks: bench/logs/gdb-wedge.log.
- Trigger is the abort itself, NOT spec config or n-max (first repro was
  n10 production combo; gdb repro used n3).
- Root cause area: the experimental rs line's cancel/rollback path
  (recurrent-state checkpoint machinery interacting with the Vulkan backend
  queue state on task cancellation). eaman's own docs label rs as
  "experimental ... not merged into production eaman" with long-run
  stability explicitly pending. Our evidence agrees.

Decision (documented, branch `eaman-prod` commit `98bb6eac9`): revert the
rs-only delta (`git apply --reverse mtp_rs_only_8144f31.patch`, applied
cleanly) keeping the production subset = refined MTP joint fit + pipeline
control + force-vec + n_streams-aware per-device fit. Branch `eaman-rs`
keeps the full cumulative for reference.

### production-subset build (build-vega20-eaman @ d25991944)

Full A/B on the f16 config (mixed q8_0-V config is unusable post-merge, see
"Fork merge regressions" below), 165k ctx, full production spec
(mtp+ngram-mod n10), PP_ABORT=0 TG_N=1024 client:

| metric | old binary (Aug-18 pre-merge) | eaman-prod binary |
|---|---|---|
| PP first-batch 16384 | 331.3 t/s | 333.9 t/s |
| TG 1024 greedy | 10.0 t/s | 10.0 t/s |
| draft acceptance | 0.677 | 0.677 |
| greedy output sha | 22c0b014e72d | 22c0b014e72d (identical) |

Conclusion: eaman production subset = speed parity (+0.8% PP, within noise),
bit-identical outputs. Correctness validated (1024 greedy tokens identical
across binaries; small-completion sanity "Paris." correct on every config).
The eaman ctx-fitting gains apply at the ctx ceiling (mixed-KV / q8 draft
configs), which the fork-merge regression currently blocks.

## Fork merge regressions (PRE-EXISTING, NOT eaman) - CORRECTED 2026-08-25

**RETRACTION: F1 and F2 below were NOT merge regressions. Both were caused by
my rebuild recipe missing `-DGGML_CUDA_FA_ALL_QUANTS=ON`** (BUILD-VEGA20.md
omitted the flag; the original production build-vega20/CMakeCache.txt had it
ON). Without it, mixed f16-K/q8_0-V fattn instances are absent -> the HIP
backend refuses FLASH_ATTN_EXT for our exact KV mix -> the scheduler drops
the attention blocks to CPU. The Aug-20 merge tree builds and runs correctly
with the right flags. The original (wrong) analysis is kept below for the
record.

Verified after the fix (eaman-prod binary, FA_ALL_QUANTS=ON, prod config):
- PP first-batch 321.0 / deep-fill run 325.4 (baseline 325.4): parity.
- TG 10.1 fresh, 10.1 @ 120k deep fill (old binary: 10.0/10.3).
- Abort-mid-PP recovery: 0.7 s (previous "wedge" gone; the cancelled batch
  drains in ~40 s which is normal ubatch-boundary cancellation).
- Output identity: 120k deep-fill greedy sha d5267dcc9d17 identical on old
  and new binary.

### Original (misdiagnosed) findings, kept for record

Both discovered while testing eaman builds; both reproduce on the fork's own
merge commit `a3fbc9321` (Aug-20 upstream sync) with ZERO eaman content
(basetest build). The Aug-18 production binary (pre-merge) is unaffected.

### F1. Abort-wedge: server deadlocks forever after a client aborts mid-PP

Repro: start any streaming completion with a large prompt, disconnect before
the prompt finishes (e.g. stop reading after the first prompt_progress SSE
event; scripts: bench-client.py default PP_ABORT=1, or /tmp/pp_driver.py).
After that, /health still answers but no task ever runs again; SIGTERM
cannot kill the wedged process (needs SIGKILL).

Mechanism (gdb, bench/triage-gdb.sh + bench/logs/gdb-wedge.log): Thread 1
(slot loop) blocked forever in ggml_vk_wait_for_fence ->
ggml_backend_vk_synchronize mid-decode (Vulkan fence never signals, all GPUs
idle); Thread 21 (httplib writer) blocked in send() on the dead socket.
Independent of spec config and n-max.

### F2. Mixed-KV (f16 K + q8_0 V) PP collapses ~19x: whole graph runs on CPU

Repro: production launcher config (-ctk f16 -ctv q8_0) on any post-a3fbc9321
build: PP = 17 t/s (was 325). f16/f16 control on the SAME binary: 297-307
t/s (GPU). During the slow PP: NVIDIA 0% util, both AMD 0% memory activity,
llama-server CPU ~440% - the entire compute graph executes on host.

Not the fattn dispatch: `git diff 923a9661d..a3fbc9321` on fattn.cu /
fattn-common.cuh / fattn-tile.cuh is only the upstream WMMA removal; the
fork tile kernels and their priority dispatch are intact, and the verbose
load log (-lv 5, bench/logs/verbose-load.log) shows KV buffers correctly on
all three GPUs. Suspects: the upstream llama-graph.cpp (+417 lines) /
llama-context.cpp (+410) refactor changing how the mixed-type cache views
are built, so some op in the chain loses HIP support and the scheduler
cascades the graph to CPU.

Extra findings from the verbose load (post-merge, upstream behavior):
- llama_memory_recurrent allocates RS buffers even for this DENSE model:
  720 MiB (ROCm0) + 617 MiB (ROCm1) + 309 MiB (Vulkan1) = ~1.65 GiB VRAM
  spent on recurrent-state storage a dense Qwen does not use.
- 994.63 MiB of model tensors land in ROCm_Host despite -ngl 333 and
  "offloaded 66/66 layers" (suspect: output head / mmproj tensors).
- "cache_reuse is not supported by multimodal, it will be disabled" -
  upstream silently drops the production --cache-reuse 256.
- New GPU-side sampler infra warns: "device 'ROCm1' does not have support
  for op TOP_K needed for sampler 'top-k'".

## Eaman benefits verdict (prod config, measured 2026-08-25)

- Speed/quality: PARITY everywhere measurable (PP/TG/120k-deep, identical
  greedy outputs at fresh and deep KV).
- Context: no gain on the prod config. The fitter aborts when -ngl/-ts/-ot
  are pinned (nothing left to fit); with pins and -c dropped it picks 135168
  (BELOW our manual 210k calibration); fully unpinned it loads 262144 but
  places 13 of 66 layers (5.1 GiB) on the host to pay for it (PP 91, TG 4.6
  - verified in bench/logs/auto-verbose.log, "offloaded 53/66"). This is the
  fitter's designed max-ctx-over-speed trade, NOT op misplacement: with
  FA_ALL_QUANTS=ON no op lands on CPU unintentionally (pinned prod run is
  66/66 GPU at PP 325.4). Our manual calibration (dual-gpu-context-balancing)
  simply prefers the other end of the trade.
- Net: adopt eaman-prod for upstream alignment + the explicit
  --pipeline-parallel / --hip-fa-force-vec knobs; expect zero perf/ctx delta
  on the current production config.

## Recommended next steps (not done in this session)

1. Investigate the 1.65 GiB dense-model RS allocation (upstream regression
   or new expected behavior) - on 16 GB cards this is ~10% of VRAM.
   (CORRECTION: model has qwen35.ssm.* tensors - it IS a hybrid SSM model;
   the RS buffers are legitimate. Only the "994 MiB ROCm_Host weights" and
   "cache_reuse silently disabled with mmproj" items remain interesting.)
2. Consider turbo3 KV-compression backport (see FORK-SURVEY-2026-08-25.md)
   for a real ctx lever; requires memory-interface surgery + quality
   validation + ROCm 7.1-era constructs replacement.
3. Watch mxxm-t/mx-llama.cpp (iacopPBK's declared successor) for qwen35-era
   model support that could make their kernel set benchable on our model.

## Final state (updated 2026-08-25)

- Production launcher: still points at build-vega20 (Aug-18 binary, still
  the known-good). The eaman-prod binary (build 10547 @ 40e61a4a7 +
  FA_ALL_QUANTS rebuild) is validated as a drop-in replacement.
- Build recipe now includes GGML_CUDA_FA_ALL_QUANTS=ON (BUILD-VEGA20.md and
  gfx906-build-recipe-rocm61 memory both corrected).
- Branches: eaman-prod (recommended), eaman-rs (reference), fix/mixed-kv-f2
  (bisect/instrumentation scratch; F2 root cause turned out to be the build
  flag, branch holds no fix anymore - the stash with instrumentation was
  never re-applied).

## Final state (2026-08-24)

- Branches pushed to gfx906 remote (milpeter/gfx906-llama-cpp):
  - `eaman-prod` (recommended): a3fbc9321 + eaman cumulative + upstream
    2fb989b9e cherry-pick + rs revert (d25991944). Validated A/B above.
  - `eaman-rs` (reference): full cumulative incl. experimental rs line;
    builds and serves, but inherits F1/F2 plus unverified rs stability.
- build-vega20 (Aug-18 binary) untouched = production binary.
- build-vega20-eaman = eaman-prod binary (build 10546, d25991944).
- Launcher llama-start-q6v.sh: repo-relative paths, BIN/LD_LIB overrides;
  still points at build-vega20 (production) by default.
- bench-client.py: TG_N and PP_ABORT knobs; bench/triage-start*.sh family
  for config A/Bs incl. gdb twin for wedge reproduction.

## Output validation

(filled after patched run: greedy sha vs baseline, manual text check)
