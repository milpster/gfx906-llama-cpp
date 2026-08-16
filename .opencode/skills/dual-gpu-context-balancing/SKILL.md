---
name: dual-gpu-context-balancing
description: Manual procedure for converting stranded per-device headroom into fitted-context capacity on multi-GPU ROCm/Vulkan llama.cpp deployments. Use when fitted n_ctx_slot does not increase despite free headroom on one or more devices; when tuning --tensor-split / --split-mode cost across rocm0,vulkan1,rocm1 device triples; when sizing -ot boundary-layer tensor overrides (including MTP/nextn layer relocation); when whole-layer split trials regress context; when investigating which device is limiting the fit. Front-loads keywords: tensor-split, split-mode cost, -ot override, MTP/nextn, fitted context, limiting device, ROCm + Vulkan multi GPU, llama.cpp.
---

# Manual Dual-GPU Context Balancing for ROCm MTP

## Purpose

Use this guide when fitted context cannot grow even though one or more GPUs
report unused headroom. The procedure converts stranded per-device headroom
into target-context capacity by refining model and MTP/nextn tensor
placement.

Apply it separately to every new combination of:

- model and model quantization;
- GPU pair and device order;
- target and draft KV formats;
- batch, microbatch, parallel-slot, and draft settings;
- llama.cpp build and backend.

Do not copy a tensor override to another model without repeating the procedure.

## Contents

