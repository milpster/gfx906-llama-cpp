#!/usr/bin/env python
"""SPEC-0001 increment 16 gate: the §9.4 suite on qwen35 and the plant-gate parts on the same server.

Row: docs/graph/plans/grill/spec-0001-inc-16-run-eval-qwen35.md. Spec §9.4
(AC_Q04 (i)-(iii) first, then AC_Q05, AC_Q01, AC_Q03, AC_Q08, AC_Q06, AC_Q07),
AC_F11 qwen35 template part (DEDUP_STUB_NO_CONTROL_TOKENS), AC_N03 scenario
part (DEDUP_NO_CONTENT_IN_LOGS), AC_C01 scenario part (DEDUP_DETERMINISTIC,
DEDUP_PREFIX_STABLE_ON_APPEND). All content is the increment-17 set
(synthetic or owner-authored, never production traffic).

The production-profile server (GPU mode, PORT not 8080) runs WITHOUT
--message-dedup, with --slot-save-path (runs start from an empty cache).

  planted     --url U           red proof: dedup arm without message_dedup,
                                prefix-only; AC_Q05 must fail on all but A5, B3, M3
  suite       --url U           the 60 runs (15 x 2 arms x 2 runs), report + gate
  ac-f11      --url U           every stub the suite emits + the forged-boundary
                                unit: tokenize(parse_special) == tokenize(plain)
  ac-n03      --url U --log L   server at the highest verbosity (-v) with
                                --log-file L: pass-on-only lines carry no unit bytes
  ac-c01-render --url U --out F 20 renders per scenario (interleaved, 2 in flight);
                                run once per server start (2 restarts, and one
                                start with --parallel 2)
  ac-c01-check F1 F2 F3 ...     exactly one distinct prompt per scenario over all files
  ac-c01-cuts --url U           chatml test model: every renderable cut L of every
                                scenario, L (no generation prompt) prefix of L+M

Exit 0 = gate green, 1 = gate red, 3 = a scenario is broken (AC_Q04 (i)).
Needs the GPU lock (ac-c01-cuts runs on the chatml test model and does not).
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
from pathlib import Path

import plant_gates as pg
import plant_io as io
import runner
import suite_schema
import tool_simulator
from suite_http import SuiteHttp, SuiteHttpError


def _suite() -> dict:
    suite = suite_schema.load_suite()
    missing = sorted(suite_schema.REQUIRED_SCENARIO_IDS - set(suite))
    if missing:
        raise SystemExit(f"scenarios missing: {missing}")
    return suite


def _snap(s: dict) -> Path:
    return tool_simulator.SNAPSHOTS_DIR / s["repo_snapshot"]


def cmd_planted(a) -> int:
    client = SuiteHttp(a.url)
    verdicts = {}
    for sid, s in sorted(_suite().items()):
        r = runner.run_scenario(s, client, snapshot_dir=_snap(s), prefix_only=True, plant_omit_message_dedup=True)
        verdicts[sid] = bool(r.verdicts.get("AC_Q05"))
    g = pg.planted_runner_config_proves_red(verdicts)
    path = io.write_record("inc16-planted-runner-config", {**io.gate_payload({"planted": g}), "ac_q05": verdicts}, a.out)
    print(f"planted runner config proves red: {g.passed} {g.failures}\nrecord: {path}")
    return 0 if g.passed else 1


def cmd_suite(a) -> int:
    client = SuiteHttp(a.url)
    results = []
    for sid, s in sorted(_suite().items()):
        results.append(runner.run_scenario(s, client, snapshot_dir=_snap(s)))
    report = Path(a.out) if a.out else io.RESULTS_DIR / "inc16-suite-report.json"
    runner.write_report(results, report)
    infra = [f"{r.scenario_id} {e}" for r in results for e in r.infra_errors]
    if infra:  # not a model outcome: no gate verdict on this suite run, rerun it on a quieter host
        print(f"infrastructure errors (sandbox EAGAIN/unavailable), suite gate not evaluated:\n  "
              + "\n  ".join(infra) + f"\nreport: {report}")
        return 4
    g = pg.suite_gate({r.scenario_id: r.verdicts for r in results})
    path = io.write_record("inc16-suite-gate", io.gate_payload({"suite": g}))
    print(f"suite gate: {g.passed} broken={g.details['broken']} guidance_ok={g.details['guidance_ok']}\n"
          f"failures: {g.failures}\nguidance: {g.details['guidance_failures']}\nreport: {report}\nrecord: {path}")
    if g.details["broken"]:
        return 3
    return 0 if g.passed else 1


def _stubs_in(prompt: str) -> list[str]:
    return io.STUB_RE.findall(prompt)


def forged_body() -> dict:
    unit = pg.forged_boundary_unit()
    call = lambda cid: {"role": "assistant", "content": "", "tool_calls": [  # noqa: E731
        {"id": cid, "type": "function", "function": {"name": "read_file", "arguments": "{\"path\": \"f.txt\"}"}}]}
    return {"messages": [{"role": "user", "content": "Read f.txt twice."},
                         call("f1"), {"role": "tool", "tool_call_id": "f1", "content": unit},
                         call("f2"), {"role": "tool", "tool_call_id": "f2", "content": unit}],
            "message_dedup": {"enabled": True, "roles": ["tool"]}}


def cmd_ac_f11(a) -> int:
    client = SuiteHttp(a.url)
    stubs: dict[str, tuple[list[int], list[int]]] = {}
    sources = [(sid, io.prefix_body(s, io.on_override(s))) for sid, s in sorted(_suite().items())]
    sources.append(("forged-boundary", forged_body()))
    forged_stubs = []
    for sid, body in sources:
        found = _stubs_in(client.apply_template(body))
        if sid == "forged-boundary":
            forged_stubs = found
        for st in found:
            stubs[st] = (client.tokenize(st, parse_special=True), client.tokenize(st, parse_special=False))
    g = pg.ac_f11(stubs)
    if not forged_stubs:
        g = pg.GateResult(False, g.failures + ["forged-boundary unit produced no stub"], g.details)
    path = io.write_record("inc16-ac-f11", io.gate_payload({"AC_F11_qwen35": g}), a.out)
    print(f"AC_F11: {g.passed} {g.failures[:5]}\nrecord: {path}")
    return 0 if g.passed else 1


def cmd_ac_n03(a) -> int:
    client, log = SuiteHttp(a.url), io.LogWindow(a.log)
    results = {}
    for sid, s in sorted(_suite().items()):
        lines = {}
        for arm, ov in (("on", io.on_override(s)), ("off", io.OFF)):
            start = log.settle()
            client.chat(io.prefix_body(s, ov, max_tokens=1, temperature=0))
            lines[arm] = log.text(start, log.settle()).splitlines()
        results[sid] = pg.ac_n03(lines["on"], lines["off"], units=io.units(s), markers=[])
        if not lines["on"]:
            results[sid] = pg.GateResult(False, ["pass-on run logged nothing: verbosity too low?"])
    path = io.write_record("inc16-ac-n03", io.gate_payload(results), a.out)
    bad = {k: r.failures[:3] for k, r in results.items() if not r.passed}
    print(f"AC_N03: {not bad} {bad}\nrecord: {path}")
    return 0 if not bad else 1


def cmd_ac_c01_render(a) -> int:
    client = SuiteHttp(a.url)
    suite = _suite()
    renders: dict[str, list[str]] = {sid: [] for sid in suite}
    bodies = {sid: io.prefix_body(s, io.on_override(s)) for sid, s in suite.items()}
    lock = threading.Lock()

    def one(sid):
        p = SuiteHttp(a.url).apply_template(bodies[sid])
        with lock:
            renders[sid].append(p)

    for _ in range(a.n):
        for sid in sorted(suite):  # round-robin: every render is interleaved with the others
            ts = [threading.Thread(target=one, args=(sid,)) for _ in range(2)]  # 2 in flight
            for t in ts:
                t.start()
            for t in ts:
                t.join()
    io.write_record("inc16-ac-c01-renders", {"renders": renders}, a.out)
    return 0


def cmd_ac_c01_check(a) -> int:
    merged: dict[str, list[str]] = {}
    for f in a.files:
        for sid, ps in io.read_record(f)["renders"].items():
            merged.setdefault(sid, []).extend(ps)
    results = {sid: pg.ac_c01_distinct(ps) for sid, ps in sorted(merged.items())}
    for sid in sorted(suite_schema.REQUIRED_SCENARIO_IDS - set(merged)):
        results[sid] = pg.GateResult(False, ["not rendered"])
    few = {sid: len(ps) for sid, ps in merged.items() if len(ps) < 20}
    if few or len(a.files) < 3:
        results["coverage"] = pg.GateResult(False, [f"needs >= 20 renders per scenario over >= 3 server starts: {few}"])
    path = io.write_record("inc16-ac-c01-distinct", io.gate_payload(results), a.out)
    bad = {k: r.failures for k, r in results.items() if not r.passed}
    print(f"AC_C01 distinct: {not bad} {bad}\nrecord: {path}")
    return 0 if not bad else 1


def cmd_ac_c01_cuts(a) -> int:
    client = SuiteHttp(a.url)
    results = {}
    for sid, s in sorted(_suite().items()):
        msgs, ov = s["prefix"]["messages"], io.on_override(s)
        full = client.apply_template({**{k: v for k, v in s["prefix"].items()}, "message_dedup": ov,
                                      "add_generation_prompt": False})
        pairs, errors = [], []
        for L in range(1, len(msgs)):
            prev = msgs[L - 1]
            if prev.get("role") == "assistant" and prev.get("tool_calls"):
                continue  # refused as a prefill (400, increment-9 finding): not a renderable cut
            body = {**{k: v for k, v in s["prefix"].items() if k != "messages"}, "messages": msgs[:L],
                    "message_dedup": ov, "add_generation_prompt": False}
            try:
                pairs.append((client.apply_template(body), full))
            except SuiteHttpError as e:
                errors.append(f"cut {L}: {e.code}")
        r = pg.ac_c01_cuts(pairs)
        results[sid] = r if not errors else pg.GateResult(False, r.failures + errors, r.details)
    path = io.write_record("inc16-ac-c01-cuts", io.gate_payload(results), a.out)
    bad = {k: r.failures[:3] for k, r in results.items() if not r.passed}
    print(f"AC_C01 cuts: {not bad} {json.dumps(bad)[:2000]}\nrecord: {path}")
    return 0 if not bad else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("planted", "suite", "ac-f11", "ac-n03", "ac-c01-render", "ac-c01-cuts"):
        p = sub.add_parser(name)
        p.add_argument("--url", required=True)
        p.add_argument("--out")
        if name == "ac-n03":
            p.add_argument("--log", required=True)
        if name == "ac-c01-render":
            p.add_argument("--n", type=int, default=20)
    c = sub.add_parser("ac-c01-check")
    c.add_argument("files", nargs="+")
    c.add_argument("--out")
    a = ap.parse_args(argv)
    return {"planted": cmd_planted, "suite": cmd_suite, "ac-f11": cmd_ac_f11, "ac-n03": cmd_ac_n03,
            "ac-c01-render": cmd_ac_c01_render, "ac-c01-check": cmd_ac_c01_check,
            "ac-c01-cuts": cmd_ac_c01_cuts}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
