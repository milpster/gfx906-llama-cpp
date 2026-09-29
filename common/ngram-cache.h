#pragma once

#include "llama.h"

#include <ankerl/unordered_dense.h>

#include <cstdint>
#include <memory>
#include <string>
#include <utility>
#include <vector>

#define LLAMA_NGRAM_MIN    1
#define LLAMA_NGRAM_MAX    4
#define LLAMA_NGRAM_STATIC 2

// Data structures to map n-grams to empirical token probabilities:

struct common_ngram {
    llama_token tokens[LLAMA_NGRAM_MAX];

    common_ngram() {
        for (int i = 0; i < LLAMA_NGRAM_MAX; ++i) {
            tokens[i] = LLAMA_TOKEN_NULL;
        }
    }

    common_ngram(const llama_token * input, const int ngram_size) {
        for (int i = 0; i < LLAMA_NGRAM_MAX; ++i) {
            tokens[i] = i < ngram_size ? input[i] : LLAMA_TOKEN_NULL;
        }
    }

    bool operator==(const common_ngram & other) const {
        for (int i = 0; i < LLAMA_NGRAM_MAX; ++i) {
            if (tokens[i] != other.tokens[i]) {
                return false;
            }
        }
        return true;
    }
};

struct common_token_hash_function {
    size_t operator()(const llama_token token) const {
        // see https://probablydance.com/2018/06/16/fibonacci-hashing-the-optimization-that-the-world-forgot-or-a-better-alternative-to-integer-modulo/
        return token * 11400714819323198485llu;
    }
};

struct common_ngram_hash_function {
    size_t operator()(const common_ngram & ngram) const {
        size_t hash = common_token_hash_function{}(ngram.tokens[0]);
        for (int i = 1; i < LLAMA_NGRAM_MAX; ++i) {
            hash ^= common_token_hash_function{}(ngram.tokens[i]);
        }
        return hash;
    }
};

// token -> number of times token has been seen
struct common_ngram_cache_part {
    typedef std::pair<llama_token, int32_t>          value_type;
    typedef std::vector<value_type>::iterator       iterator;
    typedef std::vector<value_type>::const_iterator const_iterator;

    std::vector<value_type> entries;

    iterator find(const llama_token token) {
        const iterator it = lower_bound(token);
        return it != entries.end() && it->first == token ? it : entries.end();
    }

    const_iterator find(const llama_token token) const {
        const const_iterator it = lower_bound(token);
        return it != entries.end() && it->first == token ? it : entries.end();
    }

    // Callers emplace a token only after find did not return it.
    void emplace(const llama_token token, const int32_t count) {
        entries.insert(lower_bound(token), value_type(token, count));
    }

    iterator       begin()       { return entries.begin(); }
    iterator       end()         { return entries.end(); }
    const_iterator begin() const { return entries.begin(); }
    const_iterator end()   const { return entries.end(); }
    size_t         size()  const { return entries.size(); }
    bool           empty() const { return entries.empty(); }

    // fixed-length binary search variant of std::lower_bound
    static size_t lower_bound(const value_type * pairs, size_t n, const llama_token token) {
        if (n == 0) {
            return 0;
        }
        const value_type * base = pairs;
        while (n > 1) {
            const size_t half = n / 2;
            base = base[half].first < token ? base + half : base;
            n -= half;
        }
        return (base - pairs) + (base->first < token);
    }

private:
    iterator lower_bound(const llama_token token) {
        return entries.begin() + lower_bound(entries.data(), entries.size(), token);
    }

    const_iterator lower_bound(const llama_token token) const {
        return entries.begin() + lower_bound(entries.data(), entries.size(), token);
    }
};

// n-gram -> empirical distribution of following tokens
// A segmented map grows in fixed-size blocks, so loading a large cache never holds two copies of its entries.
typedef ankerl::unordered_dense::segmented_map<common_ngram, common_ngram_cache_part, common_ngram_hash_function> common_ngram_cache;

// token and number of times it has been seen, as stored in a static ngram cache
typedef common_ngram_cache_part::value_type common_ngram_cache_static_entry;

