#include "arg.h"
#include "common.h"
#include "llama.h"

#include <algorithm>
#include <clocale>
#include <cmath>
#include <cstdio>
#include <vector>

static llama_context * make_ctx(
        const common_params & params,
        llama_model * model,
        uint32_t n_rs_seq = 8,
        uint32_t n_seq_max = 1) {
    auto cparams = common_context_params_to_llama(params);
    cparams.n_seq_max = n_seq_max;
    cparams.n_rs_seq  = n_rs_seq;
    cparams.n_batch   = std::max(cparams.n_batch,  (uint32_t) (cparams.n_rs_seq + 1));
    cparams.n_ubatch  = std::max(cparams.n_ubatch, (uint32_t) (cparams.n_rs_seq + 1));
    return llama_init_from_model(model, cparams);
}

static bool test_fragmented_on_device_fallback(
        const common_params & params,
        llama_model * model,
        const std::vector<llama_token> & tokens) {
    llama_context * ctx = make_ctx(params, model, 1, 3);
    if (ctx == nullptr) {
        fprintf(stderr, "%s : failed to initialize fragmented context\n", __func__);
        return false;
    }

    llama_batch batch = llama_batch_init(3, 0, 3);
    for (llama_seq_id seq_id = 0; seq_id < 3; ++seq_id) {
        common_batch_add(batch, tokens[seq_id % tokens.size()], 0, { seq_id }, seq_id == 2);
    }
    bool ok = llama_decode(ctx, batch) == 0;
    llama_batch_free(batch);

    if (ok) {
        ok = llama_memory_seq_rm(llama_get_memory(ctx), 1, -1, -1);
    }

    common_prompt_checkpoint ckpt;
    constexpr llama_state_seq_flags flags =
        LLAMA_STATE_SEQ_FLAGS_PARTIAL_ONLY | LLAMA_STATE_SEQ_FLAGS_ON_DEVICE;
    if (ok) {
        ckpt.update_tgt(ctx, -1, flags);
        if (ckpt.data_tgt_on_device) {
            fprintf(stderr, "%s : fragmented checkpoint did not fall back to host storage\n", __func__);
            ok = false;
        }
    }
    if (ok) {
        // The caller still requests ON_DEVICE here. load_tgt() must use the
        // actual host mode recorded when the checkpoint was saved.
        ckpt.load_tgt(ctx, -1, flags);
    }

    llama_free(ctx);
    return ok;
}

static bool test_preallocated_device_checkpoints(
        const common_params & params,
        llama_model * model,
        const std::vector<llama_token> & tokens) {
    constexpr int32_t n_seq = 2;
    llama_context * ctx = make_ctx(params, model, 1, n_seq);
    if (ctx == nullptr) {
        fprintf(stderr, "%s : failed to initialize multi-sequence context\n", __func__);
        return false;
    }

    bool ok = llama_state_seq_reserve_device_buffers(ctx);
    if (!ok) {
        fprintf(stderr, "%s : failed to preallocate device checkpoints\n", __func__);
    }

    llama_batch batch = llama_batch_init(n_seq, 0, n_seq);
    for (llama_seq_id seq_id = 0; seq_id < n_seq; ++seq_id) {
        common_batch_add(batch, tokens[seq_id % tokens.size()], 0, { seq_id }, true);
    }
    if (ok) {
        ok = llama_decode(ctx, batch) == 0;
    }
    llama_batch_free(batch);

    constexpr llama_state_seq_flags flags =
        LLAMA_STATE_SEQ_FLAGS_PARTIAL_ONLY | LLAMA_STATE_SEQ_FLAGS_ON_DEVICE;
    std::vector<common_prompt_checkpoint> checkpoints(n_seq);
    for (llama_seq_id seq_id = 0; ok && seq_id < n_seq; ++seq_id) {
        checkpoints[seq_id].update_tgt(ctx, seq_id, flags);
        if (!checkpoints[seq_id].data_tgt_on_device) {
            fprintf(stderr, "%s : sequence %d did not reuse its preallocated device checkpoint\n",
                    __func__, seq_id);
            ok = false;
        }
    }
    for (llama_seq_id seq_id = 0; ok && seq_id < n_seq; ++seq_id) {
        checkpoints[seq_id].load_tgt(ctx, seq_id, flags);
    }

    llama_free(ctx);
    return ok;
}

