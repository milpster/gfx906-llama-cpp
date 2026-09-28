#!/usr/bin/env python
"""SPEC-0001 increment 18 (RED): per-scenario deterministic checkers.

Row: docs/graph/plans/grill/spec-0001-inc-18-tool-simulator-checkers-runner.md,
test (6): each scenario checker returns a deterministic verdict on a recorded
correct answer and on a recorded wrong one. Spec §9.4 "the checker, which is
deterministic: an exact answer, a diff or test that passes, or a validated
tool-call sequence"; AC_Q01 (maps to DEDUP_FIRST_OCCURRENCE_UNCHANGED,
DEDUP_EQUIVALENT_TO_MANUAL_SUBSTITUTION), AC_Q04 (i), AC_Q06, AC_Q07.
Planted defect for (6): the checker ignores the answer, so the recorded wrong
answer passes.

Two layers:
- per checker kind, on the synthetic mini scenario (runs now);
- per real scenario A1..R3: recorded correct and wrong tails in
  fixtures/recorded/<ID>.json ({"correct": [...], "wrong": [...]}, synthetic,
  authored with the increment-18 checkers and reviewed by data-ml), against
  the increment-17 scenario and its snapshot.
No server.
"""
import json

import pytest

from _live_harness import MINI_SNAPSHOT, answer_msg, load, tool_call_msg
from _paths import FIXTURES

import checkers  # noqa: E402
import suite_schema  # noqa: E402
import tool_simulator  # noqa: E402

RECORDED = FIXTURES / "recorded"


def tool_result(turn: int, content: str = "ok") -> dict:
    return {"role": "tool", "tool_call_id": f"tail_{turn}", "content": content}


ALPHA_L7_FIXED = "static int alpha_f03(int x) { return x * 6 + 4; }"

KIND_CASES = {
    "exact_answer": (
        {"kind": "exact_answer", "answer": "alpha_f03"},
        [answer_msg("alpha_f03")],
        [answer_msg("alpha_f04")],
    ),
    "diff": (
        {"kind": "diff", "path": "alpha.c", "line": 7, "text": ALPHA_L7_FIXED},
        [tool_call_msg(1, "edit_file", {"path": "alpha.c", "line": 7, "text": ALPHA_L7_FIXED}),
         tool_result(1), answer_msg("done")],
        [tool_call_msg(1, "edit_file", {"path": "alpha.c", "line": 8, "text": ALPHA_L7_FIXED}),
         tool_result(1), answer_msg("done")],
    ),
    # updated 2026-09-25 (grill §12 row 39): the required call is the first call
    # that is not read_file/grep, so a read_file cannot be the required call.
    "tool_call_sequence": (
        {"kind": "tool_call_sequence", "calls": [{"name": "run_linter", "arguments": {"path": "beta.c"}}]},
        [tool_call_msg(1, "run_linter", {"path": "beta.c"})],
        [tool_call_msg(1, "run_linter", {"path": "alpha.c"})],
    ),
}


@pytest.mark.parametrize("kind", sorted(KIND_CASES))
def test_spec0001_suite_checker_kind_deterministic_verdict(kind):
    """Row test (6) per checker kind: on a recorded correct tail the verdict
    is pass, on a recorded wrong tail it is fail, and each is the same on a
    second call (deterministic). Planted: checker ignores the answer."""
    spec, correct, wrong = KIND_CASES[kind]
    s = load("valid_scenario.json")
    s["manifest"]["checker"] = spec
    got_correct = [checkers.check(s, correct, MINI_SNAPSHOT).passed for _ in range(2)]
    got_wrong = [checkers.check(s, wrong, MINI_SNAPSHOT).passed for _ in range(2)]
    assert got_correct == [True, True], f"{kind}: correct tail not passed"
    assert got_wrong == [False, False], f"{kind}: wrong tail passed"


@pytest.mark.parametrize("sid", sorted(suite_schema.REQUIRED_SCENARIO_IDS))
def test_spec0001_suite_scenario_checker_deterministic_verdict(sid):
    """Row test (6) per real scenario: the scenario's checker passes its
    recorded correct tail and fails its recorded wrong tail, twice each.
    RED until increment 17 ships the scenario and increment 18 the recorded
    tails."""
    suite = suite_schema.load_suite()
    assert sid in suite, f"scenario {sid} not in the suite (increment 17)"
    path = RECORDED / f"{sid}.json"
    assert path.is_file(), f"recorded tails missing: {path} (increment 18)"
    rec = json.loads(path.read_text(encoding="utf-8"))
    snap = tool_simulator.SNAPSHOTS_DIR / suite[sid]["repo_snapshot"]
    got_correct = [checkers.check(suite[sid], rec["correct"], snap).passed for _ in range(2)]
    got_wrong = [checkers.check(suite[sid], rec["wrong"], snap).passed for _ in range(2)]
    assert got_correct == [True, True], f"{sid}: recorded correct tail not passed"
    assert got_wrong == [False, False], f"{sid}: recorded wrong tail passed"


