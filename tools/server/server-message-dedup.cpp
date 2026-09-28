#include "server-message-dedup.h"

#include "common.h"
#include "llama.h"

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <memory>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

// Every check below tests the JSON type before reading a value, so no accessor
// can throw common_json_error; each rejection is a std::invalid_argument whose
// message holds only fixed field names and rules, never a client value (§5 S1).

// an unknown key is named only when it cannot carry client content in disguise
static bool dedup_key_is_echo_safe(const std::string & key) {
    // ^[A-Za-z0-9_]{1,32}$ in explicit ASCII ranges, so the answer does not depend on LC_CTYPE
    return !key.empty() && key.size() <= 32 && std::all_of(key.begin(), key.end(), [](char c) {
        return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '_';
    });
}

static bool dedup_resolve_enabled(const common_json & value) {
    if (!value.is_boolean()) {
        throw std::invalid_argument("message_dedup.enabled must be a boolean");
    }
    return value.get<bool>();
}

static int32_t dedup_resolve_min_bytes(const common_json & value) {
    // a JSON float (1e3, 1.5, or an integer beyond 2^64) is not an integer, and an
    // unsigned integer beyond 2^63 reads as negative, so one range check covers both ends
    if (!value.is_number_integer()) {
        throw std::invalid_argument("message_dedup.min_bytes must be an integer");
    }
    const long long n = value.get<long long>();
    if (n < 1 || n > INT32_MAX) {
        throw std::invalid_argument("message_dedup.min_bytes must be in [1, 2147483647]");
    }
    return (int32_t) n;
}

static std::set<std::string> dedup_resolve_roles(const common_json & value) {
    if (!value.is_array()) {
        throw std::invalid_argument("message_dedup.roles must be an array of strings");
    }
    std::set<std::string> roles;
    for (const auto & role : value) {
        if (!role.is_string()) {
            throw std::invalid_argument("message_dedup.roles must be an array of strings");
        }
        const std::string name = role.get<std::string>();
        if (name == "assistant") {
            // the rule, not just the allowed set: the model's own turns are never stubbed (spec §8.3)
            throw std::invalid_argument("message_dedup.roles: 'assistant' never takes part");
        }
        if (!common_message_dedup_role_allowed(name)) {
            throw std::invalid_argument("message_dedup.roles may only hold \"tool\", \"user\" and \"system\"");
        }
        roles.insert(name);
    }
    return roles;
}

dedup_settings dedup_resolve(const common_json & message_dedup, const dedup_settings & defaults) {
    dedup_settings settings = defaults;
    if (message_dedup.is_null()) {
        return settings;
    }
    if (!message_dedup.is_object()) {
        throw std::invalid_argument("message_dedup must be an object");
    }
    for (const auto & [key, value] : message_dedup.items()) {
        if (key != "enabled" && key != "min_bytes" && key != "roles") {
            throw std::invalid_argument(dedup_key_is_echo_safe(key)
                ? "message_dedup has an unknown field \"" + key + "\""
                : std::string("message_dedup has an unknown field"));
        }
        if (value.is_null()) {
            continue; // null == absent: the field keeps its default
        }
        if (key == "enabled") {
            settings.enabled = dedup_resolve_enabled(value);
        } else if (key == "min_bytes") {
            settings.min_bytes = dedup_resolve_min_bytes(value);
        } else {
            settings.roles = dedup_resolve_roles(value);
        }
    }
    return settings;
}

// the words that name a role in a stub (spec §6.4 ROLEWORD); nullptr for a role that never takes part
static const char * dedup_roleword(const std::string & role) {
    if (role == "tool")   { return "tool result"; }
    if (role == "user")   { return "user message"; }
    if (role == "system") { return "system message"; }
    return nullptr;
}

// ^[A-Za-z0-9_.-]{1,64}$ in explicit ASCII ranges, so the answer does not depend on LC_CTYPE
static bool dedup_toolname_is_safe(const std::string & name) {
    return !name.empty() && name.size() <= 64 && std::all_of(name.begin(), name.end(), [](char c) {
        return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '_' || c == '.' || c == '-';
    });
}

