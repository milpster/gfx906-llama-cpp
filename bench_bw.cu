// Minimal HBM2 streaming read benchmark for gfx906
#include <cstdio>
#include <cstdlib>
#include <chrono>
#include <hip/hip_runtime.h>

__global__ void bw_read(const char* __restrict__ data, size_t nbytes, unsigned long long* result) {
    extern __shared__ unsigned long long ssum[];
    size_t tid = threadIdx.x;
    size_t gtid = (size_t)blockIdx.x * blockDim.x + threadIdx.x;
    size_t stride = (size_t)gridDim.x * blockDim.x;

    const int4* data4 = (const int4*)data;
    size_t n4 = nbytes / 16;

    unsigned long long sum = 0;
    for (size_t i = gtid; i < n4; i += stride) {
        int4 v = __ldg(&data4[i]);
        sum += (unsigned)v.x + (unsigned)v.y + (unsigned)v.z + (unsigned)v.w;
    }
    ssum[tid] = sum;
    __syncthreads();

    for (int s = blockDim.x / 2; s > 0; s >>= 1) {
        if (tid < s) ssum[tid] += ssum[tid + s];
        __syncthreads();
    }
    if (tid == 0) atomicAdd(result, ssum[0]);
}

#define HIP_CHECK(x) do { hipError_t err = x; if (err != hipSuccess) { fprintf(stderr, "HIP error at %s:%d: %s\n", __FILE__, __LINE__, hipGetErrorString(err)); exit(1); } } while(0)

int main(int argc, char** argv) {
    int device = argc > 1 ? atoi(argv[1]) : 0;
    HIP_CHECK(hipSetDevice(device));

    size_t nbytes = (argc > 2) ? atol(argv[2]) * 1024ULL * 1024 * 1024 : 2ULL * 1024 * 1024 * 1024;
    char* d_data;
    unsigned long long* d_result;
    HIP_CHECK(hipMalloc(&d_data, nbytes));
    HIP_CHECK(hipMalloc(&d_result, sizeof(unsigned long long)));
    HIP_CHECK(hipMemset(d_data, 1, nbytes));

    printf("Device %d, testing %zu MB streaming read:\n", device, nbytes / (1024*1024));

    int configs[] = {60, 120, 180, 240};
    int threads = 256;

    for (int ci = 0; ci < 4; ci++) {
        int blocks = configs[ci];
        int smem = threads * sizeof(unsigned long long);
        int wf_per_block = threads / 64;
        int wf_per_cu = blocks * wf_per_block / 60;

        // Warmup
        HIP_CHECK(hipMemset(d_result, 0, sizeof(unsigned long long)));
        bw_read<<<blocks, threads, smem>>>(d_data, nbytes, d_result);
        HIP_CHECK(hipDeviceSynchronize());

        double best_ms = 1e9;
        for (int run = 0; run < 5; run++) {
            HIP_CHECK(hipMemset(d_result, 0, sizeof(unsigned long long)));
            auto start = std::chrono::high_resolution_clock::now();
            bw_read<<<blocks, threads, smem>>>(d_data, nbytes, d_result);
            HIP_CHECK(hipDeviceSynchronize());
            auto end = std::chrono::high_resolution_clock::now();
            double ms = std::chrono::duration<double, std::milli>(end - start).count();
            best_ms = (ms < best_ms) ? ms : best_ms;
        }

        double gbs = (double)nbytes / (best_ms / 1000.0) / 1e9;
        printf("  blocks=%3d  WF/block=%d  WF/CU~%2d  %5.0f GB in %7.1f ms = %6.1f GB/s\n",
               blocks, wf_per_block, wf_per_cu, nbytes/1e9, best_ms, gbs);
    }

    (void)hipFree(d_data);
    (void)hipFree(d_result);
    return 0;
}