// the distribution of following tokens of one n-gram, sorted by token
struct common_ngram_cache_static_part {
    const common_ngram_cache_static_entry * entries = nullptr;
    size_t                                  size    = 0;
};

struct fcm_verified_constmap;

// Read-only ngram cache of LLAMA_NGRAM_STATIC-grams. A constmap
// (https://github.com/lemire/fastconstmap) maps each n-gram to a span of one
// contiguous entries array.
struct common_ngram_cache_static {
    std::vector<uint64_t>                   buffer;
    const common_ngram_cache_static_entry * entries = nullptr;
    std::unique_ptr<fcm_verified_constmap>  map;

    common_ngram_cache_static();
    ~common_ngram_cache_static();
};

// Look up the distribution of tokens following an n-gram. Returns an empty part if the n-gram is not in the cache.
common_ngram_cache_static_part common_ngram_cache_static_find(const common_ngram_cache_static & nc_static, const common_ngram & ngram);


// Update an ngram cache with tokens.
// ngram_cache:         the cache to modify.
// ngram_min/ngram_max: the min/max size of the ngrams to extract from inp_data.
// inp_data:            the token sequence with which to update ngram_cache.
// nnew:                how many new tokens have been appended to inp_data since the last call to this function.
// print_progress:      whether to print progress to stderr.
//
// In order to get correct results inp_data can ONLY BE APPENDED TO.
// Changes in the middle need a complete rebuild.
void common_ngram_cache_update(
    common_ngram_cache & ngram_cache, int ngram_min, int ngram_max, std::vector<llama_token> & inp_data, int nnew, bool print_progress);

// Try to draft tokens from ngram caches.
// inp:                the tokens generated so far.
// draft:              the token sequence to draft. Expected to initially contain the previously sampled token.
// n_draft:            maximum number of tokens to add to draft.
// ngram_min/gram_max: the min/max size of the ngrams in nc_context and nc_dynamic.
// nc_context:         ngram cache based on current context.
// nc_dynamic:         ngram cache based on previous user generations.
// nc_static:          ngram cache generated from a large text corpus, used for validation. May be null.
// strict_context:     whether request-local matches use the stronger dynamic-cache thresholds.
// p_min_dynamic:      minimum share of observations the top continuation must hold to be drafted
//                     from the dynamic cache (0.0 = built-in strict thresholds only).
void common_ngram_cache_draft(
    std::vector<llama_token> & inp, std::vector<llama_token> & draft, int n_draft, int ngram_min, int ngram_max,
    common_ngram_cache & nc_context, common_ngram_cache & nc_dynamic, const common_ngram_cache_static * nc_static,
    bool strict_context = false, float p_min_dynamic = 0.0f);

// Save an ngram cache to a file.
// ngram_cache: the ngram cache to save.
// filename:    the path under which to save the ngram cache.
void common_ngram_cache_save(common_ngram_cache & ngram_cache, const std::string & filename);

// Load an ngram cache saved with common_ngram_cache_save.
// filename: the path from which to load the ngram cache.
// returns:  an ngram cache containing the information saved to filename.
common_ngram_cache common_ngram_cache_load(const std::string & filename);

// Save the LLAMA_NGRAM_STATIC-grams of an ngram cache as a static ngram cache file.
// ngram_cache: the ngram cache to save.
// filename:    the path under which to save the static ngram cache.
void common_ngram_cache_static_save(const common_ngram_cache & ngram_cache, const std::string & filename);

// Load a static ngram cache saved with common_ngram_cache_static_save.
// filename: the path from which to load the static ngram cache.
// returns:  a read-only static ngram cache, shareable between sequences.
std::shared_ptr<const common_ngram_cache_static> common_ngram_cache_static_load(const std::string & filename);

// Merge two ngram caches.
// ngram_cache_target: the ngram cache to which to add the information from ngram_cache_add.
// ngram_cache_add:    the ngram cache to add to ngram_cache_target.
void common_ngram_cache_merge(common_ngram_cache & ngram_cache_target, common_ngram_cache & ngram_cache_add);
