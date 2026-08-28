# Fork vs mainline A/B - 2026-08-28

Question: does our fork (dflash2 @ 688ff5c4f = upstream 18443257a + our
patches) actually yield perf benefits over stock mainline, on our champion
config and rig (2x Radeon VII + RTX 3080 Laptop, ROCm 6.1 + Vulkan)?

Method: stock = ggml-org master 18443257a checked out in ~/dev/llama.cpp,
built with the identical pinned 6.1 recipe (build-stock). Champion command
(i1-Q6_K + Q8_0 drafter + f16K/q8V + ts 35,20,45 + n_max 4 + ub 384) run
on both binaries. Stock cannot parse --pipeline-parallel (fork flag, made
conditional in the runner). Protocol metrics cross-checked on server-log
timings because stock desyncs the fork's streaming progress client.

## Headline numbers (identical command, c 200192)

| metric | stock 18443257a | fork (ours) | winner |
|---|---:|---:|---|
| PP first-batch 16384 | 347.7-354.3 | 361.8 | fork +2-4% |
| fill 120,003 (single-pass) | 226.6 | 218.9 | stock +3.5% |
| TG@120k, 1024 tok | 11.51 | 9.0 | stock +28% |
| acceptance (acc/predicted) | .655* | .646 | par (*see bug note) |
| max ctx, this config | ~215k listens only via deferred oversubscription; 200k safe | 250k validated, 260k opt-in | fork +25% |
| per-device compute buffers | 1302/1021/1332 MiB | 276/282/276 MiB | fork 4.7x smaller |
| temp-0 reproducibility | corrupt (Vulkan #27805) | passes (our #27812 port) | fork |
| 250k champion config | does not fit at all | ships (PP 363, TG 9.0) | fork |

## Findings

- F1 STOCK CANNOT FIT THE CHAMPION. Stock's compute buffers are ~4.7x ours
  on every device; at 250k VK1 and ROCm1 are oversubscribed before the
  drafter even loads. Stock's practical ceiling for this config is ~200k.
  The fork's compute-buffer frugality (no_alloc/explicit-size machinery)
  is what buys 250-260k of context on this rig.
- F2 STOCK WINS DEEP TG BY 28% (11.5 vs 9.0 t/s) at equal acceptance.
  Ruled out: the Vulkan graph optimizer and our view-alias fix (AB5:
  optimizer disabled = identical 9.0). Prime remaining suspect: the fork's
  aggressive buffer reuse - 276 MiB buffers force reuse dependencies that
  may serialize the speculative verify rounds, where stock's 1.3 GiB
  buffers let ops overlap. Follow-up: measure with artificially enlarged
  fork buffers, or profile one verify round on both binaries.
- F3 STOCK'S NUMBERS CARRY THE VULKAN BUG: mainline 18443257a predates the
  #27812 fix, so its speculative verification on Vulkan1 is corrupted
  (accepts tokens it did not choose). Its .655 acceptance and its outputs
  are not trustworthy at temp 0; our repro gate passes, stock's cannot.
- F4 STOCK DESYNCS THE FORK'S BENCH CLIENT (streaming progress API
  differences) - A/B used server-log timings for all cross-binary claims.

## Verdict

The fork is not a uniform perf win: it trades ~28% deep-TG speed (cause
under investigation, F2) for +25% context headroom (F1), temp-0
correctness (F3), PP parity-plus, and the campaign tooling. For the
nightly 250k sessions the fork is the only option; if a workload fits in
200k and prioritizes deep generation speed, stock mainline is currently
faster - until F2 is understood and closed.

Artifacts: bench/logs/lane-AB1..AB5*, /tmp/opencode/ab3-server.log,
~/dev/llama.cpp (stock checkout + build-stock).
