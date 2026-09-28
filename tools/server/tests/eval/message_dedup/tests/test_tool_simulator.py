#!/usr/bin/env python
"""SPEC-0001 increment 18 (RED): the deterministic tool simulator.

Row: docs/graph/plans/grill/spec-0001-inc-18-tool-simulator-checkers-runner.md,
test (1). Spec §9.4 "a deterministic tool simulator answers its tool calls
from a fixed synthetic repository snapshot"; the simulator is deterministic,
offline, time-limited, and edits only a temporary copy of the snapshot.
Planted defect for (1): the simulator uses a random seed (the determinism
tests then differ between two fresh simulators).

No server. Snapshot: fixtures/snapshots/mini-snapshot-0001 (synthetic).
"""
import hashlib
import json
import time

from _live_harness import MINI_SNAPSHOT

import tool_simulator  # noqa: E402
from tool_simulator import ToolSimulator  # noqa: E402

SEQUENCE = [
    ("read_file", {"path": "alpha.c"}),
    ("grep", {"pattern": "alpha_f03"}),
    ("run_tests", {}),
    ("run_linter", {}),
    ("edit_file", {"path": "beta.c", "line": 8, "text": "static int beta_f04(int x) { return x * 7 + 5; }"}),
    ("read_file", {"path": "beta.c"}),
    ("read_file", {"path": "does_not_exist.c"}),
    ("no_such_tool", {"x": 1}),
]


def snapshot_digest() -> str:
    h = hashlib.sha256()
    for p in sorted(MINI_SNAPSHOT.rglob("*")):
        if p.is_file():
            h.update(str(p.relative_to(MINI_SNAPSHOT)).encode())
            h.update(p.read_bytes())
    return h.hexdigest()


def replay() -> list[str]:
    with ToolSimulator(MINI_SNAPSHOT) as sim:
        return [sim.call(name, json.dumps(args)) for name, args in SEQUENCE]


def test_spec0001_suite_simulator_read_file_serves_snapshot_bytes():
    """Row test (1) precondition (§9.4 "answers ... from a fixed synthetic
    repository snapshot"): read_file returns the snapshot file's content."""
    expected = (MINI_SNAPSHOT / "alpha.c").read_text(encoding="utf-8")
    with ToolSimulator(MINI_SNAPSHOT) as sim:
        assert sim.call("read_file", json.dumps({"path": "alpha.c"})) == expected


def test_spec0001_suite_simulator_grep_finds_only_matching_file():
    """Row test (1): grep answers from the snapshot (the pattern occurs in
    alpha.c only)."""
    with ToolSimulator(MINI_SNAPSHOT) as sim:
        out = sim.call("grep", {"pattern": "alpha_f03"})
    assert "alpha.c" in out and "beta.c" not in out


def test_spec0001_suite_simulator_same_sequence_byte_identical():
    """Row test (1): the same tool-call sequence on two fresh simulators over
    the same snapshot gives byte-identical responses (planted: random seed)."""
    first, second = replay(), replay()
    assert all(r for r in first[:2]), "read_file/grep answered nothing"
    assert [r.encode("utf-8") for r in first] == [r.encode("utf-8") for r in second]


def test_spec0001_suite_simulator_unknown_tool_one_fixed_error():
    """Row test (1): an unknown tool gets ONE fixed, non-empty error,
    whatever its name or arguments (exactness: a prefix- and a
    suffix-extension of a real tool name are unknown too)."""
    with ToolSimulator(MINI_SNAPSHOT) as sim:
        outs = {sim.call(n, "{}") for n in ("no_such_tool", "read_fil", "read_file_x", "delete_repo")}
    assert tool_simulator.UNKNOWN_TOOL_ERROR != ""
    assert outs == {tool_simulator.UNKNOWN_TOOL_ERROR}


def test_spec0001_suite_simulator_edit_applies_to_temporary_copy_only():
    """Row: "applies edits only to a temporary copy of that snapshot". An
    edit is visible to the same simulator's next read_file; the snapshot on
    disk is unchanged, and a fresh simulator reads the original."""
    before = snapshot_digest()
    new_line = "static int beta_f04(int x) { return x * 7 + 5; }"
    with ToolSimulator(MINI_SNAPSHOT) as sim:
        sim.call("edit_file", {"path": "beta.c", "line": 8, "text": new_line})
        edited = sim.call("read_file", {"path": "beta.c"})
    assert edited.splitlines()[7] == new_line
    assert snapshot_digest() == before
    with ToolSimulator(MINI_SNAPSHOT) as sim:
        assert sim.call("read_file", {"path": "beta.c"}) == (MINI_SNAPSHOT / "beta.c").read_text(encoding="utf-8")


def test_spec0001_suite_simulator_test_report_same_on_any_interpreter():
    """run_tests reports are a pure function of the files on any interpreter
    (increment-17 review `orchestrator.88.reviewer.3`): Python 3.11 prints
    `^^^^` caret lines under a traceback frame, 3.13+ prints `~~~^^^` ones or
    none. normalise_test_report drops lines made only of spaces, `^` and `~`,
    and keeps every other line, including one that merely starts with `~`."""
    d = "/tmp/dedup-sim-abc123"
    frame = f'  File "{d}/src/m.py", line 3, in f\n    return a[i] + b\n'
    tail = "IndexError: list index out of range\n~tilde text stays\n\nRan 1 test in 0.123s\n\nFAILED (errors=1)\n"
    py311 = frame + "           ~^^^\n" + tail
    py314 = frame + "           ~~~~~~^^^^^^^^^^\n" + tail
    bare = frame + tail
    outs = {tool_simulator.normalise_test_report(r, d) for r in (py311, py314, bare)}
    assert len(outs) == 1
    (out,) = outs
    assert "^" not in out and "~tilde text stays" in out
    assert 'File "src/m.py", line 3' in out and "Ran 1 tests in 0.004s" in out


# --- increment-18 review (orchestrator.91.reviewer.5) (e): grep time limit within one file

def _grep_in_child(snapshot, pattern, limit, q):
    with ToolSimulator(snapshot, time_limit_s=limit) as sim:
        q.put(sim.call("grep", {"pattern": pattern}))


def test_spec0001_suite_simulator_grep_catastrophic_regex_bounded(tmp_path):
    """Review (e); §9.4 "time-limited per call": a catastrophic regex on ONE
    long line answers a fixed one-line error within the time limit (plus 2 s
    slack), the same bytes on a second call. Today the deadline is checked
    only between files. The call runs in a forked child that is killed at
    the bound, so the RED cannot hang the suite."""
    import multiprocessing as mp
    snap = tmp_path / "snapshot"
    snap.mkdir()
    (snap / "long.txt").write_text("a" * 40 + "b\n", encoding="utf-8")
    limit, slack = 1.0, 2.0
    ctx = mp.get_context("fork")
    answers = []
    for _ in range(2):
        q = ctx.Queue()
        p = ctx.Process(target=_grep_in_child, args=(snap, r"(a+)+$", limit, q))
        t0 = time.monotonic()
        p.start()
        try:
            ans = q.get(timeout=limit + slack)
        except Exception:  # noqa: BLE001 - queue.Empty: no answer within the bound
            ans = None
        finally:
            p.kill()
            p.join()
        answers.append((ans, time.monotonic() - t0))
    for ans, dt in answers:
        assert ans is not None, f"grep gave no answer within {limit + slack:g}s"
        assert ans.startswith("error: ") and ans.endswith("\n") and ans.count("\n") == 1, ans
    assert answers[0][0] == answers[1][0]
