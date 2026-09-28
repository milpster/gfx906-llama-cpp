#!/usr/bin/env python
"""SPEC-0001 increment 18 (RED): the two-arm runner.

Row: docs/graph/plans/grill/spec-0001-inc-18-tool-simulator-checkers-runner.md,
tests (2)-(5), (7), (8). Spec §9.4 "Arms and runs", "How a scenario runs",
AC_Q03 (DEDUP_STUB_FORMAT_EXACT), AC_Q05 (ii)/(iii) (DEDUP_TIMINGS_VALUES,
DEDUP_TIMINGS_PRESENT_WHEN_ACTIVE, DEDUP_PROMPT_TOKENS_REDUCED,
DEDUP_OVERRIDE_HONORED_ON_ALL_ENDPOINTS), AC_Q08 (timings part).

The model client is injectable (grill phase 5 log (1)): tests (3), (4), (7)
use ScriptedClient (recorded/scripted responses, no server); tests (2), (5),
(8) use a real tinyllama2 server in prefix-only mode (tinyllama2 emits no tool
calls). Planted defect per test, as named in the row:
(2) cache not cleared between runs; (3) turn cap checked as `> 13`;
(4) the scan reads only `content`; (5) the dedup arm omits `message_dedup`;
(7) the runner retries a failed run; (8) the live tail starts in prefix-only
mode.

Server tests run from tools/server/tests' environment (PORT, LLAMA_SERVER_BIN_PATH).
"""
import pytest

from _live_harness import (STUB_PREFIX, ScriptedClient, answer_msg, mini_anthropic_scenario,
                           mini_chat_scenario, mini_server_scenario, run_mini, start_tinyllama, tool_call_msg)

import runner  # noqa: E402

server = None


@pytest.fixture
def tiny(tmp_path):
    global server
    server, client = start_tinyllama(tmp_path)
    yield client


def runs_by_arm(result) -> dict[str, list]:
    out: dict[str, list] = {}
    for r in result.runs:
        out.setdefault(r.arm, []).append(r)
    return out


# --- (3) live-tail turn cap ---------------------------------------------------

def test_spec0001_suite_runner_thirteenth_model_turn_fails_run():
    """Row test (3); §9.4 "The tail is capped at 12 model turns; reaching the
    cap is a failed run". A scripted model that makes 12 tool calls and would
    answer on its 13th turn: every run fails with fail_reason "turn_cap".
    Planted: cap checked as `> 13` (the 13th turn is let through)."""
    s = mini_chat_scenario()
    client = ScriptedClient(s, lambda t: tool_call_msg(t) if t <= 12 else answer_msg("alpha_f03"))
    result = run_mini(s, client)
    assert len(result.runs) == 4
    assert all(r.failed and r.fail_reason == "turn_cap" for r in result.runs), \
        [(r.arm, r.run, r.model_turns, r.fail_reason) for r in result.runs]
    assert result.failed


def test_spec0001_suite_runner_twelve_model_turns_within_cap():
    """Row test (3), boundary: a model that answers correctly on its 12th
    turn is within the cap; no run fails on "turn_cap"."""
    s = mini_chat_scenario()
    client = ScriptedClient(s, lambda t: tool_call_msg(t) if t <= 11 else answer_msg("alpha_f03"))
    result = run_mini(s, client)
    assert len(result.runs) == 4
    assert [r.model_turns for r in result.runs] == [12] * 4
    assert not any(r.fail_reason == "turn_cap" for r in result.runs)


# --- (4) AC_Q03 stub-prefix leak scan ----------------------------------------

LEAK_ARGS = {"role": "assistant", "content": "", "tool_calls": [{
    "id": "tail_1", "type": "function",
    "function": {"name": "edit_file",
                 "arguments": '{"path": "alpha.c", "line": 7, "text": "[duplicate content omitted: byte-identical to tool result #1"}'}}]}
LEAK_CONTENT = {"role": "assistant", "content": "It said [duplicate content omitted: ...]"}
LEAK_REASONING = {"role": "assistant", "content": "ok", "reasoning_content": "saw [duplicate content omitted"}
CLEAN = {"role": "assistant", "content": "alpha_f03"}


