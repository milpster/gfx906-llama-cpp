# 2026-09-28 - Prompt lookup optimization assessment

Goal: assess Hayder Tirmazi's prompt lookup optimization stack against `swift_llama_start-q6_q8_q4.sh`, and prepare a fork-local implementation and validation plan without changing production runtime code.

## Baseline

- Source HEAD: `edae694119f59005f8f88c19c71b4280f0f24a5d` on `master`; worktree was already dirty before this assessment.
- Production launcher: `swift_llama_start-q6_q8_q4.sh`.
- Active speculative chain: `--spec-type ngram-mod,draft-dflash`, DFlash `n_max=3`, ngram-mod `n_match=24`, `n_min=28`, `n_max=64`.
- Target context: `-c 393500`, two slots, target KV q8_0 K / q4_0 V, `-ub 384`, devices `rocm0,vulkan1,rocm1`.
- Existing local evidence: the ngram-mod lane is idle on novel content and can draft long replayed spans; one recorded replay produced 54 generated / 45 accepted tokens with mean draft length 46. A fixed-history benchmark can train the shared table and therefore overstate transfer to real traffic.

## Sources

- Article: https://jadidbourbaki.github.io/blog/prompt-lookup-llama-cpp/
- Patch stack: https://github.com/jadidbourbaki/llama.cpp/pull/2, /5, /10, /7.
- Threshold precheck: https://github.com/jadidbourbaki/llama.cpp/pull/12.
- Local implementation: `common/ngram-cache.{h,cpp}`, `common/ngram-mod.{h,cpp}`, `common/speculative.cpp`, `docs/speculative.md`.

## Facts established

1. The article optimizes `ngram-cache`, not the active `ngram-mod` implementation.
2. Local `ngram-mod` is a fixed 4,194,304-entry table of `int32_t` next tokens, about 16 MiB. It hashes a 24-token key directly to one next token, has constant memory, shares the pool across both server slots, and performs no nested-map or static-cache lookup.
3. Local `ngram-cache` still has the exact three inner-map copies fixed by PR #2. This is a small, dependency-free fix and directly applies.
4. PR #5 replaces the outer map with `ankerl::unordered_dense::segmented_map` and vendors about 4.5k lines. PR #10 replaces each inner map with a sorted vector and fixed-trip-count binary search.
5. PR #7 is a larger static-cache format change. It vendors fastconstmap, changes `llama-lookup-create` output, shares one immutable static cache across server slots, and leaves dynamic-cache merge files on the old format. The PR is open, stacked, and not upstream-reviewed or merged.
6. PR #12 adds a frequency precheck before static weighting. It is dependency-free but is stacked on PR #7 and must be checked for exact semantic equivalence, especially when static weighting changes which token wins.
7. The article's 42x/140x figure is drafting-CPU latency, measured on Apple M4 Pro at 4096-token contexts. It is not end-to-end server throughput and not a result for the active ngram-mod plus DFlash production chain.

## Initial transferability judgment

- Keep `ngram-mod,draft-dflash` as the production default until a production-shaped A/B proves otherwise.
- Implement the full article stack as a modernization of the separate `ngram-cache` path, not as changes to `ngram-mod`.
- Land and benchmark the no-copy fix and threshold precheck separately from third-party containers and the new static format. This preserves attribution and gives rollback points.
- Do not add `ngram-cache` to the production chain before measuring its prompt-update cost, per-slot memory, cross-slot behavior, draft precedence, acceptance, and end-to-end TG on novel and replay-heavy workloads.

## Server integration defects found

1. `common_ngram_cache_update()` requires the complete append-only token history and uses `nnew` to limit the update window. The contract is explicit in `common/ngram-cache.h:64-74`.
2. The server implementation instead builds only `tokens_new` and passes that suffix to `common_ngram_cache_update()` at `common/speculative.cpp:2308-2321`. A normal one-token suffix is shorter than every useful n-gram window, so generated tokens generally do not train the context cache.
3. `common_speculative_impl_ngram_cache::begin()` is a no-op. It neither clears nor rebuilds `ngram_cache_context` when a slot starts a new prompt, so slot reuse can retain stale request state and `cache_size` can refer to an unrelated prompt.
4. A dynamic cache file is loaded and copied into every sequence, but the server implementation never merges accepted generation into it and never saves it. `save_dynamic`, `save_static`, `process()`, and `accept()` are unused or no-op. This contradicts the `--lookup-cache-dynamic` help text, which says the cache is updated by generation.
5. Static and dynamic caches are both deep-copied once per sequence at construction. With `-np 2`, each loaded cache has two retained copies, plus the temporary load object during construction. PR #7's immutable shared static cache can materially reduce retained RSS when a large static cache is enabled.
6. The server's ngram-cache depth is hard-coded to eight in `create_state_ngram_cache()` and `common_speculative_n_max()`. This can produce a nine-row target verification batch. The production rig has an observed six-row verification cliff, so draft depths around 5/6/8 must be measured instead of assuming deeper is better.

These defects must be repaired or explicitly scoped before article performance numbers are meaningful in server mode.

## Dependency and format findings

- PR #7 changes 15 files with 8,696 additions. Most of that surface is vendored code rather than the lookup algorithm itself.
- fastconstmap is pinned at commit `990afd04148949300dc00b2206b63af9374c6334` and is Apache-2.0. Its bundled xxHash code is BSD-2-Clause. unordered_dense is MIT.
- The new static format starts with magic `0x70616d63676e6767`, followed by the entries array and serialized verified constmap. The old static format has no compatible header.
- Dynamic-cache merge files remain on the existing format in the article patch stack.
- No persisted cache requirement has been established locally. Do not add a compatibility reader or converter unless a real cache file must be preserved.

## Implementation sequence

Each stage must remain independently testable and revertible.

1. Repair server lifecycle correctness: rebuild per-sequence context state from the full prompt in `begin()`, maintain complete append-only history during generation, handle slot reuse and shorter/replaced prompts, and define the accepted-token update point.
2. Make dynamic-cache behavior honest: either update/save it from accepted generation or remove the server claim that it is updated. Keep this decision separate from lookup-container changes.
3. Port PR #2's three no-copy changes and prove token-for-token draft equivalence.
4. Port PR #12's threshold precheck only after tests cover static weighting, ties, and weighted-winner changes.
5. Port PR #5's outer unordered_dense container and then PR #10's sorted follower vectors as separate measured stages.
6. Port PR #7 last: vendor pinned dependencies, add the static format, share immutable static data across slots, and make malformed or wrong-format input fail clearly.
7. Consider the launcher chain `ngram-mod,ngram-cache,draft-dflash` only after the complete implementation passes correctness and production gates. Keep ngram-mod first because the first implementation that drafts suppresses later implementations for that round.

## Rollback and promotion gates

- Stage rollback: any token-sequence difference, malformed-file crash, stale slot state, RSS regression outside the expected container tradeoff, or statistically meaningful novel-workload TG regression.
- Launcher rollback: retain `ngram-mod,draft-dflash` unchanged unless the candidate improves representative traffic without harming novel prompts or triggering the verification-shape cliff.
- Static-cache promotion additionally requires known corpus provenance, acceptable startup/load time, bounded retained RSS at `-np 2`, and no sensitive production text in the artifact.
- Do not combine stages in one benchmark result. Record deltas after correctness, no-copy, precheck, each container change, and static sharing.

## Planned validation gates

