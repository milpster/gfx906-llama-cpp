# llama.cpp build guide — Vega 20 (gfx906) + Vulkan hybrid

## Hardware

- 2x AMD Radeon VII (Vega 20, gfx906, 16GB VRAM each) — via ROCm 6.1.0
- 1x NVIDIA RTX 3080 Laptop (8GB VRAM) — via Vulkan
- AMD Ryzen 9 5900HX (8c/16t)
- 64GB system RAM

## Prerequisites

```
ROCm 6.1.0 installed at /opt/rocm-6.1.0/
Custom rocBLAS built for gfx906+xnack at /home/srcds/rocm-gfx906-xnack/lib/
Vulkan SDK (for NVIDIA Vulkan backend)
cmake >= 3.22, ninja, gcc/g++ or clang
```

## CMake configuration

```bash
cmake -S . -B build-vega20 \
    -DCMAKE_BUILD_TYPE=Release \
    -DGGML_HIP=ON \
    -DAMDGPU_TARGETS=gfx906 \
    -DGPU_TARGETS=gfx906 \
    -DGGML_HIP_GRAPHS=ON \
    -DGGML_HIP_NO_VMM=ON \
    -DGGML_CUDA_FORCE_MMQ=ON \
    -DGGML_CUDA_FA_ALL_QUANTS=ON \
    -DGGML_LTO=OFF \
    -DGGML_VULKAN=ON \
    -DCMAKE_HIP_FLAGS="-ffast-math -fno-math-errno" \
    -DCMAKE_EXE_LINKER_FLAGS="-L/opt/rocm-6.1.0/lib -L/home/srcds/rocm-gfx906-xnack/lib" \
    -DCMAKE_SHARED_LINKER_FLAGS="-L/opt/rocm-6.1.0/lib -L/home/srcds/rocm-gfx906-xnack/lib" \
    -DCMAKE_HIP_COMPILER=/opt/rocm-6.1.0/lib/llvm/bin/clang
```

CRITICAL: `GGML_CUDA_FA_ALL_QUANTS=ON` is REQUIRED for the mixed-KV production
config (f16 K + q8_0 V). Without it the mixed-type fattn instances are absent,
the HIP backend refuses FLASH_ATTN_EXT, and the scheduler drops the whole
attention block to CPU (~19x PP collapse, verified 2026-08-25). Also required:
`ROCM_PATH=/opt/rocm-6.1.0` in the environment at configure time (see
EAMAN-INTEGRATION-2026-08-24.md knowledge log).

### Flag rationale

| Flag | Value | Why |
|---|---|---|
| `CMAKE_BUILD_TYPE` | Release | -O3 optimization |
| `GGML_HIP` | ON | Enable HIP/ROCm backend for AMD GPUs |
| `AMDGPU_TARGETS` | gfx906 | Compile for Vega 20 architecture |
| `GPU_TARGETS` | gfx906 | Same, for HIP runtime |
| `GGML_HIP_GRAPHS` | ON | HIP graph capture reduces kernel dispatch overhead |
| `GGML_HIP_NO_VMM` | ON | gfx906 lacks virtual memory management support |
| `GGML_CUDA_FORCE_MMQ` | ON | Redundant for gfx906 (MMQ always used) but harmless |
| `GGML_LTO` | OFF | LTO causes ~4% TG regression on HIP (tested) |
| `GGML_VULKAN` | ON | Enable Vulkan backend for NVIDIA GPU |
| `CMAKE_HIP_FLAGS` | -ffast-math -fno-math-errno | HIP defaults already include -ffast-math; explicit for clarity |

### Flags NOT set (and why)

| Flag | Why not |
|---|---|
| `GGML_HIP_MMQ_MFMA` | No-op for gfx906 (gated by IS_CDNA check, Vega 20 is not CDNA) |
| `GGML_HIP_ROCWMMA_FATTN` | Vega 20 has no WMMA matrix cores |
| `GGML_HIP_RCCL` | No multi-node inference |

## Build

