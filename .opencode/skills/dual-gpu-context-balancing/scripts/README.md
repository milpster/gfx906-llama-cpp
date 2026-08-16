# Balancing scripts

Three short bash scripts that automate the manual procedure in `../SKILL.md`.
They hard-code the user's production launcher (model, env, args) and accept
**only the placement + ctx-size variables** as parameters: `-ts`, `-ot`, `-sm`, `-c`.

Constraint: nothing else is parameterized. Quantization, `--pipeline-parallel`,
batch sizes, MTP settings, etc. are baked in on purpose so a trial can never
silently change them. `-c` IS parameterized because it is the *output* variable
we are sizing for.

## Files

| script    | purpose                                                  |
|-----------|----------------------------------------------------------|
| `run.sh`  | launch one trial, fully detached; log to `logs/<name>.log` |
| `capture.sh` | block until fit/listening/fail, then print breakdown |
| `kill.sh` | stop any running trial                                   |
| `logs/`   | one `.log` per trial (gitignored except `.gitkeep`)     |

## Usage

```bash
cd .opencode/skills/dual-gpu-context-balancing/scripts

# baseline (defaults to -ts 43,22,35 -sm cost)
./run.sh baseline

# wait for fit, see per-device breakdown
./capture.sh baseline

# whole-layer trial: shift 1 slot off vulkan1
./run.sh trial_b1 -ts 43,21,36
./capture.sh trial_b1

# fine-grained override: move boundary tensors off vulkan1
./run.sh trial_c1 -ts 43,22,35 -ot '^blk\.39\.ffn_(up|gate|down)\.weight$=ROCm0'
./capture.sh trial_c1

# stop the running trial
./kill.sh
```

`run.sh` kills any prior `llama-server` before launching, so back-to-back
trials are safe.

## What to record for each trial

After `capture.sh` finishes, copy these from the printed breakdown into the
trial table in `../SKILL.md` (or a `trials.md` next to this README):

```
fitted n_ctx_slot
model buffer size per device (dev0/dev1/dev2)
target KV buffer per device
MTP KV buffer per device
compute buffer per device
graph splits / scheduler copies
startup status (listening / FAIL)
```

## Notes

- `run.sh` writes logs under `logs/` so the source repo's tree stays clean.
- All paths are absolute; the scripts can be invoked from anywhere.
- If you need to vary something other than placement, edit `run.sh`'s
  `COMMON`-equivalent block in-place - do not parameterize it. The whole
  point of these scripts is to keep the non-placement knobs fixed.
