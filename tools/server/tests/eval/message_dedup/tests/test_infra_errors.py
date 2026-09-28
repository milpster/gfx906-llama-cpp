#!/usr/bin/env python
"""SPEC-0001 increment 18: a run_tests that fails on host resources is an
infrastructure error, not a model outcome (security residual R1,
docs/graph/plans/spec-0001-inc-18-security-note.md; `orchestrator.92.security.1`).

The sandbox's process cap is the owner's task count + NPROC_HEADROOM, so a
burst of host load can make bwrap or its fork fail with EAGAIN
(BlockingIOError). Such a run must not be judged as the model's failure: the
simulator answers one fixed text and records the error, the checker marks its
verdict, and the runner reports the run separately and withholds the
model-judged verdicts of that scenario.

Written test-first by tool-smith (`orchestrator.82.tool-smith.2`). The EAGAIN is
simulated by patching ``tool_simulator._run_group``; no host load, no server.
"""
import json
import subprocess

import pytest

from _live_harness import ScriptedClient, answer_msg, tool_call_msg
from _paths import FIXTURES  # noqa: F401  (sys.path)

import checkers  # noqa: E402
import runner  # noqa: E402
import tool_simulator  # noqa: E402
from tool_simulator import ToolSimulator  # noqa: E402

EAGAIN_BWRAP = "bwrap: Creating new namespace failed: Resource temporarily unavailable\n"