static bool decode_tokens(llama_context * ctx, const std::vector<llama_token> & tokens, uint32_t count) {
    llama_batch batch = llama_batch_init(count, 0, 1);
    for (uint32_t pos = 0; pos < count; ++pos) {
        common_batch_add(batch, tokens[pos], pos, { 0 }, pos + 1 == count);
    }
    const bool ok = llama_decode(ctx, batch) == 0;
    llama_batch_free(batch);
    return ok;
}

static bool decode_one(llama_context * ctx, llama_token tok, llama_pos pos) {
    llama_batch batch = llama_batch_init(1, 0, 1);
    common_batch_add(batch, tok, pos, { 0 }, true);
    const bool ok = llama_decode(ctx, batch) == 0;
    llama_batch_free(batch);
    return ok;
}

static bool decode_range(
        llama_context * ctx,
        const std::vector<llama_token> & tokens,
        uint32_t first,
        uint32_t count) {
    if (count == 0) {
        return true;
    }

    llama_batch batch = llama_batch_init(count, 0, 1);
    for (uint32_t i = 0; i < count; ++i) {
        common_batch_add(batch, tokens[first + i], first + i, { 0 }, i + 1 == count);
    }
    const bool ok = llama_decode(ctx, batch) == 0;
    llama_batch_free(batch);
    return ok;
}

static bool compare_logits(
        llama_context * ctx_full,
        llama_context * ctx_depth,
        int n_vocab,
        uint32_t n_accepted,
        const char * stage,
        float eps) {
    const float * logits_full  = llama_get_logits(ctx_full);
    const float * logits_depth = llama_get_logits(ctx_depth);
    if (logits_full == nullptr || logits_depth == nullptr) {
        fprintf(stderr, "%s : missing %s logits after accepting %u draft tokens\n", __func__, stage, n_accepted);
        return false;
    }

    int argmax_full  = 0;
    int argmax_depth = 0;
    float max_diff = 0.0f;
    for (int token = 0; token < n_vocab; ++token) {
        if (logits_full[token] > logits_full[argmax_full]) {
            argmax_full = token;
        }
        if (logits_depth[token] > logits_depth[argmax_depth]) {
            argmax_depth = token;
        }

        const float diff = std::fabs(logits_full[token] - logits_depth[token]);
        max_diff = std::max(max_diff, diff);
        if (eps >= 0.0f && diff > eps) {
            fprintf(stderr, "%s : %s logits mismatch after accepting %u draft tokens, token %d (%g != %g)\n",
                    __func__, stage, n_accepted, token, (double) logits_full[token], (double) logits_depth[token]);
            return false;
        }
    }
    if (eps < 0.0f && argmax_full != argmax_depth) {
        fprintf(stderr, "%s : %s greedy token mismatch after accepting %u draft tokens (%d != %d, max logit diff %g)\n",
                __func__, stage, n_accepted, argmax_full, argmax_depth, (double) max_diff);
        return false;
    }
    if (eps < 0.0f) {
        fprintf(stderr, "%s : %s greedy token %d preserved after accepting %u draft tokens (max logit diff %g)\n",
                __func__, stage, argmax_full, n_accepted, (double) max_diff);
    }
    return true;
}

