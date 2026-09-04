// VRAM integrity test for gfx906 rigs: allocate near-full device memory,
// write a deterministic hash pattern, read back and verify. Two passes with
// different patterns catch stuck/bridged bits that survive one pattern.
// Usage: HSA_OVERRIDE_GFX_VERSION=9.0.6 ./vram-test <dev> <mib> [passes]
#include <cstdio>
#include <cstdint>
#include <vector>
#include <hip/hip_runtime.h>

#define HIP_CHECK(x) do { hipError_t e = (x); if (e != hipSuccess) { \
    fprintf(stderr, "HIP error %s at %s:%d\n", hipGetErrorString(e), __FILE__, __LINE__); return 1; } } while (0)

__global__ void fill_kernel(uint64_t * buf, size_t n, uint64_t salt) {
    size_t i = (size_t) blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) return;
    uint64_t x = (uint64_t) i + salt * 0x9E3779B97F4A7C15ull;
    x ^= x >> 33; x *= 0xFF51AFD7ED558CCDull; x ^= x >> 33;
    buf[i] = x;
}

__global__ void verify_kernel(const uint64_t * buf, size_t n, uint64_t salt, uint64_t * bad) {
    size_t i = (size_t) blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) return;
    uint64_t x = (uint64_t) i + salt * 0x9E3779B97F4A7C15ull;
    x ^= x >> 33; x *= 0xFF51AFD7ED558CCDull; x ^= x >> 33;
    if (buf[i] != x) atomicAdd(bad, 1);
}

int main(int argc, char ** argv) {
    if (argc < 3) { fprintf(stderr, "usage: %s <dev> <mib> [passes]\n", argv[0]); return 2; }
    int dev = atoi(argv[1]);
    size_t mib = (size_t) atoi(argv[2]);
    int passes = argc > 3 ? atoi(argv[3]) : 2;

    HIP_CHECK(hipSetDevice(dev));
    hipDeviceProp_t prop;
    HIP_CHECK(hipGetDeviceProperties(&prop, dev));
    printf("device %d: %s, %.1f MiB free / %.1f MiB total\n", dev, prop.name,
            prop.totalGlobalMem ? 0.0 : 0.0, prop.totalGlobalMem / 1048576.0);

    size_t bytes = mib * 1024 * 1024;
    size_t n = bytes / 8;
    uint64_t * buf = nullptr;
    hipError_t e = hipMalloc(&buf, bytes);
    if (e != hipSuccess) { fprintf(stderr, "alloc %.1f MiB failed: %s\n", mib / 1.0, hipGetErrorString(e)); return 1; }
    printf("allocated %zu MiB\n", bytes / 1048576);

    size_t block = 256;
    size_t grid = (n + block - 1) / block;
    uint64_t * bad = nullptr;
    HIP_CHECK(hipMalloc(&bad, 8));
    int failures = 0;

    for (int p = 0; p < passes; ++p) {
        uint64_t salt = 0x1234567 + p;
        HIP_CHECK(hipMemset(bad, 0, 8));
        fill_kernel<<<grid, block>>>(buf, n, salt);
        HIP_CHECK(hipDeviceSynchronize());
        verify_kernel<<<grid, block>>>(buf, n, salt, bad);
        HIP_CHECK(hipDeviceSynchronize());
        uint64_t hbad = 0;
        HIP_CHECK(hipMemcpy(&hbad, bad, 8, hipMemcpyDeviceToHost));
        printf("pass %d (salt %#lx): %llu mismatched words\n", p, (unsigned long) salt, (unsigned long long) hbad);
        if (hbad) failures++;
    }
    printf(failures ? "VERDICT: FAIL\n" : "VERDICT: PASS\n");
    return failures ? 1 : 0;
}
