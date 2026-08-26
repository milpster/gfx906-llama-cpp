# DRAFT GitHub comment for PR #27210 - multi-GPU PP regression from the delta-net conv-state hunk

Status: DRAFT for your review. You post it; edit freely. Written to be
pasted as-is into the PR conversation. All numbers from our measurement
logs (bench/logs/, trials.md in our fork).

---

Hi @stew675 - first, thanks for this PR: on our system the adaptive
controller is a large win (below). One heads-up on the last commit
(a8f2138e, "fix rs snapshot copies") for multi-GPU users.

**Environment:** 2x Radeon VII (gfx906, ROCm 6.1) + 1x RTX 3080 Laptop
(Vulkan) in one process, `--split-mode layer` with a fixed tensor split,
dense-27B-class hybrid (Qwen3.8-27B Q6_K_XL, 65 dense + 1 nextn layer),
`-b 16384 -ub 384`, MTP speculative decoding (`--spec-draft-n-max 10`),
GGML_CUDA_FA_ALL_QUANTS=ON.

**What we measure with commit 5/5 applied** (PR tip, everything else stock):

| config | PP (16384-token batch, first server batch) |
|---|---|
| spec off | 369 t/s |
| ngram-only | 296 t/s |
| MTP n_max=1 | 271 t/s |
| MTP n_max=4..10 | ~202 t/s (flat) |

**Baseline without the PR** on the same tree/config: 325 t/s with MTP n=10.
So the bundle costs us ~38% PP whenever MTP is enabled, scaling with
n_max and saturating around n_max>=4.

**Isolation:** reverting *only* the delta-net-base.cpp `t_min` hunk from
commit 5/5 restores PP to parity (326 t/s) while keeping the full adaptive
feature. Interleaved A/B, repeated, same machine state. The other four
commits are clean for us.

**Observations that may help pin it down:**
- For 384-token prefill ubatches the modified loop is arithmetically
  identical to stock (`t_min` clamps to 1), so prefill graphs are unchanged:
  we dumped node-level scheduler assignments (GGML_SCHED_DEBUG=2) and the
  16384-batch PP graphs are identical in node count, op histogram and
  device placement between PR and no-PR builds.
- The only graphs the hunk changes are the small ones: the 1-token
  probe/warmup graph loses ~30 conv-state CPY nodes (first GDN node moves
  from #74 to #44), and fused-op resolution on the target context takes
  ~20x longer at load (0.19s vs 0.01s), though the probe verdicts are
  identical (fused GDN AR/CH enabled in both).
- Under HIP_LAUNCH_BLOCKING=1 the wall-clock gap largely disappears while
  per-op GPU time stays close, which points at lost cross-device overlap
  during prefill rather than slower kernels.

We did not chase the mechanism further than this - reverting the hunk is
free for us - but since the commit message estimates ~2.6% overhead savings
on single-GPU verify, it may be worth a look for anyone running layer-split
multi-GPU with MTP: the swing is 326 -> 202 t/s on our box.

For completeness, the adaptive controller itself on our config:
TG 1024 greedy 10.2 -> 19.3 t/s (+89%) at PP parity once the hunk is
reverted; acceptance 0.69 -> 0.63 as the controller trims wasted depth.
Great work - happy to share full logs if useful.

---

## Our internal references (do not paste)

- Interleaved A/B logs: bench/logs/ab-*.log, gab-*.log, eab-*.log (PR-tax
  investigation) and logs/pfab-*.log (prefetch experiment, unrelated)
- Full-protocol verification: logs/dn-full.log (PP 326.4 / TG 19.3)
- Probe/node-dump evidence: logs/nodes-pr.log vs logs/nodes-nopr.log
- Root-cause saga incl. ruled-out list: PR27210-ADAPTIVE-MTP-2026-08-25.md