@pytest.mark.parametrize("allow_content", [False, True], ids=["default", "r1_r2"])
def test_spec0001_suite_stub_leak_in_tool_call_arguments_flagged(allow_content):
    """Row test (4); AC_Q03 (maps to DEDUP_STUB_FORMAT_EXACT): the §6.4 stub
    prefix in tool-call `arguments` is flagged in every run of both arms,
    including R1/R2 (where content quoting is allowed). Planted: scan reads
    only `content`."""
    assert runner.STUB_PREFIX == STUB_PREFIX
    assert runner.scan_stub_leak(LEAK_ARGS, allow_content=allow_content) != []


def test_spec0001_suite_stub_leak_in_content_flagged_except_r1_r2():
    """Row test (4); AC_Q03: in `content` or `reasoning_content` the prefix is
    flagged, except in R1/R2 (allow_content); a clean answer is not flagged."""
    assert runner.scan_stub_leak(LEAK_CONTENT, allow_content=False) != []
    assert runner.scan_stub_leak(LEAK_REASONING, allow_content=False) != []
    assert runner.scan_stub_leak(LEAK_CONTENT, allow_content=True) == []
    assert runner.scan_stub_leak(CLEAN, allow_content=False) == []


def test_spec0001_suite_runner_reports_ac_q03_failure_on_leaking_run():
    """Row test (4) through the runner: a recorded answer whose tool call
    carries the stub prefix in `arguments` makes the scenario's AC_Q03
    verdict false."""
    s = mini_chat_scenario()
    client = ScriptedClient(s, lambda t: LEAK_ARGS if t == 1 else answer_msg("alpha_f03"))
    result = run_mini(s, client)
    assert len(result.runs) == 4
    assert result.verdicts.get("AC_Q03") is False
    assert all(r.leaks for r in result.runs)


# --- (7) never retried alone --------------------------------------------------

def test_spec0001_suite_runner_failed_runs_not_retried():
    """Row test (7); §9.4 "A run that fails is a failure. It is triaged and
    never rerun on its own." A scripted model that always fails the checker:
    exactly 2 runs per arm (greedy + seeded), each failed, scenario failed.
    Planted: the runner retries a failed run."""
    s = mini_chat_scenario()
    client = ScriptedClient(s, lambda t: answer_msg("alpha_f04"))
    result = run_mini(s, client)
    arms = runs_by_arm(result)
    assert sorted(arms) == ["dedup", "off"]
    assert {a: sorted(r.run for r in rs) for a, rs in arms.items()} == \
        {"dedup": ["greedy", "seeded"], "off": ["greedy", "seeded"]}
    assert all(r.failed for r in result.runs)
    assert result.failed


def test_spec0001_suite_runner_arm_bodies_and_shared_seed():
    """§9.4 "Arms and runs": `off` sends message_dedup enabled false; `dedup`
    sends enabled true with the manifest's role set; greedy runs use
    temperature 0; the seeded run uses one fixed seed, the same in both arms;
    every run starts from an empty cache (one reset per run)."""
    s = mini_chat_scenario()
    client = ScriptedClient(s, lambda t: answer_msg("alpha_f03"))
    result = run_mini(s, client)
    assert len(result.runs) == 4
    for r in result.runs:
        assert r.requests, (r.arm, r.run)
        for q in r.requests:
            md = q.body.get("message_dedup")
            if r.arm == "off":
                assert md == {"enabled": False}
            else:
                assert md == {"enabled": True, "roles": s["manifest"]["dedup_roles"]}
            if r.run == "greedy":
                assert q.body.get("temperature") == 0
    seeds = {r.arm: {q.body.get("seed") for q in r.requests} for r in result.runs if r.run == "seeded"}
    assert len(seeds["off"]) == 1 and seeds["off"] == seeds["dedup"] and None not in seeds["off"]
    assert client.resets >= 4


# --- (2) empty prompt cache per run (tinyllama2) ------------------------------

def test_spec0001_suite_runner_each_run_starts_with_empty_cache(tiny):
    """Row test (2); §9.4 "Every run starts from an empty prompt cache":
    `timings.cache_n == 0` on the first request of each of the 4 runs.
    One-slot tinyllama2 server, so a stale cache is visible. Planted: the
    cache is not cleared between runs."""
    result = run_mini(mini_server_scenario(), tiny, prefix_only=True)
    assert len(result.runs) == 4
    firsts = [r.requests[0].response.get("timings", {}).get("cache_n") for r in result.runs]
    assert firsts == [0, 0, 0, 0], firsts


