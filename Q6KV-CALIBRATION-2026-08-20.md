# Qwen3.8-27B-UD-Q6_K_XL dual-config calibration - 2026-08-20

Hardware: 2x Radeon VII 16 GiB (ROCm0/ROCm1) + RTX 3080 Laptop 8 GiB (Vulkan1).
Binary: `build-vega20-sync` (fork, incl. mixed F16-K/q8_0-V FA tile kernel).
Full raw trial log: `.opencode/skills/dual-gpu-context-balancing/scripts/trials.md`.

## Shipped launchers

| Script | Target/draft KV | Ctx | First-batch PP | TG fresh / at depth | Deep validation |
|---|---|---:|---:|---:|---|
| `llama-start-q6v-f16.sh` | F16 / F16 | 165k | 311.9 | 18.83 / 18.35 @110k | 110k fill 215.6 avg, vision OK |
| `llama-start-q6v-mix.sh` | K=f16 V=q8_0 / F16 | 210k | 310.7 | 18.43 / 18.42 @180k | 180k fill 151.4 avg, vision OK |

Same PP class; +45k ctx for V-precision only. TG difference is noise (<2%).

## Core insights

1. **Q6 pp is split-bound, not ctx-bound (185-210k range).** PP tracks VK1
   layer count: 26/14/26 = 311.9, 27/13/26 = 309.3, 28/13/25 ~ 301.5,
   28/12/26 = 302.7-294. At fixed split, 185k vs 190k vs 210k measure flat
   (301.2 / 301.5 / 310.7 at their respective splits). Unlike Q8_0, where
   per-layer time is device-equal (serial-sum proof) and split is cosmetic.
2. **The 3080 is the fast per-layer device for Q6.** Every layer moved
   VK1 -> Vega costs ~4.5 tok/s first-batch pp. Max-VK1 splits win pp;
   ctx demands the opposite (VK1 KV + compute grow with ctx). Resolution:
   quantize V only -> frees exactly the VRAM that restores 14 VK1 layers
   at high ctx. Split gain (+10) beats mixed-kernel tax (-6).
3. **`-ot` cross-device override tax: 13-15% both metrics** (260.3 pp /
   15.26 tg vs 296.5/18.78 native-equal placement at 200k). Out-of-sequence
   placement (R1,VK1,R1 zigzag via -ot blk.63) is catastrophic: 172.3 pp.
   Keep placement contiguous, use -ts, reserve -ot for tiny bookkeeping
   groups only (nextn ~53 MiB: fine, and required).
4. **token_embd offload to ROCm0: catastrophic (pp 203.6).** Do not retry.
5. **Pipeline parallel: no single-request pp gain (4 independent
   confirmations at 180k/210k, F16 and V-q8); costs ~715 MiB compute.**
   tg swings under pp-on were acceptance variance (acc@pos0 0.66-0.78
   request-to-request, +-0.8 tok/s), not pipeline.
6. **cost == layer at equal placement (5 confirmations).** Placement
   identical -> results identical; sm mode is cosmetic on this rig.
7. **VK1 memory cliff (~2.6 GiB KV / <100 MiB free): NVIDIA Vulkan driver
   silently backs VRAM with sysmem** -> pp collapses (~297 -> 248 in old
   build). Deterministic. 210k leaves 219 MiB (3x margin); 220k only 93.
   230k is structurally dead: VK1 4691 model + 2753 KV + 280 compute > 8192.
8. **`--device-draft`/`-devd` is a no-op for nextn-embedded MTP drafts.**
   Draft KV (860 MiB at 210k) stays on ROCm1; it only steers separate
   draft models.
9. **Layer boundaries are sticky/discrete.** -ts 42,19,39 / 42,20,38 /
   42,18,40 can all produce identical 28/12/26 placement. Compute
   ceil(66 * cumulative) thresholds; verify per-device model-buffer MiB
   in the log, never trust the -ts numbers alone.
10. **Validation protocol (mandatory for ctx claims):** first-batch bench
    (first run after startup - cache-reuse poisons reruns: a 388-tok
    "pp" was one such contaminated measure), then single deep fill at
    >=80% ctx depth, tg 1024 at depth, vision at depth, per-device VRAM
    floor check. Margins >=~200 MiB/device after fill = safe.
11. **Deep-fill rates decay with depth** (KV scan grows): 215.6 avg @110k
    fill (165k cfg) vs 151.4 avg @180k fill (210k cfg). First-batch PP
    is the throughput-sane comparison; deep avg is a stability metric.
12. **Rejected/perf-equal levers:** ub 352 (294.2) and 416; ub 384 optimal
    from both directions. n-max deeper drafts: only q8 data exists (2
    optimal), Q6 F16 sweep still pending (aborted, never run). MMQ force
    neutral. VK f16 env flags no-op.

## Known limits & follow-ups

- 220k V-q8: startup-only (VK1 93 MiB, cliff zone). 230k: dead.
- 170k F16 (27/13/26, pp 309.3): bench-only, never deep-validated - the
  one unexplored point of the pure-F16 ladder.
- `--spec-draft-n-max 3/4` sweep on Q6: not yet run.
- Vision probe = synthetic 64x64 PNG (few vision tokens). Real photo at
  ~180k depth untested; low risk (startup covers worst-case mmproj).
- `--cache-reuse` silently disabled with mmproj (server logs it; flag
  kept only for stack parity with q8v launcher).
