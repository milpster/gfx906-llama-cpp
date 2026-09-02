// Standalone flash_attn_ext (fattn_tile path) microbenchmark for gfx906
// PP tuning. Drives the real ggml op through the HIP backend at production
// shapes (Qwen3.5-class: DKQ=DV=256, 24 Q heads / 4 KV heads, ub 384) so the
// backend's own launch switch picks the same kernel the server runs
// (flash_attn_tile<256,256,16,2,false,...> on the convert path).
//
// build: g++ -O2 -std=c++17 bench-fattn-tile.cpp -o bench-fattn-tile \
//          -I ../ggml/include -L ../build-dflash-novega/bin \
//          -lggml-hip -lggml-base -lggml -Wl,-rpath,$PWD/../build-dflash-novega/bin
// run:   HIP_VISIBLE_DEVICES=0 HSA_OVERRIDE_GFX_VERSION=9.0.6 HSA_XNACK=0 \
//        LD_LIBRARY_PATH=/home/srcds/rocm-gfx906-xnack/lib:../build-dflash-novega/bin:/opt/rocm-6.1.0/lib \
//        ./bench-fattn-tile [kv_len] [n_tok] [iters]
//
// default: kv 120000, tok 384 (the fill120k class), 30 iters.
// correctness: small-kv run diffed against the CPU backend, max-abs reported.

#include "ggml.h"
#include "ggml-cuda.h"
#include "ggml-alloc.h"
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <vector>
#include <algorithm>

struct Shapes {
    int dkq, dv, nh_q, nh_kv, kv, tok;
};

static void fill_uniform(float * p, int64_t n, unsigned seed) {
    for (int64_t i = 0; i < n; ++i) {
        p[i] = ((seed = seed * 1664525u + 1013904223u) >> 8 & 0xffff) / 65535.0f - 0.5f;
    }
}

static void fill_causal_mask(uint16_t * m16, int kv, int tok) {
    for (int j = 0; j < tok; ++j) {
        for (int i = 0; i < kv; ++i) {
            m16[j * (int64_t) kv + i] = (i <= (kv - tok) + j)
                ? ggml_fp32_to_fp16(0.0f) : ggml_fp32_to_fp16(-INFINITY);
        }
    }
}

struct Built {
    ggml_context * ctx;
    ggml_tensor * q, * k, * v, * m, * out;
    ggml_cgraph * gf;
    std::vector<float> hq, hk, hv;
    std::vector<uint16_t> hm;
};

static Built build(const Shapes & s) {
    Built b;
    struct ggml_init_params ip = {(size_t) 512 << 20, NULL, false};
    b.ctx = ggml_init(ip);
    b.q = ggml_new_tensor_4d(b.ctx, GGML_TYPE_F32, s.dkq, s.tok, s.nh_q, 1);
    b.k = ggml_new_tensor_4d(b.ctx, GGML_TYPE_F16, s.dkq, s.kv, s.nh_kv, 1);
    b.v = ggml_new_tensor_4d(b.ctx, GGML_TYPE_F16, s.dv,  s.kv, s.nh_kv, 1);
    b.m = ggml_new_tensor_4d(b.ctx, GGML_TYPE_F16, s.kv, s.tok, 1, 1);
    b.out = ggml_flash_attn_ext(b.ctx, b.q, b.k, b.v, b.m, 1.0f / sqrtf((float) s.dkq), 0.0f, 0.0f);
    b.gf = ggml_new_graph(b.ctx);
    ggml_build_forward_expand(b.gf, b.out);

    b.hq.resize(ggml_nbytes(b.q) / 4); fill_uniform(b.hq.data(), b.hq.size(), 1);
    b.hk.resize(ggml_nbytes(b.k) / 4); fill_uniform(b.hk.data(), b.hk.size(), 2);
    b.hv.resize(ggml_nbytes(b.v) / 4); fill_uniform(b.hv.data(), b.hv.size(), 3);
    b.hm.resize(ggml_nbytes(b.m) / 2); fill_causal_mask(b.hm.data(), s.kv, s.tok);
    return b;
}

