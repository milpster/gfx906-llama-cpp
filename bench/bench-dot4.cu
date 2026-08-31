// gfx906 dp4a (v_dot4_u32_u8) issue-rate microbenchmark.
// Answers: how many int8 dot-product MACs/s can one Vega 20 actually sustain?
// Compare against MMQ demand derived from server PP throughput - see bench/README.md.
//
// build: hipcc -O3 --offload-arch=gfx906 bench-dot4.cu -o bench-dot4
// run:   ./bench-dot4 [device] [iters_per_thread]

#include <cstdio>
#include <cstdlib>
#include <chrono>
#include <hip/hip_runtime.h>

__device__ __forceinline__ unsigned int dot4(unsigned int a, unsigned int b, unsigned int c) {
    return (unsigned int) __builtin_amdgcn_sdot4((int) a, (int) b, (int) c, false);
}

// independent register chains; nothing touches memory inside the loop.
// 8 independent accumulators exposed so the compiler cannot serialize them.
__global__ void dot4_rate(unsigned long long* sink, int iters) {
    unsigned int a0 = threadIdx.x * 3 + 1, b0 = threadIdx.x * 5 + 2;
    unsigned int a1 = a0 ^ 0x55aa55aau, b1 = b0 ^ 0x0f0f0f0fu;
    unsigned int a2 = a0 + 0x01010101u, b2 = b0 + 0x10101010u;
    unsigned int a3 = a1 ^ 0x77777777u, b3 = b1 + 0x11111111u;
    unsigned int a4 = a2 ^ 0x33333333u, b4 = b2 + 0x01000100u;
    unsigned int a5 = a3 + 0x00100010u, b5 = b3 ^ 0x66666666u;
    unsigned int a6 = a4 ^ 0x99999999u, b6 = b4 + 0x00010001u;
    unsigned int a7 = a5 + 0x01001000u, b7 = b5 ^ 0xaaaaaaaau;

    unsigned int acc = blockIdx.x;
    for (int i = 0; i < iters; ++i) {
        acc ^= dot4(a0, b0, acc);
        acc ^= dot4(a1, b1, acc);
        acc ^= dot4(a2, b2, acc);
        acc ^= dot4(a3, b3, acc);
        acc ^= dot4(a4, b4, acc);
        acc ^= dot4(a5, b5, acc);
        acc ^= dot4(a6, b6, acc);
        acc ^= dot4(a7, b7, acc);
        a0 += acc; b0 ^= acc; a1 ^= b1; b1 += a1;  // rotate inputs, defeat constant folding
    }
    if (acc == 0xdeadbeefu) atomicAdd(sink, 1);  // keep everything live
}

#define HIP_CHECK(x) do { hipError_t err = x; if (err != hipSuccess) { \
    fprintf(stderr, "HIP error at %s:%d: %s\n", __FILE__, __LINE__, hipGetErrorString(err)); exit(1); } } while(0)

int main(int argc, char** argv) {
    int device = argc > 1 ? atoi(argv[1]) : 0;
    HIP_CHECK(hipSetDevice(device));

    hipDeviceProp_t prop;
    HIP_CHECK(hipGetDeviceProperties(&prop, device));
    printf("device %d: %s (%s), %d CUs, warp %d\n",
           device, prop.name, prop.gcnArchName, prop.multiProcessorCount, prop.warpSize);

    const int iters = argc > 2 ? atoi(argv[2]) : 20000;

    // enough blocks to fill every CU several times over; 256 threads/block (4 wave64s)
    int blocks = prop.multiProcessorCount * 8;

    unsigned long long* sink;
    HIP_CHECK(hipMalloc(&sink, sizeof(unsigned long long)));
    HIP_CHECK(hipMemset(sink, 0, sizeof(unsigned long long)));

    // warmup
    dot4_rate<<<blocks / 4, 256>>>(sink, 100);
    HIP_CHECK(hipDeviceSynchronize());

    auto t0 = std::chrono::steady_clock::now();
    dot4_rate<<<blocks, 256>>>(sink, iters);
    HIP_CHECK(hipDeviceSynchronize());
    auto t1 = std::chrono::steady_clock::now();

    double secs = std::chrono::duration<double>(t1 - t0).count();
    double dot4_total = (double) blocks * 256.0 * iters * 8.0;  // 8 dp4a per loop iter
    double macs = dot4_total * 4.0;

    printf("blocks=%d threads=256 iters=%d  time=%.3f s\n", blocks, iters, secs);
    printf("dp4a rate : %.3f T-instr/s\n", dot4_total / secs / 1e12);
    printf("int8 MACs : %.3f T-MAC/s  (= %.3f TOPS)\n", macs / secs / 1e12, 2.0 * macs / secs / 1e12);
    printf("vs MMQ demand per VII at pp1=324 (80/93 of layers): 0.940 T-instr/s, 3.76 T-MAC/s\n");
    return 0;
}
