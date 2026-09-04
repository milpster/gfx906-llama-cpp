> ## gfx906 fork (this repository)
>
 > **Why this fork exists:** upstream llama.cpp carries no tuning for AMD
 > Vega 20 (gfx906: Radeon VII / MI50 / MI60) - GCN5 wave64 hardware
 > silently falls back to wave32 RDNA2 kernel tables - and its multi-GPU
 > pipeline-parallel path offers no user control and no safe fallback on
 > tight mixed ROCm+Vulkan fits (audit E117). This fork
 > keeps those GPUs production-viable: it runs Qwen3.8-27B (i1-Q6_K) with
> DFlash2 speculative decoding at **250k context on 40 GB of VRAM**
 > across 2x Radeon VII + a GTX 3080 (Vulkan), at **+20% prefill over
 > upstream master** (includes the 2026-09-03 Q6_K tile retune)
 > with **bit-identical outputs**.
>
> ### Who it benefits, and how
>
> | You run... | You get... |
> |---|---|
 > | gfx906 / MI50 / Radeon VII | wave64-correct MMQ, top-k and flash-attn tables: +20% PP and +12% deep fill vs upstream master (same binary-config A/B 2026-09-03); sha-gated so speed is the only thing that moves |
 > | mixed ROCm + Vulkan GPUs | `-sm layer` **pipeline parallelism** with explicit `--pipeline-parallel on|off` control and a safe reserve fallback, drafter pinning to one device, 35/20/45-style tensor splits |
> | big models, long context, tight VRAM | 250k ctx on 40 GB: f16-K/q8_0-V KV cache, split fitting, HIP-graph + allocation robustness fixes for deliberately tight fits |
> | Qwen3.8 / qwen4exp (MoE + GDN hybrid) | DFlash2 drafter integration, adaptive MTP draft depth, per-round acceptance logging, GDN chunked prefill kernel, upstream qwen4exp fixes merged same-week |
> | anyone valuing reproducibility | every tuning change and every upstream merge is gated on unchanged temp-0 sha - if the hash moves, the change does not ship |
>
> ### Numbers
>
> Current production (2026-09-03, full prod shape: 250k ctx, 35/20/45
> `-sm layer`, f16-K/q8_0-V, DFlash2 depth-4): PP16384 **393 t/s**, 120k
> deep fill **257 t/s**, TG1024 12.0-12.3 t/s, draft acc 0.65-0.66,
> repro gate true.
>
> Draft mirror A/B (2026-09-04, same full protocol, prod binary vs
> prod+mirror; temp-0 sha identical across builds, e54019ff6b42, plus a
> direct token-for-token greedy comparison with the full spec chain:
> byte-identical output):
>
> | | PP16384 t/s | 120k fill t/s | TG1024 t/s @120k | draft ms/round | draft acc. |
> |---|---|---|---|---|---|
> | prod baseline | 394.7 | 259.4 | 11.7 | 32.2 | 0.644 |
> | + draft mirror | **406.5** | **263.8** | **13.0 (+11%)** | **18.8 (-42%)** | 0.657 |
>
> At shallow fill the TG gain is larger (+28%); the mirror is validated
> but not yet in the production launcher (promotion pending).
>
 > Versus upstream master (A/B 2026-09-03, identical config, -c 200000,
 > only the binary differs; upstream at c5a5535e6 = this fork's sync
 > point 95ef7fc16 +2 commits, Q6_K retune included on the fork side;
 > temp-0 sha identical across builds, e54019ff6b42):
 >
 > | | PP16384 t/s | 120k fill t/s | TG512 t/s (temp 0) | draft acc. |
 > |---|---|---|---|---|
 > | fork (tuned) | **398.5** | **259.7** | 13.6 | 0.691 |
 > | upstream master | 332.5 | 231.4 | 13.6 | 0.691 |
>
> ### What is changed
>
 > - **Kernel tuning** (`GGML_CUDA_VEGA_TUNE_*`, default-on): per-arch MMQ
 >   GEMM table `mmq-config-vega.cuh` (Q6_K at I=64/occ2: +4.5% PP, +2.7%
 >   fill, sha-identical - Q6_K is 96.9% of this model's MMQ cycles and
 >   prefill is GEMM-bound; I=64 shrinks the VGPR accumulator footprint,
 >   lifting occupancy from 1 to 2 waves so the GPU hides the latency the
 >   1-wave config waited on; gfx906 is VGPR-sensitive, cf. the E93
 >   dual-acc rejection), tiled top-k, HIP graph tuning. Rejected probes
 >   (fattn cols16/occ3/qpipe, MMQ dual-acc, q8_0 loader remap) stay in
 >   tree, default-off, for reruns.
