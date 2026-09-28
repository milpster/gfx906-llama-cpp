#!/usr/bin/env python
"""SPEC-0001 increment 18: the suite report keeps each run's live tail for triage.

A failed run is triaged, never rerun alone (spec §9.4), so the report must say
what the model did: for every run, each tool call with its name and raw
``arguments`` in order, and the final answer text (null when the run ended
without one, e.g. at the turn cap).

Written test-first by tool-smith (`orchestrator.82.tool-smith.2`); scripted
client, mini scenario, no server.
"""
import json

from _live_harness import ScriptedClient, answer_msg, mini_chat_scenario, run_mini, tool_call_msg

import runner  # noqa: E402

ARGS1 = {"path": "alpha.c"}
ARGS2 = {"pattern": "alpha_f03"}


def _report(tmp_path, script):
    s = mini_chat_scenario()
    result = run_mini(s, ScriptedClient(s, script))
    out = tmp_path / "report.json"
    runner.write_report([result], out)
    return json.loads(out.read_text(encoding="utf-8"))["scenarios"][s["id"]]


def test_spec0001_suite_report_keeps_tool_call_arguments_and_final_answer(tmp_path):
    """Every run's report entry lists each tail tool call as {name, arguments}
    (the raw JSON string the model sent), in order, and the final answer."""
    script = {1: tool_call_msg(1, "read_file", ARGS1), 2: tool_call_msg(2, "grep", ARGS2),
              3: answer_msg("It is alpha_f03.")}
    sc = _report(tmp_path, lambda t: script[t])
    for arm in ("off", "dedup"):
        for run in ("greedy", "seeded"):
            a = sc["arms"][arm][run]
            assert a["tail_tool_calls"] == [{"name": "read_file", "arguments": json.dumps(ARGS1)},
                                            {"name": "grep", "arguments": json.dumps(ARGS2)}], (arm, run)
            assert a["final_answer"] == "It is alpha_f03.", (arm, run)


def test_spec0001_suite_report_final_answer_null_at_turn_cap(tmp_path):
    """A run that hit the turn cap has no final answer: null, and all 12 tool
    calls are kept."""
    sc = _report(tmp_path, lambda t: tool_call_msg(t, "read_file", ARGS1))
    a = sc["arms"]["dedup"]["greedy"]
    assert a["fail_reason"] == "turn_cap"
    assert a["final_answer"] is None
    assert len(a["tail_tool_calls"]) == 12
