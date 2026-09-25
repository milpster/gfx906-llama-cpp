// LD_PRELOAD tracer: log backtraces of sleep calls to find the stall site
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <execinfo.h>

static int trace_fd(void) {
    const char * env = getenv("NS_TRACE_FD");
    return env ? atoi(env) : 2;
}

static void log_bt(const char * who) {
    void * bt[12];
    int n = backtrace(bt, 12);
    char head[128];
    int len = snprintf(head, sizeof head, "[ns-trace] %s pid=%d\n", who, (int) getpid());
    if (len > 0) {
        if (write(trace_fd(), head, len)) {}
    }
    backtrace_symbols_fd(bt, n, trace_fd());
    if (write(trace_fd(), "\n", 1)) {}
}

int nanosleep(const struct timespec * req, struct timespec * rem) {
    static int (* real)(const struct timespec *, struct timespec *);
    if (!real) {
        real = dlsym(RTLD_NEXT, "nanosleep");
    }
    log_bt("nanosleep");
    return real(req, rem);
}

int clock_nanosleep(clockid_t clk, int flags, const struct timespec * req, struct timespec * rem) {
    static int (* real)(clockid_t, int, const struct timespec *, struct timespec *);
    if (!real) {
        real = dlsym(RTLD_NEXT, "clock_nanosleep");
    }
    log_bt("clock_nanosleep");
    return real(clk, flags, req, rem);
}

unsigned int sleep(unsigned int s) {
    static unsigned int (* real)(unsigned int);
    if (!real) {
        real = dlsym(RTLD_NEXT, "sleep");
    }
    log_bt("sleep");
    return real(s);
}

int usleep(useconds_t us) {
    static int (* real)(useconds_t);
    if (!real) {
        real = dlsym(RTLD_NEXT, "usleep");
    }
    log_bt("usleep");
    return real(us);
}