static void upload_and_run(Built & b, ggml_backend_t backend, std::vector<float> & result) {
    ggml_backend_buffer * buf = ggml_backend_alloc_ctx_tensors(b.ctx, backend);
    ggml_backend_tensor_set(b.q, b.hq.data(), 0, ggml_nbytes(b.q));
    ggml_backend_tensor_set(b.k, b.hk.data(), 0, ggml_nbytes(b.k));
    ggml_backend_tensor_set(b.v, b.hv.data(), 0, ggml_nbytes(b.v));
    ggml_backend_tensor_set(b.m, b.hm.data(), 0, ggml_nbytes(b.m));
    if (ggml_backend_graph_compute(backend, b.gf) != GGML_STATUS_SUCCESS) {
        fprintf(stderr, "graph compute failed\n"); exit(1);
    }
    result.resize(ggml_nbytes(b.out) / 4);
    ggml_backend_tensor_get(b.out, result.data(), 0, ggml_nbytes(b.out));
    ggml_backend_buffer_free(buf);
}

int main(int argc, char ** argv) {
    Shapes s = {256, 256, 24, 4,
                argc > 1 ? atoi(argv[1]) : 120000,
                argc > 2 ? atoi(argv[2]) : 384};
    const int iters = argc > 3 ? atoi(argv[3]) : 30;

    ggml_time_init();

    {
        Shapes sc = s; sc.kv = 8192;
        Built bc = build(sc);
        Built br = build(sc);
        ggml_backend_t bcuda = ggml_backend_cuda_init(0);
        if (!bcuda) { fprintf(stderr, "cuda backend init failed\n"); return 1; }
        ggml_backend_t bcpu = ggml_backend_dev_init(ggml_backend_dev_by_type(GGML_BACKEND_DEVICE_TYPE_CPU), NULL);
        std::vector<float> res, ref;
        upload_and_run(bc, bcuda, res);
        upload_and_run(br, bcpu, ref);
        double maxabs = 0; int64_t nbad = 0;
        for (size_t i = 0; i < res.size(); ++i) {
            double d = fabs((double) res[i] - ref[i]);
            maxabs = std::max(maxabs, d);
            if (d > 1e-2) nbad++;
        }
        printf("correctness (kv=%d): max-abs %.5f, >1e-2: %ld/%zu\n", sc.kv, maxabs, (long) nbad, res.size());
        ggml_free(bc.ctx); ggml_free(br.ctx);
        ggml_backend_free(bcuda); ggml_backend_free(bcpu);
    }

    Built b = build(s);
    ggml_backend_t backend = ggml_backend_cuda_init(0);
    ggml_backend_buffer * buf = ggml_backend_alloc_ctx_tensors(b.ctx, backend);
    ggml_backend_tensor_set(b.q, b.hq.data(), 0, ggml_nbytes(b.q));
    ggml_backend_tensor_set(b.k, b.hk.data(), 0, ggml_nbytes(b.k));
    ggml_backend_tensor_set(b.v, b.hv.data(), 0, ggml_nbytes(b.v));
    ggml_backend_tensor_set(b.m, b.hm.data(), 0, ggml_nbytes(b.m));
    ggml_backend_graph_compute(backend, b.gf);

    int64_t t0 = ggml_time_us();
    for (int i = 0; i < iters; ++i) {
        ggml_backend_graph_compute(backend, b.gf);
    }
    int64_t t1 = ggml_time_us();
    double ms = (t1 - t0) / 1000.0 / iters;
    double flops = 2.0 * 2.0 * s.dkq * (double) s.kv * s.tok * s.nh_q;
    printf("kv=%d tok=%d heads %d/%d: %.3f ms/op, %.2f TFLOP/s\n",
           s.kv, s.tok, s.nh_q, s.nh_kv, ms, flops / (ms * 1e-3) / 1e12);

    ggml_backend_buffer_free(buf);
    ggml_free(b.ctx);
    ggml_backend_free(backend);
    return 0;
}