```bash
cmake --build build-vega20 --target llama-server llama-bench -j$(nproc)
```

Build output: `build-vega20/bin/llama-server`, `build-vega20/bin/llama-bench`

## Custom rocBLAS

A custom rocBLAS build tuned for gfx906 with xnack disabled lives at `/home/srcds/rocm-gfx906-xnack/lib/`. This is loaded at runtime via `LD_LIBRARY_PATH` and provides better GEMM performance than the stock ROCm rocBLAS for Vega 20.

## Runtime environment

```bash
export HIP_GRAPH=1
export AMD_LOG_LEVEL=0
export GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16
export HSA_OVERRIDE_GFX_VERSION=9.0.6
export HIP_VISIBLE_DEVICES=0,1
export HSA_XNACK=0
export HIP_FORCE_P2P=1
export GPU_SINGLE_ALLOC_PERCENT=100
export HSA_ENABLE_SDMA=1
export HSA_DISABLE_FRAGMENT_ALLOCATOR=0
export GPU_MAX_ALLOC_PERCENT=100
export USE_MLOCK=true
export GGML_CUDA_PDL=1
export LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:/home/srcds/dev/rocm6.1_llama.cpp/build-vega20/bin:/opt/rocm-6.1.0/lib
```

### Runtime env rationale

| Var | Value | Why |
|---|---|---|
| `HIP_GRAPH=1` | Enable HIP graph capture | Reduces per-kernel dispatch overhead |
| `HSA_OVERRIDE_GFX_VERSION=9.0.6` | Force gfx906 detection | Required — runtime may misdetect Vega 20 |
| `HIP_VISIBLE_DEVICES=0,1` | Only AMD GPUs visible to HIP | Excludes APU integrated graphics |
| `HSA_XNACK=0` | Disable GPU memory fault retry | Production mode, no debugging overhead |
| `HIP_FORCE_P2P=1` | Force peer-to-peer between AMD GPUs | Direct D2D copies between the 2x Vega 20 |
| `HSA_ENABLE_SDMA=1` | Use SDMA engine for memory copies | Dedicated DMA engine, faster than compute shader copies |
| `HSA_DISABLE_FRAGMENT_ALLOCATOR=0` | Allow fragment allocation | Needed for tight VRAM situations |
| `GPU_SINGLE_ALLOC_PERCENT=100` | Allow 100% single allocation | Needed for large model weight buffers |
| `GPU_MAX_ALLOC_PERCENT=100` | Allow 100% max allocation | Same |
| `USE_MLOCK=true` | Lock model in RAM | Prevents swapping, reduces latency |
| `GGML_CUDA_PDL=1` | Programmatic dependent launch | Overlaps kernel dispatch (tested: neutral but harmless) |
| `GGML_CUDA_CUBLAS_COMPUTE_TYPE=f16` | F16 compute for rocBLAS | Inert on HIP (rocBLAS picks internally) but harmless |

### Env vars tested but NOT set (no improvement)

| Var | Result |
|---|---|
| `HSA_ENABLE_PEER_SDMA=1` | Tie (no measurable effect) |
| `GPU_NUM_COMPUTE_RINGS=4` | Tie |
| `GPU_MAX_HW_QUEUES=8` | Tie |
| `HSA_SDMA_WAIT_IDLE=0` | Tie |
| `ROCBLAS_USE_HIPBLASLT=1` | Tie |

## Production server command

```bash
$LD_LIBRARY_PATH_LEADING/llama-server \
    -m ~/ai/ai/Qwen3.6-27B-Fable-Fus-711-UnHeretic-NM-DAU-NEO-MAX-NEO-MTP-Q8_0.gguf \
    -c 130000 --threads-batch 10 --threads 9 --no-mmap -fa on -ngl 333 \
    -b 16384 -ub 384 --ctx-checkpoints 30 \
    --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0.0 \
    --presence_penalty 0.0 --repeat-penalty 1.0 \
    --device rocm0,vulkan1,rocm1 --port 8009 -np 1 \
    -ts 43,22,35 -mg 0 \
    --reasoning-preserve --reasoning on --spec-type draft-mtp --spec-draft-n-max 3 \
    -cram 20000 --reasoning-format deepseek \
    --chat-template-file ~/dev/llama.cpp/q36chat_template.jinja \
    --pipeline-parallel auto -sm cost
```

