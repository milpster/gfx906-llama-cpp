# Trial results — Qwen3.6-27B-Fable-Fus-...-MTP Q8_0

Hardware: 2x Radeon VII (16 GiB ROCm) + RTX 3080 Laptop (8 GiB Vulkan).
Software: `build-vega20/bin/llama-server`, `-sm cost`, `--pipeline-parallel on`,
MTP `draft-mtp --spec-draft-n-max 3`. No KV quantization (F16 throughout).

## Final winner

```
-ts 42,19,39 -sm cost -ot '^blk\.64\.nextn\..*=ROCm0' -c 144000
```

Validated end-to-end: server reaches listening state, `/v1/chat/completions`
returns at ~19 tg/s with MTP speculative enabled, `/slots` reports
`n_ctx: 144128`.

Net gain: **+14,000 tokens of context (+10.8%)** over the user's baseline
`-c 130000`, with positive free headroom on all three devices (was -62 MiB
oversubscribed on Vulkan1 in baseline).

## Trial table

All trials use `-sm cost`, `-c` per the column, `--pipeline-parallel on`,
identical non-placement args.

| Trial          | -ts       | -ot                            | -c      | ROCm0 free | Vulkan1 free | ROCm1 free | Status                  |
|----------------|-----------|--------------------------------|--------:|-----------:|-------------:|-----------:|-------------------------|
| baseline       | 43,22,35  | -                              | 130000  | 403        | **-62**      | 1298       | oversubscribed, runs    |
| trial_b1       | 42,21,37  | -                              | 130000  | 818        | -62          | 885        | dev1 unchanged (no-op)  |
| trial_b2       | 43,20,37  | -                              | 130000  | 403        | 347          | 885        | dev1 cleared, dev0 lim  |
| trial_b3       | 42,19,39  | -                              | 130000  | 818        | 347          | 472        | balanced whole-layer    |
| verify_b3_138k | 42,19,39  | -                              | 138000  | 570        | 227          | 256        | MTP alloc fail          |
| verify_b3_137k | 42,19,39  | -                              | 137000  | 601        | 242          | 283        | MTP alloc fail          |
| verify_b3_135k | 42,19,39  | -                              | 135000  | 663        | 272          | 337        | MTP alloc fail          |
| trial_c1       | 42,19,39  | `blk.64.nextn.*=ROCm0`         | 130000  | **1080**   | **715**      | **871**    | compute bufs ~ -1 GiB   |
| verify_c1_142k | 42,19,39  | `blk.64.nextn.*=ROCm0`         | 142000  | ~700       | ~545         | ~515       | listening               |
| **verify_c1_144k** | **42,19,39** | **`blk.64.nextn.*=ROCm0`** | **144000** | **685** | **540**      | **530**    | **listening + inferred**|
| verify_c1_145k | 42,19,39  | `blk.64.nextn.*=ROCm0`         | 145000  | 656        | 527          | 505        | MTP alloc fail          |

## Second lever: blk.63 boundary-layer move (2026-08-13)

The c1 winner reaches listening at 144k but the fitter reports a 2035 MiB
deficit — the trials above only validated startup, not runtime fill. In
practice 144k fill-OOMs because the MTP draft KV (~547-768 MiB depending
on -c) lands on ROCm1 AFTER the fitter ran, consuming headroom the fitter
did not account for. Actual ROCm1 free at 144k was negative (530 fitter
free minus ~750 draft).

New override: move blk.63 (last regular layer, 377 MiB) from ROCm1 to
ROCm0 via a second -ot. This relieves the device that carries the draft
KV burden. Model buffers shift exactly 377 MiB (ROCm0 10852->11230,
ROCm1 11670->11293).

| Trial              | -ot (both applied)                    | -c     | ROCm0 free | Vulkan1 | ROCm1 free | Deficit | Fill test         | tg/s  |
|--------------------|---------------------------------------|--------|-----------:|--------:|-----------:|--------:|-------------------|------:|
| baseline_140k      | blk.64.nextn only                     | 140000 | 800        | 620     | 629        | 1751    | user-validated    | 19.29 |
| blk63_140k         | + blk.63.*=ROCm0                      | 140000 | 423        | 620     | 1006       | 1024    | not tested        | -     |
| blk63_144k         | + blk.63.*=ROCm0                      | 144000 | 308        | 566     | 907        | 1289    | 65k tok (45%) OK  | 21.37 |
| blk63_148k         | + blk.63.*=ROCm0                      | 148000 | 193        | 515     | 808        | 1554    | 22k tok (15%) OK  | 22.50 |