static bool test_recompute_fallback(
        const common_params & params,
        llama_model * model,
        const std::vector<llama_token> & input_tokens,
        int n_vocab) {
    constexpr uint32_t n_prefix = 4;
    constexpr uint32_t n_draft  = 5;
    constexpr uint32_t n_verify = n_draft + 1;

    std::vector<llama_token> tokens = input_tokens;
    tokens.resize(n_prefix + n_verify + 2, tokens.back());

    for (uint32_t n_accepted = 0; n_accepted < n_draft; ++n_accepted) {
        llama_context * ctx_full  = make_ctx(params, model, n_draft);
        llama_context * ctx_depth = make_ctx(params, model, 1);
        if (ctx_full == nullptr || ctx_depth == nullptr) {
            fprintf(stderr, "%s : failed to initialize fallback contexts\n", __func__);
            llama_free(ctx_full);
            llama_free(ctx_depth);
            return false;
        }

        bool ok = decode_range(ctx_full, tokens, 0, n_prefix) &&
                  decode_range(ctx_depth, tokens, 0, n_prefix);
        if (ok) {
            ok = compare_logits(ctx_full, ctx_depth, n_vocab, n_accepted, "prefix", 1e-5f);
        }

        constexpr llama_state_seq_flags partial_flags =
            LLAMA_STATE_SEQ_FLAGS_PARTIAL_ONLY | LLAMA_STATE_SEQ_FLAGS_ON_DEVICE;
        common_prompt_checkpoint ckpt;
        if (ok) {
            ckpt.update_tgt(ctx_depth, 0, partial_flags);
            if (!ckpt.data_tgt_on_device) {
                fprintf(stderr, "%s : contiguous recurrent checkpoint unexpectedly fell back to host storage\n", __func__);
                ok = false;
            }
        }
        if (ok) {
            ok = decode_range(ctx_full, tokens, n_prefix, n_verify) &&
                 decode_range(ctx_depth, tokens, n_prefix, n_verify);
        }

        const llama_pos rollback_pos = n_prefix + 1 + n_accepted;
        const uint32_t n_rollback = n_draft - n_accepted;
        if (ok) {
            ok = llama_memory_seq_rm(llama_get_memory(ctx_full), 0, rollback_pos, -1);
        }
        if (ok && n_rollback <= 1) {
            ok = llama_memory_seq_rm(llama_get_memory(ctx_depth), 0, rollback_pos, -1);
        } else if (ok) {
            ckpt.load_tgt(ctx_depth, 0, partial_flags);
            ok = llama_memory_seq_rm(llama_get_memory(ctx_depth), 0, n_prefix, -1);
        }

        const llama_pos replacement_pos = rollback_pos;
        if (ok && n_rollback <= 1) {
            ok = decode_one(ctx_full, tokens[n_prefix + n_verify], replacement_pos) &&
                 decode_one(ctx_depth, tokens[n_prefix + n_verify], replacement_pos);
        } else if (ok) {
            std::vector<llama_token> replay_tokens = tokens;
            replay_tokens[replacement_pos] = tokens[n_prefix + n_verify];
            ok = decode_one(ctx_full, tokens[n_prefix + n_verify], replacement_pos) &&
                 decode_range(ctx_depth, replay_tokens, n_prefix, 2 + n_accepted);
        }
        if (ok) {
            ok = compare_logits(ctx_full, ctx_depth, n_vocab, n_accepted, "replacement", -1.0f);
        }
        if (ok) {
            ok = decode_one(ctx_full, tokens[n_prefix + n_verify + 1], replacement_pos + 1) &&
                 decode_one(ctx_depth, tokens[n_prefix + n_verify + 1], replacement_pos + 1) &&
                 compare_logits(ctx_full, ctx_depth, n_vocab, n_accepted, "continuation", -1.0f);
        }

        llama_free(ctx_full);
        llama_free(ctx_depth);

        if (!ok) {
            fprintf(stderr, "%s : fallback validation failed after accepting %u draft tokens\n", __func__, n_accepted);
            return false;
        }
    }

    fprintf(stderr, "%s : depth-1 recomputation preserves depth-5 greedy decisions at every rejection position\n", __func__);
    return true;
}