> - **Flash attention dispatch**: context-based path selector, native
>   q8_0-V tile geometry, small-Q narrow tiles for MTP-verify batches.
> - **Speculative decoding**: DFlash2 integration + per-round acceptance
>   logging, `draft-mtp-adaptive` depth (upstream PR #27210 carried here),
>   and the **DFlash2 draft output-head mirror** (`LLAMA_DFLASH_MIRROR_OUTPUT=1`,
>   env-gated, plus `--spec-draft-device ROCm0`): the draft context gets a
>   device-local copy of the borrowed target output head (995 MiB, host-staged
>   copy, head+tail verified), so the draft graph runs single-device - no
>   cross-device hop per round. Draft rounds 32.2 -> 18.8 ms, TG +11% at
>   120k depth, PP top-of-band, bit-exact.
> - **Multi-GPU**: `--pipeline-parallel` for `-sm layer` (fork-only),
>   drafter pinning via `--spec-draft-override-tensor`.
> - **Ported extras, env-gated, bit-exact** (mx-llama.cpp survey): GDN
>   chunked prefill (`GGML_CUDA_GDN_CHUNK`), q8_1 activation cache
>   (`GGML_CUDA_Q8_1_CACHE`), robustness fixes (fattn-vec mask stride,
>   pipeline drain before seq-layout reset, HIP graph exec
>   reinstantiation).
 > - **Upstream sync cadence**: repeated full merges, latest 2026-09-03
 >   evening (65 commits, upstream 95ef7fc16). Every merge is lane-gated:
 >   same-day A/B vs the prior binary; pass = unchanged canonical sha +
 >   perf inside the day's noise.
>
> ### Provenance: what we surveyed, adopted, and rejected
>
> Nothing here is taken on faith - every external idea ran through a lane
> A/B or a code-path check. Full logs in `journal/`.
>
> **Adopted**
>
> | Source | What | Result |
> |---|---|---|
> | upstream #27210 (open) | adaptive MTP draft depth (`draft-mtp-adaptive`) | carried in fork; TG win at depth |
> | upstream #27816 | DFlash2 drafter rewrite | merged 2026-08-28, taken wholesale |
> | upstream #27812 | vulkan view-alias fix (spec verify corruption) | ported verbatim (E18), later converged via merge |
> | upstream #27841 (open) | GCN MMQ tile table (Radeon VII-tuned) | Q6_K I=64/occ2 row adopted: **+4.5% PP, +2.7% fill**, sha-identical; Q8_0 rows cross-checked equal to ours |
 > | eaman patch store (https://store.piffa.net/lm/bug/) | refined MTP joint fit (target+draft fitted together), `--pipeline-parallel` and `--hip-fa-force-vec` controls, per-device fixed-layout fit | adopted 2026-08-24 (branch eaman-prod): +0.8% PP = noise, bit-identical outputs; origin of the production `--pipeline-parallel` control |
 > | mx-llama.cpp fork | GDN chunked prefill, q8_1 activation cache | bit-exact, perf-neutral on this model; kept default-on, env-gated |
> | mx-llama.cpp fork | robustness family (fattn-vec stride, pipeline drain, HIP graph exec reinstantiate) | adopted; targets our tight-VRAM + HIP-graph regime |
> | upstream 2026-09-03 merge | qwen4exp fixes, MoE expert-reduction fusion (#25952), vulkan FA dequant (#28190), RAM-peak (#27483), quantize row-slab (#27830) | all ride along at zero measured cost (lane-gated) |
> | fork E119 (own; mirror-output idea kin to #27173's) | DFlash2 draft output-head mirror + single-device draft ctx | draft rounds **-42%**, TG **+11% @120k / +28% shallow**, PP top-of-band, bit-exact (sha + token-for-token temp-0) |
>
> **Measured and rejected** (kept default-off in tree where cheap)
>
> | Source | Idea | Why rejected |
> |---|---|---|
> | upstream #21698 | q8_0 loader remap (MMQ) | +28-36% claimed on MI50; +1.0% here - benefit is tile-config-dependent, our vega table already there (E95) |
> | upstream #23685 | 4x packed q8_1 MMVQ | flat on our Q6_K mix (E93-adjacent lanes) |
> | mx fork | gallocr layout cache (+377% fill claim) | pathology absent on `-sm layer`: 6 reserves per fill, not per-ubatch (E109 probe) |
> | mx fork | DFlash replay coupling (+74% PP claim) | our 8.6% spec prefill tax is SM contention on ROCm0, not replay stalls (E110) |
 > | eaman patch store | experimental rs line (recurrent-state speculative checkpoints) | wedges the server permanently on a client abort mid-PP (Vulkan fence never signals; gdb evidence bench/logs/gdb-wedge.log); author marks it experimental - reverted, branch `eaman-rs` kept for reference |
 > | mx fork | TP/`-sm tensor` + custom AllReduce stack | homogeneous-AMD-only; this rig is heterogeneous ROCm+Vulkan `-sm layer` |
> | fork probes | fattn cols16/occ3/qpipe, MMQ dual-acc | measured, rejected (E93: -13.1% pp; E101: -5.8%), kept env-off for reruns |
> | fork lane | `--spec-draft-n-max 5` rebracket on the cheap draft | TG -28%: the 6-row verify batch hits a kernel-shape cliff (~+50 ms/round, MoE MUL_MAT_ID batch threshold or shadow-convert geometry suspected); depth stays 4; fixing the cliff is a parked lever |
> | fork lane | checkpoint sparsify (`--checkpoint-min-step 16384`) | perf-neutral vs baseline (restore intact); checkpoints off cannot be measured by the lane protocol (breaks prompt restore, AB6/AB8 class) |
>
> **Checked, not applicable** (code-path or measurement proof)
>
> | Source | Idea | Why not applicable |
> |---|---|---|
> | upstream #28102 | FA tuning, +143% PP on the same model | fix lives in the WMMA/mma path; gfx906 has no WMMA (RDNA3/4-only), we run the tile kernel |
> | upstream #25635 | XOR swizzle fattn K/V smem | touches `fattn-mma-f16.cuh` only - our tile kernel unaffected |
> | upstream #28136 | qwen4exp PLE direct reads (>2x prefill) | pathology is mmap lazy paging; we run `--no-mmap` in prod and bench |
> | upstream #28178 | copy kernel for small D2D copies | measured via `bench/rd2d-count` shim: 2.3 D2D calls/token, <0.2% of TG budget; GDN state stays in-graph |
> | upstream #24546 | MoE MMQ N-tiles from expert width | 96.9% of our MMQ cycles run J=64 with zero fallback - no tile-tail waste to recover |
> | upstream #28313 | ROCm top-k rewrite | our tiled top-k already validated; entire class bounded at <=0.4 t/s (E53) |
> | upstream #27825 | HIP AllReduce | `-sm tensor`-only feature |
> | upstream #26705, #27962 | Q4_K/Q5_K MMVQ branchless, IQ2/IQ3 SWAR | wrong quant mix (i1-Q6_K) |
> | upstream #21170 | ROCm multi-GPU IMA fix | crash never recurred; branch `crash-test-setdevice` parked with runbook |
>
> Also on watch (upstream, unmerged): #27692 speculative prefill (lossy),
> #27694 probabilistic drafter + rejection-sampling verify (changes
> sampling semantics = sha-breaking), #28391 default spec config (flag
> semantics change at next sync: `--spec-type` additive,
> `--no-spec-type`), #28333 MTP carrier zeroing (check dflash carrier on
> sync). #27173 spec draft chain is CLOSED for us: rejected whole (D7
> multi-GPU regression profile; our DFlash2 already drafts in one
> decode, SCHED_POOL moot - launch overhead measured TG-neutral, and
> defer-catch-up structurally absent); its mirror-output idea landed as
> the fork's own draft head mirror (adopted table). #21849 stale,
> superseded by #27841.
>
> Tooling provenance: PMU profiling via an archived 6.1-matched rocprof
> stack (`bench/rocprof-stack/`, rebuildable; note: the TG-phase profile
> zone crashes under the interposer - E91 class, twice - keep rocprof
> PP-only until the stack is repaired), D2D-copy histogramming via
> the `bench/rd2d-count` LD_PRELOAD shim (version-script interposition for
> `hipMemcpyAsync@hip_4.2`), VRAM integrity probing via `bench/vram-test`
> (write/readback pattern test per card; born from the 2026-09-04
> transient-corruption incident, which self-healed and is documented in
> the journal).
>
> ### Evidence and build
>
> - `journal/` (E-numbered experiment log - every claim above has a lane
>   row behind it), `bench/` (lane/A/B harness, `FINDINGS.md` decision
>   record, `trials.md` results), `.opencode/skills/` rig runbooks
>   (`dual-gpu-context-balancing`, `requant-gguf-gfx906-perf`)
> - Build: `./build-dflash-novega.sh` (ROCm 6.1 + Vulkan, gfx906 target,
>   tunes on). Runtime env lives in the launchers
>   (`2llama-start-iq6v-dflash2.sh`): HIP graphs, pinned ROCm 6.1 libs,
>   HSA_XNACK=0, P2P.