- [Problem](#problem)
- [Safety and test discipline](#safety-and-test-discipline)
- [Required inputs](#required-inputs)
- [Procedure](#procedure)
- [Worked example: 3-GPU hybrid ROCm + Vulkan, Qwen3.6-27B MTP Q8_0](#worked-example-3-gpu-hybrid-rocm--vulkan-qwen36-27b-mtp-q8_0)
- [Launcher pattern](#launcher-pattern)
- [Common failure modes](#common-failure-modes)
- [Result record template](#result-record-template)
- [Helper scripts](#helper-scripts)
- [Future automation target](#future-automation-target)

## Problem

`--split-mode layer` places complete model layers on devices. A setting such as:

```text
--device rocm0,rocm1
--split-mode layer
--tensor-split 0.6,0.4
```

defines a coarse layer boundary. Context-dependent allocations are then added
per device:

- target KV;
- recurrent state;
- target compute buffers;
- MTP KV and compute buffers;
- backend-specific workspace.

The fitted context is the lowest context supported by any selected device. A
saving on one device (model weight, MTP relocation, or compute bookkeeping)
becomes headroom, not context, when another device remains limiting. Total
free memory is not interchangeable across GPUs.

Changing `--tensor-split` may not solve this because its layer-mode placement is
discrete. Moving one complete layer can transfer too much model memory and make
the other GPU limiting. Use target tensor-buffer overrides for finer placement.

## Safety and test discipline

1. Confirm the notes repository is on `master` and the source repository is on
   `sol` before changing investigation artifacts.
2. Do not rebuild or modify the source repository merely to tune placement.
3. Use the intended binary and its matching shared libraries.
4. Ensure no earlier server owns the selected port before each trial.
5. Change one placement variable per trial.
6. Stop each diagnostic server after it reaches the listening state.
7. Treat startup fitting as capacity evidence only, not stability or performance
   validation.
8. Preserve at least the configured `--fit-target`; do not manufacture gains by
   silently reducing the safety margin.

## Required inputs

Start from a known launcher and record:

```text
binary and LD_LIBRARY_PATH
model path and quantization
device order
split mode and tensor split
n_gpu_layers
KV format (target / MTP)
draft maximum
batch and microbatch
parallel slots
pipeline mode
fit target
```

Use `-lv 4` during fitting trials. Capture these output fields for every device:

```text
fitted n_ctx_slot
model buffer size
target KV buffer size
recurrent-state buffer size
target compute buffer size
MTP KV buffer size
MTP compute buffer size
refined MTP memory estimate
graph splits and scheduler copies
allocation failures or fallbacks
```

Do not assume that editing a launcher changed an already-running process.

## Procedure

### 1. Establish baseline fit

Run the production launcher with `-lv 4` appended. Require the run to reach
the listening state. Capture the per-device memory breakdown tables (model,
context, compute, free) for use as the comparison baseline.

If you intend to also evaluate a KV-format change (e.g. F16 -> a quantized
format), run that variant with otherwise identical arguments and capture its
breakdown too. The per-device delta is informative; it is not required for
the placement tuning below.

The stranded-headroom case is: at least one device has positive free memory
but fitted context cannot grow, or a context increase you expected from a
placement change did not appear. Continue to step 2.

### 2. Locate the limiting device and the lever

Identify the device with the lowest free memory (or the only negative free).
This is the limiting device. Compare per-device model, target KV, recurrent,
compute, and MTP allocations.

Look for one of two levers:

- A **boundary-layer move**: a whole layer on the limiting device can be
  shifted to a device with stranded headroom via `-ts`.
- A **specialised tensor move**: a small, semantically distinct tensor group
  on the limiting device - typically the MTP/nextn layer (`blk.<N>.nextn.*`)
  or a single FFN/attention projection - can be relocated via `-ot`.
  Moving the MTP layer also moves its compute bookkeeping, which can
  collapse per-device compute buffers by ~1 GiB total - often the largest
  single lever in an F16-KV deployment.

Rules:

- A saving on a non-limiting device becomes headroom, not context.
- Moving target storage away from the limiting device can convert that
  headroom into context.
- Moving storage in the other direction makes the imbalance worse.

Do not add the devices' free memory together. The fit is constrained by the
minimum per-device capacity.

### 3. Calculate the adjacent whole-layer split

Use this only as a diagnostic and retain it only if it improves the fit.

For two devices, normalize the first split:

```text
p0 = split0 / (split0 + split1)
N  = min(n_gpu_layers, n_layer_all + 1)
i_gpu_start = max(n_layer_all + 1 - n_gpu_layers, 0)
```

Layer-mode placement uses cumulative split thresholds. The approximate number
of GPU positions assigned to device 0 is:

```text
b = ceil(N * p0)
```

Here, `b` is the approximate number of offloaded positions assigned to device 0.
The last device-0 model-layer index is approximately:

```text
boundary_layer = i_gpu_start + b - 1
```

Verify the boundary empirically because the input/output tensors and
architecture-specific placement can affect buffer totals.

To move the last device-0 position to device 1, choose a new normalized split at
or slightly below:

```text
p0_next = (b - 1) / N
```

Use a decimal safely below the boundary to avoid floating-point ambiguity. For
66 GPU positions and `0.6,0.4`:

```text
b       = ceil(66 * 0.6) = 40
boundary = 39 / 66       = 0.590909...
trial    = 0.59,0.41
```

Run the trial and compare fitted context and per-device model buffers. If the
destination becomes limiting or context falls, restore the original split. This
means a whole layer is too large for the available headroom.

### 4. Select a fine-grained target tensor override

Keep the selected coarse `--tensor-split` in the command. If the whole-layer
trial regressed, restore the original coarse split first. Then select tensors
from the boundary layer on the limiting GPU and place them on the GPU with
stranded headroom. The `-ot` rule is an exception layered on top of the coarse
placement; it does not replace `--tensor-split`.

Use:

```text
-ot '<exact-target-tensor-regex>=ROCm1'
```

Use `-ot`, not `-otd`:

- `-ot` moves target-model tensors and changes the target device balance.
- `-otd` changes draft-model tensor placement and does not solve this case.

Quote the regex so the shell does not interpret parentheses or backslashes.
When splitting a command across lines, place `\` at the end of every continued
line with no trailing characters after it.

Prefer a compute-coherent tensor group from one boundary layer. Useful candidate
groups often include:

```text
one FFN projection
all FFN projections from the boundary layer
one attention projection group
another architecture-specific tensor group
```

Do not assume these names exist. Derive names from the model architecture or
tensor listing. Verify a match by confirming that model-buffer bytes moved from
the source GPU to the destination GPU. Unchanged model-buffer sizes mean the
regex did not match.

### 5. Size the first override

Treat the limiting device's measured free memory as the placement budget, not
the amount to move immediately. Reserve space on the destination for the
extra KV and compute memory created by a larger context.

Start by moving approximately 20%-50% of the stranded headroom. Prefer one
natural tensor group rather than arbitrary fragments. After each trial record:

```text
X = model bytes moved from limiting GPU to destination GPU
C = fitted context
G = target graph splits
```

Accept the candidate provisionally when:

- fitted context increases;
- both devices satisfy the fit target;
- model-buffer movement matches the requested override;
- the server reaches the listening state;
- there is no allocation fallback;
- graph splits do not increase unexpectedly.

If context falls, the override moved too much or targeted the wrong device.
Reduce the tensor group or revert it. If context is unchanged, move another
small coherent group or check whether the result was hidden by the 256-token
rounding boundary.

### 6. Search for the best manual placement

Use this bounded search:

```text
baseline
  -> adjacent whole-layer trial
  -> revert if worse
  -> one boundary tensor/group
  -> add a second coherent tensor/group if context improves
  -> stop at the first regression, allocation failure, or unacceptable graph change
```

Keep a table for all trials:

| Trial | Layer split | Override | Model MiB dev0/dev1 | Context | Graph splits | Result |
|---|---|---|---:|---:|---:|---|
| baseline | ... | none | .../... | ... | ... | keep/reject |

Do not optimize only for the largest startup context. Prefer the smallest
override that produces near-maximum context while preserving throughput and
stability.

### 7. Validate the selected override

After selecting a startup candidate:

1. Repeat startup from a clean GPU state.
2. Run a fixed-context comparison against the no-override configuration.
3. Compare prompt-processing and generation throughput.
4. Compare draft acceptance using the same prompts and sampling settings.
5. Exercise prompts close to the fitted context.
6. Run long generations and monitor delayed OOM, corruption, and scheduler
   errors.
7. Record peak per-device VRAM and free memory.
8. Keep the override model-specific until all checks pass.

## Worked example: 3-GPU hybrid ROCm + Vulkan, Qwen3.6-27B MTP Q8_0

Real run on 2x Radeon VII (16 GiB, ROCm0/ROCm1) + RTX 3080 Laptop (8 GiB,
Vulkan1), `-sm cost`, `--pipeline-parallel on`, MTP `draft-mtp
--spec-draft-n-max 3`, F16 KV throughout (no quantization).

Baseline `-ts 43,22,35 -c 130000` left Vulkan1 oversubscribed by 62 MiB.
Whole-layer `-ts` steps uncovered two failure modes:

1. **Sticky layer boundaries.** `-ts 42,21,37` produced identical dev1
   placement to `-ts 43,22,35` because `ceil(66 * (p0+p1))` stayed at 43.
   Verify the cumulative threshold before assuming a 1-unit shift moves a
   layer.
2. **MTP allocation cliff.** With `blk.64.nextn.*` on ROCm1, MTP KV is
   allocated on ROCm1 only. Once ROCm1 free drops below the MTP buffer
   size (~650-720 MiB), startup fails with `failed to create MTP context`
   even when the other two devices have hundreds of MiB free. Whole-layer
   rebalancing alone capped context near `-c 130000`.

The fix was a fine-grained `-ot` overriding the four MTP model tensors
(`blk.64.nextn.eh_proj.weight`, `enorm`, `hnorm`, `shared_head_norm`, ~53
MiB total) onto ROCm0:

```text
-ts 42,19,39 -sm cost -ot '^blk\.64\.nextn\..*=ROCm0'
```

The MTP model move is tiny. The lever is that this also moves MTP compute
bookkeeping onto ROCm0, and per-device compute buffers collapse from
`502/556/532` MiB to `186/188/186` MiB - a ~1,030 MiB saving spread across
all three devices. That stranded compute buffer was the hidden constraint.

Measured result:

```text
ROCm0 free:   403 ->  685 MiB   (limiting, but positive)
Vulkan1 free: -62 ->  540 MiB   (was oversubscribed)
ROCm1 free:  1298 ->  530 MiB
context:    130000 -> 144000    (+14,000 tokens, +10.8%)
startup:    listening, /slots reports n_ctx=144128
inference:  19 tg/s with MTP speculative enabled, validated end-to-end
```

Trial-by-trial table, log captures, and the exact launcher are in
`scripts/trials.md`.

## Launcher pattern

Place the coarse split and the override in the same continued command. Both
placement options are required to reproduce a calibrated result. Target and
draft/MTP KV stay at the default F16 - no `--cache-type-*` flags:

```bash
--device rocm0,vulkan1,rocm1 \
--split-mode cost \
--tensor-split 42,19,39 \
--pipeline-parallel on \
-ot '^blk\.64\.nextn\..*=ROCm0'
```

After starting, verify the effective command or log contains:

```text
the expected ROCm0-from-ROCm1 model-buffer movement
the MTP compute-buffer collapse (~1 GiB total saving)
the improved n_ctx_slot
```

## Common failure modes

| Symptom | Cause | Action |
|---|---|---|
| Override produces no model-buffer movement | Regex matched no tensor | Correct the model-specific tensor name |
| `command not found` on `-ot` | Previous line ended without `\` | Fix command continuation |
| New run cannot bind the port | Earlier server is still running | Stop the earlier server before testing |
| Whole-layer split reduces context | Complete layer overshot destination headroom | Restore split and use `-ot` |
| Context changes by only 0 or 256 | Fit result crossed no additional rounding boundary | Try one small coherent tensor group |
| More context but slower generation | Override added costly cross-device transfers | Reduce/regroup overrides and benchmark |
| Different model fails or ignores override | Tensor names and boundary differ | Repeat the complete procedure |
| Correct binary but old behavior | Shared libraries do not match binary | Deploy and select the complete build together |

## Result record template

Store the following with every model-specific override:

```text
date:
llama.cpp commit/build:
binary and library directory:
model path and quantization:
GPU names, sizes, and order:
common launcher arguments:
baseline split and context:
KV format (target / MTP):
per-device MTP allocation:
tested whole-layer split and result:
selected tensor override:
model bytes moved per device:
fitted context:
graph splits and scheduler copies:
startup status:
throughput result:
acceptance result:
long-context result:
known risks or pending validation:
```

## Helper scripts

`scripts/` contains three short bash wrappers that hard-code the production
launcher and accept only placement args (`-ts`, `-ot`, `-sm`). They keep every
other knob (quantization, `--pipeline-parallel`, batch sizes, MTP settings)
fixed by design, so a trial cannot silently regress them.

```bash
./scripts/run.sh baseline                                # default -ts 43,22,35 -sm cost
./scripts/run.sh trial_b1 -ts 43,21,36                   # whole-layer shift
./scripts/run.sh trial_c1 -ts 43,22,35 -ot '^blk\.39\..*=ROCm0'
./scripts/capture.sh baseline                            # wait + print breakdown
./scripts/kill.sh                                        # stop trial
```

See `scripts/README.md` for the full reference.

## Future automation target

Automate this procedure by extending the fitter to measure target and MTP memory
per device, identify the limiting device, enumerate boundary-layer tensor groups,
simulate their placement, and choose the smallest transfer that maximizes the
minimum per-device context capacity. Penalize extra graph splits and require a
final measured refit before accepting the generated overrides.
