// rd-trace: LD_PRELOAD shim timestamping HIP launches for TG round
// decomposition. Extends the rd2d-count pattern (E115): satisfies the
// versioned symbols libggml-hip references via rd-trace.map (hip_4.2 +
// hip_4.3 nodes), so plain LD_PRELOAD interposition works on ROCm 6.1.
// Records kernel launches / memcpys / memsets / graph launches + a
// gpu_busy_percent sampler thread (amdgpu sysfs) into an mmap'd ring
// file; survives SIGKILL (mmap writes hit the page cache as they go).
// Run servers with GGML_CUDA_DISABLE_GRAPHS=1 so individual
// hipLaunchKernel calls are visible (graphs are TG-neutral, E119.1.1).
// Usage (see bench/README.md):
//   RD_TRACE_FILE=/tmp/opencode/rd-trace.bin RD_TRACE_MB=512
//   LD_PRELOAD=$PWD/rd-trace.so .../llama-server ...
// Post-process: python3 rd-trace-analyze.py /tmp/opencode/rd-trace.bin

#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>

// record kinds
enum { RK_KERNEL = 0, RK_MEMCPY = 1, RK_MEMSET = 2, RK_GRAPH = 3, RK_BUSY = 4, RK_MARKER = 5, RK_SYNC = 6 };

#pragma pack(push, 1)
typedef struct {
    uint64_t ts_ns;
    uint64_t stream;   // hipStream_t value or graph exec
    uint64_t a0;       // grid.x / size / busy pct / marker id
    uint64_t a1;       // grid.y | blockDim packed
    uint64_t a2;       // grid.z | blockDim packed
    uint32_t shm;      // sharedMemBytes or memset val/kind
    uint8_t  kind;
    uint8_t  pad[3];
} rec_t;               // 48 bytes
#pragma pack(pop)

_Static_assert(sizeof(rec_t) == 48, "record size");

static rec_t * ring = NULL;
static size_t   ring_recs = 0;
static _Atomic size_t ring_pos = 0;       // multi-producer ticket
static int      busy_cards[8];
static int      n_busy_cards = 0;
static int      sampler_ms = 20;
static struct timespec t0;

static uint64_t now_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC_RAW, &ts);
    int64_t d = (int64_t)(ts.tv_sec - t0.tv_sec) * 1000000000ll
              + (int64_t)ts.tv_nsec - (int64_t)t0.tv_nsec;
    return d > 0 ? (uint64_t)d : 0;
}

static void rec_put(uint8_t kind, uint64_t stream, uint64_t a0, uint64_t a1, uint64_t a2, uint32_t shm) {
    if (!ring) return;
    size_t i = atomic_fetch_add(&ring_pos, 1);
    if (i >= ring_recs) return;             // past capacity: drop (tail kept by sizing)
    rec_t * r = &ring[i % ring_recs];
    r->ts_ns = now_ns(); r->stream = stream;
    r->a0 = a0; r->a1 = a1; r->a2 = a2; r->shm = shm;
    r->kind = kind;
}