// the EXCERPT of spec §6.4, steps 1-4
static std::string dedup_excerpt(std::string_view unit, const dedup_special_pred & pred) {
    constexpr size_t max_bytes = 40;

    // 1. length cut: back off from byte 40 over UTF-8 continuation bytes (10xxxxxx) to the start of the
    //    code point that crosses it, unless the cut already falls on a code-point boundary
    std::string_view excerpt = unit;
    if (excerpt.size() > max_bytes) {
        size_t n = max_bytes;
        while (n > 0 && (static_cast<unsigned char>(unit[n]) & 0xC0) == 0x80) {
            n--;
        }
        excerpt = unit.substr(0, n);
    }

    // 2. special cut, on the raw bytes
    if (const auto p = pred(excerpt); p && *p < excerpt.size()) {
        excerpt = excerpt.substr(0, *p);
    }

    // 3. byte map, one byte to one byte
    std::string out(excerpt);
    for (char & c : out) {
        const auto b = static_cast<unsigned char>(c);
        if (b <= 0x1F || b == 0x7F) {
            c = ' ';
        } else if (c == '"') {
            c = '\'';
        } else if (c == ']') {
            c = ')';
        }
    }

    // 4. ellipsis when step 1 or 2 removed bytes
    if (excerpt.size() < unit.size()) {
        out += "...";
    }
    return out;
}

// 5. assemble the stub from the grammar; an empty toolname omits the group (a rendered name is never empty)
static std::string dedup_assemble_stub(const char * roleword, size_t ordinal, std::string_view toolname, const std::string & excerpt) {
    std::string stub = "[duplicate content omitted: byte-identical to ";
    stub += roleword;
    stub += " #" + std::to_string(ordinal);
    if (!toolname.empty()) {
        stub += " (";
        stub += toolname;
        stub += ")";
    }
    stub += ", which begins \"" + excerpt + "\"; unchanged since then]";
    return stub;
}

std::optional<std::string> dedup_build_stub(std::string_view                   first_unit,
                                            const std::string &                role,
                                            size_t                             ordinal,
                                            const std::optional<std::string> & toolname,
                                            const dedup_special_pred &         pred) {
    const char * roleword = dedup_roleword(role);
    if (!roleword) {
        return std::nullopt; // not a participating role: no stub, the unit is rendered in full
    }
    const std::string_view name = (role == "tool" && toolname && dedup_toolname_is_safe(*toolname)) ? std::string_view(*toolname) : std::string_view();

    // 6. verify: a special-text match (only where fixed text meets the excerpt or the name) falls back to the
    //    empty excerpt without the name; if even that matches, no conforming stub exists
    std::string stub = dedup_assemble_stub(roleword, ordinal, name, dedup_excerpt(first_unit, pred));
    if (!pred(stub)) {
        return stub;
    }
    stub = dedup_assemble_stub(roleword, ordinal, {}, "...");
    if (!pred(stub)) {
        return stub;
    }
    return std::nullopt;
}

//
// apply (spec §6.3): the seeded index and the pass itself
//

static uint64_t dedup_rotl(uint64_t x, int b) {
    return (x << b) | (x >> (64 - b));
}

// splitmix64 finalizer: spreads a 64-bit value over all bits
static uint64_t dedup_mix(uint64_t x) {
    x += 0x9e3779b97f4a7c15ULL;
    x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
    x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
    return x ^ (x >> 31);
}

// the 128-bit SipHash key; never logged or exposed (§5 S7)
struct dedup_sip_key {
    uint64_t k0;
    uint64_t k1;
};

// the process default: a random 64-bit handle, which dedup_process_seed() gives out as the default seed,
// and an independent random 128-bit key that only that handle selects. Knowing the handle reveals no key bit
struct dedup_process_key {
    uint64_t      handle;
    dedup_sip_key key;
};

static const dedup_process_key & dedup_process_key_get() {
    static const dedup_process_key pk = [] {
        uint64_t w[4];
        try {
            std::random_device rd;
            for (auto & x : w) {
                x = ((uint64_t) rd() << 32) | rd(); // two 32-bit draws per word, 256 bits in all
            }
        } catch (const std::exception &) {
            // no entropy source: steady_clock and an address, spread by splitmix64. Far weaker, but the server
            // keeps serving; the output never depends on the key, only the flood resistance does
            static const int anchor = 0;
            uint64_t x = (uint64_t) std::chrono::steady_clock::now().time_since_epoch().count() ^ (uint64_t) (uintptr_t) &anchor;
            for (auto & y : w) {
                x = dedup_mix(x);
                y = x;
            }
        }
        return dedup_process_key{w[0] ^ w[1], {w[2], w[3]}};
    }();
    return pk;
}