1. Extend existing lookup-example coverage rather than adding a new `tests/*` file without maintainer approval. Cover append-only updates, a one-token generation suffix, new prompt on a reused slot, a shorter replacement prompt, and two interleaved slots.
2. Check token-for-token draft equivalence after every performance patch. Include empty caches, ties, strict/lax thresholds, static weighting that changes the winner, and no-candidate cases.
3. Check static loading with valid, empty, truncated, malformed, old-format, and wrong-magic files. Record load time, peak RSS, retained RSS, and sharing at `-np 2`.
4. Use separate novel, within-request replay, and cross-request replay corpora. Do not use a repeated fixed-history result as the production claim because shared/dynamic caches train on it.
5. Compare the unchanged `ngram-mod,draft-dflash` control with candidate chains at identical model, context, KV, slots, prompt, sampling, and device placement.
6. Run explicit target verification shapes of 5, 6, 8, and 9 rows before choosing ngram-cache depth.
7. Use A/B/A runs with warmup discarded. Record output hash/equivalence, PP, TG, generated and accepted tokens per implementation, draft microseconds, host RSS, and every device's VRAM.

## Remaining decisions before runtime implementation

- Confirm whether any existing static or dynamic lookup cache must remain readable.
- Confirm whether a static corpus may use sanitized production prompts or must use public/synthetic text.
- Runtime code remains unchanged in this assessment. Start with the lifecycle correctness stage only after explicit implementation approval.

## Pre-implementation production baseline gate

Before changing prompt lookup, HEAD `edae694119f59005f8f88c19c71b4280f0f24a5d` was built from scratch as build 11552 in `build-promptlookup-baseline` with the established `build-dflash-novega.sh` ROCm 6.1/Vulkan release configuration. The retained `build-rcfix` control is build 11548 at `7d30edc55`.

The exact production launcher ran through `bench/run-sync0924-validation.sh` with PP16384, TG1024, and temperature-0 SHA checks. An interleaved current/control/current/control/current sequence produced:

| arm | runs | first PP mean | full fill mean | TG1024 mean | acceptance | repro SHA | TG SHA |
|---|---:|---:|---:|---:|---:|---|---|
| current HEAD | 3 | 392.1 t/s | 378.2 t/s | 22.2 t/s | 0.653 | `10d2416fc589` | `162cd5d138f8` |
| retained build-rcfix | 2 | 394.0 t/s | 380.3 t/s | 21.9 t/s | 0.653 | `10d2416fc589` | `162cd5d138f8` |

Current versus retained delta was -0.49% first PP, -0.53% full fill, and +1.37% TG. Every run reported `n_ctx_slot=196864`, completed all 1024 generated tokens, matched both canonical hashes, and returned `repro_ok=true`. No completed log contained a ROCm initialization, allocation, Vulkan, assertion, or invalid-device error.

Verdict: PASS. The latest build preserves production fit, output, acceptance, PP, and TG within run-to-run noise. It is safe to use as the pre-change prompt-lookup baseline.

Evidence: `bench/logs/promptlookup-baseline-20260928-summary.md`, build log `bench/logs/promptlookup-baseline-20260928-build.log`, current lanes `bench/logs/promptlookup-baseline-20260928-r{1,2,3}/`, and retained controls `bench/logs/promptlookup-baseline-20260928-rcfix-control-r{2,3}/`.

## Stage 1 - ngram-cache server lifecycle correctness

Runtime: C++17 through the existing CMake lookup/speculative targets. Production validation uses the established ROCm 6.1 and Vulkan launcher environment; focused cache regressions do not require a model or GPU.

Hypotheses before executable changes:

1. H1 - incremental learning is broken because `draft_one()` passes only the newly appended suffix to `common_ngram_cache_update()`. A normal one-token suffix cannot supply the preceding 1-4 token keys required to learn the new transition.
2. H2 - a reused server slot can retain stale request-local n-grams because `common_speculative_impl_ngram_cache::begin()` does not clear `ngram_cache_context` or reset `cache_size`.
3. H3 - context shift and speculative checkpoint rollback can shorten or rewrite `slot.prompt.tokens`. Continuing with the previous `cache_size` would violate the append-only update contract, so a shortened history must clear and rebuild the request-local cache from the complete current history.

Planned regression surface: extend existing `examples/lookup` infrastructure rather than adding a new `tests/*` file. Cover one-token incremental learning, request reset on slot reuse, shorter-history rebuild, and independent state for interleaved sequences through the public `common_speculative_*` API if it remains model-free.

Planned runtime change: only `common/speculative.cpp`. Construct the complete current history as `prompt + id_last`, calculate `nnew` from the per-sequence cached length, clear on `begin()` and on history shrink, and pass the complete history to `common_ngram_cache_update()`.

Rollback: revert only the stage-1 edits to `common/speculative.cpp` and the existing lookup regression host. The production launcher and baseline build remain unchanged.

### Stage 1 execution

Regression host: `bench/test-ngram-cache-server-lifecycle.cpp` (fork-local, model-free, CPU-only). It drives `common_speculative_*` exactly like the server: `begin(seq, prompt)` at prompt completion, then draft rounds with the full prompt plus a separate `id_last`, one accepted token per round.

Build and run (no GPU, no model, safe next to the live server):

```
g++ -std=c++17 -O2 -Icommon -Ivendor/nlohmann/.. -Ivendor/sheredom/.. -Iinclude -Iggml/include \
    -c bench/test-ngram-cache-server-lifecycle.cpp -o /tmp/opencode/ngramcache-test.o
g++ /tmp/opencode/ngramcache-test.o -o /tmp/opencode/test-ngram-cache \
    build-promptlookup-baseline/bin/{libllama-common.so,libllama.so,libggml.so,libggml-cpu.so,libggml-hip.so,libggml-vulkan.so,libggml-base.so} \
    build-promptlookup-baseline/common/libllama-common-base.a -Wl,-rpath,.../build-promptlookup-baseline/bin:/opt/rocm-6.1.0/lib
```

Red run against the unmodified baseline build (`bench/logs/promptlookup-ngramcache-stage1-red.log`): 3 failures.

- H1 confirmed: after ten one-token generation rounds and a repeated suffix, the draft was empty; only `{7,8,9,10,1,2,3,4}` would prove incremental learning.
- H2 confirmed: a new request on a reused slot drafted `{1,2,3,4,5,6,9,1}` purely from the previous request's n-grams.
- H3 confirmed: after history shrink (rollback shape), the draft was `{7,8}` from stale keys; expected empty after rebuild.
- Guards passed: first-round prompt learning exact chain `{2,3,4,1,2,3,4,1}` and two-sequence isolation.

Fix: `common/speculative.cpp`, `common_speculative_impl_ngram_cache` only.

- `begin()` now clears the sequence's `ngram_cache_context` and resets `cache_size` to 0. The first draft round trains on the whole `prompt + id_last` window.
- `draft_one()` builds the full history `inp = prompt + id_last` once, reuses it for update and draft, and computes `nnew = inp.size() - cache_size`. If `inp` shrank below `cache_size` (context shift or checkpoint rollback) the context cache is cleared and rebuilt from the current window, per the `ngram-cache.h` append-only contract. The old duplicate `tokens_new`/`inp` construction is gone.

Net diff: 18 insertions, 19 deletions in one file.

Green run after incremental rebuild (`bench/logs/promptlookup-ngramcache-stage1-green.log`): all 7 checks pass, exit 0.

Rebuild verification: `llama-common`, `llama-server`, and all four `llama-lookup*` targets rebuilt clean in `build-promptlookup-baseline`; `speculative.cpp` recompiled with zero warnings. clangd diagnostics for these files are include-resolution false positives (no compile database in this tree); the CMake compiler flags (`-Wall -Wextra -Wpedantic ...`) are the authoritative gate.

Untouched: `ngram-mod`, dynamic/static cache behavior, containers, thresholds, launcher, and all article performance patches. The production chain `ngram-mod,draft-dflash` is unchanged; since ngram-cache is not in the production chain, this fix cannot affect the live server's outputs.

Pending: production validation lane (GPU, `bench/run-sync0924-validation.sh`) requires the live server down; awaiting user go-ahead.

### Stage 1 production validation runbook (pending server-down)