The blk.63 move also improved generation speed (19.29 -> 21.37-22.50 tg/s),
likely from better weight locality reducing cross-device transfers.

Recommended production config: `-c 144000` with both overrides (deep-fill
validated). `-c 148000` is viable for moderate use but ROCm0 headroom
(193 MiB) is thin for very deep fills.

## Third lever: --spec-draft-n-max 2 (2026-08-13)

`--spec-draft-n-max 2` (instead of 3) reduces MTP compute burden. The
draft KV does NOT shrink (still ~579-800 MiB depending on -c, allocated
for full context regardless of n-max), but overall MTP compute and
scheduling overhead drops, freeing ~100-130 MiB per device.

Acceptance rate improves (87% vs 74%) because shorter drafts are easier
to verify. Effective speed is nearly identical (~22 vs ~21 tg/s).

| Trial              | n-max | -c     | ROCm0 free | Vulkan1 | ROCm1 free | Fill test          | tg/s  | accept |
|--------------------|------:|-------:|-----------:|--------:|-----------:|--------------------|------:|-------:|
| blk63_148k         | 3     | 148000 | 193        | 515     | 808        | 58k tok (39%) OK   | 22.50 | 74%    |
| nmax2_148k         | 2     | 148000 | 322        | 577     | 913        | not tested         | 22.25 | 87%    |
| nmax2_155k         | 2     | 155000 | 128        | 491     | 746        | 44k tok (29%) OK   | 20.94 | 80%    |

nmax2_148k is the headroom winner (+129 MiB ROCm0 vs nmax3). nmax2_155k
is the max-context option (+15k over baseline 140k) but ROCm0 at 128 MiB
is thin for very deep fills.

## q8_0 KV + mmproj vision + n-max 3 (2026-08-16)

Config change: `-ctk q8_0 -ctv q8_0 -ctkd q8_0 -ctvd q8_0`,
`--spec-draft-n-max 3`, `--mmproj mmproj-F16.gguf` (CLIP on ROCm0 via -mg 0).
Trial harness: `run_q8.sh`. q8 KV shrinks target KV 9008 -> ~4786 MiB @144k
and MTP KV 563 -> ~299 MiB.

Layer map at `-ts 42,19,39 -sm cost` (probed): ROCm0 blk.0-25 (~26 layers),
Vulkan1 blk.26-37 (12), ROCm1 blk.38-63 + nextn (28). Cost split is NOT
proportional to -ts ratios. All F16-era `-ot` overrides are no-ops here:
`blk.63.*` / `blk.6x.*` are natively on ROCm1, `blk.64.nextn.*` does not
move MTP bookkeeping in this config (MTP KV stays on ROCm1).

New binding constraints:

1. **CLIP encode is size-fixed (~1162 MiB worst-case on ROCm0)**. A tiny
   64x64 image already OOM'd at 946 MiB free (CUBLAS_STATUS_ALLOC_FAILED
   in clip_image_batch_encode, server exits). Vision-safe rule:
   ROCm0 free >= ~1260 MiB.
2. **ROCm1 MTP cliff persists**: adding model weight to ROCm1
   (blk.25->ROCm1 trial) kills `failed to create MTP context` even when
   the fitter shows positive free.

