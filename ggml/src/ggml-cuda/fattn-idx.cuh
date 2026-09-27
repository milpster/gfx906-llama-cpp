#pragma once

#include "common.cuh"
#include "fattn-common.cuh"

// indexed sparse attention: query row t attends only KV cells idx[i][t],
// filtered by the causal cutoff nvis[t]. replaces the [n_kv, n_tps] QSA mask
// chain: its {0, -inf} pattern is exactly (idx[i][t] < nvis[t]).

typedef struct { __half d; int8_t qs[32]; } fattn_idx_q8_0;
typedef struct { __half d; uint8_t qs[16]; } fattn_idx_q4_0;

template<ggml_type T>
static __device__ __forceinline__ float fattn_idx_el(const char * row, int d);

template<>
__device__ __forceinline__ float fattn_idx_el<GGML_TYPE_F16>(const char * row, int d) {
    return __half2float(((const __half *) row)[d]);
}

template<>
__device__ __forceinline__ float fattn_idx_el<GGML_TYPE_F32>(const char * row, int d) {
    return ((const float *) row)[d];
}

template<>
__device__ __forceinline__ float fattn_idx_el<GGML_TYPE_Q8_0>(const char * row, int d) {
    const fattn_idx_q8_0 * b = (const fattn_idx_q8_0 *) (row + (d >> 5) * sizeof(fattn_idx_q8_0));
    return __half2float(b->d) * b->qs[d & 31];
}

template<>
__device__ __forceinline__ float fattn_idx_el<GGML_TYPE_Q4_0>(const char * row, int d) {
    const fattn_idx_q4_0 * b = (const fattn_idx_q4_0 *) (row + (d >> 5) * sizeof(fattn_idx_q4_0));
    const uint8_t q = b->qs[d & 15];
    const int v = (d & 16) ? (q >> 4) : (q & 0xF);
    return __half2float(b->d) * (v - 8);
}

template<int D, ggml_type type_K, ggml_type type_V>
__launch_bounds__(128, 1)
static __global__ void flash_attn_ext_idx(
        const char * __restrict__ Q_ptr,
        const char * __restrict__ K_ptr,
        const char * __restrict__ V_ptr,
        const int  * __restrict__ idx_ptr,
        const int  * __restrict__ nvis_ptr,
        float      * __restrict__ dst_ptr,
        const float scale,
        const int   width,
        const int   n_tps,
        const int   n_head,
        const int   n_head_kv,
        const size_t q_nb1, const size_t q_nb2, const size_t q_nb3,
        const size_t k_nb1, const size_t k_nb2, const size_t k_nb3,
        const size_t v_nb1, const size_t v_nb2, const size_t v_nb3,
        const size_t idx_nb1, const size_t idx_nb3,
        const size_t dst_nb1, const size_t dst_nb2, const size_t dst_nb3) {

    constexpr int ni = D / WARP_SIZE;

    const int lane  = threadIdx.x % WARP_SIZE;
    const int qwarp = threadIdx.x / WARP_SIZE;
    const int t     = blockIdx.x * (blockDim.x / WARP_SIZE) + qwarp;
    if (t >= n_tps) {
        return;
    }

    const int h   = blockIdx.y;
    const int seq = blockIdx.z;

    const int kvh = h / (n_head / n_head_kv);

    const char * q_row = Q_ptr + seq*q_nb3 + h*q_nb2 + t*q_nb1;

    float qv[ni];
#pragma unroll
    for (int j = 0; j < ni; ++j) {
        qv[j] = *(const float *) (q_row + (lane + j*WARP_SIZE)*sizeof(float)) * scale;
    }

    const int nvis_t = nvis_ptr ? nvis_ptr[t] : INT_MAX;
    const int * idx_row = idx_ptr + seq*(int) (idx_nb3/sizeof(int)) + t*(int) (idx_nb1/sizeof(int));

    const char * k_head = K_ptr + seq*k_nb3 + kvh*k_nb2;
    const char * v_head = V_ptr + seq*v_nb3 + kvh*v_nb2;

    float m = -FLT_MAX;
    float l = 0.0f;
    float av[ni];
#pragma unroll
    for (int j = 0; j < ni; ++j) {
        av[j] = 0.0f;
    }

    for (int i = 0; i < width; ++i) {
        int p = lane == 0 ? idx_row[i] : 0;
        p = __shfl_sync(0xffffffffu, p, 0, 32);
        if (p < 0 || p >= nvis_t) {
            continue;
        }

        const char * kr = k_head + p*k_nb1;
        float kv[ni];
#pragma unroll
        for (int j = 0; j < ni; ++j) {
            kv[j] = fattn_idx_el<type_K>(kr, lane + j*WARP_SIZE);
        }

        float s = 0.0f;
#pragma unroll
        for (int j = 0; j < ni; ++j) {
            s += qv[j]*kv[j];
        }
        s = warp_reduce_sum(s);

        const float m_new = fmaxf(m, s);
        const float so = m > -FLT_MAX ? expf(m - m_new) : 0.0f;
        const float pv = expf(s - m_new);

        m = m_new;
        l = l*so + pv;

        const char * vr = v_head + p*v_nb1;
#pragma unroll
        for (int j = 0; j < ni; ++j) {
            av[j] = av[j]*so + pv*fattn_idx_el<type_V>(vr, lane + j*WARP_SIZE);
        }
    }

    const float inv_l = l > 0.0f ? 1.0f/l : 0.0f;
    float * out = dst_ptr + seq*(dst_nb3/sizeof(float)) + t*(dst_nb2/sizeof(float)) + h*(dst_nb1/sizeof(float));
#pragma unroll
    for (int j = 0; j < ni; ++j) {
        out[lane + j*WARP_SIZE] = av[j]*inv_l;
    }
}

