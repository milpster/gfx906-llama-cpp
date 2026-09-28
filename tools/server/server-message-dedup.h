#pragma once

// SPEC-0001 (server message dedup): the pure, stateless pass behind the unit
// seam of spec §10. Free functions only; the server will call them from
// oaicompat_chat_params_parse (increment 8), and tests/test-server-message-dedup.cpp
// calls them directly. Later seam functions (predicate, apply, key) arrive with
// their own increments.

#include "json.h"

#include <cstddef>
#include <cstdint>
#include <functional>
#include <optional>
#include <set>
#include <string>
#include <string_view>
#include <vector>

// resolved settings of the pass for one request (spec §6.1, §6.2)
struct dedup_settings {
    bool                  enabled   = false;
    int32_t               min_bytes = 1024;
    std::set<std::string> roles     = {"tool"};
};

// resolve the request's `message_dedup` value against the server defaults
// (spec §6.2). Null means absent. Each field resolves on its own: request
// value if present, else the default. Any value that violates §6.2 throws
// std::invalid_argument whose message names `message_dedup.<field>` and holds
// no client value (§5 S1, S2); nothing else may escape.
dedup_settings dedup_resolve(const common_json & message_dedup, const dedup_settings & defaults);

// special-text predicate (spec §4.0): the smallest byte offset at which the text
// of a CONTROL, USER_DEFINED or UNKNOWN token of the served vocab begins in the
// given bytes, or nullopt. Built once per served model (increment 7); tests
// inject a hand-written one.
using dedup_special_pred = std::function<std::optional<size_t>(std::string_view)>;

struct llama_vocab;

// the special-text predicate of a served vocab (spec §4.0): its match set is
// every token with the CONTROL, USER_DEFINED or UNKNOWN attribute, the set the
// tokenizer splits out of text (src/llama-vocab.cpp:3033). Built once per
// process from the loaded model's vocab; the predicate owns its match set and
// holds no pointer into the request or the vocab, so it may outlive both.
dedup_special_pred dedup_special_text_predicate_from_vocab(const llama_vocab * vocab);

// build the stub (spec §6.4) that references a first occurrence.
//   first_unit : the first occurrence's unit bytes (source of the EXCERPT); must be
//                valid UTF-8, as units come from parsed JSON strings
//   role       : "tool", "user" or "system" (the ROLEWORD); any other role
//                (including "assistant") gives nullopt
//   ordinal    : the first occurrence's ORDINAL, rendered as given
//   toolname   : the TOOLNAME candidate, used only for role "tool"; nullopt
//                means no candidate. It is rendered only if the whole
//                candidate matches ^[A-Za-z0-9_.-]{1,64}$, else the group is
//                omitted (never cut, mapped or escaped)
//   pred       : the special-text predicate
// Returns the stub, or nullopt when no conforming stub exists (§6.4 step 6)
// or the role is not one of the three.
std::optional<std::string> dedup_build_stub(std::string_view                   first_unit,
                                            const std::string &                role,
                                            size_t                             ordinal,
                                            const std::optional<std::string> & toolname,
                                            const dedup_special_pred &         pred);

// hash used to bucket units in the index (spec §6.3, §5 S7); injectable for
// tests (§7 DEDUP_HASH_COLLISION, DEDUP_HASH_FLOOD). An empty function means
// the default seeded hash.
using dedup_hash_fn = std::function<uint64_t(std::string_view unit, uint64_t seed)>;

// one replaced unit: its byte length and the stub that replaced it
struct dedup_replacement {
    size_t      unit_bytes = 0;
    std::string stub;
};

// statistics of one active pass, reported in `timings` (spec §6.5). Written only
// by the server: the parser fills n and bytes_saved from the replacement records,
// the completion handler fills tokens_saved_est once the prompt is tokenized
struct dedup_stats {
    uint64_t n                = 0; // units replaced by a stub
    uint64_t bytes_saved      = 0; // Σ (unit bytes - stub bytes), exact
    uint64_t tokens_saved_est = 0; // dedup_tokens_saved_est(bytes_saved, T, B)
};

struct dedup_result {
    common_json                    messages;                // the rewritten messages
    std::vector<dedup_replacement> replacements;            // one record per replaced unit, in message/part order
    size_t                         n_byte_comparisons = 0;  // full byte comparisons made against candidates

    // n and bytes_saved of the replacement records; tokens_saved_est is left 0
    dedup_stats stats() const;
};

// the proportional token estimate of spec §6.5, O(1), tokenizing nothing:
// round-half-up(bytes_saved * n_text_tokens / n_text_bytes), i.e.
// (2·S·T + B) / (2·B) in 64-bit unsigned arithmetic, and 0 when S or B is 0.
//   n_text_tokens : T, the text tokens of the tokenized prompt (media chunks excluded)
//   n_text_bytes  : B, the rendered prompt's bytes minus the bytes of its media markers
uint64_t dedup_tokens_saved_est(uint64_t bytes_saved, uint64_t n_text_tokens, uint64_t n_text_bytes);

// the per-process seed of the default hash: unpredictable to clients, fixed
// for the life of the process (§5 S7)
uint64_t dedup_process_seed();

// apply the pass (spec §6.3) to the converted OAI `messages` array, as the
// template would receive it after the media loop of oaicompat_chat_params_parse
// (string content, or arrays of {type:"text"} and {type:"media_marker"} parts).
// Only unit text changes; every other field is kept as is. The caller calls it
// only when the pass is active.
dedup_result dedup_apply(const common_json &        messages,
                         const dedup_settings &     settings,
                         const dedup_special_pred & pred,
                         const dedup_hash_fn &      hash = {},
                         uint64_t                   seed = dedup_process_seed());

// the index key of a unit under a seed (the §7 DEDUP_HASH_FLOOD check (c))
uint64_t dedup_key(const std::string & role, std::string_view unit, uint64_t seed);
