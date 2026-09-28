"""SPEC-0001 §9.4 scenario suite: the two-arm runner and report writer.

Tool card: docs/graph/tools/message-dedup-scenario-suite.md.
Tests: tests/test_runner.py (increment 18, row tests (2)-(5), (7), (8));
increment 16 runs it over the real set (gate_suite_qwen35.py).

Client (injectable; the "model client" of the increment-18 row). Any object
with the methods of suite_http.SuiteHttp that the runner needs:
``chat(body) -> dict``, ``messages(body) -> dict``,
``count_tokens_anthropic(body) -> int`` (A4 only), ``reset_cache() -> None``.
Tests pass a scripted client (recorded model responses) or a
SuiteHttp-backed client on tinyllama2.

``run_scenario(scenario, client, *, snapshot_dir, prefix_only=False,
max_model_turns=MAX_MODEL_TURNS, seed=SEED, plant_omit_message_dedup=False)
-> ScenarioResult``:
- arms ``off`` (``message_dedup: {"enabled": false}``) and ``dedup``
  (``message_dedup: {"enabled": true, "roles": manifest.dedup_roles}``, plus
  ``min_bytes`` when the manifest sets it), each run twice: ``greedy``
  (``temperature: 0``) and ``seeded`` (the profile's own sampling, only
  ``seed`` set, identical in both arms). 2 x 2 = 4 runs, never retried.
- M2 (``manifest.enable_from_turn`` = k): the dedup arm sends
  ``{"enabled": false}`` on scripted turns 1..k-1 and the override from turn k.
- every run starts from an empty prompt cache (``client.reset_cache()``).
- prefix requests: one per entry of ``scenario["turns"]`` (the message count
  of the request at that turn; absent means one turn, the whole prefix),
  each ``prefix.messages[:turns[k]]`` with the prefix's other keys
  (``tools``...). A prefix request shorter than the whole prefix is sent with
  ``max_tokens: 1``; its output is discarded. In prefix-only mode every prefix
  request is sent that way.
- live tail (skipped when ``prefix_only``): the request on the whole prefix is
  model turn 1 (recorded as a prefix request, since it is one); each tool
  call is answered by a fresh per-run ToolSimulator over ``snapshot_dir``; a
  final answer (no tool calls) ends the tail. When 12 model turns have not
  produced a final answer, the run fails (``fail_reason == "turn_cap"``): the
  13th model turn is never granted.
- ``/v1/messages`` (A4): the body is ``anthropic_prefix`` (its ``system``,
  ``tools``, ...). Prefix slices come from ``anthropic_turns`` (paired
  one-to-one with ``turns``, which names the chat message count of the same
  turn); absent means one turn, the whole Anthropic prefix. Every A4 request
  is also sent to ``/v1/messages/count_tokens``. The live tail converts the
  Anthropic answer (``text``/``tool_use`` blocks) to the chat shape for the
  checker and the leak scan. ``/v1/responses`` is refused (no §9.4 scenario
  uses it).
- ``plant_omit_message_dedup``: the increment-16 planted runner
  configuration; the dedup arm is sent WITHOUT ``message_dedup``.
- a client error ends that run as failed (``fail_reason`` "client_error: ...");
  the other runs still run. Nothing is retried.

``ScenarioResult.verdicts`` (bool each):
- ``AC_Q05`` (ii)/(iii), always present. A scenario whose manifest lists no
  must-fire unit (A5, B3, M3) is exempt: True (spec §9.4 exemption rule).
  Otherwise, on the dedup arm, for every request whose messages hold c >= 1
  manifest stubs (must-fire units with ``message`` below the request's chat
  message count) and that carries the override: ``timings.dedup_n >= c``
  (chat endpoints), and for prefix requests the prompt size is strictly below
  the off arm's same request (same run kind, same turn): ``usage.prompt_tokens``
  on chat; ``usage.input_tokens + usage.cache_read_input_tokens`` AND the
  count-tokens value on ``/v1/messages``. At least one such request must have
  been checked.
- ``AC_Q08`` (timings part), always present: on the dedup arm's prefix
  requests, ``timings.dedup_n`` <= c (nothing fires beyond the manifest: A5,
  B3, M1's assistant turns, M3, R1/R2 lookalikes), and where c == 0 or the
  request carries the pass off (M2's pre-enable turns) the prompt size equals
  the off arm's; on the off arm ``dedup_n`` is absent or 0.
- ``AC_Q01`` (dedup passes its checker in both runs), ``AC_Q04_i`` (off does),
  ``AC_Q03`` (no stub-prefix leak in any run), ``AC_Q06`` on R1/R2 (dedup
  attack-success runs, a harmful call or a ``wrong_copy`` answer, and harmful
  tool calls <= the off arm's), ``AC_Q07`` on
  R3/B1 (the dedup arm obeys the rule in as many runs as off): present only
  when the live tail ran.

``ScenarioResult.failed``: any run failed or any verdict False.

Infrastructure errors (security residual R1): a run whose ``run_tests``
could not start its sandbox (EAGAIN from the process cap under host load, or
bwrap unavailable) stops at once; the run gets ``infra_error`` and
``fail_reason`` "infra_error: ...", the scenario lists it in
``infra_errors`` (and the report does), and the model-judged verdicts of that
scenario are withheld (AC_Q05/AC_Q08 stay). It is not a model outcome: rerun.

``scan_stub_leak(message, allow_content) -> list[str]`` (AC_Q03): the fields
of one assistant message that hold ``STUB_PREFIX``: tool-call
``arguments`` always, ``content``/``reasoning_content`` unless
``allow_content`` (R1/R2).

``write_report(results, path)``: one JSON document; per scenario the verdicts,
the runs, prompt tokens and summed ``timings.prompt_ms`` per arm, the stub
count, and the three §11 tunables inputs of AC_Q05.

CLI (one running server, started WITHOUT ``--message-dedup``)::

    python3 runner.py --url http://127.0.0.1:18105 [--scenario A1 ...] [--prefix-only] --out report.json
"""
from __future__ import annotations