### Command rationale

| Flag | Value | Why |
|---|---|---|
| `-c 130000` | 130K context | Maximum that fits VRAM with all weights offloaded |
| `-ngl 333` | All layers on GPU | Full GPU offload (65 layers + output) |
| `-ub 384` | Micro-batch size | Optimal for Vega 20 VRAM (higher = slower, tested) |
| `--ctx-checkpoints 30` | Context checkpointing | Enables prompt cache slot save/restore |
| `-fa on` | Flash attention | Required for large context |
| `--device rocm0,vulkan1,rocm1` | Device order | Fast-slow-fast: slow device (vulkan) in middle for pipeline overlap |
| `-ts 43,22,35` | Tensor split | 43% rocm0, 22% vulkan1, 35% rocm1 |
| `-mg 0` | Main GPU = rocm0 | Sampling on first device |
| `--spec-type draft-mtp --spec-draft-n-max 3` | MTP speculative decoding | 76% acceptance rate, n=3 is optimal (n=4 regresses, tested) |
| `-cram 20000` | Prompt cache RAM limit | 20GB for prompt caching |
| `--pipeline-parallel auto` | Pipeline parallelism | Overlaps cross-device transfers with compute (+18-25% TG) |
| `-sm cost` | Cost-weighted split | For hybrid models, shifts ~1 layer off slow device (+3-4% TG with PP on) |

## Patches applied (3 commits on top of upstream)

### Commit 1: `--pipeline-parallel` flag + MTP fixes (10 files)
- Explicit pipeline parallelism control (on/off/auto)
- MTP draft context VRAM savings
- Per-device context fitting with pinned -ngl
- HIP VEC flash-attention for quantized KV

### Commit 2: Vega 20 MMQ tile config (2 files)
- Custom MMQ tile configuration for gfx906's 64KB LDS and wavefront size
- New file: `ggml/src/ggml-cuda/mmq-config-vega.cuh`

### Commit 3: COST split mode (5 files)
- New `-sm cost` split mode for hybrid models
- Weights layer assignment by compute cost (Mamba=1, attention=4)
- ~3-4% TG improvement on hybrid models with mixed-speed multi-GPU + PP on
- Degenerates to LAYER mode for non-hybrid models (no regression)

## Measured performance (COST + PP on, c=120000)

| Metric | Value |
|---|---|
| TG (token generation) | ~23.3 tok/s |
| PP (prompt processing) | ~170 tok/s |
| MTP acceptance | ~76% |
| Graph splits | 4 (rocm0 -> vulkan1 -> rocm1 -> rocm0) |

## Rebuild from scratch

```bash
cd /home/srcds/dev/rocm6.1_llama.cpp
rm -rf build-vega20
cmake -S . -B build-vega20 \
    -DCMAKE_BUILD_TYPE=Release \
    -DGGML_HIP=ON \
    -DAMDGPU_TARGETS=gfx906 \
    -DGPU_TARGETS=gfx906 \
    -DGGML_HIP_GRAPHS=ON \
    -DGGML_HIP_NO_VMM=ON \
    -DGGML_CUDA_FORCE_MMQ=ON \
    -DGGML_LTO=OFF \
    -DGGML_VULKAN=ON \
    -DCMAKE_HIP_FLAGS="-ffast-math -fno-math-errno" \
    -DCMAKE_EXE_LINKER_FLAGS="-L/opt/rocm-6.1.0/lib -L/home/srcds/rocm-gfx906-xnack/lib" \
    -DCMAKE_SHARED_LINKER_FLAGS="-L/opt/rocm-6.1.0/lib -L/home/srcds/rocm-gfx906-xnack/lib"
cmake --build build-vega20 --target llama-server llama-bench -j$(nproc)
```