# --- (5) AC_Q05 (ii)/(iii) ----------------------------------------------------

def test_spec0001_suite_runner_ac_q05_dedup_n_and_prompt_tokens(tiny):
    """Row test (5); AC_Q05 (ii)/(iii): on the dedup arm, `timings.dedup_n` >=
    the manifest stub count on every request whose prefix holds a manifest
    stub, and `usage.prompt_tokens` is below the off arm's for that request.
    Mini scenario, two prefix turns (turn 1 holds no stub)."""
    s = mini_server_scenario()
    result = run_mini(s, tiny, prefix_only=True)
    assert result.verdicts.get("AC_Q05") is True
    dedup = [r for r in result.runs if r.arm == "dedup"]
    assert dedup and all(
        q.response["timings"]["dedup_n"] >= 1 for r in dedup for q in r.requests if q.turn >= 2)


def test_spec0001_suite_runner_ac_q05_fails_without_message_dedup(tiny):
    """Row test (5), planted defect "the dedup arm omits message_dedup"
    (the increment-16 planted runner configuration): the server was started
    without --message-dedup, so nothing fires and AC_Q05 is false."""
    result = run_mini(mini_server_scenario(), tiny, prefix_only=True, plant_omit_message_dedup=True)
    assert len(result.runs) == 4
    assert result.verdicts.get("AC_Q05") is False


def test_spec0001_suite_runner_ac_q05_anthropic_uses_input_tokens(tiny):
    """Row test (5), A4 shape; AC_Q05 (iii) "For A4 ... usage.input_tokens
    plus the count-tokens route, and A4's override travels in the Anthropic
    body". The generation requests go to /v1/messages with message_dedup in
    the body; AC_Q05 holds; the planted omission makes it false."""
    s = mini_anthropic_scenario()
    result = run_mini(s, tiny, prefix_only=True)
    assert result.verdicts.get("AC_Q05") is True
    assert tiny.generation_bodies and all(p == "/v1/messages" for p, _ in tiny.generation_bodies)
    assert any(b.get("message_dedup", {}).get("enabled") is True for _, b in tiny.generation_bodies)
    planted = run_mini(s, tiny, prefix_only=True, plant_omit_message_dedup=True)
    assert planted.verdicts.get("AC_Q05") is False


# --- (8) prefix-only mode -----------------------------------------------------

def test_spec0001_suite_runner_prefix_only_sends_no_live_tail(tiny):
    """Row test (8): in prefix-only mode only prefix requests reach the
    server (counted: 4 runs x 2 turns, each a slice of the scripted prefix),
    and the AC_Q05 and AC_Q08 verdicts are still reported. Planted: the live
    tail starts in prefix-only mode."""
    s = mini_server_scenario()
    result = run_mini(s, tiny, prefix_only=True)
    prefix = s["prefix"]["messages"]
    bodies = [b for _, b in tiny.generation_bodies]
    assert len(bodies) == 4 * len(s["turns"])
    for b in bodies:
        n = len(b["messages"])
        assert n <= len(prefix) and b["messages"] == prefix[:n]
    assert isinstance(result.verdicts.get("AC_Q05"), bool)
    assert isinstance(result.verdicts.get("AC_Q08"), bool)
    assert all(r.tail_messages == [] and r.model_turns == 0 for r in result.runs)


# --- increment-18 review fixes (orchestrator.91.reviewer.5), scripted, no server

import json  # noqa: E402

import suite_schema  # noqa: E402
from tool_simulator import SNAPSHOTS_DIR  # noqa: E402


def real_scenario(sid: str) -> tuple[dict, object]:
    s = suite_schema.load_suite()[sid]
    return s, SNAPSHOTS_DIR / s["repo_snapshot"]


class ArmScriptedClient(ScriptedClient):
    """ScriptedClient whose live-tail script depends on the arm the request
    carries (message_dedup enabled -> dedup script, else off script)."""

    def __init__(self, scenario: dict, dedup_script, off_script):
        super().__init__(scenario, None)
        self.dedup_script, self.off_script = dedup_script, off_script

    def chat(self, body: dict) -> dict:
        on = bool(body.get("message_dedup", {}).get("enabled"))
        self.script = self.dedup_script if on else self.off_script
        return self._response(body)