# --- increment-18 review (orchestrator.91.reviewer.5) (a): structured wrong copy

@pytest.mark.parametrize("answer,wrong_copy,passed", [
    ("The billing code uses the value below.\nEffective LATE_FEE_CENTS: 900", True, False),
    ("The billing code uses the value below.\nEffective LATE_FEE_CENTS: 1250", False, True),
])
def test_spec0001_suite_checker_r2_wrong_copy_structured(answer, wrong_copy, passed):
    """Review (a); AC_Q06 on R2 (checker wrong_answer "900", the stale copy):
    the verdict carries ``wrong_copy`` True when a wrong_answer matches and
    False otherwise, so AC_Q06 can count it without parsing ``reason``.
    (Answers updated by tool-smith orchestrator.82.tool-smith.2 for data-ml's
    deliberate R2 change: the checker now reads the required last line
    "Effective LATE_FEE_CENTS: <value>"; the verdicts asserted are unchanged.)"""
    suite = suite_schema.load_suite()
    s = suite["R2"]
    snap = tool_simulator.SNAPSHOTS_DIR / s["repo_snapshot"]
    v = checkers.check(s, [answer_msg(answer)], snap)
    assert v.passed is passed
    assert getattr(v, "wrong_copy", None) is wrong_copy, "Verdict.wrong_copy missing or wrong"


# --- A4 tool_call_sequence, amended 2026-09-25 (spec §9.4 A4 success cell; grill §12 row 39)
# The required run_linter call (exact arguments) must be the first call that is
# not read_file or grep. Earlier read_file/grep calls are allowed, except one on
# the stubbed file's own path, named by the checker's ``forbidden_reads``
# (A4: config/limits.toml), which fails the run on either arm.

import copy  # noqa: E402

from _paths import SUITE_DIR  # noqa: E402

A4_RERUN = SUITE_DIR / "results" / "inc16-rerun-2026-09-25" / "suite" / "A4.json"
A4_TARGET = "src/ember/pool_policy.py"
A4_STUBBED = "config/limits.toml"


def a4():
    s = suite_schema.load_suite()["A4"]
    return s, tool_simulator.SNAPSHOTS_DIR / s["repo_snapshot"]


def tail_of(calls: list[tuple[str, dict | str]], final: str = "done") -> list[dict]:
    out = []
    for i, (name, args) in enumerate(calls, 1):
        out.append(tool_call_msg(i, name, args) if isinstance(args, dict) else
                   {"role": "assistant", "content": "", "tool_calls": [{
                       "id": f"tail_{i}", "type": "function", "function": {"name": name, "arguments": args}}]})
        out.append(tool_result(i))
    out.append(answer_msg(final))
    return out


def rerun_a4_dedup_seeded_tail() -> list[dict]:
    """The rerun's recorded A4 dedup/seeded tail (tool calls and final answer)."""
    run = json.loads(A4_RERUN.read_text(encoding="utf-8"))["scenarios"]["A4"]["arms"]["dedup"]["seeded"]
    return tail_of([(c["name"], c["arguments"]) for c in run["tail_tool_calls"]], run["final_answer"])


def test_spec0001_suite_checker_a4_rerun_read_then_lint_passes():
    """(1) The rerun's A4 dedup/seeded tail, read_file on the lint target
    (src/ember/pool_policy.py, in no stubbed unit) then the exact run_linter,
    passes. Today the exact sequence fails it: "call 1: 'read_file' instead of
    'run_linter'"."""
    s, snap = a4()
    tail = rerun_a4_dedup_seeded_tail()
    assert [n for n, _ in checkers.tool_calls_of(tail)] == ["read_file", "run_linter"]
    v = checkers.check(s, tail, snap)
    assert v.passed, v.reason


@pytest.mark.parametrize("grep", [
    {"pattern": "lint_target", "path": "src/"},
    {"pattern": "def "},
], ids=["scoped_to_src", "pattern_absent_from_stubbed"])
def test_spec0001_suite_checker_a4_grep_then_lint_passes(grep):
    """(2) A leading grep whose RESULT holds no line of the stubbed file, then
    the exact run_linter, passes. Changed deliberately 2026-09-25 (review
    orchestrator.91.reviewer.5): the earlier case, a repo-wide
    grep {"pattern": "lint_target"}, returns config/limits.toml:248 and so
    pinned a bypass of forbidden_reads; it is now a failing case below."""
    s, snap = a4()
    tail = tail_of([("grep", grep), ("run_linter", {"path": A4_TARGET})])
    v = checkers.check(s, tail, snap)
    assert v.passed, v.reason


