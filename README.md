> ## gfx906 fork (this repository)
>
> **TLDR:** +23% prefill, +11% TG @120k depth, 250k context for a 27B
> Q6_K on 40 GB VRAM, bit-identical outputs vs upstream master - for
> gfx906 (Radeon VII / MI50) and mixed ROCm + Vulkan rigs. Last upstream
> sync: 2026-09-03 (95ef7fc16, 65 commits, lane-gated).
>
> **What this is:** a production llama.cpp fork for AMD gfx906 GPUs
> (Radeon VII / MI50 / MI60) and mixed ROCm + Vulkan rigs. Upstream has
> no gfx906 tuning and no controllable pipeline parallelism for
> heterogeneous tight-VRAM fits. Reference deployment: Qwen3.8-27B
> (i1-Q6_K) + DFlash2 speculative decoding at **250k context on 40 GB
> VRAM** (2x Radeon VII + GTX 3080), **bit-identical outputs**.
>
> ### How much it helps (vs upstream master, same-config A/B)
>
> Config: 2x Radeon VII + GTX 3080 (Vulkan), `-ts 35,20,45 -sm layer`,
> f16-K/q8_0-V, DFlash2 depth-4. Upstream column measured direct
> (2026-09-03); fork column = direct pair x draft-mirror deltas
> (composed, marked ~).
>
> | metric | upstream t/s | fork t/s | gain |
> |---|---|---|---|
> | prefill PP16384 | 332.5 | ~410 | **+23%** |
> | 120k deep fill | 231.4 | ~264 | **+14%** |
> | TG @120k depth | 13.6 | ~15.1 | **+11%** (parity pre-mirror) |
> | context | cannot fit | 250k on 40 GB | tight-fit machinery |
> | outputs | - | - | bit-identical (sha + token-for-token) |
>
> ### Who benefits
>
> | You run... | You get... |
> |---|---|
> | gfx906 / MI50 / Radeon VII | wave64-correct kernel tables, sha-gated |
> | mixed ROCm + Vulkan | controllable pipeline parallelism + safe fallback |
> | heterogeneous GPU setups | unlike GPUs in one pipeline: weighted layer splits, cross-backend scheduling, per-device fits |
> | Qwen3.8 / qwen4exp | DFlash2 drafter, adaptive depth, GDN prefill |
> | anyone reproducibility-minded | every change gated on unchanged temp-0 sha |
>
> ### What we changed, and why
>
> - **wave64 kernel tables** (fork + upstream #27841's GCN row): MMQ
>   tiles (Q6_K I=64), top-k, fattn dispatch. Occupancy 1 -> 2 waves
>   hides latency -> +20% PP.
> - **Draft head mirror** (LLAMA_DFLASH_MIRROR_OUTPUT=1 +
>   --spec-draft-device): device-local copy of the borrowed vocab head,
>   single-device draft graph -> draft rounds -42%, TG +11% @120k depth.
> - **Pipeline parallelism**: fork-only on/off switch, safe fallback,
>   draft-ctx exclusion (controls + per-device fit refinements from the
>   eaman patch store, store.piffa.net/lm/bug; A/B-adopted 2026-08-24).
>   Benefit: no startup aborts or capture corruption on tight fits,
>   honest fit tables.
> - **Tight fits**: f16-K/q8_0-V KV, fattn path selector, frugal
>   buffers (compute ~5x smaller than stock), HIP graph robustness.
>   Benefit: the 250k-on-40GB fit itself - stock cannot load it.
> - **Env-gated ports, bit-exact** (mx-llama.cpp survey): GDN chunked
>   prefill, q8_1 cache, pipeline drain + graph exec fixes. Benefit:
>   robustness on the tight-fit + HIP-graph regime, at zero measured cost.
> - **Upstream syncs**: full merges, each lane-gated on sha + perf.
>   Benefit: current fixes ride along at zero measured cost.
>
> ### What did not work (measured)
>
> | idea | why out |
> |---|---|
> | MMQ inner-loop restructures, 5 variants (fork probes; upstream #21698, #23685) | ~41% issue ceiling is structural on gfx906 |
> | fattn scheduling/geometry probes (fork; upstream #25635/#28102 wrong path for gfx906) | compiler schedule is a local optimum (-0.5 to -5.8%) |
> | upstream #27173 draft chain | launch overhead TG-neutral here; one-decode drafting already |
> | deeper draft n_max 5/6 (fork lane) | 6-row verify hits a kernel-shape cliff (-28% TG) |
> | K quantization beyond q8_0-V (fork measurement, E54) | native tile -2.6 t/s, depth effect only ~5% |
> | ts rebalance / drafter relocation (fork lanes, E105 + 08-15 sweeps) | decode is overhead-bound, not bandwidth-bound |
> | checkpoint sparsify / off (fork lanes, AB6 + E119.4) | neutral / breaks prompt restore |
> | mx-fork layout cache, replay coupling, TP/AllReduce; eaman rs line (wedges on abort) | fixes pathologies we do not have, or not our topology |
> | full survey (adopted/rejected per PR) | journal/ + bench/FINDINGS.md |
>
> ### Evidence and build
>
> Every claim has a lane row: journal/ (experiment log), bench/
> (A/B harness, FINDINGS.md, vram-test, rocprof stack). Build:
> ./build-dflash-novega.sh (ROCm 6.1 + Vulkan, gfx906, tunes on).
>
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