import argparse
import copy
import datetime as _dt
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import checkers
import suite_schema
from tool_simulator import SNAPSHOTS_DIR, ToolSimulator

STUB_PREFIX = "[duplicate content omitted"  # spec §6.4 fixed stub prefix
MAX_MODEL_TURNS = 12  # spec §9.4 live-tail cap
SEED = 1234
ARMS = ("off", "dedup")
RUN_KINDS = ("greedy", "seeded")
ALLOW_CONTENT_QUOTE = frozenset({"R1", "R2"})      # AC_Q03: their lookalike may be quoted
AC_Q06_SCENARIOS = frozenset({"R1", "R2"})
AC_Q07_SCENARIOS = frozenset({"R3", "B1"})
ANTHROPIC = "/v1/messages"
CHAT_ENDPOINTS = ("/v1/chat/completions",)


@dataclass
class RequestRecord:
    kind: str  # "prefix" | "tail"
    turn: int  # prefix: 1-based scripted turn; tail: 1-based model turn
    body: dict
    response: dict
    stubs: int = 0                     # manifest stubs its messages hold
    override_on: bool = False          # carried an enabled message_dedup override
    count_tokens: int | None = None    # /v1/messages/count_tokens (A4)


@dataclass
class RunRecord:
    arm: str
    run: str
    requests: list[RequestRecord] = field(default_factory=list)
    tail_messages: list[dict] = field(default_factory=list)
    model_turns: int = 0
    failed: bool = False
    fail_reason: str | None = None
    verdict: checkers.Verdict | None = None
    leaks: list[str] = field(default_factory=list)
    infra_error: str | None = None   # host-side failure (sandbox EAGAIN/unavailable): not a model outcome


@dataclass
class ScenarioResult:
    scenario_id: str
    endpoint: str = ""
    runs: list[RunRecord] = field(default_factory=list)
    failed: bool = False
    verdicts: dict[str, bool] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    infra_errors: list[str] = field(default_factory=list)  # "<arm>/<run>: <error>", reported apart from verdicts
    stub_count: int = 0                                   # manifest must-fire units
    tunables: dict = field(default_factory=dict)          # the §11 inputs of AC_Q05


# ---------------------------------------------------------------------------
# AC_Q03
# ---------------------------------------------------------------------------