| Trial            | -ot                    | -c     | ROCm0 free | Vulkan1 | ROCm1 free | Status                |
|------------------|------------------------|-------:|-----------:|--------:|-----------:|-----------------------|
| q8v_base         | nextn+blk63->ROCm0     | 144000 | 1711       | 874     | 1963       | listening             |
| q8v_no63_155k    | nextn->ROCm0 (no-op)   | 155000 | 1993       | 770     | 1567       | listening             |
| q8v_b63r1_190k   | blk63->ROCm1 (no-op)   | 190000 | 1380       | 453     | 1027       | listening             |
| q8v_b63r1_205k   | blk6[23]->ROCm1 (no-op)| 205000 | 1121       | 317     | 799        | listening             |
| q8v_b25_220k     | blk.25->ROCm1          | 220000 | 913        | 292     | 16         | FAIL: MTP ctx         |
| q8v_b25_205k     | blk.25->ROCm1          | 205000 | 1177       | 431     | 249        | FAIL: MTP compute pp  |
| q8v_plain_215k   | none                   | 215000 | 1000       | 225     | 592        | listening             |
| q8v_plain_218k   | none                   | 218000 | 946        | 197     | 545        | listening; vision CRASH |
| q8v_ffn_205k     | blk.25.ffn_(gate/up)->Vulkan1 | 205000 | 1253 | 106 | 746 | listening, VK1 too thin |
| **q8v_plain_197k** | **none**             | **197000** | **1313** | **389** | **868**   | **listening + vision OK** |

**Winner (vision): `-ts 42,19,39 -sm cost -c 197000`, no -ot.**
**Winner (text-only): same, `-c 218000`** (220000 fails MTP ctx on ROCm1).

Net: 144k F16 -> 197k q8+vision (+37%) or 218k text-only (+51%).

Validation @197k (2026-08-16, build 604fca587):

- startup: listening; frees 1313/389/868 (ROCm0 >= CLIP 1162 + margin)
- tg 1024 out: 16.1-16.8 tok/s, MTP accept 71/46/32 %/pos, mean len 2.49
  (F16-KV was 22.5 tg/s at 84/73/64 - q8 KV costs ~28% tg speed, the price
  of +53k context)
- pp 7521 tok @ ub 384: 179-238 tok/s cold (two instances, thermal spread)
- vision: 64x64 PNG via /v1/chat/completions encodes and describes correctly

Start scripts: `/home/srcds/dev/llama-start-q8v.sh` (vision, 197k),
`/home/srcds/dev/llama-start-q8-text.sh` (218k), bench: `llama-bench-q8v.sh`.

## Speed tuning: F16 draft KV + n-max 2 (2026-08-16)

Recovering tg after the q8-KV acceptance drop. Harness: `run_tune.sh`
(env: KV_DRAFT / NMAX / UB / NGRAM; target KV stays q8_0, mmproj on).

| Trial          | draft KV | n-max | ub  | -c    | tg/s @1024 | accept %/pos | Result |
|----------------|----------|------:|----:|------:|-----------:|--------------|--------|
| q8v_plain_197k | q8_0     | 3     | 384 | 197000| 16.1-16.8 | 71/46/32     | baseline |
| tuneA_f16draft | f16      | 3     | 384 | 197000| 18.43     | 79/53/32     | +2.3 tg, +225 MiB ROCm1 |
| tuneB_nmax2    | f16      | 2     | 384 | 197000| 18.67     | 76/54        | keep |
| tuneC_ub512    | f16      | 2     | 512 | 197000| -         | -            | FAIL: MTP ctx (compute +356/dev) |
| tuneC_ub448    | f16      | 2     | 448 | 197000| 17.20*    | 66/40*       | runtime OOM on 7.5k pp |
| tuneD_ngram    | f16      | 2     | 384 | 197000| 18.30     | 74/51        | ngram-mod 0 acc (fresh-gen workload) |
| tuneE_text_218k| f16      | 2     | 384 | 218000| -         | -            | FAIL: MTP ctx (ROCm1 650 free) |
| tuneE_text_210k| f16      | 2     | 384 | 210000| -         | -            | FAIL: MTP ctx (ROCm1 772 free) |
| tuneE_text_202k| f16      | 2     | 384 | 202000| 17.69     | 69/44        | text-only alt: -16k ctx for +1.6 tg |

*ub448 numbers unreliable (crashed during bench).

**Production vision config updated: q8 target KV + F16 draft KV + n-max 2
@ -c 197000 -> 18.3-19.0 tg/s (+15%), acceptance 76-79%/54.**
Final validation from `llama-start-q8v.sh` itself: tg 19.04, vision OK,
pp 181.7 (cold) / ~238 (warm band).

