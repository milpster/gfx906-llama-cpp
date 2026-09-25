// H2D bandwidth: pageable vs mlock vs hipHostRegister vs hipHostMalloc (gfx906 probe)
#include <hip/hip_runtime.h>
#include <cstdio>
#include <cstring>
#include <ctime>
#include <sys/mman.h>

static double now_s() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static double bench_h2d(const void * src, void * dst, size_t bytes) {
    // one warmup then two timed passes, sync each
    hipMemcpy(dst, src, bytes, hipMemcpyHostToDevice);
    hipDeviceSynchronize();
    double best = 1e9;
    for (int r = 0; r < 2; ++r) {
        double t0 = now_s();
        hipMemcpy(dst, src, bytes, hipMemcpyHostToDevice);
        hipDeviceSynchronize();
        double dt = now_s() - t0;
        if (dt < best) best = dt;
    }
    return bytes / best / (1024.0 * 1024.0 * 1024.0);
}

int main(int argc, char ** argv) {
    const size_t gb = argc > 1 ? atol(argv[1]) : 2;
    const size_t bytes = gb << 30;

    void * dev = nullptr;
    hipMalloc(&dev, bytes);

    void * pageable = malloc(bytes);
    memset(pageable, 1, bytes);
    printf("pageable      : %.2f GB/s\n", bench_h2d(pageable, dev, bytes));

    void * locked = mmap(nullptr, bytes, PROT_READ | PROT_WRITE,
                         MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    memset(locked, 1, bytes);
    mlock(locked, bytes);
    printf("mlock         : %.2f GB/s\n", bench_h2d(locked, dev, bytes));

    hipError_t err = hipHostRegister(locked, bytes, hipHostRegisterPortable | hipHostRegisterReadOnly);
    if (err != hipSuccess) {
        printf("hipHostRegister failed: %s\n", hipGetErrorString(err));
    } else {
        double t0 = now_s();
        (void) t0;
        printf("mlock+reg     : %.2f GB/s\n", bench_h2d(locked, dev, bytes));
    }

    void * pinned = nullptr;
    if (hipHostMalloc(&pinned, bytes, hipHostMallocDefault) == hipSuccess) {
        memset(pinned, 1, bytes);
        printf("hipHostMalloc : %.2f GB/s\n", bench_h2d(pinned, dev, bytes));
    }
    return 0;
}