// the key for a seed: the process key for the process handle, else a key derived from the seed alone,
// so that an injected seed (tests) gives the same key on every run
static dedup_sip_key dedup_sip_key_for(uint64_t seed) {
    const auto & pk = dedup_process_key_get();
    if (seed == pk.handle) {
        return pk.key;
    }
    return {seed, dedup_mix(seed)};
}

// the default hash: SipHash-2-4, a keyed hash built against hash flooding, so a client that does not know
// the key cannot build colliding units (§5 S7). std::hash alone would not do: its multicollisions do not
// depend on any seed mixed in afterwards
static uint64_t dedup_siphash(std::string_view unit, const dedup_sip_key & key) {
    const uint64_t k0 = key.k0;
    const uint64_t k1 = key.k1;
    uint64_t v0 = 0x736f6d6570736575ULL ^ k0;
    uint64_t v1 = 0x646f72616e646f6dULL ^ k1;
    uint64_t v2 = 0x6c7967656e657261ULL ^ k0;
    uint64_t v3 = 0x7465646279746573ULL ^ k1;
    auto round = [&]() {
        v0 += v1; v1 = dedup_rotl(v1, 13); v1 ^= v0; v0 = dedup_rotl(v0, 32);
        v2 += v3; v3 = dedup_rotl(v3, 16); v3 ^= v2;
        v0 += v3; v3 = dedup_rotl(v3, 21); v3 ^= v0;
        v2 += v1; v1 = dedup_rotl(v1, 17); v1 ^= v2; v2 = dedup_rotl(v2, 32);
    };
    auto compress = [&](uint64_t m) {
        v3 ^= m;
        round();
        round();
        v0 ^= m;
    };

    const auto * p = reinterpret_cast<const unsigned char *>(unit.data());
    const size_t n = unit.size();
    size_t i = 0;
    for (; i + 8 <= n; i += 8) {
        uint64_t m = 0;
        for (int j = 0; j < 8; j++) {
            m |= (uint64_t) p[i + j] << (8 * j);
        }
        compress(m);
    }
    uint64_t last = (uint64_t) n << 56;
    for (int j = 0; i + j < n; j++) {
        last |= (uint64_t) p[i + j] << (8 * j);
    }
    compress(last);

    v2 ^= 0xff;
    round();
    round();
    round();
    round();
    return v0 ^ v1 ^ v2 ^ v3;
}

// the index key: the unit's (role, byte length, hash). Candidates under one key are still checked for role
// and length before any byte comparison, so a colliding key costs no comparison unless both match
// (an injected hash gets the seed as given; the default hash gets the seed's key)
static uint64_t dedup_index_key(const std::string & role, std::string_view unit, uint64_t seed, const dedup_sip_key & key,
                                const dedup_hash_fn & hash) {
    const uint64_t h = hash ? hash(unit, seed) : dedup_siphash(unit, key);
    return dedup_mix(h ^ dedup_mix(unit.size() ^ dedup_mix(std::hash<std::string>{}(role))));
}

uint64_t dedup_key(const std::string & role, std::string_view unit, uint64_t seed) {
    return dedup_index_key(role, unit, seed, dedup_sip_key_for(seed), {});
}

uint64_t dedup_process_seed() {
    return dedup_process_key_get().handle;
}

// a first occurrence the later units of its role may reference
struct dedup_candidate {
    std::string                role;
    std::string                bytes;    // the unit's original bytes (common_json offers no view, so indexed units are copied once)
    size_t                     ordinal;  // ORDINAL of its message (§6.4)
    std::optional<std::string> toolname; // TOOLNAME candidate of its message (§6.4), before the allowlist
};