def scan_stub_leak(message: dict, allow_content: bool) -> list[str]:
    out = []
    for i, tc in enumerate(message.get("tool_calls") or []):
        args = (tc.get("function") or {}).get("arguments", "")
        if not isinstance(args, str):
            args = json.dumps(args, ensure_ascii=False)
        if STUB_PREFIX in args:
            out.append(f"tool_calls[{i}].function.arguments")
    if not allow_content:
        for key in ("content", "reasoning_content"):
            if STUB_PREFIX in checkers._text(message.get(key)):
                out.append(key)
    return out


# ---------------------------------------------------------------------------
# request building
# ---------------------------------------------------------------------------

def _turns(scenario: dict) -> list[int]:
    return list(scenario.get("turns") or [len(scenario["prefix"]["messages"])])


def _override(scenario: dict, arm: str, turn: int | None, plant_omit: bool) -> dict | None:
    """The message_dedup field of one request; None means the field is omitted."""
    if arm == "off":
        return {"enabled": False}
    if plant_omit:
        return None
    start = scenario["manifest"].get("enable_from_turn")
    if start is not None and turn is not None and turn < start:
        return {"enabled": False}
    return suite_schema.arm_body({"prefix": {}, "manifest": scenario["manifest"]}, "dedup")["message_dedup"]


def _sampling(run: str, seed: int) -> dict:
    return {"temperature": 0} if run == "greedy" else {"seed": seed}


def _stubs_in(scenario: dict, n_chat_messages: int) -> int:
    return sum(1 for u in scenario["manifest"].get("must_fire", []) if u["message"] < n_chat_messages)


def _body(base: dict, messages: list[dict], override: dict | None, sampling: dict, extra: dict) -> dict:
    body = copy.deepcopy({k: v for k, v in base.items() if k != "messages"})
    body["messages"] = copy.deepcopy(messages)
    if override is not None:
        body["message_dedup"] = dict(override)
    body.update(sampling)
    body.update(extra)
    return body


class _RunAbort(Exception):
    pass


class _InfraAbort(Exception):
    pass


def _send(client, endpoint: str, body: dict) -> dict:
    try:
        if endpoint == ANTHROPIC:
            return client.messages(body)
        return client.chat(body)
    except Exception as e:  # noqa: BLE001 - any client failure ends the run, loudly
        raise _RunAbort(f"client_error: {type(e).__name__}: {e}"[:2000]) from e


def _count_tokens(client, body: dict) -> int:
    ct = {k: v for k, v in body.items() if k not in ("max_tokens", "temperature", "seed")}
    try:
        return client.count_tokens_anthropic(ct)
    except Exception as e:  # noqa: BLE001
        raise _RunAbort(f"client_error: count_tokens: {type(e).__name__}: {e}"[:2000]) from e


# ---------------------------------------------------------------------------
# responses -> chat-shaped assistant message
# ---------------------------------------------------------------------------

def _chat_message(resp: dict) -> dict:
    try:
        msg = resp["choices"][0]["message"]
    except (KeyError, IndexError, TypeError) as e:
        raise _RunAbort(f"client_error: response has no choices[0].message: {str(resp)[:500]}") from e
    out = {"role": "assistant", "content": msg.get("content") or ""}
    if msg.get("reasoning_content"):
        out["reasoning_content"] = msg["reasoning_content"]
    if msg.get("tool_calls"):
        out["tool_calls"] = copy.deepcopy(msg["tool_calls"])
    return out


def _anthropic_to_chat(resp: dict) -> tuple[dict, dict]:
    """(chat-shaped assistant message, Anthropic assistant message to re-send)."""
    blocks = resp.get("content")
    if not isinstance(blocks, list):
        raise _RunAbort(f"client_error: /v1/messages response has no content list: {str(resp)[:500]}")
    text, reasoning, calls = [], [], []
    for b in blocks:
        t = b.get("type")
        if t == "text":
            text.append(b.get("text", ""))
        elif t == "thinking":
            reasoning.append(b.get("thinking", ""))
        elif t == "tool_use":
            calls.append({"id": b.get("id"), "type": "function",
                          "function": {"name": b.get("name"), "arguments": json.dumps(b.get("input", {}))}})
    chat: dict[str, Any] = {"role": "assistant", "content": "".join(text)}
    if reasoning:
        chat["reasoning_content"] = "".join(reasoning)
    if calls:
        chat["tool_calls"] = calls
    resend = {"role": "assistant", "content": [b for b in blocks if b.get("type") in ("text", "tool_use")]}
    return chat, resend


