// fork-local regression: ngram-cache speculative server lifecycle
//
// exercises common_speculative_impl_ngram_cache through the public API the
// server uses (begin -> draft rounds with prompt + id_last -> slot reuse),
// with no model and no GPU. build/run instructions live in
// journal/JOURNAL-2026-09-28-prompt-lookup.md.

#include "speculative.h"

#undef NDEBUG

#include <cassert>
#include <cstdio>
#include <string>
#include <vector>

static int n_fail = 0;

using tokens = std::vector<llama_token>;

static void check(const tokens & got, const tokens & want, const char * what) {
    bool ok = got == want;
    if (!ok) {
        n_fail++;
    }
    printf("%s %s\n", ok ? "pass" : "FAIL", what);
    if (!ok) {
        printf("  got  : ");
        for (auto t : got)  { printf("%d ", t); }
        printf("\n  want : ");
        for (auto t : want) { printf("%d ", t); }
        printf("\n");
    }
}

struct spec_ctx {
    common_params_speculative params;
    common_speculative_ptr spec;

    explicit spec_ctx(uint32_t n_seq, const std::string & dyn_path = "", int32_t n_max = 8, int32_t n_min = 0, bool context_strict = false) {
        params.types = { COMMON_SPECULATIVE_TYPE_NGRAM_CACHE };
        params.ngram_cache.lookup_cache_dynamic = dyn_path;
        params.ngram_cache.context_strict = context_strict;
        params.draft.n_max = n_max;
        params.draft.n_min = n_min;
        spec.reset(common_speculative_init(params, n_seq));
        assert(spec);
    }
};

// one server draft round: fresh result, full prompt, separate last sampled token
static tokens round(common_speculative * spec, llama_seq_id seq, const tokens & prompt, llama_token id_last) {
    tokens result;

    common_speculative_get_draft_params(spec, seq) = {
        /* .drafting = */ true,
        /* .n_max    = */ 8,
        /* .pos0     = */ (llama_pos) prompt.size(),
        /* .id_last  = */ id_last,
        /* .prompt   = */ &prompt,
        /* .result   = */ &result,
    };

    common_speculative_draft(spec);

    return result;
}

// first call must learn the whole prompt window, before and after the fix
static void test_first_round_learns_prompt(void) {
    spec_ctx ctx(1);
    tokens prompt = {1,2,3,4,1,2,3,4};

    common_speculative_begin(ctx.spec.get(), 0, prompt);

    check(round(ctx.spec.get(), 0, prompt, 1), {2,3,4,1,2,3,4,1}, "first round drafts the prompt loop");
}

// generated tokens must train the context cache incrementally
static void test_incremental_generation_learns(void) {
    spec_ctx ctx(1);
    tokens prompt = {1,2,3,4,5};
    tokens gen    = {6,7,8,9,10,1,2,3,4,5};

    common_speculative_begin(ctx.spec.get(), 0, prompt);

    tokens hist = prompt;
    for (size_t k = 0; k < gen.size(); ++k) {
        // accept one token per round, like a full-accept speculative loop
        round(ctx.spec.get(), 0, hist, gen[k]);
        hist.push_back(gen[k]);
    }

    // the model now repeats the prompt; only generation-time n-grams can predict it
    check(round(ctx.spec.get(), 0, hist, 6), {7,8,9,10,1,2,3,4}, "incremental generation trains the cache");
}

// a new request on a reused slot must not draft from the old request
static void test_begin_resets_slot_state(void) {
    spec_ctx ctx(1);
    tokens prompt_a = {1,2,3,4,5,6,9,1,2,3,4,5,6};

    common_speculative_begin(ctx.spec.get(), 0, prompt_a);
    round(ctx.spec.get(), 0, prompt_a, 9); // learns (4,5,6,9)->1 inside prompt_a

    // slot reused by a new request that shares only the prefix
    tokens prompt_b = {1,2,3,4,5,6};
    common_speculative_begin(ctx.spec.get(), 0, prompt_b);

    check(round(ctx.spec.get(), 0, prompt_b, 9), {}, "begin() drops the previous request state");
}

// a shortened history (context shift / checkpoint rollback) must be rebuilt
static void test_shrunk_history_rebuilds(void) {
    spec_ctx ctx(1);
    tokens prompt = {1,2,3,4,5,6,7};

    common_speculative_begin(ctx.spec.get(), 0, prompt);
    round(ctx.spec.get(), 0, prompt, 8); // learns (3,4,5,6)->7, (4,5,6,7)->8

    // rollback: the context shrinks, the discarded suffix no longer exists
    tokens prompt_short = {1,2,3,4,5};

    check(round(ctx.spec.get(), 0, prompt_short, 6), {}, "shrunk history is rebuilt, stale keys dropped");
}

// begin() on one sequence must not disturb another
static void test_sequences_are_isolated(void) {
    spec_ctx ctx(2);
    tokens prompt_0 = {1,2,3,4,1,2,3,4};
    tokens prompt_1 = {50,51,52,53};

    common_speculative_begin(ctx.spec.get(), 0, prompt_0);
    tokens first = round(ctx.spec.get(), 0, prompt_0, 1);
    check(first, {2,3,4,1,2,3,4,1}, "isolation: seq 0 drafts");

    common_speculative_begin(ctx.spec.get(), 1, prompt_1);
    check(round(ctx.spec.get(), 1, prompt_1, 54), {}, "isolation: seq 1 starts empty");

    check(round(ctx.spec.get(), 0, prompt_0, 1), first, "isolation: seq 0 unaffected by seq 1 begin");
}