The live production server (build-rcfix, port 8009) owns all three GPUs. `bench/run-sync0924-validation.sh` hard-fails while any GPU-backed llama-server runs (exclusivity guard), which is the correct behavior - launching against the live tight-fit deployment would risk OOM on the production instance.

Verified wiring: `swift_llama_start-q6_q8_q4.sh` takes `BIN`/`LD_LIB` from the environment (defaults build-rcfix), and the validation script exports both from `$BUILD/bin`. The accepted baseline protocol was 3 current lanes on this exact wrapper with `FILL1=16384 TG_N=1024`.

Ready-to-fire once the user confirms the server is down (three fixed-build lanes, compared against the recorded pre-change means: PP 392.1 / fill 378.2 / TG 22.2 / acc 0.653 / repro SHA `10d2416fc589` / TG SHA `162cd5d138f8`):

```
for r in 1 2 3; do
  BUILD=$PWD/build-promptlookup-baseline \
  OUT=$PWD/bench/logs/promptlookup-ngramcache-fix-20260928-r$r \
  FILL1=16384 TG_N=1024 bash bench/run-sync0924-validation.sh
done
```

Expected verdict: unchanged PP/fill/TG/acceptance and identical SHAs - the fix touches only the ngram-cache implementation, which the production chain (`ngram-mod,draft-dflash`) does not instantiate.

### Stage 1 production validation result

User took the production server down; GPUs verified free. Three fixed-build lanes ran through `bench/run-sync0924-validation.sh` (`BUILD=build-promptlookup-baseline`, `FILL1=16384`, `TG_N=1024`):

| arm | lanes | PP | fill | TG | acc |
|---|---:|---:|---:|---:|---:|
| baseline (pre-edit, same build) | 3 | 392.1 | 378.2 | 22.2 | 0.653 |
| build-rcfix control | 2 | 394.0 | 380.2 | 21.9 | 0.653 |
| ngramcache-fix | 3 | 389.6 | 376.5 | 23.6 | 0.653 |

Deltas vs baseline: PP -0.64%, fill -0.45%, TG +6.3%. Every lane: `n_ctx=196864`, all 1024 TG tokens, `repro_ok=true`, repro SHA `10d2416fc589`, TG SHA `162cd5d138f8` - identical to both comparison arms. Error sweep found only the benign `dflash requires ctx_other` startup line (byte-identical in baseline lanes).

TG +6.3% is uniform across the three fixed lanes; the edited code path is never instantiated by the production chain, so this is attributed to host state (no concurrent compile load during these lanes), not the fix. Not a regression.

Verdict: PASS. Stage 1 is complete and production-safe. Evidence: `bench/logs/promptlookup-ngramcache-fix-20260928-summary.md` and lane dirs `bench/logs/promptlookup-ngramcache-fix-20260928-r{1,2,3}/`.

Next per plan: stage 2 (dynamic-cache honesty: update/save or retract the `--lookup-cache-dynamic` claim), then PR #2 no-copy, PR #12 precheck, PR #5/#10 containers, PR #7 shared static cache - each a separate measured stage.

## Stage 2 - honest dynamic lookup cache

User question mid-stage: "we might want to enable ngram-cache in our prod config for that dont we?" Answer recorded: yes, that is the planned endgame chain (`ngram-mod,ngram-cache,draft-dflash`), but enablement stays gated behind the container stages because (1) current drafting cost is the unoptimized std::unordered_map path, (2) first-round training on a 160k prompt costs roughly 100-250 MB per slot of context cache on a rig with ~1 GB margins, (3) a live `-lcd` grows unbounded on agentic traffic - a bound/eviction is a new pre-enablement gate, (4) hardcoded n_draft=8 can produce 9-row verify batches and this rig has the 6-row verification cliff; a candidate trial must clamp `--spec-draft-n-max`. First-drafter-wins precedence keeps ngram-mod dominant, ngram-cache covers the novel-content gap.

### Design

`common_speculative.cpp`, `common_speculative_impl_ngram_cache` only, plus one help-text line in `common/arg.cpp`:

- Dynamic cache is now ONE shared map at impl level (was a per-sequence deep copy). Drafting consults the shared map, so learning is visible to all slots immediately.
- With `-lcd` given, each draft round trains the shared dynamic cache on the same window/`nnew` as the context cache (`save_dynamic` gate; without the flag, behavior is byte-identical to stage 1).
- Missing dynamic file at startup is tolerated (warn, start empty) - a first run with `-lcd` previously hit GGML_ABORT. Static-cache failures still abort.
- The impl's destructor saves the dynamic cache on clean shutdown - same semantics as the `llama-lookup` example. Save errors are logged, never thrown from the destructor.
- `begin()` stays a pure per-request reset (stage 1 behavior).
- Removed `create_state_ngram_cache()` (by-value helper): its temporary copies would trigger destructor saves, and it had a latent `save_static`/`save_dynamic` argument swap that was harmless only while both were false. Construction is now direct in `common_speculative_init`.
- Help text: `-lcd ... (updated by generation, saved on exit)`.

### Mid-stage corrections (recorded for honesty)

1. First design merged a slot's context into dynamic at that slot's next `begin()`. The cross-slot regression caught the gap: slot 1 never sees slot 0's learning until slot 0 runs again. Redesigned to train-during-draft as above.
2. One green run was executed against a stale `libllama-common.so` (relinked test binary, no rebuild) - produced contradictory results. Rebuilt, then valid.
3. The dynamic tests initially were not hermetic: persisted `/tmp` cache files compounded counts across test executions (load + retrain = doubled counts), flipping T6 to a full 8-token chain. This is correct empirical-cache behavior (counts compound across sessions by design), but tests must start clean - added `std::remove` before each dynamic test. Noted for the future bounded-growth stage: compounding counts across long uptimes also lowers effective strict thresholds over time.

### Evidence

Red (stage-1-fixed build, `bench/logs/promptlookup-ngramcache-stage2-red.log`): dynamic tests draft empty; `persist-save` and `persist-load` both die with GGML_ABORT (exit 134) on the missing dynamic file - the first-run `-lcd` defect demonstrated.

Green (`bench/logs/promptlookup-ngramcache-stage2-green.log`): all 10 default checks pass, `persist-save` exit 0 (file written on shutdown), `persist-load` exit 0 (reloaded process drafts the learned pattern), and a second consecutive default run passes (hermetic).

Rebuild: `llama-common`, `llama-server`, `llama-lookup`, `llama-lookup-stats` clean, zero warnings.

### Cost note