Why: the MTP draft's own KV at q8_0 degraded draft logits (acceptance
71/46/32); F16 draft KV costs only ~225 MiB on ROCm1 and restores most of
it. Draft KV is tiny (~450 MiB @197k) vs target (~6.4 GiB), so the ctx
ceiling is unchanged. Text-only 218k cannot afford F16 draft KV (MTP
cliff); its alternatives are 218k/q8-draft (16.1 tg) or 202k/f16-draft
(17.7 tg) - kept 218k in llama-start-q8-text.sh.

## pp tuning: Vulkan F16 + ub ladder (2026-08-16)

User accepted ctx loss for pp. Two levers tested:

1. **Remove GGML_VK_DISABLE_F16=1** (free, no sacrifice). The env was a
   RADV workaround but it also disabled FP16 shaders on Vulkan1 = the
   NVIDIA 3080, the only Vulkan device used. VK fp16 speeds its pipeline
   stage: pp 179-238 -> **282-285 tok/s** (+19-58%), tg unchanged within
   the 16.8-19.0 thermal noise band. Adopted everywhere.
2. **ub ladder paid with ctx**: ub 512 @180k (frees 1521/386/1006):
   pp 272 - no gain over ub 384 @197k (282). pp is pipeline-stage-bound,
   not ubatch-bound. ub 384 retained; no ctx sacrificed.

| Trial          | vk f16 | ub  | -c    | pp tok/s | Verdict        |
|----------------|--------|----:|------:|---------:|----------------|
| q8v_plain_197k | off    | 384 | 197000| 179-238  | old baseline   |
| tuneF_vkfp16   | on     | 384 | 197000| 282.06   | adopt          |
| tuneH_final_197k | on   | 384 | 197000| 284.76   | confirmed (distinct prompt) |
| tuneG_ub512_180k | on   | 512 | 180000| 272.37   | reject: -17k ctx, no pp gain |

**Final production (vision): -c 197000, q8 target KV, F16 draft KV, n-max 2,
ub 384, vk f16 on: tg 16.8-19.0/s, pp 282-285/s, vision OK.**
Both start scripts updated (GGML_VK_DISABLE_F16 removed).

## q8_0-native FA tile kernel (2026-08-16, code change)

Problem: on HIP, quantized-KV FA always dispatched to the VEC kernel
(fattn.cu HIP guard), which re-reads the whole KV cache per query row -
no GQA amortization. Deep-fill pp degraded linearly: 297 tok/s @5k fill
down to ~106 @100k.

Fix (this fork, ggml/src/ggml-cuda/):
- fattn-tile.cuh: q8_0 tile loaders (half2 + float variants) that
  dequantize block-aligned 32-elem groups during tile load; `kv_q8_0`
  template param through kernel/iter/iter_KQ; HIP launcher branch
  (DKQ<=128 -> 64 cols, DKQ<=256 -> 32 cols per AMD config table)
  selects the q8 kernel when K,V are both Q8_0 and block-aligned
  (nbatch_K % 32 == 0, DKQ % nbatch_K == 0).
- fattn.cu: `ggml_cuda_fattn_tile_q8_0_native()` routes GCN q8 batches
  to TILE instead of VEC, and `get_alloc_size` skips the F16 shadow
  reservation for this path (without this the +~800 MB/op reservation
  OOMs the fit - found the hard way at -c 197000).

Head dim of this model is 256 (not 128): Q=[256,384] observed.
Config used: AMD (256,256,32): nthreads 256, nbatch_fa 32, nbatch_K 128.

Measured (single slot, -ts 39,21,40 -sm layer -c 130000, fill to 103k):

| cache depth | VEC (old) | q8 TILE (new) | speedup |
|------------:|----------:|--------------:|--------:|
| 5k          | 297-301   | 328           | +10%    |
| 16k         | 275       | 348           | +27%    |
| 32k         | 209       | 314           | +50%    |
| 48k         | 167       | 286           | +71%    |
| 64k         | 140       | 262           | +87%    |
| 82k         | 121       | 242           | 2.0x    |
| 103k        | ~106      | 216-218       | 2.05x   |

Full 103k fill: 920 s -> 479 s. tg unchanged (VEC path, Q rows <= 2).
Vision unchanged. Production 197k config validated end-to-end after the
alloc-size fix (startup, vision, tg 17.1, pp 334 @4.8k fresh).

Correctness notes: dequant math matches the shadow path bit-for-bit
(same make_half2(d*q) conversion); oob zero-fill preserved; mask and
softcap paths untouched. tg uses VEC (n rows <= 2) -> no change there.

