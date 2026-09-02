# Server-level A/B benchmark harness

Measures end-to-end `llama-server` performance (prompt processing, generation,
MTP draft acceptance) for one configuration at a time, against the real
production launcher arguments. Use it to compare binaries, splits, context
sizes, env flags, or `-ot` overrides while holding everything else fixed.

This is a complementary tool to `tools/llama-bench`: it drives the HTTP server
with the full launcher config (pipeline parallel, MTP, checkpoints, devices)
instead of raw backend micro-benchmarks.

## Layout

| File | Purpose |
|---|---|
| `ab-bench.sh` | Starts a server variant, runs the client, stops the server, appends a trial row |
| `bench-client.py` | HTTP client: health wait, PP test, TG test, acceptance, JSON output |
| `bench-dot4.cu` | gfx906 dp4a (`v_dot4_u32_u8`) issue-rate microbenchmark - the MMQ compute ceiling |
| `rocprof.sh` | Runs rocprofv2 from the archived 6.1-matched stack (see "PMU profiling verdict" in FINDINGS.md) |
| `rocprof-server.sh` | Profiling twin of the production launcher (env differences documented inside) |
| `rebuild-rocprof-stack.sh` | Re-downloads the full rocprofiler tool tree if the archived stack breaks |
| `rocprof-stack/` | Archived rocprofv2 6.1 (build 60100) runtime matching /opt/rocm-6.1.0 |
| `rocprof-pmc-{a,b,c}.txt` | Verified PMC counter-group recipes |
| `analyze-pmc.py` | Aggregates results CSVs by kernel class, derives pipe-utilization metrics |
| `trials.md` | Append-only results table, one row per trial |
| `FINDINGS.md` | Decision record: measured frontier, failed routes, env-var status, rejected ideas, profiler status |
| `logs/` | Per-trial server logs (stdout+stderr) |

## bench-dot4

```bash
hipcc -O3 --offload-arch=gfx906 bench-dot4.cu -o bench-dot4
HSA_OVERRIDE_GFX_VERSION=9.0.6 HIP_VISIBLE_DEVICES=0,1 ./bench-dot4 0 2000000
```

Measures sustainable dp4a instructions/s from register-resident chains (no
memory traffic). Compare against MMQ demand: `pp1_tok_s x 27e9 params x
(layer share) / 4 MACs per dot4 / n_gpus`. Measured 2026-08-15: 2.27 T
dot4-instr/s per Radeon VII (9.06 T-MAC/s); MMQ demand at pp1=324 is
0.94 T-instr/s per VII - see `FINDINGS.md` for the headroom analysis.

## Usage

```bash
cd bench

# baseline: production config, current binary
./ab-bench.sh my-baseline

# one variable per trial - examples:
SPEC=3            ./ab-bench.sh spec3
TS=42,19,39       ./ab-bench.sh ts42
VK_F16=1          ./ab-bench.sh vkf16          # drops GGML_VK_DISABLE_F16
CTX=144000        ./ab-bench.sh ctx144
BIN=/path/to/other/build/bin/llama-server ./ab-bench.sh old-binary

# extra server args pass through after the trial name:
./ab-bench.sh mtp-ot -ot '^blk\.64\.nextn\..*=ROCm0'
```

## Knobs (environment)

| Var | Default | Meaning |
|---|---|---|
| `BIN` | `../build-dflash-novega/bin/llama-server` | Server binary under test |
| `PORT` | `8013` | Listen port (must be free) |
| `CTX` | `155000` | `-c` value |
| `SPEC` | `2` | `--spec-draft-n-max` |
| `TS` | `41,20,39` | `-ts` value |
| `UB` | `448` | `-ub` (ubatch) value |
| `LIVE_LOG` | `logs/live.log` | append target for the tee'd live stream (tmux users: `tail -f` this) |
| `VK_F16` | `0` | `1` = do not set `GGML_VK_DISABLE_F16` |
| `MODEL` | `$HOME/ai/ai/Qwen3.8-27B-Q8_0.gguf` | Model file |
| `SPEC_TYPE` | `draft-mtp` | `none` disables speculative decoding entirely |
| `LIVE` | `1` | client streams the TG completion text to stderr as it generates; `0` silences |

All other production flags (pipeline-parallel, cost split, poll, cram,
checkpoints, sampling defaults) are hard-coded in `ab-bench.sh` so a trial
cannot silently regress them.

## Output fields

Each trial appends one row to `trials.md`:

- `pp1_tps` - throughput of the **first server batch** (16384 tokens) of a
  fresh 33009-token prompt, from the first `prompt_progress` SSE event. This
  is the primary PP number: it matches the launcher calibration metric
  ("PP 311-315 tok/s @ 16384-token batch") and is not diluted by later
  batches that run slower as the KV cache grows.
- `pp_tps` - aggregate throughput over the whole 33009-token prompt (shows
  batch-to-batch decay vs `pp1_tps`)
- `tg_tps` - generation throughput, 1024 greedy tokens (temperature 0)
- `acc` - accepted draft tokens per generated token, from
  `timings.draft_n_accepted` (only meaningful with speculative decoding)
- `load_s` - seconds until `/health` returns ok
- `n_ctx` - fitted context reported by `/slots`
- `sha` - short hash of the generated text (greedy) for cross-trial comparison
- `ok` - whether two identical greedy completions produced identical text

## Caveats

- `ok=0` is expected in some configurations even with temperature 0: logits
  are not guaranteed bit-for-bit identical across runs with different KV/batch
  states (documented llama.cpp behavior). Treat `sha` as a signal, not a
  hard invariant.
- Throughput numbers depend on GPU thermals and background load; rerun a
  trial or compare against a fresh baseline when in doubt.
- The harness kills the server after each trial and waits for VRAM release;
  do not start trials back-to-back faster than the script allows.
