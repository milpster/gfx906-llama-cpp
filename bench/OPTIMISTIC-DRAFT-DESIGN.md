# Optimistic draft overlap - design note (E122, for review)

Status: DESIGN, not implemented. Decision doc for the owner.

## Goal

Hide draft time inside the verify wait, the only untouched slice of
the TG round. Everything else measured this campaign is closed.

## Measured basis (E120.1/E120.2, journal 2026-09-05)

- Round @120k ~= draft (13-19 ms) + verify chain (rocm0 seg +
  3080 seg + rocm1 seg). Host blocked in HIP syncs 65 pct of wall;
  VIIs busy 41/46 pct; machinery < 1 pct CPU (perf: 89 pct HSA
  spin, 7.4 pct vk fence).
- Draft = up to n sequential llama_decode(ctx_dft) steps on
  ROCm0, each ~3-4 ms, host sampling between steps
  (common/speculative.cpp, dflash drafter, chain_heads mode:
  draft KV region seq_rm'd per head step - discard is cheap).
- VII1 + 3080 idle during the whole draft phase; ROCm0 idle
  during 3080+VII1 verify segments.

## Mechanism

Before verify N completes, draft round N+1 optimistically under
the all-accept assumption, extending the SAME draft chain (chain
tip is known pre-verify). Enqueue on ctx_dft while ctx_tgt's
verify graph executes (separate context, separate stream, same
GPU - ROCm0 is ~60 pct idle mid-round, kernels co-run).

- full accept (~20-25 pct of rounds at acc ~0.66, 4 drafts):
  draft N+1 already computed -> round loses the whole draft
  phase.
- partial accept: optimistic tail discarded (chain_heads KV
  reset makes this near-free); redraft from the accepted tip
  exactly as today. No loss - the wasted work ran in GPU idle.

sha-safe by construction: accepted tokens still decided by the
same greedy verify; optimistic tokens never enter the output
unless the verify accepts them.

## Honest expected gain

My earlier "+8-12 pct" was wrong - it assumed the whole draft
phase hides every round. Only full-accept rounds benefit:

  saving ~= P(full accept) x draft_time ~= 0.22 x 15 ms
          ~= 3.3 ms of ~108 ms round ~= +3 pct TG

Best case +3-4 pct. That is the ceiling of this design.

## Open questions (check before any code)

1. Does llama_decode(ctx_tgt) return before GPU completion in
   this fork (--pipeline-parallel on / the drain port)? If not,
   same-thread interleaving needs an async-eval path, or a
   drafter thread (then: does the HIP backend hold a per-device
   mutex across the sync wait? If yes, threaded overlap is dead
   and only async-eval works).
2. ctx_dft (mirror mode) and ctx_tgt share ROCm0: confirm
   separate streams actually co-schedule (rd-trace can answer:
   look for draft-stream kernels inside the verify quiet).
3. Accept-rollback correctness with an in-flight optimistic
   chain: the checkpoint machinery (ctx-checkpoints 30) must
   rewind draft KV + recurrent state while the optimistic graph
   may still be executing (or be drained first - measure the
   drain cost).

## Implementation sketch (if approved)

- server slot loop (tools/server/server-context.cpp): after
  enqueueing verify and before its sync, run the draft chain
  extension loop guarded by a "optimistic" flag; on accept,
  reconcile (full: keep chain; partial: seq_rm + redraft).
- common/speculative.cpp dflash drafter: expose a
  draft_extend(n_steps, from_tip) entry that reuses the existing
  per-head loop without resetting pending state.
- Gates: temp-0 sha lane (must be e54019ff6b42), pp/fill
  unchanged, tg lane +acc-matched pair, no new syncs in rd-trace
  burst profile.

## Recommendation

+3-4 pct ceiling for moderate invasiveness in the exact machinery
that is hardest to test (spec rollback). Only worth doing if a
3 pct TG win matters more than the risk surface, or as a
stepping stone if deeper pipelining is ever wanted (e.g. verify
N+1 enqueued while accept N is still being computed host-side).
Park unless the owner wants it.

## Kill criteria during implementation

- Any temp-0 sha move (mechanism is scheduling-only; a move means
  a real bug).
- Partial-accept redraft costing more than today's serial draft
  (would flip the sign on ~75 pct of rounds).
- New host syncs appearing between draft steps during verify
  (would eat the idle window the design lives in).