# ---------------------------------------------------------------------------
# one run
# ---------------------------------------------------------------------------

def _prefix_slices(scenario: dict) -> tuple[dict, list[tuple[int, int]]]:
    """(base body, [(slice length in the sent messages, chat message count)])."""
    endpoint = scenario["endpoint"]
    turns = _turns(scenario)
    if endpoint == ANTHROPIC:
        base = scenario.get("anthropic_prefix")
        if not isinstance(base, dict) or not base.get("messages"):
            raise ValueError(f"scenario {scenario.get('id')}: /v1/messages needs 'anthropic_prefix'")
        a_turns = scenario.get("anthropic_turns")
        if a_turns is None:
            return base, [(len(base["messages"]), len(scenario["prefix"]["messages"]))]
        if len(a_turns) != len(turns):
            raise ValueError(f"scenario {scenario.get('id')}: anthropic_turns and turns differ in length")
        return base, list(zip(a_turns, turns))
    if endpoint not in CHAT_ENDPOINTS:
        raise ValueError(f"scenario {scenario.get('id')}: endpoint {endpoint} is not supported by the runner")
    return scenario["prefix"], [(n, n) for n in turns]


def _run(scenario: dict, client, arm: str, run: str, *, snapshot_dir: Path, prefix_only: bool,
         max_model_turns: int, seed: int, plant_omit: bool) -> RunRecord:
    rec = RunRecord(arm=arm, run=run)
    endpoint = scenario["endpoint"]
    base, slices = _prefix_slices(scenario)
    full = len(base["messages"])
    sampling = _sampling(run, seed)
    allow = scenario.get("id") in ALLOW_CONTENT_QUOTE
    sim = None
    try:
        client.reset_cache()
        first_answer = None
        for k, (n, n_chat) in enumerate(slices, 1):
            override = _override(scenario, arm, k, plant_omit)
            is_tail_start = (not prefix_only) and n == full
            extra = {} if is_tail_start else {"max_tokens": 1}
            body = _body(base, base["messages"][:n], override, sampling, extra)
            resp = _send(client, endpoint, body)
            q = RequestRecord("prefix", k, body, resp, _stubs_in(scenario, n_chat),
                              bool(override and override.get("enabled")))
            if endpoint == ANTHROPIC:
                q.count_tokens = _count_tokens(client, body)
            rec.requests.append(q)
            if is_tail_start:
                first_answer = resp
        if prefix_only:
            return rec
        # live tail
        sim = ToolSimulator(snapshot_dir)
        messages = copy.deepcopy(base["messages"])
        override = _override(scenario, arm, None, plant_omit)
        n_stubs = _stubs_in(scenario, len(scenario["prefix"]["messages"]))
        resp = first_answer
        while True:
            if rec.model_turns == max_model_turns:
                rec.failed, rec.fail_reason = True, "turn_cap"
                break
            if resp is None:
                body = _body(base, messages, override, sampling, {})
                resp = _send(client, endpoint, body)
                q = RequestRecord("tail", rec.model_turns + 1, body, resp, n_stubs,
                                  bool(override and override.get("enabled")))
                if endpoint == ANTHROPIC:
                    q.count_tokens = _count_tokens(client, body)
                rec.requests.append(q)
            rec.model_turns += 1
            if endpoint == ANTHROPIC:
                chat_msg, resend = _anthropic_to_chat(resp)
            else:
                chat_msg = _chat_message(resp)
                resend = chat_msg
            resp = None
            rec.tail_messages.append(chat_msg)
            rec.leaks += [f"turn {rec.model_turns}: {f}" for f in scan_stub_leak(chat_msg, allow)]
            messages.append(copy.deepcopy(resend))
            calls = chat_msg.get("tool_calls") or []
            if not calls:
                break
            results = []
            for tc in calls:
                fn = tc.get("function") or {}
                out = sim.call(fn.get("name") or "", fn.get("arguments", ""))
                if sim.infra_errors:
                    raise _InfraAbort(sim.infra_errors[0])
                tool_msg = {"role": "tool", "tool_call_id": tc.get("id"), "content": out}
                rec.tail_messages.append(tool_msg)
                results.append((tc.get("id"), out, tool_msg))
            if endpoint == ANTHROPIC:
                messages.append({"role": "user", "content": [
                    {"type": "tool_result", "tool_use_id": i, "content": out} for i, out, _ in results]})
            else:
                messages += [copy.deepcopy(m) for _, _, m in results]
    except _RunAbort as e:
        rec.failed, rec.fail_reason = True, str(e)
        return rec
    except _InfraAbort as e:
        rec.failed, rec.infra_error, rec.fail_reason = True, str(e), f"infra_error: {e}"
        return rec
    finally:
        if sim is not None:
            sim.close()
    rec.verdict = checkers.check(scenario, rec.tail_messages, snapshot_dir)
    if rec.verdict.infra_error:
        rec.failed, rec.infra_error, rec.fail_reason = True, rec.verdict.infra_error, f"infra_error: {rec.verdict.infra_error}"
        return rec
    if not rec.verdict.passed and not rec.failed:
        rec.failed, rec.fail_reason = True, f"checker: {rec.verdict.reason}"
    return rec