// Lazy init on the FIRST interposed HIP call: LD_PRELOAD reaches every
// child (bash wrappers, the python lane client), and a constructor-time
// open(O_TRUNC) in each of them wipes the server's records - the client
// runs after the server and destroyed its trace (E120 first window).
// Only HIP-calling processes may create/truncate the ring.
static void lazy_init(void) {
    static _Atomic int done = 0;
    if (atomic_exchange(&done, 1)) return;
    clock_gettime(CLOCK_MONOTONIC_RAW, &t0);
    const char * path = getenv("RD_TRACE_FILE");
    if (!path) return;
    long mb = 512;
    const char * mb_s = getenv("RD_TRACE_MB");
    if (mb_s) mb = atol(mb_s);
    if (mb <= 0) return;
    size_t bytes = (size_t)mb << 20;
    ring_recs = bytes / sizeof(rec_t);
    int fd = open(path, O_RDWR | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) return;
    if (ftruncate(fd, (off_t)bytes) != 0) { close(fd); return; }
    void * m = mmap(NULL, bytes, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    close(fd);
    if (m == MAP_FAILED) { ring = NULL; ring_recs = 0; return; }
    ring = (rec_t *)m;
    madvise(m, bytes, MADV_SEQUENTIAL);
    const char * ms_s = getenv("RD_TRACE_BUSY_MS");
    if (ms_s) sampler_ms = atoi(ms_s);
    if (sampler_ms > 0) {
        for (int c = 0; c < 64 && n_busy_cards < 8; c++) {
            char p[128];
            snprintf(p, sizeof(p), "/sys/class/drm/card%d/device/gpu_busy_percent", c);
            if (access(p, R_OK) == 0) busy_cards[n_busy_cards++] = c;
        }
    }
    rec_put(RK_MARKER, 0, 0x54414345525430ull, 0, 0, 0); // "TRACER0"
}

static void * sampler_loop(void * arg) {
    (void)arg;
    char p[128];
    while (1) {
        for (int i = 0; i < n_busy_cards; i++) {
            snprintf(p, sizeof(p), "/sys/class/drm/card%d/device/gpu_busy_percent", busy_cards[i]);
            int fd = open(p, O_RDONLY);
            if (fd >= 0) {
                char buf[16] = {0};
                ssize_t n = read(fd, buf, sizeof(buf) - 1);
                close(fd);
                if (n > 0) rec_put(RK_BUSY, 0, (uint64_t)busy_cards[i], (uint64_t)atoi(buf), 0, 0);
            }
        }
        usleep((useconds_t)sampler_ms * 1000);
    }
    return NULL;
}

// start the sampler on first HIP call (after init decided the card set)
static void maybe_start_sampler(void) {
    lazy_init();
    static _Atomic int started = 0;
    static pthread_t th;
    if (n_busy_cards > 0 && !atomic_exchange(&started, 1)) {
        pthread_create(&th, NULL, sampler_loop, NULL);
        pthread_detach(th);
    }
}

typedef struct { unsigned x, y, z; } dim3_t;

typedef int (*launch_fn)(const void *, dim3_t, dim3_t, void **, size_t, void *);
int hipLaunchKernel(const void * func, dim3_t gridDim, dim3_t blockDim, void ** args, size_t sharedMemBytes, void * stream) {
    static launch_fn real;
    if (!real) real = (launch_fn)dlsym(RTLD_NEXT, "hipLaunchKernel");
    maybe_start_sampler();
    rec_put(RK_KERNEL, (uint64_t)stream,
            gridDim.x,
            ((uint64_t)gridDim.y << 32) | blockDim.x,
            ((uint64_t)gridDim.z << 32) | blockDim.y,
            (uint32_t)sharedMemBytes);
    return real(func, gridDim, blockDim, args, sharedMemBytes, stream);
}

typedef int (*cpy_fn)(void *, const void *, size_t, int);
typedef int (*cpy_async_fn)(void *, const void *, size_t, int, void *);

int hipMemcpy(void * dst, const void * src, size_t size, int kind) {
    static cpy_fn real;
    if (!real) real = (cpy_fn)dlsym(RTLD_NEXT, "hipMemcpy");
    maybe_start_sampler();
    uint64_t ts = now_ns();
    int r = real(dst, src, size, kind);
    rec_put(RK_MEMCPY, 0, size, now_ns() - ts, 0, (uint32_t)kind);
    return r;
}

int hipMemcpyAsync(void * dst, const void * src, size_t size, int kind, void * stream) {
    static cpy_async_fn real;
    if (!real) real = (cpy_async_fn)dlsym(RTLD_NEXT, "hipMemcpyAsync");
    maybe_start_sampler();
    rec_put(RK_MEMCPY, (uint64_t)stream, size, 0, 0, (uint32_t)kind);
    return real(dst, src, size, kind, stream);
}

typedef int (*memset_async_fn)(void *, int, size_t, void *);
int hipMemsetAsync(void * dst, int value, size_t size, void * stream) {
    static memset_async_fn real;
    if (!real) real = (memset_async_fn)dlsym(RTLD_NEXT, "hipMemsetAsync");
    maybe_start_sampler();
    rec_put(RK_MEMSET, (uint64_t)stream, size, 0, 0, (uint32_t)value);
    return real(dst, value, size, stream);
}

typedef int (*graph_launch_fn)(void *, void *);
int hipGraphLaunch(void * graphExec, void * stream) {
    static graph_launch_fn real;
    if (!real) real = (graph_launch_fn)dlsym(RTLD_NEXT, "hipGraphLaunch");
    maybe_start_sampler();
    rec_put(RK_GRAPH, (uint64_t)graphExec, (uint64_t)stream, 0, 0, 0);
    return real(graphExec, stream);
}

// blocking-sync durations: splits host quiet time into GPU-dependency
// wait (sync) vs pure CPU machinery (everything else)
typedef int (*sync_fn)(void *);
int hipStreamSynchronize(void * stream) {
    static sync_fn real;
    if (!real) real = (sync_fn)dlsym(RTLD_NEXT, "hipStreamSynchronize");
    maybe_start_sampler();
    uint64_t ts = now_ns();
    int r = real(stream);
    rec_put(RK_SYNC, (uint64_t)stream, now_ns() - ts, 0, 0, 0);
    return r;
}

int hipEventSynchronize(void * event) {
    static sync_fn real;
    if (!real) real = (sync_fn)dlsym(RTLD_NEXT, "hipEventSynchronize");
    maybe_start_sampler();
    uint64_t ts = now_ns();
    int r = real(event);
    rec_put(RK_SYNC, (uint64_t)event, now_ns() - ts, 0, 0, 0);
    return r;
}