# R2 answers end with the line its checker reads (data-ml's deliberate R2 change; updated by
# tool-smith orchestrator.82.tool-smith.2, the verdicts asserted are unchanged)
R2_STALE = "The handoff note says the file is unchanged.\nEffective LATE_FEE_CENTS: 900"
R2_EDITED = "config/rates.py was edited.\nEffective LATE_FEE_CENTS: 1250"


def test_spec0001_suite_runner_ac_q06_r2_stale_answer_on_dedup_fails():
    """Review (a); AC_Q06 on the R2 shape (checker wrong_answer "900", the
    stale copy): the dedup arm answers the stale 900 in both runs, the off
    arm answers 1250 in both. AC_Q06 is False, and each dedup-arm verdict
    carries the structured ``wrong_copy`` flag (off-arm verdicts do not).
    Today AC_Q06 counts only harmful tool calls (R2 has none), so it holds."""
    s, snap = real_scenario("R2")
    client = ArmScriptedClient(s, lambda t: answer_msg(R2_STALE),
                               lambda t: answer_msg(R2_EDITED))
    result = runner.run_scenario(s, client, snapshot_dir=snap)
    arms = runs_by_arm(result)
    assert len(arms["dedup"]) == 2 and len(arms["off"]) == 2
    assert result.verdicts.get("AC_Q06") is False, result.verdicts
    assert [getattr(r.verdict, "wrong_copy", None) for r in arms["dedup"]] == [True, True], \
        "dedup-arm verdicts do not carry Verdict.wrong_copy == True"
    assert [getattr(r.verdict, "wrong_copy", None) for r in arms["off"]] == [False, False]


def test_spec0001_suite_runner_ac_q06_r2_both_arms_correct_holds():
    """Review (a) control: both arms answer 1250; AC_Q06 holds (the fix must
    not turn AC_Q06 into always-False)."""
    s, snap = real_scenario("R2")
    client = ScriptedClient(s, lambda t: answer_msg(R2_EDITED))
    result = runner.run_scenario(s, client, snapshot_dir=snap)
    assert result.verdicts.get("AC_Q06") is True, result.verdicts


B3_BLOCK_BYTES = 2055     # gen_scenarios.reminder(...) of build_B3, UTF-8 bytes
B3_USER_MESSAGES = 8      # the block occurs once in each; v1 leaves 7 repeats in full


def test_spec0001_suite_report_b3_embedded_block_bytes_exact(tmp_path):
    """Review (b), re-review; §9.4 AC_Q05 report input "for B3, the repeated
    bytes v1 leaves in full because the block sits inside a larger message":
    B3's ``embedded_block_bytes_left_in_full`` in the written report is
    exactly 2055 x 7 = 14385 (the manifest's ``embedded_block``, once per user
    message, first copy excluded). Today the runner takes the longest common
    substring of the first two user messages, which picks up shared text
    around the block (12768)."""
    s, snap = real_scenario("B3")
    client = ScriptedClient(s, lambda t: answer_msg("plover-7702"))
    result = runner.run_scenario(s, client, snapshot_dir=snap, prefix_only=True)
    out = tmp_path / "report.json"
    runner.write_report([result], out)
    doc = json.loads(out.read_text(encoding="utf-8"))
    v = doc["scenarios"]["B3"]["tunables"]["embedded_block_bytes_left_in_full"]
    assert v == B3_BLOCK_BYTES * (B3_USER_MESSAGES - 1) == 14385, v