// a finished request's generation must train the dynamic cache for the next one
static void test_dynamic_cross_request(void) {
    std::remove("/tmp/opencode/ngramcache-dyn-t6.bin"); // counts must not compound across test runs
    spec_ctx ctx(1, "/tmp/opencode/ngramcache-dyn-t6.bin");
    tokens prompt_a = {3,4,5,6,9,1,3,4,5,6,9,1};

    common_speculative_begin(ctx.spec.get(), 0, prompt_a);
    check(round(ctx.spec.get(), 0, prompt_a, 3), {4,5,6,9,1,3,4,5}, "dynamic: request 1 learns");

    tokens prompt_b = {50,5,6,9};
    common_speculative_begin(ctx.spec.get(), 0, prompt_b);

    check(round(ctx.spec.get(), 0, prompt_b, 1), {3}, "dynamic: request 2 drafts learned pattern");
}

// dynamic learning must be shared across slots
static void test_dynamic_shared_across_slots(void) {
    std::remove("/tmp/opencode/ngramcache-dyn-t7.bin");
    spec_ctx ctx(2, "/tmp/opencode/ngramcache-dyn-t7.bin");
    tokens prompt_a = {3,4,5,6,9,1,3,4,5,6,9,1};
    tokens prompt_b = {50,5,6,9};

    common_speculative_begin(ctx.spec.get(), 0, prompt_a);
    round(ctx.spec.get(), 0, prompt_a, 3);

    common_speculative_begin(ctx.spec.get(), 1, prompt_b);
    check(round(ctx.spec.get(), 1, prompt_b, 1), {3}, "dynamic: other slot drafts learned pattern");
}

// draft depth must follow --spec-draft-n-max instead of a hard-coded value
static void test_depth_follows_config(void) {
    spec_ctx ctx(1, "", 2);
    tokens prompt = {1,2,3,4,1,2,3,4};

    common_speculative_begin(ctx.spec.get(), 0, prompt);

    check(round(ctx.spec.get(), 0, prompt, 1), {2,3}, "depth: ngram-cache honors --spec-draft-n-max");
}

static void test_min_depth_follows_config(void) {
    std::remove("/tmp/opencode/ngramcache-dyn-t8.bin");
    spec_ctx ctx(1, "/tmp/opencode/ngramcache-dyn-t8.bin", 3, 2);
    tokens prompt_a = {3,4,5,6,9,1,3,4,5,6,9,1};

    common_speculative_begin(ctx.spec.get(), 0, prompt_a);
    round(ctx.spec.get(), 0, prompt_a, 3);

    tokens prompt_b = {50,5,6,9};
    common_speculative_begin(ctx.spec.get(), 0, prompt_b);

    check(round(ctx.spec.get(), 0, prompt_b, 1), {}, "depth: ngram-cache honors --spec-draft-n-min");
}

static void test_single_observation_is_not_confident(void) {
    spec_ctx ctx(1, "", 3, 0, true);
    tokens prompt = {1,2,3,4,9,50,51,52,1,2,3};

    common_speculative_begin(ctx.spec.get(), 0, prompt);

    check(round(ctx.spec.get(), 0, prompt, 4), {}, "confidence: one observed continuation does not draft");
}

static const char * DYN_PATH = "/tmp/opencode/ngramcache-dyn-persist.bin";

// process 1: learn, then save on shutdown
static int persist_save(void) {
    std::remove(DYN_PATH);

    {
        spec_ctx ctx(1, DYN_PATH);
        tokens prompt_a = {3,4,5,6,9,1,3,4,5,6,9,1};

        common_speculative_begin(ctx.spec.get(), 0, prompt_a);
        round(ctx.spec.get(), 0, prompt_a, 3);
    } // shutdown: dynamic cache must be written

    FILE * f = std::fopen(DYN_PATH, "rb");
    if (!f) {
        printf("FAIL persist-save: no dynamic cache file written on shutdown\n");
        return 1;
    }
    std::fclose(f);
    printf("pass persist-save: dynamic cache file written on shutdown\n");
    return 0;
}

// process 2: reload and draft from the persisted learning
static int persist_load(void) {
    spec_ctx ctx(1, DYN_PATH);
    tokens prompt_b = {50,5,6,9};

    common_speculative_begin(ctx.spec.get(), 0, prompt_b);
    check(round(ctx.spec.get(), 0, prompt_b, 1), {3}, "persist: reloaded cache drafts learned pattern");

    return n_fail ? 1 : 0;
}

int main(int argc, char ** argv) {
    if (argc > 1 && std::string(argv[1]) == "persist-save") {
        return persist_save();
    }
    if (argc > 1 && std::string(argv[1]) == "persist-load") {
        return persist_load();
    }

    test_first_round_learns_prompt();
    test_incremental_generation_learns();
    test_begin_resets_slot_state();
    test_shrunk_history_rebuilds();
    test_sequences_are_isolated();
    test_dynamic_cross_request();
    test_dynamic_shared_across_slots();
    test_depth_follows_config();
    test_min_depth_follows_config();
    test_single_observation_is_not_confident();

    printf("%s: %d failure(s)\n", n_fail ? "test-ngram-cache-server-lifecycle: FAILED" : "test-ngram-cache-server-lifecycle: all tests OK", n_fail);

    return n_fail ? 1 : 0;
}