// the TOOLNAME candidate of a tool message: the name of the latest earlier assistant tool_call with its
// tool_call_id, else its own string "name", else none
static std::optional<std::string> dedup_toolname_candidate(const common_json &                                  msg,
                                                           const std::unordered_map<std::string, std::string> & call_names) {
    if (msg.contains("tool_call_id") && msg.at("tool_call_id").is_string()) {
        const auto it = call_names.find(msg.at("tool_call_id").get<std::string>());
        if (it != call_names.end()) {
            return it->second;
        }
    }
    if (msg.contains("name") && msg.at("name").is_string()) {
        return msg.at("name").get<std::string>();
    }
    return std::nullopt;
}

// remember the function name of every tool_call of an assistant message, the later call winning
static void dedup_record_tool_calls(const common_json & msg, std::unordered_map<std::string, std::string> & call_names) {
    if (!msg.contains("tool_calls") || !msg.at("tool_calls").is_array()) {
        return;
    }
    for (const auto & call : msg.at("tool_calls")) {
        if (!call.is_object() || !call.contains("id") || !call.at("id").is_string() ||
            !call.contains("function") || !call.at("function").is_object()) {
            continue;
        }
        const common_json & fn = call.at("function");
        if (fn.contains("name") && fn.at("name").is_string()) {
            call_names[call.at("id").get<std::string>()] = fn.at("name").get<std::string>();
        }
    }
}

dedup_result dedup_apply(const common_json &        messages,
                         const dedup_settings &     settings,
                         const dedup_special_pred & pred,
                         const dedup_hash_fn &      hash,
                         uint64_t                   seed) {
    dedup_result result;
    result.messages = messages; // the one copy; only replaced unit text is written into it
    if (!messages.is_array()) {
        return result;
    }

    // a unit no longer than the shortest stub the grammar allows can never be replaced, and neither can one below
    // min_bytes; equal bytes mean equal length, so neither can be a referenced first occurrence either (§5 S7)
    const size_t shortest_stub = dedup_assemble_stub(dedup_roleword("tool"), 1, {}, "").size();
    const size_t min_indexed = std::max<size_t>((size_t) std::max<int32_t>(settings.min_bytes, 1), shortest_stub + 1);

    const dedup_sip_key key = dedup_sip_key_for(seed);

    std::vector<dedup_candidate>                           candidates;
    std::unordered_map<uint64_t, std::vector<size_t>>      index;      // key -> candidates, every one reachable
    std::unordered_map<std::string, size_t>                role_count; // messages seen so far, per role
    std::unordered_map<std::string, std::string>           call_names; // tool_call id -> function name, latest wins

    for (size_t i = 0; i < messages.size(); i++) {
        const common_json & msg = messages.at(i);
        if (!msg.is_object() || !msg.contains("role") || !msg.at("role").is_string()) {
            continue;
        }
        const std::string role    = msg.at("role").get<std::string>();
        const size_t      ordinal = ++role_count[role];
        if (role == "assistant") {
            dedup_record_tool_calls(msg, call_names);
        }
        if (settings.roles.count(role) == 0 || !msg.contains("content")) {
            continue;
        }

        // the stub for `unit` if it repeats an earlier candidate of this role; indexes it otherwise
        auto process_unit = [&](std::string unit) -> std::optional<std::string> {
            if (unit.size() < min_indexed) {
                return std::nullopt;
            }
            std::vector<size_t> & chain = index[dedup_index_key(role, unit, seed, key, hash)];
            for (const size_t c : chain) {
                const dedup_candidate & first = candidates[c];
                if (first.role != role || first.bytes.size() != unit.size()) {
                    continue;
                }
                result.n_byte_comparisons++;
                if (first.bytes != unit) {
                    continue;
                }
                auto stub = dedup_build_stub(first.bytes, role, first.ordinal, first.toolname, pred);
                if (stub && stub->size() < unit.size()) {
                    result.replacements.push_back({unit.size(), *stub});
                    return stub;
                }
                return std::nullopt; // a repeat, kept in full; the earlier unit stays the reference
            }
            chain.push_back(candidates.size());
            candidates.push_back({role, std::move(unit), ordinal,
                                  role == "tool" ? dedup_toolname_candidate(msg, call_names) : std::nullopt});
            return std::nullopt;
        };

        const common_json & content = msg.at("content");
        if (content.is_string()) {
            if (auto stub = process_unit(content.get<std::string>())) {
                result.messages.at(i)["content"] = *stub;
            }
        } else if (content.is_array()) {
            for (size_t j = 0; j < content.size(); j++) {
                const common_json & part = content.at(j);
                if (!part.is_object() || !part.contains("type") || part.at("type") != "text" ||
                    !part.contains("text") || !part.at("text").is_string()) {
                    continue; // media_marker and any other part is never a unit
                }
                if (auto stub = process_unit(part.at("text").get<std::string>())) {
                    result.messages.at(i).at("content").at(j)["text"] = *stub;
                }
            }
        }
    }
    return result;
}

