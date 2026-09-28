#!/usr/bin/env python
"""SPEC-0001 increment 15 plant gate: AC_N01, AC_C03 (M1) and AC_C04 (M2).

Contracts: DEDUP_PASS_COST_WITHIN_BUDGET (AC_N01), DEDUP_CACHE_HIT_ACROSS_TURNS
and DEDUP_PREFIX_STABLE_ON_APPEND (AC_C03), DEDUP_ENABLE_MIDCONVERSATION_DIVERGES_AT_FIRST_STUB
(AC_C04 qwen35 part). Row: docs/graph/plans/grill/spec-0001-inc-15-cost-and-cache-plant-gate.md.

Runs against ONE already-running production-profile server
(docs/graph/product/production-profile.md settings, GPU mode, PORT not 8080)
started WITHOUT --message-dedup (the pass is toggled per request through the
override), with ``--slot-save-path <dir>`` (every replay starts from an empty
cache through slot erase) and ``-lv 4`` writing to ``--log-file`` (the AC_C03
trace line is SLT_TRC). Decisions: plant_gates.ac_n01 / ac_c03 / ac_c04_divergence.

  python bench_dedup_pass_cost_within_budget.py --url http://127.0.0.1:$PORT \
      --log /path/to/server.log [--runs 21] [--out results/x.json]

Exit 0 when every gate passes, 1 otherwise. Needs the GPU lock.
"""
from __future__ import annotations

import argparse
import sys

import plant_gates as pg
import plant_io as io
import suite_schema
from suite_http import SuiteHttp


def replay(client: SuiteHttp, s: dict, arm_of_turn, log: io.LogWindow | None, ks: range) -> list[dict]:
    """Turn-by-turn replay with cache_prompt true from an empty cache.
    arm_of_turn(k) -> override. Records prompt_n, prompt_ms, the pass-on log
    window's checkpoint signal and prefix stability per turn."""
    client.erase_slots()
    out, prev_nogen = [], None
    for k in ks:
        ov = arm_of_turn(k)
        start = log.settle() if log else 0
        res = client.chat(io.turn_body(s, k, ov, max_tokens=1, temperature=0, cache_prompt=True))
        end = log.settle() if log else 0
        prompt = client.apply_template(io.turn_body(s, k, ov))
        rec = {"turn": k + 1, "enabled": bool(ov.get("enabled")),
               "prompt_n": res["timings"]["prompt_n"], "prompt_ms": res["timings"]["prompt_ms"],
               "checkpoint_restored": pg.checkpoint_restored(log.text(start, end)) if log else False,
               "prefix_stable": prev_nogen is None or pg.prefix_stable(prev_nogen, prompt)}
        prev_nogen = client.apply_template(io.turn_body(s, k, ov, add_generation_prompt=False))
        out.append(rec)
    return out


def c03_turns(off: list[dict], on: list[dict]) -> list[dict]:
    return [{"off_prompt_n": a["prompt_n"], "on_prompt_n": b["prompt_n"],
             "checkpoint_restored": b["checkpoint_restored"], "prefix_stable": b["prefix_stable"]}
            for a, b in zip(off, on)]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--url", required=True)
    ap.add_argument("--log", required=True, help="the server's --log-file (-lv 4)")
    ap.add_argument("--runs", type=int, default=21)
    ap.add_argument("--out")
    a = ap.parse_args(argv)

    client, log = SuiteHttp(a.url), io.LogWindow(a.log)
    suite = suite_schema.load_suite()
    m1, m2 = suite["M1"], suite["M2"]
    on1 = io.on_override(m1)
    n1 = len(io.turns_of(m1))

    # AC_C03 on M1: pass-off replay, then pass-on replay (settings unchanged throughout)
    off_rep = replay(client, m1, lambda k: io.OFF, None, range(n1))
    on_rep = replay(client, m1, lambda k: on1, log, range(n1))

    # AC_N01 on M1: per turn 21 x on and 21 x off /apply-template, interleaved
    on_ms, off_ms = [], []
    for k in range(n1):
        b_on, b_off = io.turn_body(m1, k, on1), io.turn_body(m1, k, io.OFF)
        t_on, t_off = [], []
        for _ in range(a.runs):
            t_on.append(client.timed_apply_template(b_on)[1] * 1000.0)
            t_off.append(client.timed_apply_template(b_off)[1] * 1000.0)
        on_ms.append(t_on)
        off_ms.append(t_off)

    # AC_C04 on M2: off through turn enable_from_turn-1, on from enable_from_turn
    on2 = io.on_override(m2)
    k_on = m2["manifest"]["enable_from_turn"] - 1          # 0-based first pass-on turn
    n2 = len(io.turns_of(m2))
    mixed = replay(client, m2, lambda k: on2 if k >= k_on else io.OFF, log, range(n2))
    off2 = replay(client, m2, lambda k: io.OFF, None, range(n2))
    p_prev = client.apply_template(io.turn_body(m2, k_on - 1, io.OFF, add_generation_prompt=False))
    p_on = client.apply_template(io.turn_body(m2, k_on, on2))
    stub_at = p_on.find(io.STUB_PREFIX)

    results = {
        "AC_N01": pg.ac_n01(on_ms, off_ms, [t["prompt_ms"] for t in off_rep]),
        "AC_C03_M1": pg.ac_c03(c03_turns(off_rep, on_rep)),
        "AC_C04_M2_divergence": (pg.ac_c04_divergence(p_prev, p_on, stub_at) if stub_at >= 0
                                 else pg.GateResult(False, [f"turn {k_on + 1}: no stub rendered"])),
        # turns after k+1 meet AC_C03 against the pass-off replay (turn k+1 itself is the uncounted first)
        "AC_C04_M2_after": pg.ac_c03(c03_turns(off2[k_on:], mixed[k_on:])),
    }
    payload = io.gate_payload(results)
    payload["raw"] = {"M1_off": off_rep, "M1_on": on_rep, "M2_mixed": mixed, "M2_off": off2,
                      "AC_N01_on_ms": on_ms, "AC_N01_off_ms": off_ms}
    path = io.write_record("inc15-pass-cost-cache", payload, a.out)
    for k, r in results.items():
        print(f"{k}: {'PASS' if r.passed else 'FAIL'} {r.failures[:5]}")
    print(f"record: {path}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