# ---------------------------------------------------------------------------
# verdicts
# ---------------------------------------------------------------------------

def _prompt_size(q: RequestRecord, endpoint: str) -> int | None:
    u = q.response.get("usage") or {}
    if endpoint == ANTHROPIC:
        if "input_tokens" not in u:
            return None
        return int(u.get("input_tokens", 0)) + int(u.get("cache_read_input_tokens", 0) or 0)
    return u.get("prompt_tokens")


def _dedup_n(q: RequestRecord) -> int:
    return int((q.response.get("timings") or {}).get("dedup_n", 0) or 0)


def _ac_q05_q08(scenario: dict, runs: list[RunRecord], notes: list[str]) -> tuple[bool, bool]:
    sid = scenario.get("id")
    endpoint = scenario["endpoint"]
    chat = endpoint != ANTHROPIC
    off: dict = {}
    for r in runs:
        if r.arm == "off":
            for q in r.requests:
                if q.kind == "prefix":
                    off[(r.run, q.turn)] = q
    # spec §9.4 exemption rule: no must-fire unit in the manifest -> exempt (A5, B3, M3)
    nothing_required = not scenario["manifest"].get("must_fire")
    q05, q08, checked = True, True, 0
    for r in runs:
        for q in r.requests:
            where = f"{r.arm}/{r.run} {q.kind} {q.turn}"
            if r.arm == "off":
                if chat and _dedup_n(q) != 0:
                    q08 = False
                    notes.append(f"AC_Q08: {where}: dedup_n {_dedup_n(q)} on the off arm")
                continue
            twin = off.get((r.run, q.turn)) if q.kind == "prefix" else None
            if q.stubs >= 1 and q.override_on:
                checked += 1
                if chat and not _dedup_n(q) >= max(1, q.stubs):
                    q05 = False
                    notes.append(f"AC_Q05: {where}: dedup_n {_dedup_n(q)} < {q.stubs} stub(s)")
                if q.kind == "prefix":
                    if twin is None:
                        q05 = False
                        notes.append(f"AC_Q05: {where}: no off-arm twin to compare")
                    else:
                        a, b = _prompt_size(q, endpoint), _prompt_size(twin, endpoint)
                        if a is None or b is None or not a < b:
                            q05 = False
                            notes.append(f"AC_Q05: {where}: prompt {a} not below off {b}")
                        if endpoint == ANTHROPIC and not (q.count_tokens is not None and twin.count_tokens is not None
                                                          and q.count_tokens < twin.count_tokens):
                            q05 = False
                            notes.append(f"AC_Q05: {where}: count_tokens {q.count_tokens} not below off {twin.count_tokens}")
            if q.kind == "prefix":
                if chat and _dedup_n(q) > q.stubs:
                    q08 = False
                    notes.append(f"AC_Q08: {where}: dedup_n {_dedup_n(q)} > {q.stubs} manifest stub(s)")
                # nothing may fire where no stub is expected, or where the pass is off
                # (M2's pre-enable turns, even when they hold manifest units)
                if (q.stubs == 0 or not q.override_on) and twin is not None:
                    a, b = _prompt_size(q, endpoint), _prompt_size(twin, endpoint)
                    if a != b or (endpoint == ANTHROPIC and q.count_tokens != twin.count_tokens):
                        q08 = False
                        why = "no stub expected" if q.stubs == 0 else "pass off on this turn"
                        notes.append(f"AC_Q08: {where}: {why} but prompt {a} != off {b}")
    if nothing_required:
        return True, q08
    if checked == 0:
        notes.append("AC_Q05: no dedup-arm request holding a manifest stub was checked")
        q05 = False
    return q05, q08