template<int D>
static void fattn_idx_launch(ggml_backend_cuda_context & ctx, ggml_tensor * dst) {
    const ggml_tensor * Q = dst->src[0];
    const ggml_tensor * K = dst->src[1];
    const ggml_tensor * V = dst->src[2];
    const ggml_tensor * idx = dst->src[6];
    const ggml_tensor * nvis = dst->src[5];

    float scale;
    memcpy(&scale, dst->op_params, sizeof(scale));

    const int width    = idx->ne[0];
    const int n_tps    = Q->ne[1];
    const int n_head   = Q->ne[2];
    const int n_head_kv = K->ne[2];

    const int nwarps = 4;
    dim3 block(nwarps*WARP_SIZE);
    dim3 grid((n_tps + nwarps - 1) / nwarps, n_head, Q->ne[3]);

    cudaStream_t stream = ctx.stream();

#define FATTN_IDX_LAUNCH(type_K, type_V)                                                                              \
    flash_attn_ext_idx<D, type_K, type_V><<<grid, block, 0, stream>>>(                 \
            (const char *) Q->data, (const char *) K->data, (const char *) V->data,   \
            (const int *) idx->data, (const int *) (nvis ? nvis->data : nullptr),     \
            (float *) dst->data, scale, width, n_tps, n_head, n_head_kv,               \
            Q->nb[1], Q->nb[2], Q->nb[3],                                              \
            K->nb[1], K->nb[2], K->nb[3],                                              \
            V->nb[1], V->nb[2], V->nb[3],                                              \
            idx->nb[1], idx->nb[3],                                                    \
            dst->nb[1], dst->nb[2], dst->nb[3])

    switch (K->type) {
        case GGML_TYPE_F16:
            switch (V->type) {
                case GGML_TYPE_F16: FATTN_IDX_LAUNCH(GGML_TYPE_F16, GGML_TYPE_F16); break;
                case GGML_TYPE_Q8_0: FATTN_IDX_LAUNCH(GGML_TYPE_F16, GGML_TYPE_Q8_0); break;
                case GGML_TYPE_Q4_0: FATTN_IDX_LAUNCH(GGML_TYPE_F16, GGML_TYPE_Q4_0); break;
                default: GGML_ABORT("unsupported V type");
            }
            break;
        case GGML_TYPE_Q8_0:
            switch (V->type) {
                case GGML_TYPE_F16: FATTN_IDX_LAUNCH(GGML_TYPE_Q8_0, GGML_TYPE_F16); break;
                case GGML_TYPE_Q8_0: FATTN_IDX_LAUNCH(GGML_TYPE_Q8_0, GGML_TYPE_Q8_0); break;
                case GGML_TYPE_Q4_0: FATTN_IDX_LAUNCH(GGML_TYPE_Q8_0, GGML_TYPE_Q4_0); break;
                default: GGML_ABORT("unsupported V type");
            }
            break;
        case GGML_TYPE_Q4_0:
            switch (V->type) {
                case GGML_TYPE_F16: FATTN_IDX_LAUNCH(GGML_TYPE_Q4_0, GGML_TYPE_F16); break;
                case GGML_TYPE_Q8_0: FATTN_IDX_LAUNCH(GGML_TYPE_Q4_0, GGML_TYPE_Q8_0); break;
                case GGML_TYPE_Q4_0: FATTN_IDX_LAUNCH(GGML_TYPE_Q4_0, GGML_TYPE_Q4_0); break;
                default: GGML_ABORT("unsupported V type");
            }
            break;
        default: GGML_ABORT("unsupported K type");
    }
#undef FATTN_IDX_LAUNCH
}

static void ggml_cuda_flash_attn_ext_idx(ggml_backend_cuda_context & ctx, ggml_tensor * dst) {
    ggml_cuda_set_device(ctx.device);

    switch (dst->src[0]->ne[0]) {
        case  64: fattn_idx_launch< 64>(ctx, dst); break;
        case 128: fattn_idx_launch<128>(ctx, dst); break;
        case 256: fattn_idx_launch<256>(ctx, dst); break;
        default: GGML_ABORT("unsupported head size");
    }
}
