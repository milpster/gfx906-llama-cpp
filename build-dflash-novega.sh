#!/usr/bin/env bash
# Release build script: gfx906 HIP + Vulkan, VEGA_TUNE FATTN selector/geometry.
# Reproduces build-dflash-novega exactly (validated lanes 12.3-12.6 t/s,
# JOURNAL-2026-08-27.md E50-V2..E69). Flags recovered from CMakeCache.txt
# of the validated build + ggml/CMakeLists.txt defaults.
#
# Baseline = validated config (E82: vega MMQ/TOPK/GRAPHS tunes restored,
# pp 371 / fill 329 / tg 13.4, sha canonical). Remaining unmeasured opt-in:
#   HIP_FAST_MATH=1    -ffast-math -fno-math-errno (numerics change:
#                      temp-0 canonical sha will move; was on in the
#                      vega20/sync25 era, dropped since build-dflash)
# Useful vars: BUILD_DIR=build-ab1 FRESH=1 JOBS=16 TARGETS="llama-server"
#
# Runtime env (HSA_XNACK=0, HIP_FORCE_P2P=1, HIP_GRAPH=1, LD_LIBRARY_PATH
# with /home/srcds/rocm-gfx906-xnack/lib) lives in the launcher scripts,
# e.g. 2llama-start-iq6v-dflash2.sh; not needed at build time.

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
BUILD_DIR=${BUILD_DIR:-$SCRIPT_DIR/build-dflash-novega}
JOBS=${JOBS:-$(nproc)}
TARGETS=${TARGETS:-}

on_off() { [ "$1" = "1" ] && echo ON || echo OFF; }
VEGA_MMQ=$(on_off    "${VEGA_TUNE_MMQ:-1}")
VEGA_MMQ_DUALACC=$(on_off "${VEGA_TUNE_MMQ_DUALACC:-0}")
VEGA_TOPK=$(on_off   "${VEGA_TUNE_TOPK:-1}")
VEGA_GRAPHS=$(on_off "${VEGA_TUNE_GRAPHS:-1}")
HIP_FLAGS=""
[ "${HIP_FAST_MATH:-0}" = "1" ] && HIP_FLAGS="-ffast-math -fno-math-errno"

# ROCm 6.1 toolchain must be on PATH for hipcc/hipconfig discovery
export PATH=/opt/rocm-6.1.0/bin:$PATH
export HSA_OVERRIDE_GFX_VERSION=9.0.6

if [ "${FRESH:-0}" = "1" ]; then
    rm -rf "$BUILD_DIR"
fi

# D11 pins: without these find_package(HIP) resolves via /opt/rocm
# (= ROCm 7.15.0) and injects its headers into the 6.1 clang build
cmake -B "$BUILD_DIR" -S "$SCRIPT_DIR" \
    -DCMAKE_HIP_COMPILER=/opt/rocm-6.1.0/lib/llvm/bin/clang \
    -Dhip_DIR=/opt/rocm-6.1.0/lib/cmake/hip \
    -Dhipblas_DIR=/opt/rocm-6.1.0/lib/cmake/hipblas \
    -Drocblas_DIR=/opt/rocm-6.1.0/lib/cmake/rocblas \
    -Dhsa-runtime64_DIR=/opt/rocm-6.1.0/lib/cmake/hsa-runtime64 \
    -Damd_comgr_DIR=/opt/rocm-6.1.0/lib/cmake/amd_comgr \
    -DAMDDeviceLibs_DIR=/opt/rocm-6.1.0/lib/cmake/AMDDeviceLibs \
    -DGGML_CUDA_FA_ALL_QUANTS=ON \
    -DCMAKE_BUILD_TYPE=Release \
    -DGGML_HIP=ON \
    -DAMDGPU_TARGETS=gfx906 \
    -DGGML_VULKAN=ON \
    -DGGML_CUDA_VEGA_TUNE=ON \
    -DGGML_CUDA_VEGA_TUNE_FATTN=ON \
    -DGGML_CUDA_VEGA_TUNE_MMQ="$VEGA_MMQ" \
    -DGGML_CUDA_VEGA_TUNE_MMQ_DUALACC="$VEGA_MMQ_DUALACC" \
    -DGGML_CUDA_VEGA_TUNE_TOPK="$VEGA_TOPK" \
    -DGGML_CUDA_VEGA_TUNE_GRAPHS="$VEGA_GRAPHS" \
    -DGGML_HIP_NO_VMM=ON \
    -DGGML_HIP_MMQ_MFMA=ON \
    -DCMAKE_HIP_FLAGS="$HIP_FLAGS"

# shellcheck disable=SC2086
cmake --build "$BUILD_DIR" -j"$JOBS" ${TARGETS:+--target $TARGETS}

echo
echo "== artifacts"
ls -la "$BUILD_DIR/bin/llama-server" "$BUILD_DIR"/bin/libggml-hip.so*
readelf -h "$BUILD_DIR/bin/llama-server" > /dev/null \
    && echo "llama-server: valid ELF"
echo
echo "== config actually in the cache"
grep -E "^GGML_CUDA_VEGA_TUNE(_FATTN|_MMQ|_MMQ_DUALACC|_TOPK|_GRAPHS)?:BOOL|^CMAKE_HIP_FLAGS:STRING" \
    "$BUILD_DIR/CMakeCache.txt" | grep -v ADVANCED