int main(int argc, char ** argv) {
    std::setlocale(LC_NUMERIC, "C");

    common_params params;
    params.sampling.seed = 1234;
    params.n_predict = 1;

    common_init();

    if (!common_params_parse(argc, argv, params, LLAMA_EXAMPLE_COMMON)) {
        return 1;
    }

    ggml_backend_load_all();

    common_init_result_ptr llama_init = common_init_from_params(params);
    llama_model * model = llama_init->model();
    if (model == nullptr) {
        fprintf(stderr, "%s : failed to init model\n", __func__);
        return 1;
    }

    if (!llama_model_is_recurrent(model) && !llama_model_is_hybrid(model)) {
        fprintf(stderr, "%s : skipping for non-recurrent model\n", __func__);
        return 0;
    }

    const llama_vocab * vocab   = llama_model_get_vocab(model);
    const int           n_vocab = llama_vocab_n_tokens(vocab);

    std::vector<llama_token> tokens;
    if (llama_vocab_type(vocab) == LLAMA_VOCAB_TYPE_NONE) {
        tokens = { 1, 2, 3, 4, 5, 6, 7, 8, 9 };
    } else {
        tokens = common_tokenize(vocab, "The quick brown fox jumps over the lazy dog", true);
    }
    if (tokens.empty()) {
        fprintf(stderr, "%s : not enough prompt tokens\n", __func__);
        return 1;
    }
    if (!test_fragmented_on_device_fallback(params, model, tokens)) {
        return 1;
    }
    if (!test_preallocated_device_checkpoints(params, model, tokens)) {
        return 1;
    }
    if (!test_recompute_fallback(params, model, tokens, n_vocab)) {
        return 1;
    }

    llama_context * ctx_src = make_ctx(params, model);
    llama_context * ctx_dst = make_ctx(params, model);
    if (ctx_src == nullptr || ctx_dst == nullptr) {
        fprintf(stderr, "%s : failed to init contexts\n", __func__);
        return 1;
    }

    if (llama_n_rs_seq(ctx_src) == 0) {
        fprintf(stderr, "%s : skipping because n_rs_seq is disabled\n", __func__);
        llama_free(ctx_src);
        llama_free(ctx_dst);
        return 0;
    }

    const uint32_t n_rs_seq = llama_n_rs_seq(ctx_src);
    constexpr uint32_t n_rollback = 3;
    if (n_rs_seq < n_rollback) {
        fprintf(stderr, "%s : skipping because n_rs_seq is too small\n", __func__);
        llama_free(ctx_src);
        llama_free(ctx_dst);
        return 0;
    }
    tokens.resize(n_rs_seq + 1, tokens.back());

    const uint32_t  n_tokens     = tokens.size();
    const llama_pos rollback_pos = (llama_pos) n_tokens - n_rollback;

    // Decode the full prompt on the source, then roll back three positions.
    // Replaying them crosses DSV4's ratio-4 compressor boundary.
    // Rollback leaves the recurrent memory in a snapshot state (rs_idx != 0).
    if (!decode_tokens(ctx_src, tokens, n_tokens)) {
        fprintf(stderr, "%s : failed to decode prompt\n", __func__);
        return 1;
    }
    if (!llama_memory_seq_rm(llama_get_memory(ctx_src), 0, rollback_pos, -1)) {
        fprintf(stderr, "%s : rollback failed\n", __func__);
        return 1;
    }

    // Save the rolled-back state and restore it into a fresh context.
    common_prompt_checkpoint ckpt;
    ckpt.update_tgt(ctx_src, 0, 0);
    ckpt.load_tgt(ctx_dst, 0, 0);

    constexpr float eps = 1e-5f;
    std::vector<std::vector<float>> logits_src_replay(n_rollback);
    const auto replay_and_compare = [&](const char * mode) {
        for (uint32_t i = 0; i < n_rollback; ++i) {
            const llama_pos pos = rollback_pos + i;
            if (!decode_one(ctx_src, tokens[pos], pos) ||
                !decode_one(ctx_dst, tokens[pos], pos)) {
                fprintf(stderr, "%s : %s replay failed at position %d\n", __func__, mode, pos);
                return false;
            }

            const float * logits_src = llama_get_logits_ith(ctx_src, 0);
            const float * logits_dst = llama_get_logits_ith(ctx_dst, 0);
            if (logits_src == nullptr || logits_dst == nullptr) {
                fprintf(stderr, "%s : missing %s logits at position %d\n", __func__, mode, pos);
                return false;
            }

            logits_src_replay[i].assign(logits_src, logits_src + n_vocab);
            for (int token = 0; token < n_vocab; ++token) {
                if (std::fabs(logits_src[token] - logits_dst[token]) > eps) {
                    fprintf(stderr, "%s : %s logits mismatch at position %d, token %d (%g != %g)\n",
                            __func__, mode, pos, token, (double) logits_src[token], (double) logits_dst[token]);
                    return false;
                }
            }
        }
        return true;
    };
    if (!replay_and_compare("full")) {
        return 1;
    }

    if (!llama_memory_seq_rm(llama_get_memory(ctx_src), 0, rollback_pos, -1) ||
        !llama_memory_seq_rm(llama_get_memory(ctx_dst), 0, rollback_pos, -1)) {
        fprintf(stderr, "%s : partial rollback failed\n", __func__);
        return 1;
    }

    constexpr llama_state_seq_flags partial_flags = LLAMA_STATE_SEQ_FLAGS_PARTIAL_ONLY;
    common_prompt_checkpoint ckpt_partial;
    ckpt_partial.update_tgt(ctx_src, 0, partial_flags);
    if (ckpt_partial.data_tgt_on_device) {
        fprintf(stderr, "%s : host recurrent checkpoint recorded device storage\n", __func__);
        return 1;
    }
    ckpt_partial.load_tgt(ctx_dst, 0, partial_flags);

    if (!replay_and_compare("partial")) {
        return 1;
    }

    // Repeat the load into a context that already has its own rollback state:
    // groups 1..n_rs_seq hold a different prompt's history, and rs_idx[0] is
    // non-zero at load time. The restore must wipe that state and still match.
    llama_context * ctx_dirty = make_ctx(params, model);
    if (ctx_dirty == nullptr) {
        fprintf(stderr, "%s : failed to init dirty ctx\n", __func__);
        return 1;
    }

    std::vector<llama_token> noise = tokens;
    for (auto & t : noise) {
        t = (t + 1) % n_vocab;
        if (t < 0) {
            t = 0;
        }
    }
    if (!decode_tokens(ctx_dirty, noise, n_tokens)) {
        fprintf(stderr, "%s : dirty prompt decode failed\n", __func__);
        return 1;
    }
    if (!llama_memory_seq_rm(llama_get_memory(ctx_dirty), 0, rollback_pos, -1)) {
        fprintf(stderr, "%s : dirty rollback failed\n", __func__);
        return 1;
    }

    ckpt.load_tgt(ctx_dirty, 0, 0);

    for (uint32_t i = 0; i < n_rollback; ++i) {
        const llama_pos pos = rollback_pos + i;
        if (!decode_one(ctx_dirty, tokens[pos], pos)) {
            fprintf(stderr, "%s : dirty replay failed at position %d\n", __func__, pos);
            return 1;
        }

        const float * logits_dirty = llama_get_logits_ith(ctx_dirty, 0);
        if (logits_dirty == nullptr) {
            fprintf(stderr, "%s : missing dirty logits at position %d\n", __func__, pos);
            return 1;
        }

        for (int token = 0; token < n_vocab; ++token) {
            if (std::fabs(logits_src_replay[i][token] - logits_dirty[token]) > eps) {
                fprintf(stderr, "%s : dirty-ctx logits mismatch at position %d, token %d (%g != %g)\n",
                        __func__, pos, token, (double) logits_src_replay[i][token], (double) logits_dirty[token]);
                return 1;
            }
        }
    }

    fprintf(stderr, "%s : recurrent rollback checkpoint restored successfully\n", __func__);
    llama_free(ctx_src);
    llama_free(ctx_dst);
    llama_free(ctx_dirty);
    return 0;
}