def make_snapshot(tmp_path):
    snap = tmp_path / "snapshot"
    (snap / "tests").mkdir(parents=True)
    (snap / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (snap / "tests" / "test_ok.py").write_text(
        "import unittest\n\n\nclass T(unittest.TestCase):\n    def test_ok(self):\n        self.assertTrue(True)\n",
        encoding="utf-8")
    return snap


def fork_fails(*a, **k):
    raise BlockingIOError(11, "Resource temporarily unavailable")


def bwrap_eagain(argv, timeout, preexec):
    return subprocess.CompletedProcess(argv, 1, "", EAGAIN_BWRAP)


@pytest.mark.parametrize("failure", [fork_fails, bwrap_eagain], ids=["fork_eagain", "bwrap_eagain"])
def test_spec0001_suite_simulator_run_tests_eagain_is_infra_error(tmp_path, monkeypatch, failure):
    """EAGAIN when forking bwrap, or bwrap itself failing with EAGAIN: run_tests
    answers exactly SANDBOX_RESOURCE_EXHAUSTED and the simulator records one
    infrastructure error (never an exception, never a test report)."""
    snap = make_snapshot(tmp_path)
    monkeypatch.setattr(tool_simulator, "_run_group", failure)
    with ToolSimulator(snap) as sim:
        ans = sim.call("run_tests", "{}")
        assert ans == tool_simulator.SANDBOX_RESOURCE_EXHAUSTED
        assert len(sim.infra_errors) == 1 and "Resource temporarily unavailable" in sim.infra_errors[0]


def test_spec0001_suite_simulator_run_tests_healthy_records_no_infra_error(tmp_path):
    """Control: a healthy run_tests records nothing."""
    with ToolSimulator(make_snapshot(tmp_path)) as sim:
        assert sim.call("run_tests", "{}").rstrip().endswith("OK")
        assert sim.infra_errors == []


def test_spec0001_suite_checker_tests_pass_eagain_is_infra_error(tmp_path, monkeypatch):
    """A tests_pass checker whose replay hits EAGAIN returns a verdict that
    carries ``infra_error`` (and does not pass)."""
    snap = make_snapshot(tmp_path)
    monkeypatch.setattr(tool_simulator, "_run_group", fork_fails)
    s = {"id": "X1", "manifest": {"checker": {"kind": "tests_pass"}}}
    v = checkers.check(s, [answer_msg("done")], snap)
    assert not v.passed and v.infra_error


def test_spec0001_suite_runner_reports_infra_error_separately(tmp_path, monkeypatch):
    """A run whose live tail calls run_tests while the host is out of process
    slots: every run is tagged ``infra_error`` (fail_reason "infra_error: ..."),
    the scenario lists them in ``infra_errors`` and in the report, and the
    model-judged verdicts (AC_Q01, AC_Q04_i, AC_Q03) are withheld."""
    from _live_harness import mini_chat_scenario
    snap = make_snapshot(tmp_path)
    monkeypatch.setattr(tool_simulator, "_run_group", fork_fails)
    s = mini_chat_scenario()
    client = ScriptedClient(s, lambda t: tool_call_msg(t, "run_tests", {}) if t == 1 else answer_msg("alpha_f03"))
    result = runner.run_scenario(s, client, snapshot_dir=snap)
    assert len(result.runs) == 4
    assert all(r.infra_error and r.fail_reason.startswith("infra_error") for r in result.runs), \
        [(r.fail_reason, r.infra_error) for r in result.runs]
    assert len(result.infra_errors) == 4
    for key in ("AC_Q01", "AC_Q04_i", "AC_Q03"):
        assert key not in result.verdicts, result.verdicts
    assert "AC_Q05" in result.verdicts and "AC_Q08" in result.verdicts
    out = tmp_path / "report.json"
    runner.write_report([result], out)
    doc = json.loads(out.read_text(encoding="utf-8"))["scenarios"][s["id"]]
    assert len(doc["infra_errors"]) == 4


# ---------------------------------------------------------------------------
# increment-18 final re-check (orchestrator.91.reviewer.5), written by tester
# (orchestrator.93.tester.3). Pure: real bwrap as the oracle, no server.
# ---------------------------------------------------------------------------

EAGAIN_TEXT = "bwrap: Resource temporarily unavailable"

SPOOF_IN_TEST = (
    "import os\nimport sys\nimport unittest\n\n\n"
    "class T(unittest.TestCase):\n"
    "    def test_spoof(self):\n"
    f"        sys.stderr.write('\\n' + {EAGAIN_TEXT!r} + '\\n')  # after unittest's 'test_spoof ... '\n"
    "        sys.stderr.flush()\n"
    "        os._exit(1)\n"
)
SPOOF_AT_IMPORT = (
    "import os\nimport unittest\n"
    f"os.write(2, {(EAGAIN_TEXT + chr(10)).encode()!r})\n"
    "os._exit(1)\n\n\n"
    "class T(unittest.TestCase):\n"
    "    def test_x(self):\n"
    "        pass\n"
)
SPOOF_SYSTEM_EXIT = (
    "import unittest\n\n\n"
    "class T(unittest.TestCase):\n"
    "    def test_spoof(self):\n"
    f"        raise SystemExit('\\n' + {EAGAIN_TEXT!r})  # traceback line starts with it\n"
)
SPOOFS = {"in_test": SPOOF_IN_TEST, "at_import": SPOOF_AT_IMPORT, "system_exit": SPOOF_SYSTEM_EXIT}


def make_spoof_snapshot(tmp_path, body: str):
    snap = tmp_path / "snapshot"
    (snap / "tests").mkdir(parents=True)
    (snap / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (snap / "tests" / "test_spoof.py").write_text(body, encoding="utf-8")
    return snap


@pytest.mark.parametrize("spoof", sorted(SPOOFS))
def test_spec0001_suite_simulator_spoofed_bwrap_eagain_is_model_failure(tmp_path, spoof):
    """Re-check (1): model-written test code that prints the bwrap EAGAIN text
    to stderr (and exits non-zero) runs INSIDE a sandbox that started, so it
    is the model's test failure: run_tests answers the test report (not
    SANDBOX_RESOURCE_EXHAUSTED) and records no infrastructure error. Real
    bwrap is the oracle. Today the stderr text alone makes it infra."""
    with ToolSimulator(make_spoof_snapshot(tmp_path, SPOOFS[spoof])) as sim:
        ans = sim.call("run_tests", "{}")
        assert ans != tool_simulator.SANDBOX_RESOURCE_EXHAUSTED, "spoofed stderr judged an infrastructure error"
        assert sim.infra_errors == [], sim.infra_errors


def test_spec0001_suite_checker_spoofed_bwrap_eagain_fails_tests_pass(tmp_path):
    """Re-check (1) through the checker: a tests_pass replay of the spoofing
    snapshot is a plain model failure (not passed, no infra_error)."""
    snap = make_spoof_snapshot(tmp_path, SPOOF_IN_TEST)
    s = {"id": "X1", "manifest": {"checker": {"kind": "tests_pass"}}}
    v = checkers.check(s, [answer_msg("done")], snap)
    assert not v.passed
    assert not v.infra_error, v


FAKE_BWRAP = """#!/bin/sh
# A bwrap that cannot start its sandbox for lack of host resources (EAGAIN).
# mode=run: the preflight (last argument /usr/bin/true) goes to the real bwrap,
# the test run fails before any child starts. mode=always: every call fails.
for last; do :; done
if [ "{mode}" = run ] && [ "$last" = /usr/bin/true ]; then exec /usr/bin/bwrap "$@"; fi
echo "bwrap: Creating new namespace failed: Resource temporarily unavailable" >&2
exit 1
"""


@pytest.mark.parametrize("mode", ["run", "always"])
def test_spec0001_suite_simulator_genuine_bwrap_start_eagain_is_infra(tmp_path, monkeypatch, mode):
    """Re-check (1) control: a bwrap that fails to start its sandbox with
    EAGAIN (no child ever started), at the preflight or at the run, is still
    an infrastructure error: SANDBOX_RESOURCE_EXHAUSTED and one recorded
    error. Pins behaviour, not mechanism (e.g. --json-status-fd)."""
    fake = tmp_path / "bwrap"
    fake.write_text(FAKE_BWRAP.format(mode=mode), encoding="utf-8")
    fake.chmod(0o755)
    monkeypatch.setattr(tool_simulator, "BWRAP", str(fake))
    with ToolSimulator(make_snapshot(tmp_path)) as sim:
        ans = sim.call("run_tests", "{}")
        assert ans == tool_simulator.SANDBOX_RESOURCE_EXHAUSTED, ans
        assert len(sim.infra_errors) == 1, sim.infra_errors


# --- re-check (3): SANDBOX_UNAVAILABLE is an infrastructure error --------------

def test_spec0001_suite_simulator_sandbox_unavailable_is_infra_error(tmp_path, monkeypatch):
    """Re-check (3): with bwrap missing, run_tests answers SANDBOX_UNAVAILABLE
    and the simulator records exactly one infrastructure error."""
    monkeypatch.setattr(tool_simulator, "BWRAP", str(tmp_path / "no-such-bwrap"))
    with ToolSimulator(make_snapshot(tmp_path)) as sim:
        assert sim.call("run_tests", "{}") == tool_simulator.SANDBOX_UNAVAILABLE
        assert len(sim.infra_errors) == 1, sim.infra_errors


def test_spec0001_suite_runner_sandbox_unavailable_is_infra_error(tmp_path, monkeypatch):
    """Re-check (3) through the runner: a live tail that calls run_tests with
    bwrap missing tags every run infra_error and lists it in infra_errors."""
    from _live_harness import mini_chat_scenario
    monkeypatch.setattr(tool_simulator, "BWRAP", str(tmp_path / "no-such-bwrap"))
    s = mini_chat_scenario()
    client = ScriptedClient(s, lambda t: tool_call_msg(t, "run_tests", {}) if t == 1 else answer_msg("alpha_f03"))
    result = runner.run_scenario(s, client, snapshot_dir=make_snapshot(tmp_path))
    assert all(r.infra_error and r.fail_reason.startswith("infra_error") for r in result.runs), \
        [(r.fail_reason, r.infra_error) for r in result.runs]
    assert len(result.infra_errors) == 4


# --- re-check (2): exit code 4 -------------------------------------------------

def fake_result(sid: str, infra: bool) -> "runner.ScenarioResult":
    return runner.ScenarioResult(scenario_id=sid, failed=True, verdicts={"AC_Q05": False},
                                 infra_errors=["dedup/greedy: run_tests: sandbox unavailable"] if infra else [])


@pytest.mark.parametrize("infra,code", [(True, 4), (False, 1)], ids=["infra", "model_failure"])
def test_spec0001_suite_runner_cli_exit_4_on_infra_error(tmp_path, monkeypatch, infra, code):
    """Re-check (2): the runner CLI exits 4 when any scenario hit an
    infrastructure error (even if it also failed), 1 on a plain model failure;
    the report is written either way."""
    monkeypatch.setattr(runner, "run_scenario", lambda s, client, **kw: fake_result(s["id"], infra))
    out = tmp_path / "report.json"
    rc = runner.main(["--url", "http://127.0.0.1:9", "--scenario", "A1", "--out", str(out)])
    assert rc == code
    assert json.loads(out.read_text(encoding="utf-8"))["scenarios"]["A1"]["infra_errors"] == \
        fake_result("A1", infra).infra_errors


class _Judged(Exception):
    pass


@pytest.mark.parametrize("infra", [True, False], ids=["infra", "clean"])
def test_spec0001_inc16_gate_suite_exit_4_before_judging(tmp_path, monkeypatch, infra):
    """Re-check (2): ``gate_suite_qwen35.py suite`` returns 4 when a scenario
    hit an infrastructure error, before the suite gate judges or records
    anything; without one it goes on to judge (the stubbed gate is reached)."""
    import argparse
    import gate_suite_qwen35 as gate

    def judged(*a, **k):
        raise _Judged
    monkeypatch.setattr(gate.runner, "run_scenario",
                        lambda s, client, **kw: fake_result(s["id"], infra and s["id"] == "M2"))
    monkeypatch.setattr(gate.pg, "suite_gate", judged)
    monkeypatch.setattr(gate.io, "write_record", judged)
    a = argparse.Namespace(url="http://127.0.0.1:9", out=str(tmp_path / "report.json"))
    if infra:
        assert gate.cmd_suite(a) == 4
    else:
        with pytest.raises(_Judged):
            gate.cmd_suite(a)
    assert (tmp_path / "report.json").is_file()
