#!/usr/bin/env python
"""SPEC-0001 increment 15 plant gate: AC_N02 (pass-off cost vs the baseline build).

No §4 contract; binds spec §5 "Performance, pass off". Row:
docs/graph/plans/grill/spec-0001-inc-15-cost-and-cache-plant-gate.md. The bar,
the run design and every limit are spec §9.3 AC_N02's (constants in
plant_gates.py, which cite it).

Two builds never share the GPU, so each measured run is one `measure` call
against the build currently serving, and the runs follow the balanced order
of plant_gates.AC_N02_BALANCED_ORDERS (4 runs per build for a PASS verdict):

  python bench_dedup_off_cost_unmeasurable.py measure --url URL --label this     --position 1 --out run1.json
  python bench_dedup_off_cost_unmeasurable.py measure --url URL --label baseline --position 2 --out run2.json
  ...                                                               (positions 1..8 in the balanced order)
  python bench_dedup_off_cost_unmeasurable.py compare run1.json ... run8.json [--out verdict.json]

`measure`: per M1 turn, one untimed warm call and then --calls (21) pass-off
/apply-template calls (no `message_dedup` field: the server-default arm, which
the feature-free baseline understands), wall-clock ms. It writes ONE run
record (`run_record`): label, position in the run order, build commit, UTC
start and end, os.getloadavg() at start and end, and the [turn][call] ms. The
build commit is --commit, or the commit in the server's /props build_info;
when both are given they must agree. `compare`: plant_gates.ac_n02_from_records
over the N records; exit 0 on PASS, 1 on FAIL, 3 on INCONCLUSIVE (fewer than 4
runs per build: can show FAIL, never PASS), 2 on INVALID (bad records or order).
The server runs with the production-profile settings and no --message-dedup.
Needs the GPU lock (or the same host settings for every run).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import os
import re
import sys

import plant_gates as pg
import plant_io as io
import suite_schema
from suite_http import SuiteHttp

EXIT = {"PASS": 0, "FAIL": 1, "INVALID": 2, "INCONCLUSIVE": 3}


def run_record(label: str, position: int, build_commit: str, started_utc: str, ended_utc: str,
               loadavg_start, loadavg_end, ms) -> dict:
    """One AC_N02 run record (spec §9.3: "Record each run's position, build
    commit, timestamps and host load"). Raises ValueError on anything
    plant_gates.ac_n02_record_problems refuses."""
    rec = {"label": label, "position": position, "build_commit": build_commit,
           "started_utc": started_utc, "ended_utc": ended_utc,
           "loadavg_start": list(loadavg_start) if isinstance(loadavg_start, (list, tuple)) else loadavg_start,
           "loadavg_end": list(loadavg_end) if isinstance(loadavg_end, (list, tuple)) else loadavg_end,
           "ms": ms}
    problems = pg.ac_n02_record_problems(rec)
    if problems:
        raise ValueError("AC_N02 run record refused: " + "; ".join(problems))
    return rec


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def server_commit(client: SuiteHttp) -> str | None:
    """The commit in /props build_info ("b<number>-<commit>"), if any."""
    info = str(client.get("/props").get("build_info", ""))
    m = re.search(r"-([0-9a-f]{7,40})\b", info)
    return m.group(1) if m else None


def measure(url: str, calls: int) -> list[list[float]]:
    client = SuiteHttp(url)
    m1 = suite_schema.load_suite()["M1"]
    out = []
    for k in range(len(io.turns_of(m1))):
        body = io.turn_body(m1, k, None)
        client.apply_template(body)  # one untimed warm call per turn
        out.append([client.timed_apply_template(body)[1] * 1000.0 for _ in range(calls)])
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("measure", help="measure ONE run and write its record")
    m.add_argument("--url", required=True)
    m.add_argument("--label", required=True, choices=["this", "baseline"])
    m.add_argument("--position", required=True, type=int, help="1-based position in the balanced run order")
    m.add_argument("--commit", help="build commit of the serving build (default: from /props build_info)")
    m.add_argument("--calls", type=int, default=21, help="timed calls per turn (spec §9.3: 21)")
    m.add_argument("--out", required=True)
    c = sub.add_parser("compare", help="score the N run records")
    c.add_argument("records", nargs="+")
    c.add_argument("--out")
    a = ap.parse_args(argv)

    if a.cmd == "measure":
        reported = server_commit(SuiteHttp(a.url))
        commit = a.commit or reported
        if not commit:
            print("error: no build commit: pass --commit (the server's /props build_info names none)", file=sys.stderr)
            return 2
        if a.commit and reported and not (a.commit.startswith(reported) or reported.startswith(a.commit)):
            print(f"error: --commit {a.commit} but the server reports build {reported}", file=sys.stderr)
            return 2
        started, load0 = _utc_now(), os.getloadavg()
        ms = measure(a.url, a.calls)
        ended, load1 = _utc_now(), os.getloadavg()
        rec = run_record(a.label, a.position, commit, started, ended, load0, load1, ms)
        path = io.write_record(f"inc15-ac-n02-run{a.position}-{a.label}", rec, a.out)
        print(f"run {a.position} ({a.label}, {commit}) {started} .. {ended}, load {load0} -> {load1}\nrecord: {path}")
        return 0
    records = []
    for p in a.records:
        try:
            records.append(io.read_record(p))
        except (OSError, ValueError) as e:   # unreadable file or not JSON: INVALID, never a traceback
            print(f"AC_N02: INVALID: record {p} cannot be read: {e}", file=sys.stderr)
            return EXIT["INVALID"]
    r = pg.ac_n02_from_records(records)
    path = io.write_record("inc15-ac-n02", io.gate_payload({"AC_N02": r}), a.out)
    d = r.details
    print(f"AC_N02: {d['verdict']} failed_clauses={d.get('failed_clauses')} order={d.get('order')}\n"
          f"failures: {r.failures[:5]}\nrecord: {path}")
    return EXIT[d["verdict"]]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