## pp push: 296 ceiling (2026-08-16, layer mode + pp off)

Target: user wanted 320+. Result: **295.84 is the config ceiling**; 320
needs per-layer kernel speed, not placement.

Structure discovered: with --pipeline-parallel off (or on - no overlap for
single-request pp), pp time = SERIAL SUM of all 66 layer-times. Moving a
layer between devices with equal per-layer cost changes nothing
(27/13/26 -> 26/14/26: 295.89 -> 295.84). Per-layer time is ~equal on
Vega20-ROCm and 3080-Vulkan-fp16.

| Trial            | mode    | split      | ub  | KV  | pp tok/s | Verdict            |
|------------------|---------|------------|----:|-----|---------:|--------------------|
| tuneK_ppoff      | cost    | 42,19,39   | 384 | q8  | 288.45   | pp off > on        |
| tuneI_mmq        | cost    | 42,19,39   | 384 | q8  | 285.99   | MMQ force neutral  |
| tuneJ_smlayer    | layer   | 42,19,39   | 384 | q8  | 284.92   | = cost mode        |
| tuneM_bal13      | layer   | 40,20,40   | 384 | q8  | 295.89   | 27/13/26           |
| tuneO_26_14_26   | layer   | 39,21,40   | 384 | q8  | 295.84   | 26/14/26 = proof of serial-sum |
| tuneP_ub416      | layer   | 39,21,40   | 416 | q8  | 276.91   | worse (vega tiles) |
| tuneQ_kvq4       | layer   | 39,21,40   | 384 | q4  | 235.13   | much worse (scalar dequant) |
| tuneR_r1_25      | layer   | 40,22,38   | 384 | q8  | 289.90   | 27/14/25 worse     |
| tuneN_tensor     | tensor  | -          | -   | -   | -        | CRASH: meta backend multi-buffer (mixed ROCm+Vulkan unsupported) |
| tuneL_bal (row via -ts 40,23,37) | layer | - | 384 | q8 | - | VK1 oversubscribed |

**Production (vision): `-sm layer -ts 39,21,40 -c 197000 --pipeline-parallel
off` -> pp 295.84, tg 16.4-18.1, vision OK (validated end-to-end).**
llama-start-q8v.sh updated. Session pp progression: 179-238 -> 285 (vk f16)
-> 296 (layer 26/14/26 + pp off).

To exceed ~296: needs code (vectorized q8 FA path / better pipelining in
the fork), or homogeneous backends for -sm tensor. Not config-reachable.

## Why trial_c1 unlocks the gain

`-ot '^blk\.64\.nextn\..*=ROCm0'` relocates the four MTP model tensors
(`blk.64.nextn.eh_proj.weight`, `enorm.weight`, `hnorm.weight`,
`shared_head_norm.weight`, total ~53 MiB) off ROCm1 onto ROCm0.

The MTP **model** move is tiny. The lever is that this relocation also moves
the **MTP compute and KV bookkeeping** to ROCm0, and the per-device compute
buffers collapse from `502/556/532` MiB (≈1.5 GiB total) down to
`186/188/186` MiB (≈0.5 GiB total) — a **~1,030 MiB** saving spread across
all three devices. That stranded compute buffer was the hidden constraint.

## Failure modes observed

1. **Whole-layer `-ts` steps don't always cross a layer boundary.**
   `-ts 42,21,37` produced identical dev1 placement as `-ts 43,22,35` because
   `ceil(66 * (p0+p1))` stayed at 43. Calculate the cumulative boundary,
   don't assume a 1-unit `-ts` shift moves a layer.
2. **MTP context allocation is the hard cliff, not linear KV growth.**
   With `blk.64.nextn.*` on ROCm1, every extra token of context grows the
   MTP buffer on ROCm1 specifically. Once ROCm1's free drops below the MTP
   buffer size (~650-720 MiB), startup fails with
   `failed to create MTP context` even though all other devices have
   hundreds of MiB free.
3. **Moving MTP to ROCm0 redistributes the cliff** to ROCm0's free headroom.
   The new ceiling (-c 144000) is where ROCm0's free (~685 MiB) just barely
   accommodates the grown MTP buffer (~716 MiB).