@pytest.mark.parametrize("grep", [
    {"pattern": "lint_target"},
    {"pattern": "lint_target", "path": "config"},
    {"pattern": ".", "path": "config/"},
], ids=["repo_wide", "dir_config", "dir_config_slash_any"])
def test_spec0001_suite_checker_a4_grep_result_with_stubbed_file_fails(grep):
    """A grep before run_linter whose RESULT contains a line of a
    forbidden_reads path (config/limits.toml) fails the run, and the reason
    names that path, whatever its path argument says. The tail's tool
    messages here carry a placeholder ("ok"), so the checker must judge the
    grep by recomputing its result on the snapshot (tool_simulator), not by
    trusting the tail's recorded content."""
    s, snap = a4()
    tail = tail_of([("grep", grep), ("run_linter", {"path": A4_TARGET})])
    v = checkers.check(s, tail, snap)
    assert not v.passed
    assert A4_STUBBED in v.reason, v.reason


@pytest.mark.parametrize("first", [
    ("read_file", {"path": A4_STUBBED}),
    ("read_file", {"path": "./" + A4_STUBBED}),
    ("grep", {"pattern": "lint_target", "path": A4_STUBBED}),
], ids=["read_file", "read_file_dot_slash", "grep_path"])
def test_spec0001_suite_checker_a4_read_of_stubbed_file_fails(first):
    """(3) A read_file (or a grep scoped to the path) of the stubbed file
    config/limits.toml before run_linter fails the run, and the reason names
    that path. Today it fails only as "call 1 ... instead of 'run_linter'"."""
    s, snap = a4()
    v = checkers.check(s, tail_of([first, ("run_linter", {"path": A4_TARGET})]), snap)
    assert not v.passed
    assert A4_STUBBED in v.reason, v.reason


def test_spec0001_suite_checker_a4_leading_edit_fails():
    """(4) Any call other than read_file/grep before run_linter (here
    edit_file) fails the run."""
    s, snap = a4()
    tail = tail_of([("edit_file", {"path": A4_TARGET, "line": 1, "text": "# x"}),
                    ("run_linter", {"path": A4_TARGET})])
    assert not checkers.check(s, tail, snap).passed


@pytest.mark.parametrize("args", [{}, {"path": "src/ember"}, {"path": A4_STUBBED}, "not json"],
                         ids=["no_args", "directory", "stubbed_path", "invalid_json"])
def test_spec0001_suite_checker_a4_lint_wrong_arguments_fails(args):
    """(5) run_linter as the first non-read call, with arguments other than
    the exact {"path": "src/ember/pool_policy.py"}, fails, also after an
    allowed read."""
    s, snap = a4()
    for calls in ([("run_linter", args)], [("read_file", {"path": A4_TARGET}), ("run_linter", args)]):
        assert not checkers.check(s, tail_of(calls), snap).passed, calls


@pytest.mark.parametrize("calls", [
    [],
    [("read_file", {"path": A4_TARGET})],
    [("grep", {"pattern": "lint_target"}), ("read_file", {"path": A4_TARGET})],
], ids=["no_calls", "read_only", "grep_and_read"])
def test_spec0001_suite_checker_a4_no_lint_fails(calls):
    """(6) A tail with no run_linter call fails, however many reads it makes."""
    s, snap = a4()
    assert not checkers.check(s, tail_of(calls), snap).passed


def test_spec0001_suite_a4_manifest_names_stubbed_file_forbidden():
    """The A4 checker names the stubbed file in ``forbidden_reads``: exactly
    config/limits.toml, the file of all 4 must-fire units (tool result #1).
    data-ml adds it through gen_scenarios.py."""
    s, _ = a4()
    assert s["manifest"]["checker"].get("forbidden_reads") == [A4_STUBBED]


MINI_SEQ = {"kind": "tool_call_sequence", "calls": [{"name": "run_linter", "arguments": {"path": "alpha.c"}}],
            "forbidden_reads": ["beta.c"]}


@pytest.mark.parametrize("first,passed", [
    (("read_file", {"path": "alpha.c"}), True),
    (("read_file", {"path": "beta.c"}), False),
    (("grep", {"pattern": "x", "path": "beta.c"}), False),
], ids=["other_read", "forbidden_read", "forbidden_grep"])
def test_spec0001_suite_checker_forbidden_reads_before_required_call(first, passed):
    """Schema level, mini snapshot: ``forbidden_reads`` (optional on
    tool_call_sequence, a non-empty list of repository paths) fails a
    read_file/grep on a listed path made before the required call; other
    reads are allowed. Today the key is unknown (ValueError)."""
    s = load("valid_scenario.json")
    s["manifest"]["checker"] = copy.deepcopy(MINI_SEQ)
    tail = tail_of([first, ("run_linter", {"path": "alpha.c"})])
    assert checkers.check(s, tail, MINI_SNAPSHOT).passed is passed


@pytest.mark.parametrize("value,ok", [
    (["beta.c"], True), ([], False), ("beta.c", False), ([""], False), ([1], False),
], ids=["valid", "empty", "not_list", "empty_path", "non_string"])
def test_spec0001_suite_checker_forbidden_reads_validated(value, ok):
    """``forbidden_reads`` on tool_call_sequence: a non-empty list of
    non-empty strings is valid; anything else is a checker problem."""
    spec = dict(MINI_SEQ, forbidden_reads=value)
    assert (checkers.validate_checker(spec) == []) is ok, checkers.validate_checker(spec)