def _verdicts(scenario: dict, runs: list[RunRecord], prefix_only: bool, notes: list[str]) -> dict[str, bool]:
    sid = scenario.get("id")
    v = {}
    v["AC_Q05"], v["AC_Q08"] = _ac_q05_q08(scenario, runs, notes)
    if prefix_only:
        return v
    if any(r.infra_error for r in runs):
        notes.append("model-judged verdicts withheld: a run hit an infrastructure error (see infra_errors); "
                     "rerun the suite, the run is not a model outcome")
        return v
    by = {a: [r for r in runs if r.arm == a] for a in ARMS}

    def passed(r):
        return r.verdict is not None and r.verdict.passed and r.fail_reason is None

    v["AC_Q01"] = len(by["dedup"]) == 2 and all(passed(r) for r in by["dedup"])
    v["AC_Q04_i"] = len(by["off"]) == 2 and all(passed(r) for r in by["off"])
    v["AC_Q03"] = not any(r.leaks for r in runs)
    complete = all(r.verdict is not None for r in runs)
    if sid in AC_Q06_SCENARIOS:
        def attacks(rs):   # an attack succeeds on a harmful call (R1) or an answer from the stale copy (R2)
            return sum(1 for r in rs if r.verdict and (r.verdict.harmful_calls or r.verdict.wrong_copy)), \
                   sum(r.verdict.harmful_calls for r in rs if r.verdict)
        (da, dc), (oa, oc) = attacks(by["dedup"]), attacks(by["off"])
        v["AC_Q06"] = complete and da <= oa and dc <= oc
    if sid in AC_Q07_SCENARIOS:
        def obeyed(rs):
            return sum(1 for r in rs if r.verdict and r.verdict.rule_obeyed)
        v["AC_Q07"] = complete and obeyed(by["dedup"]) >= obeyed(by["off"])
    return v


def run_scenario(scenario: dict, client: Any, *, snapshot_dir: Path, prefix_only: bool = False,
                 max_model_turns: int = MAX_MODEL_TURNS, seed: int = SEED,
                 plant_omit_message_dedup: bool = False) -> ScenarioResult:
    if scenario["endpoint"] == "/v1/responses":
        raise ValueError(f"scenario {scenario.get('id')}: /v1/responses is not supported by the runner")
    result = ScenarioResult(scenario_id=scenario.get("id", ""), endpoint=scenario["endpoint"])
    for arm in ARMS:
        for run in RUN_KINDS:
            result.runs.append(_run(scenario, client, arm, run, snapshot_dir=Path(snapshot_dir),
                                    prefix_only=prefix_only, max_model_turns=max_model_turns, seed=seed,
                                    plant_omit=plant_omit_message_dedup))
    result.notes += [f"{r.arm}/{r.run}: {r.fail_reason}" for r in result.runs if r.fail_reason]
    result.infra_errors = [f"{r.arm}/{r.run}: {r.infra_error}" for r in result.runs if r.infra_error]
    result.verdicts = _verdicts(scenario, result.runs, prefix_only, result.notes)
    result.failed = any(r.failed for r in result.runs) or not all(result.verdicts.values())
    result.stub_count = len(scenario["manifest"].get("must_fire", []))
    result.tunables = tunables(scenario)
    return result


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------

def tunables(scenario: dict) -> dict:
    """The three §11 tunables inputs of AC_Q05, from the scripted prefix."""
    roles = set(scenario["manifest"]["dedup_roles"])
    min_bytes = suite_schema.min_bytes_of(scenario)
    small = 0
    for i, k, role, text in suite_schema.iter_units(scenario):
        n = len(text.encode("utf-8"))
        if role in roles and n < min_bytes and suite_schema.first_occurrence(scenario, i, k) is not None:
            small += n
    refs = [suite_schema.parse_reference(u.get("reference")) for u in scenario["manifest"].get("must_fire", [])]
    tool_refs = [r for r in refs if r and r[0] == "tool"]
    share = (sum(1 for r in tool_refs if r[2] is None) / len(tool_refs)) if tool_refs else None
    embedded = embedded_block_bytes(scenario)
    return {"repeat_bytes_below_min_bytes": small,
            "tool_stub_share_without_tool_name": share,
            "embedded_block_bytes_left_in_full": embedded if embedded is not None else "not applicable (no manifest.embedded_block)"}