//
// statistics (spec §6.5)
//

dedup_stats dedup_result::stats() const {
    dedup_stats res;
    res.n = replacements.size();
    for (const dedup_replacement & r : replacements) {
        res.bytes_saved += r.unit_bytes - r.stub.size(); // a stub is always shorter than its unit (§5 S6)
    }
    return res;
}

uint64_t dedup_tokens_saved_est(uint64_t bytes_saved, uint64_t n_text_tokens, uint64_t n_text_bytes) {
    if (bytes_saved == 0 || n_text_bytes == 0) {
        return 0;
    }
    return (2 * bytes_saved * n_text_tokens + n_text_bytes) / (2 * n_text_bytes);
}

//
// the special-text predicate of a served vocab (spec §4.0)
//

// the texts of the vocab's special set, indexed for a scan that costs O(input × distinct lengths per first byte):
// at each input offset only the lengths of texts starting with that byte are looked up in the hash set
struct dedup_special_matcher {
    std::unordered_set<std::string>      storage;               // owns the texts; node-based, so views stay valid
    std::unordered_set<std::string_view> texts;                 // views into storage, looked up without allocating
    std::array<std::vector<size_t>, 256> lengths_by_first_byte; // distinct text lengths, per first byte

    // a copy's views would point into the source's storage; it is only ever held as shared_ptr<const ...>
    dedup_special_matcher()                                          = default;
    dedup_special_matcher(const dedup_special_matcher &)             = delete;
    dedup_special_matcher & operator=(const dedup_special_matcher &) = delete;
    dedup_special_matcher(dedup_special_matcher &&)                  = delete;
    dedup_special_matcher & operator=(dedup_special_matcher &&)      = delete;

    std::optional<size_t> find_first(std::string_view input) const {
        for (size_t i = 0; i < input.size(); i++) {
            for (const size_t len : lengths_by_first_byte[static_cast<unsigned char>(input[i])]) {
                if (len <= input.size() - i && texts.count(input.substr(i, len)) > 0) {
                    return i;
                }
            }
        }
        return std::nullopt;
    }
};

dedup_special_pred dedup_special_text_predicate_from_vocab(const llama_vocab * vocab) {
    // the set the tokenizer splits out of text before BPE/SPM (src/llama-vocab.cpp, the special tokens cache)
    constexpr int special_attrs = LLAMA_TOKEN_ATTR_CONTROL | LLAMA_TOKEN_ATTR_USER_DEFINED | LLAMA_TOKEN_ATTR_UNKNOWN;

    auto matcher = std::make_shared<dedup_special_matcher>();
    const int32_t n_tokens = llama_vocab_n_tokens(vocab);
    for (llama_token id = 0; id < n_tokens; id++) {
        if ((llama_vocab_get_attr(vocab, id) & special_attrs) == 0) {
            continue;
        }
        std::string text = llama_vocab_get_text(vocab, id);
        if (text.empty()) {
            continue;
        }
        auto & lengths = matcher->lengths_by_first_byte[static_cast<unsigned char>(text[0])];
        if (std::find(lengths.begin(), lengths.end(), text.size()) == lengths.end()) {
            lengths.push_back(text.size());
        }
        matcher->storage.insert(std::move(text));
    }
    for (const auto & text : matcher->storage) {
        matcher->texts.insert(text);
    }

    // the predicate owns its match set and keeps no pointer into the vocab
    return [matcher = std::shared_ptr<const dedup_special_matcher>(std::move(matcher))](std::string_view input) {
        return matcher->find_first(input);
    };
}
