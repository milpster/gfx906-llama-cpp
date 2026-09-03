// rd2d-count: LD_PRELOAD shim counting HIP memcpy calls by kind + size.
// Purpose: screen upstream PR #28178 relevance (small D2D copies routed to
// SDMA via cudaMemcpyAsync on ROCm) without a full rocprof trace.
// Usage: RD2D_OUT=/tmp/rd2d.txt LD_PRELOAD=$PWD/rd2d-count.so ...server...
// Counters are atomics; histogram dumped at process exit (dtor may be
// skipped on SIGKILL - SIGTERM is handled by the dtor path via atexit).

#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

// hipMemcpyKind: 0=H2H 1=H2D 2=D2H 3=D2D 4=Default
static _Atomic unsigned long long cnt[5][16];   // [kind][log2(size) bucket, capped at 15]
static _Atomic unsigned long long bytes[5];
static _Atomic unsigned long long total_calls;

static void dump(void) {
    const char *out = getenv("RD2D_OUT");
    FILE *f = out ? fopen(out, "w") : stderr;
    if (!f) f = stderr;
    fprintf(f, "# kind size2^ n_calls n_bytes (kinds: 0=H2H 1=H2D 2=D2H 3=D2D 4=default; bucket 32768 means >=32KB)\n");
    static const char *kn[5] = {"H2H", "H2D", "D2H", "D2D", "DEF"};
    for (int k = 0; k < 5; k++) {
        for (int b = 0; b < 16; b++) {
            unsigned long long c = atomic_load(&cnt[k][b]);
            if (c) fprintf(f, "%s %d %llu %llu\n", kn[k], 1 << b, c, c << b);
        }
        unsigned long long by = atomic_load(&bytes[k]);
        if (by) fprintf(f, "%s total_bytes %llu\n", kn[k], by);
    }
    fprintf(f, "TOTAL_CALLS %llu\n", atomic_load(&total_calls));
    if (f != stderr) fclose(f);
}

__attribute__((constructor)) static void init(void) { atexit(dump); }

static int bucket(size_t n) {
    int b = 0;
    while ((1ULL << b) < n && b < 15) b++;
    return b;
}

typedef int (*cpy_fn)(void *, const void *, size_t, int);
typedef int (*cpy_async_fn)(void *, const void *, size_t, int, void *);

int hipMemcpy(void *dst, const void *src, size_t size, int kind) {
    static cpy_fn real;
    if (!real) real = (cpy_fn)dlsym(RTLD_NEXT, "hipMemcpy");
    atomic_fetch_add(&total_calls, 1);
    if (kind >= 0 && kind <= 4) {
        atomic_fetch_add(&cnt[kind][bucket(size)], 1);
        atomic_fetch_add(&bytes[kind], size);
    }
    return real(dst, src, size, kind);
}

int hipMemcpyAsync(void *dst, const void *src, size_t size, int kind, void *stream) {
    static cpy_async_fn real;
    if (!real) real = (cpy_async_fn)dlsym(RTLD_NEXT, "hipMemcpyAsync");
    atomic_fetch_add(&total_calls, 1);
    if (kind >= 0 && kind <= 4) {
        atomic_fetch_add(&cnt[kind][bucket(size)], 1);
        atomic_fetch_add(&bytes[kind], size);
    }
    return real(dst, src, size, kind, stream);
}