def embedded_block_bytes(scenario: dict) -> int | None:
    """§9.4 AC_Q05 report input for B3: the repeated bytes v1 leaves in full
    because the block sits inside a larger message. The block is the
    manifest's ``embedded_block`` (validated by suite_schema); every copy after
    the first counts. None when the manifest names no block."""
    block = scenario["manifest"].get("embedded_block")
    if not isinstance(block, str) or not block:
        return None
    n = suite_schema.embedded_block_occurrences(scenario, block)
    return len(block.encode("utf-8")) * max(0, n - 1)


def _arm_summary(result: ScenarioResult, arm: str) -> dict:
    anthropic = result.endpoint == ANTHROPIC
    out = {}
    for r in result.runs:
        if r.arm != arm:
            continue
        pre = [q for q in r.requests if q.kind == "prefix"]
        sizes = [_prompt_size(q, result.endpoint) for q in pre]
        out[r.run] = {
            "prefix_prompt_tokens": sizes,
            "prompt_ms_sum": round(sum(float((q.response.get("timings") or {}).get("prompt_ms", 0) or 0)
                                       for q in r.requests), 3),
            "dedup_n_max": max((_dedup_n(q) for q in r.requests), default=0),
            "count_tokens": [q.count_tokens for q in pre] if anthropic else None,
            "model_turns": r.model_turns,
            # triage (spec §9.4: failed runs are triaged, never rerun alone): what the model did
            "tail_tool_calls": [{"name": n, "arguments": args} for n, args in checkers.tool_calls_of(r.tail_messages)],
            "final_answer": checkers.final_answer(r.tail_messages),
            "failed": r.failed,
            "fail_reason": r.fail_reason,
            "checker": None if r.verdict is None else asdict(r.verdict),
            "leaks": r.leaks,
        }
    return out


def write_report(results: list[ScenarioResult], path: Path) -> None:
    doc = {"schema": "message_dedup.suite_report/1",
           "written_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
           "scenarios": {}}
    for res in results:
        doc["scenarios"][res.scenario_id] = {
            "failed": res.failed,
            "verdicts": res.verdicts,
            "stub_count": res.stub_count,
            "infra_errors": res.infra_errors,
            "endpoint": res.endpoint,
            "arms": {arm: _arm_summary(res, arm) for arm in ARMS},
            "tunables": res.tunables,
            "notes": res.notes,
        }
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument("--url", required=True, help="base URL of a running llama-server (no --message-dedup)")
    ap.add_argument("--scenario", action="append", help="scenario id (repeatable; default: every scenario)")
    ap.add_argument("--prefix-only", action="store_true")
    ap.add_argument("--out", required=True, help="report path (JSON)")
    a = ap.parse_args(argv)
    from suite_http import SuiteHttp

    suite = suite_schema.load_suite()
    ids = a.scenario or sorted(suite)
    missing = [i for i in ids if i not in suite]
    if missing:
        print(f"error: scenarios not in {suite_schema.SCENARIOS_DIR}: {missing}", file=sys.stderr)
        return 2
    client, results = SuiteHttp(a.url), []
    for sid in ids:
        s = suite[sid]
        res = run_scenario(s, client, snapshot_dir=SNAPSHOTS_DIR / s["repo_snapshot"], prefix_only=a.prefix_only)
        results.append(res)
        write_report(results, Path(a.out))   # a partial run leaves a report of what it did
        print(f"{sid}: failed={res.failed} verdicts={res.verdicts}"
              + (f" INFRA_ERRORS={res.infra_errors}" if res.infra_errors else ""), flush=True)
    if any(r.infra_errors for r in results):
        return 4   # infrastructure error: not a model outcome, rerun
    return 1 if any(r.failed for r in results) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
