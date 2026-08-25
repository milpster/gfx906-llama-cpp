# Upstream sync 2026-08-25 - branch sync/upstream-2026-08-25

Base: master @ 293a48049 (pre-eaman line + docs). Upstream: origin/master
@ f1357e499 (563 commits integrated). Merge commit: b6ecf695e (amended).

## Conflict resolutions (8 files, all fork-vs-upstream collisions)

- common/common.cpp: kept both (fork cost_attn_weight + upstream load_mode)
- src/llama-model.cpp: kept both struct fields, order per llama.h
  (load_mode before cost_attn_weight - wrong order = type error)
- src/llama.cpp: kept both function sets (fork pipeline_parallel_type_name,
  upstream load_mode_name/from_str)
- src/llama-context.cpp: upstream wide log format + fork pipeline-mode line
- ggml fattn.cu: fork q8_0-tile alloc branch kept, WMMA case dropped
  (upstream removed the WMMA kernel)
- ggml mmq.cuh: vega20 config dispatch re-inserted into upstream's new
  RDNA4/3.5/3 chain (host + constexpr device variants; fork's
  AMD_WMMA_AVAILABLE gate was upstream's old name for RDNA4)
- tools/server/server-context.cpp: upstream joint draft-fit
  (common_fit_extra_model) supersedes fork's old-gen MTP reservation block
- tools/llama-bench.cpp: upstream help-format realign

## Build

build-sync25 (gfx906, ROCm 6.1 pinned, GGML_CUDA_FA_ALL_QUANTS=ON):
build 10644, commit b6ecf695e, 0 errors after 3 fixup rounds (all fixups
were my merge-resolution brace/order slips, not code problems).

## Verification (prod config via llama-start-q6v.sh, BIN override)

| metric | sync25 build | pre-eaman baseline | verdict |
|---|---|---|---|
| PP first-batch 16384 | 325.9 | 325.0-325.4 | parity |
| TG 1024 fresh KV | 10.2 | 10.2 | parity |
| acc | 0.686 | 0.686 | parity |
| greedy sha fresh | 5361409ccee1 | 5361409ccee1 | identical |
| abort-mid-PP recovery | 5.6 s | 0.7-5 s | healthy, no wedge |
| PP@120k deep fill | 326.4 | 325.4 | parity |
| TG@120k deep fill | 9.5 (acc 0.766) | 10.1-10.3 (acc 0.774) | -6%, see note |
| deep sha | ee9cf1388958 | d5267dcc9d17 | different LENGTH (1014 vs 810 tok stop) |

Note: deep-fill completion now stops later (1014 vs 810 tokens) with slightly
lower acceptance - consistent with upstream spec/ngram default changes
altering draft dynamics, not with corruption: fresh-KV greedy output is
bit-identical and post-abort sanity completions match the pre-eaman binary
exactly. Watch TG@depth in production.

Deprecation: --no-mmap warns; switch launcher to --load-mode mmap when
convenient (behavior unchanged).

## Next: PR 27210 adaptive MTP

patches-pr/27210-adaptive-mtp.patch fetched (18 diffs, files: common/arg,
common.cpp/h, speculative.cpp + new speculative-adaptive.h,
server-context.cpp, tests). Integration on top of this branch next.
