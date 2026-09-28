#!/usr/bin/env python
"""SPEC-0001 increment 15 plant gate: the AC_F01 transcript part.

Contract: DEDUP_OFF_BY_DEFAULT_PROMPT_UNCHANGED (AC_F01 over every §9.4
scenario prefix). Row: docs/graph/plans/grill/spec-0001-inc-15-cost-and-cache-plant-gate.md.

For every scenario prefix, with the pass off (no `message_dedup` field, server
started without --message-dedup): the /apply-template output, the
count-tokens `input_tokens` (chat: /v1/chat/completions/input_tokens; A4 also
its Anthropic body on /v1/messages/count_tokens) and the `timings` key set of
a one-token completion must be byte-identical between this build and the
baseline c89e014cc.

  python check_dedup_off_identical_to_baseline.py measure --url URL --label this     --out this.json
  python check_dedup_off_identical_to_baseline.py measure --url URL --label baseline --out base.json
  python check_dedup_off_identical_to_baseline.py compare this.json base.json [--out verdict.json]

Exit 0 on pass, 1 on fail. Needs the GPU lock (a one-token completion per scenario).
"""
from __future__ import annotations

import argparse
import sys

import plant_gates as pg
import plant_io as io
import suite_schema
from suite_http import SuiteHttp


def measure(url: str) -> dict:
    client = SuiteHttp(url)
    out = {}
    for sid, s in sorted(suite_schema.load_suite().items()):
        body = io.prefix_body(s, None)
        res = client.chat({**body, "max_tokens": 1, "temperature": 0})
        out[sid] = {"prompt": client.apply_template(body),
                    "input_tokens": client.count_tokens_chat(body),
                    "timings_keys": sorted(res.get("timings", {}))}
        if s.get("anthropic_prefix"):
            ab = dict(s["anthropic_prefix"])
            out[sid + "/anthropic"] = {"prompt": "", "input_tokens": client.count_tokens_anthropic(ab),
                                       "timings_keys": []}
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("measure")
    m.add_argument("--url", required=True)
    m.add_argument("--label", required=True, choices=["this", "baseline"])
    m.add_argument("--out", required=True)
    c = sub.add_parser("compare")
    c.add_argument("this")
    c.add_argument("baseline")
    c.add_argument("--out")
    a = ap.parse_args(argv)

    if a.cmd == "measure":
        io.write_record("inc15-ac-f01-" + a.label, {"label": a.label, "scenarios": measure(a.url)}, a.out)
        return 0
    this, base = io.read_record(a.this), io.read_record(a.baseline)
    if this.get("label") != "this" or base.get("label") != "baseline":
        print("labels must be 'this' then 'baseline'")
        return 2
    missing = sorted(suite_schema.REQUIRED_SCENARIO_IDS - set(this["scenarios"]))
    r = pg.ac_f01(base["scenarios"], this["scenarios"])
    if missing:
        r = pg.GateResult(False, r.failures + [f"{sid}: not measured" for sid in missing], r.details)
    path = io.write_record("inc15-ac-f01", io.gate_payload({"AC_F01_transcripts": r}), a.out)
    print(f"AC_F01 transcripts: {'PASS' if r.passed else 'FAIL'} {r.failures[:5]}\nrecord: {path}")
    return 0 if r.passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
