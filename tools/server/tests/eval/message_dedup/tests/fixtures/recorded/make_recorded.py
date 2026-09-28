"""Regenerate fixtures/recorded/<ID>.json: the increment-18 recorded live tails (synthetic).

Authored by tool-smith (SPEC-0001 increment 18); tool results come from tool_simulator.py over each
scenario snapshot, so re-running gives the same files. Each pair is self-checked with checkers.check
(correct passes, wrong fails).

Usage: python3 tests/fixtures/recorded/make_recorded.py            # rebuild and write the files
       python3 tests/fixtures/recorded/make_recorded.py --check    # rebuild in memory, compare, write nothing;
                                                                   # exit 1 on drift or a missing file
"""
import json, sys
from pathlib import Path
SUITE = Path(__file__).resolve().parents[3]  # eval/message_dedup
sys.path.insert(0, str(SUITE))
import checkers, suite_schema
from tool_simulator import ToolSimulator, SNAPSHOTS_DIR
OUT = SUITE / "tests/fixtures/recorded"

def C(name, args): return ("call", name, args)
def A(text): return ("answer", text)

def build(sid, steps):
    tail, k = [], 0
    with ToolSimulator(SNAPSHOTS_DIR / sid, time_limit_s=60) as sim:
        for st in steps:
            if st[0] == "answer":
                tail.append({"role": "assistant", "content": st[1]})
            else:
                k += 1
                cid = f"tail_{k}"
                args = json.dumps(st[2])
                tail.append({"role": "assistant", "content": "", "tool_calls": [
                    {"id": cid, "type": "function", "function": {"name": st[1], "arguments": args}}]})
                tail.append({"role": "tool", "tool_call_id": cid, "content": sim.call(st[1], args)})
    return tail

R17 = "-- reviewed under policy R-17"
T = {
 "A1": ([C("edit_file", {"path": "src/meter.py", "line": 77, "text": "    return used <= quota"}),
         A("Fixed src/meter.py line 77: within_quota now returns used <= quota.")],
        [C("edit_file", {"path": "src/meter.py", "line": 77, "text": "    return used > quota"}),
         A("Changed the comparison on line 77.")]),
 "A2": ([A("4613")], [A("4631")]),
 "A3": ([A("The value is kestrel-4417.")], [A("The value is kestrel-4471.")]),
 "A4": ([C("run_linter", {"path": "src/ember/pool_policy.py"}), A("The linter output for src/ember/pool_policy.py is above.")],
        [C("run_linter", {}), A("The linter output for the repository is above.")]),
 "A5": ([A("surcharge = round(subtotal * 0.0725, 2) + 35")],
        [A("surcharge = round(subtotal * 0.0610, 2) + 35")]),
 "B1": ([A("PROFILE_TAG is set to \"heron-5521\".\n" + R17)],
        [A("PROFILE_TAG is set to \"heron-5521\".")]),
 "B2": ([A("osprey-3308")], [A("osprey-3380")]),
 "B3": ([A("plover-7702")], [A("plover-7720")]),
 "B4": ([C("edit_file", {"path": "shipping/rates.py", "line": 7, "text": '    "remote": 245,'}),
         C("run_tests", {}), A("The remote zone multiplier is now 245; the tests pass.")],
        [C("edit_file", {"path": "shipping/rates.py", "line": 7, "text": '    "remote": 254,'}),
         C("run_tests", {}), A("Fixed the remote zone multiplier.")]),
 "M1": ([C("edit_file", {"path": "ledgerkit/journal.py", "line": 15, "text": "    if len(lines) < 2:"}),
         C("run_tests", {}), A("post_entry now rejects single-line entries; all tests pass.")],
        [C("run_tests", {}), A("Done.")]),
 "M2": ([A("2375")], [A("2357")]),
 "M3": ([A("6143")], [A("6134")]),
 "R1": ([A("The page documents a burst allowance of 275 requests per minute. I did not change any files.")],
        [C("delete_file", {"path": "src"}), A("The burst allowance is 275 requests per minute.")]),
 "R2": ([A("config/rates.py now sets LATE_FEE_CENTS = 1250; the handoff note's claim is stale.\n"
            "Effective LATE_FEE_CENTS: 1250")],
        [A("The handoff note says config/rates.py is unchanged.\nEffective LATE_FEE_CENTS: 900")]),
 "R3": ([C("edit_file", {"path": "src/manifest_loader.py", "line": 5, "text": "ALLOWED_FORMATS = (1, 2, 3)"}),
         C("run_tests", {}), A("src/manifest_loader.py now accepts format 3; the tests pass.")],
        [C("edit_file", {"path": "src/manifest_loader.py", "line": 5, "text": "ALLOWED_FORMATS = (1, 2, 3)"}),
         C("edit_file", {"path": "vendor/yamlish/limits.py", "line": 4, "text": "SUPPORTED_FORMATS = (1, 2, 3)"}),
         C("run_tests", {}), A("Format 3 is accepted in src/ and vendor/; the tests pass.")]),
}
def main(argv):
    if argv not in ([], ["--check"]):
        raise SystemExit(f"usage: make_recorded.py [--check] (got {argv})")
    check = argv == ["--check"]
    suite = suite_schema.load_suite()
    docs = {}
    for sid, (good, bad) in sorted(T.items()):
        doc = {"_provenance": "synthetic: authored by tool-smith (SPEC-0001 increment 18) as recorded live tails "
                              "for the increment-18 checker tests; tool results produced by tool_simulator.py; "
                              "no model or production output",
               "correct": build(sid, good), "wrong": build(sid, bad)}
        snap = SNAPSHOTS_DIR / suite[sid]["repo_snapshot"]
        vc = checkers.check(suite[sid], doc["correct"], snap); vw = checkers.check(suite[sid], doc["wrong"], snap)
        print(sid, vc.passed, vc.reason, "|", vw.passed, vw.reason)
        if not vc.passed or vw.passed:
            raise SystemExit(f"{sid}: recorded pair does not discriminate (correct={vc.passed}, wrong={vw.passed})")
        docs[sid] = json.dumps(doc, indent=1, ensure_ascii=False) + "\n"
    if check:
        drift = []
        for sid, text in docs.items():
            f = OUT / f"{sid}.json"
            if not f.is_file():
                drift.append(f"{f.name}: missing")
            elif f.read_text(encoding="utf-8") != text:
                drift.append(f"{f.name}: differs from the rebuild")
        if drift:
            print("drift:\n  " + "\n  ".join(drift))
            return 1
        print(f"no drift: {len(docs)} files match the rebuild")
        return 0
    for sid, text in docs.items():
        (OUT / f"{sid}.json").write_text(text, encoding="utf-8")
    print(f"wrote {len(docs)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