# llama.cpp

![llama](https://raw.githubusercontent.com/ggml-org/llama.brand/refs/heads/master/cover/llama-cpp/cover-llama-cpp-dark.svg)

<div align="center">

<b>LLM inference in C/C++</b>

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Release](https://img.shields.io/github/v/release/ggml-org/llama.cpp?filter=v*&color=brightgreen)](https://github.com/ggml-org/llama.cpp/releases?q=tag:v0)
[![Nightly](https://img.shields.io/github/v/release/ggml-org/llama.cpp?label=nightly&filter=b*&color=orange)](https://github.com/ggml-org/llama.cpp/releases?q=b)
[![Server](https://img.shields.io/github/actions/workflow/status/ggml-org/llama.cpp/server.yml?label=Server)](https://github.com/ggml-org/llama.cpp/actions/workflows/server.yml)
[![Docker](https://img.shields.io/github/actions/workflow/status/ggml-org/llama.cpp/docker.yml?label=Docker)](https://github.com/ggml-org/llama.cpp/actions/workflows/docker.yml)
[![Winget](https://img.shields.io/github/actions/workflow/status/ggml-org/llama.cpp/winget.yml?label=Winget)](https://github.com/ggml-org/llama.cpp/actions/workflows/winget.yml)

[ggml](https://github.com/ggml-org/ggml) / [ops](https://github.com/ggml-org/llama.cpp/blob/master/docs/ops.md) / [maintainer PRs](https://github.com/ggml-org/llama.cpp/issues?q=is%3Apr%20is%3Aopen%20draft%3AFalse%20(author%3Argerganov%20OR%20author%3AKitaitiMakoto%20OR%20author%3Adanbev%20OR%20author%3Aaldehir%20OR%20author%3Amax-krasnyansky%20OR%20author%3ACISC%20OR%20author%3Aggerganov%20OR%20author%3Aam17an%20OR%20author%3Abartowski1182%20OR%20author%3Anikwen%20OR%20author%3Ahipudding%20OR%20author%3AServeurpersoCom%20OR%20author%3Apwilkin%20OR%20author%3Areeselevine%20OR%20author%3Angxson%20OR%20author%3Ajeffbolznv%20OR%20author%3Amarty1885%20OR%20author%3A0cc4m%20OR%20author%3ATitaniumtown%20OR%20author%3Aangt%20OR%20author%3AIMbackK%20OR%20author%3Aarthw%20OR%20author%3AJohannesGaessler%20OR%20author%3AORippler%20OR%20author%3Aruixiang63%20OR%20author%3Axctan%20OR%20author%3Aallozaur%20OR%20author%3Ayomaytk%20OR%20author%3Aaendk%20OR%20author%3Agaugarg-nv%20OR%20author%3Ataronaeo%20OR%20author%3Aforforever73%20OR%20author%3Alhez%20OR%20author%3Anetrunnereve%20OR%20author%3Afairydreaming)%20sort%3Aupdated-desc) / [dev stats](https://github.com/ggml-org/llama.cpp-dev) / [lib llama API](https://github.com/ggml-org/llama.cpp/issues/9289) / [llama-server REST API](https://github.com/ggml-org/llama.cpp/issues/9291)

</div>

## Quick start

A few options to get `llama.cpp` installed on your machine:

- Visit https://llama.app and follow the instructions
- Run with Docker - see our [Docker documentation](docs/docker.md)
- Download pre-built binaries from the [releases page](https://github.com/ggml-org/llama.cpp/releases)
- Build from source by cloning this repository - check out [our build guide](docs/build.md)

Once installed:

```sh
# Download and run a model directly from Hugging Face
llama cli -hf ggml-org/Qwen3.5-0.8B-GGUF

# Launch OpenAI-compatible API server
llama serve -hf ggml-org/Qwen3.5-0.8B-GGUF
```

<table align="center">
    <tr>
        <td align="center" width=50%>
            <img width="1310" height="888" alt="VLM session with `llama cli`" src="https://github.com/user-attachments/assets/88726b48-1713-48aa-a525-95a02e78afc4" />
            <i>VLM session with <b>llama cli</b></i>
        </td>
        <td align="center">
            <img width="1392" height="958" alt="Built-in web UI against `llama serve` running Qwen 3.6" src="https://github.com/user-attachments/assets/b402f972-2e32-4def-8771-8d849f08cf2e" />
            <i>Built-in web UI against <b>llama serve</b></i>
        </td>
    </tr>
<table>

## Description

The main goal of `llama.cpp` is to enable LLM (and VLM) inference with minimal setup and state-of-the-art performance on
a wide range of hardware - locally and in the cloud.

- Plain C/C++ implementation without any dependencies
- Apple silicon is a first-class citizen - optimized via ARM NEON, Accelerate and Metal frameworks
- AVX, AVX2, AVX512 and AMX support for x86 architectures
- RVV, ZVFH, ZFH, ZICBOP and ZIHINTPAUSE support for RISC-V architectures
- 1.5-bit, 2-bit, 3-bit, 4-bit, 5-bit, 6-bit, and 8-bit integer quantization for faster inference and reduced memory use
- Custom CUDA kernels for running LLMs on NVIDIA GPUs (support for AMD GPUs via HIP and Moore Threads GPUs via MUSA)
- Vulkan and SYCL backend support
- CPU+GPU hybrid inference to partially accelerate models larger than the total VRAM capacity

The `llama.cpp` project is build on top of the [ggml](https://github.com/ggml-org/ggml) library.

## Supported backends

| Backend | Target devices |
| --- | --- |
| [BLAS](docs/build.md#blas-build) | All |
| [BLIS](docs/backend/BLIS.md) | All |
| [CANN](docs/build.md#cann) | Ascend NPU |
| [CUDA](docs/build.md#cuda) | Nvidia GPU |
| [HIP](docs/build.md#hip) | AMD GPU |
| [Hexagon](docs/backend/snapdragon/README.md) | Snapdragon |
| [IBM zDNN](docs/backend/zDNN.md) | IBM Z & LinuxONE |
| [MUSA](docs/build.md#musa) | Moore Threads GPU |
| [Metal](docs/build.md#metal-build) | Apple Silicon |
| [OpenCL](docs/backend/OPENCL.md) | Adreno GPU |
| [OpenVINO [In Progress]](docs/backend/OPENVINO.md) | Intel CPUs, GPUs, and NPUs |
| [RPC](https://github.com/ggml-org/llama.cpp/tree/master/tools/rpc) | All |
| [SYCL](docs/backend/SYCL.md) | Intel GPU |
| [VirtGPU](docs/backend/VirtGPU.md) | VirtGPU APIR |
| [Vulkan](docs/build.md#vulkan) | GPU |
| [WebGPU](docs/build.md#webgpu) | All |
| [ZenDNN](docs/build.md#zendnn) | AMD CPU |

## Documentation

#### Tools

- [cli](tools/cli/README.md)
- [completion](tools/completion/README.md)
- [server](tools/server/README.md)
- [GBNF grammars](grammars/README.md)

#### Development

- [How to build](docs/build.md)
- [Running on Docker](docs/docker.md)
- [Build on Android](docs/android.md)
- [Multi-GPU usage](docs/multi-gpu.md)
- [Performance troubleshooting](docs/development/token_generation_performance_tips.md)
- [GGML tips & tricks](https://github.com/ggml-org/llama.cpp/wiki/GGML-Tips-&-Tricks)
- [XCFramework](docs/xcframework.md)
- [Completions](docs/completions.md)
- [Models](docs/models.md)
- [Release process](docs/release.md)

## Contributing

- Contributors can open PRs
- Collaborators will be invited based on contributions
- Maintainers can push to branches in the `llama.cpp` repo and merge PRs into the `master` branch
- Any help with managing issues, PRs and projects is very appreciated!
- Read the [CONTRIBUTING.md](CONTRIBUTING.md) for more information

## Acknowledgements

- [yhirose/cpp-httplib](https://github.com/yhirose/cpp-httplib) - Single-header HTTP server, used by `llama-server` - MIT license
- [nothings/stb](https://github.com/nothings/stb) - Single-header image format decoder, used by multimodal subsystem - Public domain
- [nlohmann/json](https://github.com/nlohmann/json) - Single-header JSON library, used by various tools/examples - MIT License
- [mackron/miniaudio](https://github.com/mackron/miniaudio) - Single-header audio format decoder, used by multimodal subsystem - Public domain
- [sheredom/subprocess.h](https://github.com/sheredom/subprocess.h) - Single-header process launching solution for C and C++ - Public domain
