// bench/hipbw.cu — H2D bandwidth microbenchmark: pageable vs pinned host memory.
// E147.5: ground truth for the expert-staging pinning thesis on gfx906/ROCm 6.1.
// build: hipcc -O2 -o /tmp/opencode/hipbw bench/hipbw.cu
// usage: /tmp/opencode/hipbw [device] — copies 2 GiB per mode, 5 reps each.

#include <hip/hip_runtime.h>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <chrono>

#define HIPCHK(x) do { hipError_t e = (x); if (e != hipSuccess) { \
    fprintf(stderr, "HIP error %s at %s:%d\n", hipGetErrorString(e), __FILE__, __LINE__); exit(1); } } while (0)

int main(int argc, char ** argv) {
    int dev = argc > 1 ? atoi(argv[1]) : 0;
    HIPCHK(hipSetDevice(dev));

    hipDeviceProp_t prop;
    HIPCHK(hipGetDeviceProperties(&prop, dev));
    printf("device %d: %s\n", dev, prop.name);

    const size_t bytes = 2ull << 30; // 2 GiB
    void * dst = nullptr;
    HIPCHK(hipMalloc(&dst, bytes));

    // pageable
    {
        std::vector<char> h(bytes, 1);
        // warmup
        HIPCHK(hipMemcpy(dst, h.data(), bytes, hipMemcpyHostToDevice));
        HIPCHK(hipDeviceSynchronize());
        double best = 1e9;
        for (int r = 0; r < 5; r++) {
            auto t0 = std::chrono::steady_clock::now();
            HIPCHK(hipMemcpy(dst, h.data(), bytes, hipMemcpyHostToDevice));
            HIPCHK(hipDeviceSynchronize());
            double s = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
            if (s < best) best = s;
        }
        printf("pageable : 2 GiB in %.3f s = %.2f GB/s\n", best, bytes / best / 1e9);
    }

    // pinned
    {
        void * h = nullptr;
        HIPCHK(hipHostMalloc(&h, bytes, hipHostMallocDefault));
        char * hc = (char *) h;
        for (size_t i = 0; i < bytes; i += 4096) hc[i] = 1;
        HIPCHK(hipMemcpy(dst, h, bytes, hipMemcpyHostToDevice));
        HIPCHK(hipDeviceSynchronize());
        double best = 1e9;
        for (int r = 0; r < 5; r++) {
            auto t0 = std::chrono::steady_clock::now();
            HIPCHK(hipMemcpy(dst, h, bytes, hipMemcpyHostToDevice));
            HIPCHK(hipDeviceSynchronize());
            double s = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
            if (s < best) best = s;
        }
        printf("pinned   : 2 GiB in %.3f s = %.2f GB/s\n", best, bytes / best / 1e9);
        HIPCHK(hipHostFree(h));
    }

    // small-transfer storm: 512 x 2.7 MiB (mimics grouped expert copies), pinned
    {
        const int n = 512;
        const size_t sz = 24 * 128 * 1024; // ~3 MiB
        void * h = nullptr;
        HIPCHK(hipHostMalloc(&h, (size_t) n * sz, hipHostMallocDefault));
        for (size_t i = 0; i < (size_t) n * sz; i += 4096) ((char *) h)[i] = 1;
        HIPCHK(hipDeviceSynchronize());
        auto t0 = std::chrono::steady_clock::now();
        for (int i = 0; i < n; i++) {
            HIPCHK(hipMemcpyAsync((char *) dst + (size_t) i * sz, (char *) h + (size_t) i * sz, sz, hipMemcpyHostToDevice, 0));
            HIPCHK(hipStreamSynchronize(0)); // serialized like the scheduler's per-split waits
        }
        double s = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
        printf("storm    : %d x %.2f MiB serialized = %.3f s = %.2f GB/s\n", n, sz / 1048576.0, s, (double) n * sz / s / 1e9);
        HIPCHK(hipHostFree(h));
    }

    HIPCHK(hipFree(dst));
    return 0;
}