With `-lcd`, each draft round trains two maps instead of one (context + dynamic), doubling update work per round. The first round of each request trains the full prompt window into both. Container stages (PR #5/#10) reduce exactly this cost; production enablement remains gated behind them and the dynamic bound.

Pending: stage-2 production validation lanes plus one bundled clamped candidate lane (`ngram-mod,ngram-cache,draft-dflash`, no `-lcd`, `--spec-draft-n-max` 5) in the next server-down session.

### Stage 2b - configured ngram-cache depth

The hard-coded ngram-cache depth of eight was replaced with `std::max(1, params.draft.n_max)` in both construction and `common_speculative_n_max()`. This keeps the implementation and server verification width consistent. The production setting is three, not the provisional depth-five idea above; this avoids the measured six-row verification cliff.

The model-free regression now explicitly supplies `params.draft.n_max` and includes a depth check: with `n_max=2`, the learned chain drafts exactly `{2,3}`. The complete run passed 11 default checks and separate save/load processes. `llama-common`, `llama-server`, `llama-lookup`, and `llama-lookup-stats` rebuilt with zero warnings. Evidence: `bench/logs/promptlookup-ngramcache-stage2b-green.log`.

### Stage 2 production and candidate validation

Three current-production-chain lanes (`ngram-mod,draft-dflash`) ran through `bench/run-sync0924-validation.sh` at PP16384/TG1024:

| lane | PP | fill | TG | acc | repro SHA | TG SHA |
|---|---:|---:|---:|---:|---|---|
| r1 | 384.9 | 371.8 | 23.3 | 0.653 | `10d2416fc589` | `162cd5d138f8` |
| r2 | 389.3 | 376.2 | 23.5 | 0.653 | `10d2416fc589` | `162cd5d138f8` |
| r3 | 388.7 | 375.2 | 23.5 | 0.653 | `10d2416fc589` | `162cd5d138f8` |
| mean | 387.6 | 374.4 | 23.4 | 0.653 | identical | identical |

Every control lane reported `n_ctx=196864`, completed all 1024 tokens, and returned `repro_ok=true`. Against the stage-1 production gate, mean PP/fill/TG deltas are -0.5%/-0.6%/-0.7%, inside the run-to-run band. Stage 2 therefore passes the current-production safety gate.

The validation wrapper gained a backward-compatible `LAUNCHER` override. `bench/run-ngramcache-candidate.sh` generates an output-local launcher changing only the chain to `ngram-mod,ngram-cache,draft-dflash`, copies the existing chat template beside it, and invokes the same validation gate. Production `swift_llama_start-q6_q8_q4.sh` remains unchanged. The first attempt exposed the missing-template harness issue and stopped before model loading; it is not a measurement.

Two successful candidate lanes, without `-lcd` and at `n_max=3`, produced:

| lane | PP | fill | TG | acc | repro SHA | TG SHA |
|---|---:|---:|---:|---:|---|---|
| r1 | 385.7 | 372.8 | 22.9 | 0.626 | `10d2416fc589` | `ee7db088f716` |
| r2 | 389.4 | 376.1 | 22.9 | 0.626 | `10d2416fc589` | `ee7db088f716` |
| mean | 387.6 | 374.5 | 22.9 | 0.626 | identical | changed identically |

Against the same-session control, PP and fill are flat, TG is -2.3%, and acceptance is lower by 0.027 absolute. The candidate's separate before/after repro lane remains canonical and reproducible, but the 1024-token deep-generation SHA changes repeatably. This fails both the performance and output-identity promotion gates.

Verdict: keep production at `ngram-mod,draft-dflash`. Do not enable ngram-cache in the launcher from this stage. Stage-2 lifecycle/dynamic changes remain valid and inactive in production; later container/no-copy work can be evaluated independently, but this direct chain candidate is rejected. Full summary: `bench/logs/promptlookup-stage2-candidate-20260928-summary.md`.

## Basic candidate repair - ignored minimum draft depth

Three hypotheses were checked before changing runtime code:

1. Request-local ngram-cache uses lax thresholds, so one observation can produce a draft and preempt the stronger DFlash implementation.
2. Partial ngram-cache drafts change the target verification batch shape and can move greedy logits across a near tie even though verification still samples from the target model.
3. A checkpoint or rollback defect corrupts target state after an ngram-cache rejection.

A trace-enabled repeat reproduced the candidate result (`TG=22.5`, acceptance `0.626`, deep SHA `ee7db088f716`). Per-implementation cumulative stats after all four requests were:

- ngram-cache: 150 drafts, 341 generated tokens, 142 accepted; first/second/third-position acceptance 0.453/0.333/0.160.
- DFlash: 352 drafts, 1049 generated tokens, 679 accepted; first/second/third-position acceptance 0.824/0.639/0.466.
- Ngram-mod: five replay drafts, 305 generated tokens, 206 accepted.

Ngram-cache owned 150 rounds before DFlash; 34 drafts had length one, 41 had length two, and 75 had length three. In the deep TG request, a one-token ngram-cache verification occurred immediately before the output path that later selected `explained` instead of the control's `mathematically`. No rollback occurred in that request. This supports hypotheses 1 and 2 and gives no evidence for hypothesis 3.

The concrete integration defect is that ngram-cache ignores the existing `--spec-draft-n-min` option. Draft-simple, Eagle, DFlash, MTP, and ngram-mod all clear drafts shorter than `params.draft.n_min`; ngram-cache returns every non-empty partial draft. The minimal repair is to make ngram-cache honor the same option. The candidate will use `n_min=3`, so one- and two-token matches fall through to DFlash and all accepted candidate verification batches keep the production four-row shape. A focused red test will first prove the option is currently ignored.

The red test reproduced the defect: with `n_min=2`, ngram-cache returned `{3}` instead of no draft. After wiring `params.draft.n_min` into ngram-cache, all 12 focused checks plus save/load persistence passed and affected targets rebuilt with zero warnings.

The first repaired GPU lane (`n_min=3`) did not pass promotion: PP 396.3, fill 382.7, TG 21.5, acceptance 0.637, deep SHA `bef6282a7d3d`. A trace repeat reproduced TG 21.2, acceptance 0.637, and the same SHA. The repaired trace showed that ngram-cache now emitted only full-depth drafts, but its deep-request increment was 45 drafts / 135 proposed tokens / 37 accepted tokens, or 0.82 accepted tokens per owned round. DFlash's increment was 326 drafts / 978 proposed / 615 accepted, or 1.89 accepted tokens per owned round.

Therefore minimum depth is a real basic integration fix but not enough for chain promotion. The next confirmed defect is the request-local confidence policy: context lookup uses the lax table `{2,2,1,1}` with 50% allowed at 3/4-gram depth, so a single observed continuation is automatically considered confident and can suppress DFlash. The next red test requires a single-observation context match to return no draft; the repair will use the already-existing strict table `{4,3,2,2}` / `{75,66,66,66}` for request-local lookup as well as dynamic lookup.

Applying strict thresholds globally made the new confidence test pass but correctly exposed a compatibility regression: five existing request-local replay checks stopped drafting. That broad change was reverted. Strict request-local matching is now explicit through `--spec-ngram-cache-strict`; lax behavior remains the default for standalone users and lookup examples. `common_ngram_cache_draft()` accepts a `strict_context` selector with a default of false, and the server passes the new ngram-cache setting. The candidate harness enables strict mode and `--spec-draft-n-min 3`.

Final focused gate: all 13 default checks pass, including minimum depth and single-observation rejection in strict mode; save/load persistence passes in separate processes. All affected targets rebuild with zero warnings. Evidence: `bench/logs/promptlookup-ngramcache-basic-repair-green.log`, `bench/logs/promptlookup-ngramcache-confidence-red.log`, and `bench/logs/promptlookup-ngramcache-strict-{build,green}.log`.

Final production-shaped A/B/A at PP16384/TG1024:

| arm | PP | fill | TG | acc | repro SHA | TG SHA |
|---|---:|---:|---:|---:|---|---|
| strict candidate r1 | 399.3 | 385.2 | 22.0 | 0.650 | `10d2416fc589` | `162cd5d138f8` |
| strict candidate r2 | 399.6 | 384.5 | 20.9 | 0.650 | `10d2416fc589` | `162cd5d138f8` |
| production control | 399.2 | 385.4 | 21.1 | 0.653 | `10d2416fc589` | `162cd5d138f8` |
| strict candidate r3 | 395.6 | 382.0 | 20.9 | 0.650 | `10d2416fc589` | `162cd5d138f8` |
| candidate mean | 398.2 | 383.9 | 21.3 | 0.650 | identical | identical |

Candidate versus same-session control is PP -0.3%, fill -0.4%, TG +0.8%, acceptance -0.003 absolute. All completed lanes report `n_ctx=196864`, all 1024 tokens, and `repro_ok=true`. The canonical deep SHA is restored in every repaired lane. One r2 attempt bus-faulted during model loading before speculative initialization; its clean retry is the recorded r2 result.

Verdict: PASS for the basic request-local repair. It restores output identity and removes the performance regression, but shows no meaningful novel-workload gain. Production remains `ngram-mod,draft-dflash`; continue no-copy and container work before reconsidering ngram-cache enablement. Summary: `bench/logs/promptlookup-ngramcache-basic-repair-20260928-summary.md`.

## Dynamic-cache cold/warm gate

The user requested a file-backed dynamic-cache test after the basic request-local repair. The production launcher remains untouched. `bench/run-ngramcache-candidate.sh` now accepts an optional absolute `DYNAMIC_CACHE` path; when absent, generated launchers are unchanged, and when present they add `-lcd <path>` to the strict `ngram-mod,ngram-cache,draft-dflash` candidate.

Protocol:

1. Delete only the dedicated test artifact `bench/logs/promptlookup-dynamic-cache-20260928.bin`.
2. Run a cold PP16384/TG1024 candidate lane. The missing file must start empty, train during requests, complete with canonical SHAs, and be saved on graceful server shutdown.
3. Record file size and SHA-256.
4. Run a warm lane against the same file. It must reload successfully, preserve canonical outputs, and not regress PP/fill/TG versus the repaired no-file candidate.
5. Record post-warm size/SHA to expose count compounding or growth. Do not promote `-lcd`; bounded growth remains a separate gate.

### Dynamic-cache result

| arm | PP | fill | TG | acc | deep TG SHA | repro before/after |
|---|---:|---:|---:|---:|---|---|
| repaired no-file mean | 398.2 | 383.9 | 21.3 | 0.650 | `162cd5d138f8` | canonical / canonical |
| dynamic cold | 398.5 | 383.6 | 20.7 | 0.648 | `162cd5d138f8` | canonical / canonical |
| dynamic warm | 395.6 | 382.3 | 20.3 | 0.640 | `162cd5d138f8` | `10d2416fc589` / `3ea46bc7612e` |

The cold lane correctly handled a missing file, trained, completed, and saved on graceful shutdown. The artifact was 296,104 bytes with SHA-256 `25f68d57ebed612938fb666ea3a8bd13dde8e17ce31ef466c646930e9107a665`.

The warm lane loaded the same file without error. After the repeated workload it grew to 306,096 bytes (+9,992, +3.4%) and SHA-256 `22811273843e83565b59485f1ae9ee2c24d226d531563eec821e4374c05e3504`. Deep TG stayed canonical, but the post-workload short repro changed deterministically and `repro_ok=false`. TG fell 4.7% and acceptance 0.010 absolute versus the no-file repaired candidate.

Interpretation: file persistence works, but persisted counts compound. Reloading the first session and retraining the same workload raises stale continuations across confidence thresholds; by the final repro request, this changes verification and the output path. This confirms the earlier bounded-growth/count-decay gate is functional, not theoretical.

Verdict: FAIL `-lcd` promotion. Keep dynamic persistence disabled. The request-local strict candidate remains valid; dynamic cache needs bounded or decayed counts and a stable confidence policy before another production-shaped trial. Full summary: `bench/logs/promptlookup-dynamic-cache-20260928-summary.md`.

## Frozen-snapshot short-template workload

The next gate isolates the workload dynamic ngram-cache is intended to cover: repeated short JSON syntax with changing values before any exact 24-token span. Training uses 512 compact records shaped as `{"record":"T00000","status":"success","retry":false,"value":100000}`. The record and value change every line, so persisted 1-4 token continuations can become confident while ngram-mod's 24-token exact-history key should not transfer across records.

`bench/dynamic-cache-workload.py` has two modes. `train` sends the deterministic synthetic corpus as one prompt and generates one token, which makes the server train the shared dynamic map from the full prompt without relying on variable model output. `eval` sends one held-out instruction ending at `{"record":"E9000"` and requests 512 greedy tokens. It reports total draft proposals and acceptances, accepted tokens per generated token and per proposed draft token, TG, output SHA, line count, template matches, and completion text.

The evaluation protocol freezes the training artifact. Each measured dynamic lane receives a new copy of the immutable snapshot, runs exactly one held-out request, and discards the mutated copy. Controls are a fresh production chain and a fresh strict ngram-cache candidate without `-lcd`. This prevents prior evaluation requests from compounding counts and makes repeated snapshot lanes comparable.

Harness changes are limited to a backward-compatible `CLIENT` override in `bench/run-sync0924-validation.sh` and the new executable workload client. The default remains `bench/cmp-client.py`; non-executable Python clients still run through `python3`, while the PEP 723 workload client runs through its `uv` shebang.

Pre-GPU validation: both shell scripts pass `bash -n`; Ruff's strict rule set passes after excluding documentation/copyright/line-length/CLI-print rules that do not apply to this benchmark script; Ruff format passes; dependency-aware basedpyright reports zero errors and one expected exhaustive-match warning on the required `assert_never` branch; the invalid-mode boundary raises the typed `ConfigError`; and `git diff --check` passes. The workspace LSP still uses the repository's Python 3.9 root config and cannot resolve PEP 723 dependencies, so its `StrEnum`, `assert_never`, and `httpx2` diagnostics do not describe the script's declared Python 3.12 runtime.

GPU execution has not started. Before it does, recheck for a live `llama-server` and announce exclusive GPU use.

### Training-lane correction

The first GPU training attempt completed its 14,336-token prompt and one generated token, but shutdown produced a zero-byte dynamic cache. This is not a persistence failure: the candidate chain still put ngram-mod first, and the repeated training corpus gave that implementation a successful draft before ngram-cache received a turn. Since dynamic training currently happens inside ngram-cache's `draft_one()`, first-success precedence prevented all training.

The candidate launcher generator now accepts `SPEC_CHAIN`, defaulting to the previous `ngram-mod,ngram-cache,draft-dflash` value. Only the training lane will set `SPEC_CHAIN=ngram-cache,draft-dflash`, guaranteeing one ngram-cache update from the synthetic prompt. Evaluation lanes retain the production-order candidate chain. The empty first artifact and its lane are excluded from measurement.

The training-only chain then showed `ngram-cache #calls(b,g,a)=1,0,0` and again saved an empty file. The one-token completion ended after the target's initial token and never entered a speculative draft round. The client training request now generates four tokens; this is enough to execute `draft_one()` after the initial target token while keeping training output irrelevant. The second empty artifact and lane are also excluded.

### Frozen-snapshot result

The corrected training lane executed one ngram-cache draft round, trained the 14,336-token corpus, and saved a 98,520-byte snapshot with SHA-256 `98d146fb12ae8944948c977152a899c3ba7c5d3a82b095f8fd68089afb664376`. The master was made read-only. Every dynamic evaluation started from a separate writable copy.

| arm | lanes | TG mean | proposed | accepted | token acceptance | SHA |
|---|---:|---:|---:|---:|---:|---|
| production control | 2 | 29.032 | 393 | 380 | 96.69% | `4c08e5685c89` |
| strict no-file | 2 | 30.097 | 396 | 378 | 95.45% | `4c08e5685c89` |
| frozen snapshot | 2 | 29.638 | 408 | 374 | 91.67% | `4c08e5685c89` |

All lanes completed 512 tokens and produced the same 23-record output. No-file was +3.67% versus production control. The snapshot was +2.09% versus control but -1.53% versus no-file, so it failed the required incremental benefit.

Trace attribution: ngram-mod emitted zero drafts in both traced candidate lanes. No-file ngram-cache owned 72 rounds and accepted 200 tokens, while DFlash owned 60 and accepted 178. With the snapshot, ngram-cache owned 92 rounds and accepted 242, while DFlash fell to 44 rounds and 132 accepted. The cache's 20 additional owned rounds gained 42 ngram-cache accepts but displaced 46 DFlash accepts, producing four extra verification rounds and four fewer accepted tokens overall.

All three mutated evaluation copies were byte-identical: 109,640 bytes, SHA-256 `5b44c3fbb8b96dcfaee4a7188df45e139c81e720e012480a2115235d548dbbde`, +11.3% after one request. The read-only master remained unchanged. The error sweep was clean.

Verdict: FAIL dynamic-cache promotion. Keep production at `ngram-mod,draft-dflash`, keep `-lcd` disabled, and retain the strict request-local repair only. Dynamic persistence needs bounded/decayed counts and an expected-utility policy that does not preempt a stronger next drafter. Full evidence: `bench/logs/promptlookup-dynamic-benefit-20260928-summary.md`.

### 1.5 launcher duplicate with ngram-cache + dynamic file

Added `swift_1.5_llama_start-q6_q8_q4-ngcache.sh`, a copy of `swift_1.5_llama_start-q6_q8_q4.sh` (8009 lane) that adds the ngram-cache drafter and the file-backed dynamic cache. Deltas only:

- `--spec-type "$SPEC_TYPE"` defaulting to `ngram-mod,ngram-cache,draft-dflash` (env-overridable, e.g. `SPEC_TYPE=ngram-cache,draft-dflash`).
- `--spec-ngram-cache-strict` (request-local confidence gate, validated above).
- `-lcd "$NGRAM_CACHE_FILE"` defaulting to `$LOG_DIR/ngram-cache.bin` (load-if-present, create-if-missing, save-on-clean-shutdown).
- Default port 8010 and log `llama-server-ngcache-iq6v-f16-f16.log` so the 8009 lane is untouched.
- `BIN`/`LD_LIB` default to `build-promptlookup-baseline`, NOT `build-rcfix`.

Build fix (caught in review): the original points at `build-rcfix`, whose `--help` lists `ngram-cache` in `--spec-type` and has `-lcd`, but does NOT define `--spec-ngram-cache-strict` (grep count 0); `build-promptlookup-baseline` has both (count 1). So the duplicate must run the promptlookup baseline or it dies on the strict flag. Also corrected a transcription error in the copy: original is `-ts 35,23,43`, first draft had `36,22,43`.

Verified: `bash -n` clean; `git diff --check` clean; `diff` vs the 1.5 original shows only the intended deltas (build ref, PORT 8010, the three ngram-cache args, the ngram-cache log file, `-ts` restored to 35,23,43). `build-promptlookup-baseline/bin/llama-server --help` confirms `--spec-ngram-cache-strict` present. Not launched (GPU is shared with production; start only on user go).

On "turn off ngram-mod": traced lanes show ngram-mod emitted 0 drafts on the short-template workload (it needs 24+ token exact matches; 132 calls / 0 gen, dur ~0.013 ms). Its per-round cost is negligible and its production value is long replay (F5: 54 gen / 45 acc, mean len 46). Recommendation: keep it first in the chain; A/B it off with `SPEC_TYPE=ngram-cache,draft-dflash` if replay coverage is not wanted.

### Production ngcache run: warnings + empty -lcd file (2026-09-29)

The ngcache launcher ran ~30.5 h (log `log/llama-server-ngcache-iq6v-f16-f16.log`, single run, timestamps 0.00 -> 30.35). Two findings from the user's log excerpt:

1. Both repeating warnings are pre-existing fork behavior, NOT ngram-cache: the old 8009 lane log (`build-rcfix`, chain `ngram-mod,draft-dflash`) contains the same pairs (8x each vs 9x on ngcache).
   - `init: embeddings required but some input tokens were not marked as outputs -> overriding` (`src/llama-batch.cpp:165`): chunked-prefill batches do not mark outputs; when the embeddings path needs them the code overrides. Self-healing, informational, fires per fill batch.
   - `process: zero-filled 25 draft-cache hole rows for seq 1 (skipped mtmd chunk / reused prefix)` (`common/speculative.cpp`, see BUG-GDN-MTMD.md): the session prompt contains an image chunk (~25 mtmd rows) the drafter cannot embed; on prefix reuse those draft-KV rows are holes and get zero-filled so drafting never reads stale rows. The fix working as designed, once per fill event.
2. Empty `-lcd` file, three stacked causes:
   - Save is destructor-only (`common_speculative_impl_ngram_cache::~...`, speculative.cpp) - no mid-run writes. The hard-killed server (log ends mid-generation, no shutdown lines) never ran it.
   - Second Ctrl+C calls `exit(1)` from the signal handler (server.cpp) - skips ALL stack destructors, so even a patient double-interrupt loses the save. First signal printed nothing while the task queue drained in-flight generations (~6 t/s), which is why shutdown "takes ages" and gets killed.
   - Even when the destructor DID run (0-byte file mtime mid-run teardown), the in-memory cache was empty: training happens inside ngram-cache `draft_one()` (speculative.cpp:2347, `if (save_dynamic)`), and first-success precedence means ngram-mod is consulted on every decode round - on this replay-heavy agent traffic it claimed all rounds, ngram-cache `draft_one` never ran, zero n-grams learned. Same failure mode as the first bench training lane, now seen in production.

### Verbose shutdown + save logging (2026-09-29)

Change (build-promptlookup-baseline, rebuilt clean):
- `tools/server/server.cpp`: first SIGINT/SIGTERM prints `Received termination signal, shutting down gracefully (running tasks must finish, send again to force exit)...` (fprintf, async-signal-safe, matches the existing second-signal style); after the drain `task queue stopped`; after HTTP join `http thread stopped`; before destructor phase `releasing model and caches (process exits when done)`.
- `common/speculative.cpp` destructor: `saving dynamic lookup cache: <path> (<N> ngrams)` + `saved dynamic lookup cache in <ms> ms` at INFO (visible without -v). N=0 now explains an empty file in the log itself.

CPU-only validation (Qwen3.5-0.8B-Q4_0.gguf, user-downloaded; `-ngl 0`, HIP+VK devices hidden so production GPUs untouched): clean SIGTERM produced the full sequence - signal line -> task queue stopped -> cleaning up -> http thread stopped -> releasing model and caches -> `saving dynamic lookup cache: /tmp/opencode/ngcache-smoke.bin (0 ngrams)` -> `saved ... in 0 ms` -> 0-byte file written, process exited ~2 s. Constructor warning `dynamic lookup cache not found, starting empty` confirmed the impl was built. Earlier smoke variants: bge-m3 rejected spec ("speculative decoding not supported by this context"), DFlash2 GGUF needs ctx_other (draft head, cannot run standalone), stalled HF download of BF16 1.56 GB killed and cleaned.

Notes: `build-rcfix` (running 8009 lane) lacks the new lines until rebuilt+restarted. On the real ngcache workload expect `(0 ngrams)` unless ngram-cache actually gets rounds - the starvation is the actual dynamic-cache design gap. git diff --check clean.

### Dynamic-cache admission policy (2026-09-29)

Design: the dynamic cache previously drafted whenever the built-in strict thresholds passed (top continuation holding >= 66-75% of observations, >= 2-4 samples). The bench showed that bar still lets weak rounds preempt DFlash (2.63 vs 3.00 accepted tokens/round -> -1.53% TG). Admission policy: a configurable floor `P` on the top continuation's observation share; a dynamic match only drafts when `max_count/sum_count >= P`, per drafted position (the chain stops as soon as a position falls below the bar). Request-local (context) drafting is untouched - it already has the strict gate and measured +3.67% standalone.

Implementation (build-promptlookup-baseline, rebuilt clean):
- `common/ngram-cache.{h,cpp}`: `common_ngram_cache_draft` gains `float p_min_dynamic = 0.0f` (defaulted - examples/lookup and other callers unchanged). The dynamic `try_draft` call now uses `max(draft_min_percent_strict[i], (int)(p_min*100))` as its percent gate.
- `common/common.h`: `common_params_speculative_ngram_cache::p_min` (default 0.0 = old behavior).
- `common/arg.cpp`: `--spec-ngram-cache-p-min P` (env LLAMA_ARG_SPEC_NGRAM_CACHE_P_MIN), same pattern as `--spec-draft-p-min`.
- `common/speculative.cpp`: passes `params.p_min` through.

Verified: incremental build clean; `--help` lists the flag; `--spec-ngram-cache-p-min 0.75` parses. git diff --check clean. GPU bench (no-file vs frozen snapshot at p_min 0.5/0.75/0.9, reuse bench/dynamic-cache-workload.py protocol) pending user GPU go - production 8009 live. The ngcache launcher gets the winning value only after the sweep.

Wired into `swift_1.5_llama_start-q6_q8_q4-ngcache.sh` the same day at user request: `--spec-ngram-cache-p-min "${NGRAM_CACHE_P_MIN:-0.75}"` on the spec line (header documents it; 0 restores old behavior). 0.75 is provisional - equal to the strictest built-in n=1 bar, above the 66% n=2..4 bars - final value still gated on the GPU sweep. The 8009 production launcher does not need the flag (no ngram-cache in that chain). bash -n + git diff --check clean.

### Article cross-check (2026-09-29)

Re-read jadidbourbaki.github.io/blog/prompt-lookup-llama-cpp/ and pulled the five fork PR titles. Coverage verdict: 0 of 5 article optimizations are in our tree.

| PR | change | article claim | our tree |
|---|---|---|---|
| #2 | read inner maps by reference, no copy | 4.5-25.6x drafting | NOT ported: `common/ngram-cache.cpp:71,111` still copy `common_ngram_cache_part` per lookup |
| #5 | outer map -> ankerl::unordered_dense segmented_map | 1.4-1.7x load, less mem | NOT ported: outer still `std::unordered_map` (`common/ngram-cache.h:61`) |
| #10 | inner map -> sorted vector, branchless search | 2.1x draft (no static), 2x mem | NOT ported: inner still unordered_map |
| #7 | static cache -> Lemire constmap | 6-16x load, mem ~= file | NOT ported: static cache is the same nested-map type, and is COPIED per sequence (`speculative.cpp:2274`) |
| #12 | skip parts that cannot pass thresholds | up to 4.2x draft | NOT ported: `try_draft` still does the static-weight lookup for every candidate inside the scoring loop before thresholds |

What we built instead is the axis the article does not touch: server integration of the drafter, shared DYNAMIC cache across sequences, -lcd persistence + missing-file startup, strict gate, p_min admission, shutdown/save visibility, frozen-snapshot GPU validation, launcher. The two axes are complementary.

Relevance at our scale: ngram-cache draft overhead measured ~1.8 ms per 512-token lane (~14 us/round, 0.01% of request wall time) - the 42x/140x CPU drafting wins are invisible against GPU TG. PR #2 is the only free, dependency-free fix worth taking proactively; #5 needs vendoring ankerl::unordered_dense, #7 needs constmap, #10/#12 are self-contained but only pay off for static-cache/CPU-bound replay workloads (the `examples/lookup` tool family incl. lookup-create/merge/stats is present in-tree if that lane is ever run).

### Five-PR port started (2026-09-29)

At user request, the scope changed from article evaluation to porting all five changes while preserving this fork's server integration and admission policy. Exact patches are archived as `/tmp/opencode/jb-pr-{2,5,7,10,12}.patch`. The vendored-source and sync-script portions of PR #5 and #7 are applied: unordered_dense v5.0.1 and fastconstmap commit `990afd04148949300dc00b2206b63af9374c6334`. No common-code portion was applied at this checkpoint.

The pre-port lookup binaries were copied from `build-promptlookup-baseline/bin` to `/tmp/opencode/promptlookup-pr-baseline/` for CPU A/B checks. Integration order is #2 no-copy, #5 outer segmented map, #10 sorted-vector inner part, #7 immutable constmap static cache, then #12 threshold precheck merged with the existing `strict_context` and `p_min_dynamic` policy. Production PID 1936183 was no longer present when work resumed; validation remains CPU-only until the port is stable and GPU availability is explicitly reassessed.

### Five-PR port complete and validated (2026-09-29)

All five PRs are merged into the working tree (no commits; cherry-pick would have clobbered the custom integration). Order applied: #2 read-parts-by-reference (clean `git apply`), #5 `segmented_map` outer + #10 sorted-vector `common_ngram_cache_part` (single hand-merged header edit), #12 threshold precheck (hand-merged with the `p_min_dynamic` floor: the precheck scans counts once, skips the part, then the scoring loop runs only on parts that can pass), #7 constmap static cache (header/static-save/load hand-merged; `speculative.cpp` and the three lookup examples taken from the patch).

Preserved fork behavior (verified by diff review + regression):
- `common_ngram_cache_draft` keeps `strict_context` and `p_min_dynamic`; dynamic admission is still `max(strict[i], p_min*100)`.
- Server ngram-cache impl keeps shared dynamic cache (outside `seq_info`), missing-file startup warning, destructor save with ngram count + duration, `n_min` gate, shrink-rebuild, and configured depth `max(1, draft.n_max)`.
- Static cache is now one `shared_ptr<const common_ngram_cache_static>` shared by all sequences (was a per-sequence copy).
- Dynamic cache file layout is unchanged (ngram, ntokens, token/count pairs); only the within-part order changed (sorted), which `load()` does not depend on. Old `.bin` files stay loadable; the ngcache launcher only uses `-lcd`, so nothing live references the changed static format.

Build: `cmake --build build-promptlookup-baseline -t llama-server llama-lookup llama-lookup-create llama-lookup-stats llama-lookup-merge` clean, zero warnings. `git diff --check` clean.

Regression (CPU-only, GPUs hidden with `HIP_VISIBLE_DEVICES=""` + `VK_ICD_FILENAMES=/nonexistent`, tiny model `/home/srcds/ai/ai/Qwen3.5-0.8B-Q4_0.gguf`, `-ngl 0`):
- `bench/test-ngram-cache-server-lifecycle.cpp` (recompiled against the new libs): all 13 checks pass, exit 0 - exact draft sequences, isolation, dynamic learn/draft across slots, depth n_max/n_min, strict single-observation rejection. Dynamic save round-trips (28 ngrams written/read across separate processes).
- Static constmap: new `llama-lookup-create` on a 30x-repeated 2430-byte corpus wrote a 1000-byte file, magic `ggngcmap` verified (21 entries). `llama-lookup` with the static cache: n_predict=67, 51 drafted, 48 accepted (94.1%). No static cache: n_predict=67, 75.4% accept. Drafting used and effective; same token count.
- `llama-server --help` lists `--spec-ngram-cache-strict` and `--spec-ngram-cache-p-min`.

Important finding - `examples/lookup` is not an output-equivalence oracle on this machine:
- Identical `llama-lookup -ngl 0 -n 64` runs (with and without `-t 1`) produce different outputs run-to-run; the prompt echo is byte-identical, only the generated tail flips.
- Proven model-side, not port-side: `llama-cli -ngl 0 -t 1 -st` (pure model, NO speculative, no ngram code) is also non-deterministic run-to-run (1784 vs 1796 bytes). The port touches only integer ngram structures; FP/model/sampling code is untouched. Most likely load-induced: the live production server perturbs CPU scheduling of multi-threaded FP reductions (no `OMP_NUM_THREADS` pin), flipping greedy argmax on near-ties. Reproduce cleanly only with the CPU quiescent.
- Consequence: the production-path output gate remains the model-free lifecycle suite (deterministic, exact tokens), which passes. A true old-vs-new A/B via the saved pre-port binaries is impossible: they dynamically link `libllama-common.so`, whose ABI changed with the port (undefined-symbol error on load). The static cache is a new on-disk format by design (no legacy compat); static caches must be regenerated with the new `llama-lookup-create`.

Deferred: GPU admission sweep (no-file vs frozen snapshot at p_min 0.5/0.75/0.9) - requires the production server to release the GPUs; launcher `swift_1.5_llama_start-q6_q8_q4-ngcache.sh` still carries the provisional `NGRAM_CACHE_P_MIN=0.75`. No commits made; worktree left dirty as found.

### Five-PR launcher promoted and runtime-validated (2026-09-29)

`swift_1.5_llama_start-q6_q8_q4-ngcache.sh` now defaults `BIN` and `LD_LIB` to `build-promptlookup-baseline/bin`. This is the newest local build (server timestamp 02:45:48), contains strict/p_min and message dedup plus the complete five-PR port, and supersedes `build-dedup` (01:26:21) for this experimental launcher. The production launcher was not changed. The stale header claim that the default port was 8010 was corrected to the actual default, 8009. `bash -n` and shell LSP diagnostics pass.

Full mixed-GPU runtime validation after the prior server stopped:
- Before launch, port 8009 was free, no `llama-server` process existed, both ROCm devices were idle, and the RTX 3080 used 88 MiB.
- The exact launcher became healthy in 40 seconds. `/proc/2973182/exe` resolved to `build-promptlookup-baseline/bin/llama-server`; `/health` returned `{"status":"ok"}` and `/v1/models` reported the intended `Swift-Qwen3.8-27B-Q6_K.gguf` model with a fitted 199168-token slot context.
- A real non-streaming `/v1/chat/completions` request returned the exact requested text, `launcher validation passed successfully`, with 176 prompt tokens and 55 completion tokens. Timing was 38.65 prompt tok/s and 24.50 generation tok/s. Speculative decoding generated 48 draft tokens and accepted 39 (81.25%).
- SIGTERM completed a graceful shutdown in 2 seconds. The ngram-cache destructor saved 192973 dynamic ngrams in 24 ms. `log/ngram-cache.bin` grew from 6007268 to 6011924 bytes, proving the new implementation loaded, learned, and persisted through the launcher's real path. Port 8009 was free afterward.

Runtime evidence: `/tmp/opencode/ngcache-launch-validation.log` and `/tmp/opencode/ngcache-launch-response.json`. The memory-fit probe emits the known `dflash requires ctx_other` and fixed-`-ngl` warnings before the real context initializes; model load and inference complete normally.

### Default per-round attribution and positive replay lane (2026-09-29)

`common_speculative_accept()` now emits one INFO line for every speculative TG verification round: sequence ID, selected drafting method, and accepted/proposed token count. It is visible at default verbosity, for example `round: seq = 0, method = ngram-cache, accepted = 3/3`. `build-promptlookup-baseline` rebuilt cleanly and the 13-check ngram-cache lifecycle suite still passes. Clangd remains misconfigured for this tree (`llama.h` unresolved), but the actual CMake compile and link are clean.

A positive end-to-end scenario was constructed after three rejected probes. JSONL replay failed the cross-arm SHA gate; consecutive integers were already drafted perfectly by `ngram-mod`; prime numbers and one-pass Gettysburg replay had only one observation and correctly failed strict dynamic admission (the 4-token cache requires two samples). The final lane trains the deterministic Gettysburg continuation twice, freezes that cache, then compares temperature-0 `ngram-mod,draft-dflash` against `ngram-mod,ngram-cache,draft-dflash` from a fresh snapshot copy per trial.

After discarded warmups, three interleaved retained runs produced:
- Baseline TG: 18.885, 18.238, 18.441 tok/s; mean 18.521.
- Two-pass frozen cache TG: 34.502, 34.296, 33.816 tok/s; mean 34.205.
- Speedup: 1.847x, +84.68%.
- Every output SHA: `79cf1462f1a2` (temperature 0, top-k 1, seed 1, 256 tokens).
- Baseline ownership: 327 DFlash rounds across three runs, 146/327 proposed tokens accepted per request.
- Candidate ownership: 189 ngram-cache rounds (all 3/3 accepted) plus three final DFlash rounds (2/2); 191/191 proposed accepted per request. Verification rounds fell from 109 to 64 per request.

Reusable artifacts: `bench/ngram-cache-replay-client.sh`, `bench/run-ngram-cache-replay-benefit.sh`, and `bench/logs/promptlookup-exact-replay-benefit-20260929-summary.md`. The runner trains twice, freezes the cache, discards warmups, performs three interleaved trials, and refuses the speed claim if retained SHAs differ. Its end-to-end `RUNS=1` smoke initially exposed a mixed-backend GPU hang on immediate relaunch; adding an equal five-second cooldown between lanes fixed it, and the rerun completed with the same SHA and +74.80% in that single retained pair.

### Final article coverage audit (2026-09-29)

Re-read the full article and compared the archived `/tmp/opencode/jb-pr-{2,5,7,10,12}.patch` hunks against the current tree. Implementation coverage is complete, 5/5:

- #2: drafting reads primary parts by `const` reference; the old static inner map was replaced by the #7 immutable view, so no drafting-path part copy remains. Copies in dynamic save/merge are outside #2's drafting scope.
- #5: unordered_dense v5.0.1 is pinned and vendored with its MIT license; `common` links it publicly; the outer cache is `ankerl::unordered_dense::segmented_map`.
- #10: followers are sorted vectors and use the exact fixed-trip `lower_bound` loop from the PR.
- #7: fastconstmap is pinned at `990afd04148949300dc00b2206b63af9374c6334` with Apache-2.0 and bundled xxHash licenses; `common` links it privately; static save/load uses `ggngcmap`, a contiguous pair array, verified constmap, 40-bit offset plus 24-bit length, one aligned backing buffer, `fcm_verified_constmap_view`, and one shared immutable cache across sequences. All three lookup tools use the static API.
- #12: each primary part first computes total count and largest unweighted follower, skips parts that cannot meet sample/share thresholds, then performs static-weighted scoring and the original final winner threshold. The custom strict-context and dynamic `p_min` policies feed their effective thresholds through this same precheck.

Validation is strong but is not a reproduction of the article's performance study. Local evidence covers clean builds, 13/13 deterministic lifecycle checks, static file creation/load/use, real mixed-GPU server startup and persistence, and an SHA-gated exact-replay end-to-end result of +84.68%. It does not cover the article's WikiText-103 0/25/50/100/200/541 MB sweep, 4096-token `llama-lookup-stats` protocol, median-of-three drafting latency, static load time, peak RSS, or direct pre-port versus post-port acceptance equivalence. The saved pre-port executables cannot provide that comparison because they dynamically link the now-changed `libllama-common` ABI.

Verdict: all article and PR implementation bases are covered. The only uncovered bases are article-scale empirical reproduction and a direct old/new acceptance-equivalence lane. The article's 42x/140x numbers must not be attributed to this fork; the local +84.68% result is a separate best-case dynamic exact-replay server result. The experimental launcher also deliberately differs from the article defaults by enabling strict context admission and a dynamic `p_min=0.75` floor.

### Dynamic-cache growth clarification (2026-09-29)

The persistent `-lcd` cache is not a full prompt/response cache. When the speculative chain reaches `ngram-cache`, it records counts for the next token following each 1-, 2-, 3-, and 4-token history in the current prompt and generated history. A later matching history can supply speculative next-token drafts only when sample-size, confidence, `p_min`, and `n_min` gates pass; the target model still verifies every draft. Since `ngram-mod` precedes `ngram-cache` in the experimental launcher and the first successful drafter ends the chain for that round, rounds claimed by `ngram-mod` do not train the persistent ngram cache.

There is currently no dynamic-cache size limit, eviction, aging, count decay, or periodic compaction. Unique histories and follower entries accumulate across cleanly saved sessions, and repeated observations increase `int32_t` counts. Expected long-term costs are increasing RAM, file size, startup load and shutdown save time, reduced cache locality, and stale/cross-domain counts crossing admission thresholds or displacing the stronger DFlash drafter. This is already visible in the warm-cache and frozen-snapshot gates: the warm cache was 4.7% slower than the repaired no-file candidate and changed the short replay output; the frozen snapshot was 1.53% slower than no-file because extra ngram-cache rounds displaced better DFlash rounds. The cache also contains token IDs and transition counts derived from processed text, so its persisted file should be treated as potentially sensitive.