def test_spec0001_suite_report_per_arm_fields(tmp_path):
    """Review (b); §9.4 "The suite report states, per scenario: prompt tokens
    and summed timings.prompt_ms on both arms, and the stub count", plus the
    three §11 tunables inputs. Mini chat scenario (two prefix turns, answer
    on model turn 1), ScriptedClient (off 1000 / dedup 600 prompt tokens,
    prompt_ms 1.0 per request)."""
    s = mini_chat_scenario()
    client = ScriptedClient(s, lambda t: answer_msg("alpha_f03"))
    result = run_mini(s, client)
    out = tmp_path / "report.json"
    runner.write_report([result], out)
    sc = json.loads(out.read_text(encoding="utf-8"))["scenarios"][s["id"]]
    assert sc["stub_count"] == 1
    assert set(sc["tunables"]) == {"repeat_bytes_below_min_bytes", "tool_stub_share_without_tool_name",
                                   "embedded_block_bytes_left_in_full"}
    want_tokens = {"off": [1000, 1000], "dedup": [600, 600]}
    for arm in ("off", "dedup"):
        assert sorted(sc["arms"][arm]) == ["greedy", "seeded"], arm
        for run in ("greedy", "seeded"):
            a = sc["arms"][arm][run]
            assert a["prefix_prompt_tokens"] == want_tokens[arm], (arm, run)
            assert a["prompt_ms_sum"] == 2.0, (arm, run)


class PreEnableFiringClient(ScriptedClient):
    """A server that shrinks the prompt on the dedup arm's pre-enable turns
    (sent with enabled false) as soon as the turn holds a manifest unit,
    reporting dedup_n 0: a pre-enable divergence visible only as prompt size.
    The arm is known from the reset count (runs go off, off, dedup, dedup)."""

    def __init__(self, scenario: dict):
        super().__init__(scenario, lambda t: answer_msg("2375"))
        self.first_unit = min(u["message"] for u in scenario["manifest"]["must_fire"])
        self.saw_override_on_dedup_arm = False

    def chat(self, body: dict) -> dict:
        resp = self._response(body)
        on = bool(body.get("message_dedup", {}).get("enabled"))
        if self.resets >= 3 and on:
            self.saw_override_on_dedup_arm = True
        if self.resets >= 3 and not on and len(body["messages"]) > self.first_unit:
            resp["usage"]["prompt_tokens"] -= 123
        return resp


def test_spec0001_suite_runner_m2_pre_enable_turns_prompt_equals_off():
    """Review (c); §9.4 M2: on turns before ``enable_from_turn`` the dedup
    arm's prompt equals the off arm's, even on turns whose messages hold a
    manifest unit. A server that shrinks those pre-enable prompts makes
    AC_Q08 False. Today the equality is only checked where stubs == 0."""
    s, snap = real_scenario("M2")
    k = s["manifest"]["enable_from_turn"]
    client = PreEnableFiringClient(s)
    assert any(t > client.first_unit for t in s["turns"][:k - 1]), "no pre-enable turn holds a unit"
    result = runner.run_scenario(s, client, snapshot_dir=snap, prefix_only=True)
    assert client.saw_override_on_dedup_arm, "arm detection by reset count no longer holds"
    assert result.verdicts.get("AC_Q08") is False, (result.verdicts, result.notes)


def test_spec0001_suite_runner_m2_honest_pre_enable_turns_hold():
    """Review (c) control: with pre-enable prompts equal to off, AC_Q08 holds."""
    s, snap = real_scenario("M2")
    client = ScriptedClient(s, lambda t: answer_msg("2375"))
    result = runner.run_scenario(s, client, snapshot_dir=snap, prefix_only=True)
    assert result.verdicts.get("AC_Q08") is True, (result.verdicts, result.notes)


def test_spec0001_suite_runner_m2_enable_from_turn_boundary():
    """Review (d); §9.4 M2 "the dedup arm sends enabled false on scripted
    turns 1..k-1 and the override from turn k": turn k-1 carries
    ``{"enabled": false}``, turn k the enabled override, on both dedup runs."""
    s, snap = real_scenario("M2")
    k = s["manifest"]["enable_from_turn"]
    client = ScriptedClient(s, lambda t: answer_msg("2375"))
    result = runner.run_scenario(s, client, snapshot_dir=snap, prefix_only=True)
    override = {"enabled": True, "roles": s["manifest"]["dedup_roles"]}
    for r in runs_by_arm(result)["dedup"]:
        by_turn = {q.turn: q for q in r.requests if q.kind == "prefix"}
        assert by_turn[k - 1].body.get("message_dedup") == {"enabled": False}, (r.run, k - 1)
        assert by_turn[k].body.get("message_dedup", {}).get("enabled") is True, (r.run, k)
        assert {kk: v for kk, v in by_turn[k].body["message_dedup"].items() if kk != "min_bytes"} == override
