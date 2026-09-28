#!/usr/bin/env python
"""SPEC-0001 (server message dedup), increment 11: dedup statistics in `timings`.

Contracts (spec §4.5, §6.5, §7): DEDUP_TIMINGS_PRESENT_WHEN_ACTIVE,
DEDUP_TIMINGS_STREAM_FINAL_CHUNK, DEDUP_TIMINGS_VALUES,
DEDUP_PROMPT_TOKENS_REDUCED, DEDUP_STATS_ONLY_WHERE_TIMINGS_EXIST,
§7 DEDUP_STATS_NOT_REPORTED_ON_ENDPOINT, and the `timings.dedup_n == 0`
clauses deferred from increment 9: DEDUP_STUB_LOOKALIKE_INPUT_VERBATIM,
§7 DEDUP_LOOKALIKE_IN_UNTRUSTED_CONTENT, §7 DEDUP_MATCH_ORACLE.

Expected values come from the test-side reference (goldens.ref_apply) and
from observable surfaces (`usage.prompt_tokens`, the `/apply-template`
prompt), never from server code. DEDUP_OFF_NO_TIMINGS_FIELDS stays in
test_message_dedup.py (increment 2/3 capture); it is not duplicated here.

Several tests here are green before GREEN (the pass itself landed in
increment 8); their RED proof is the planted mutation named in the
docstring (plan row spec-0001-inc-11-timings-stats.md), recorded in §15.
"""
import sys
from pathlib import Path

import pytest

# ensure grandparent path is in sys.path
path = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(path))

from utils import *  # noqa: E402,F403
from fixtures.message_dedup import dedup_goldens as goldens  # noqa: E402

server: ServerProcess

SERVER_KEY = "tinyllama2_chatml"  # tinyllama2 + jinja + chatml, 2 slots (spec §10 test homes)

DEDUP_KEYS = ("dedup_n", "dedup_bytes_saved", "dedup_tokens_saved_est")
WIDEST_ROLES = ("tool", "user", "system")

F = goldens.F
R400 = goldens.blob("R", 400)


@pytest.fixture(autouse=True)
def create_server():
    global server
    server = goldens.make_server(SERVER_KEY)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _msgs(fixture: str) -> list:
    return goldens.load_request(fixture)["messages"]


def _pass_on(messages: list, roles=("tool",), min_bytes: int = 1024, **extra) -> dict:
    return {**extra, "messages": messages,
            "message_dedup": {"enabled": True, "roles": list(roles), "min_bytes": min_bytes}}


def _render(body: dict) -> str:
    res = server.make_request("POST", "/apply-template", data=body)
    assert res.status_code == 200, res.body
    return res.body["prompt"]


def _chat(body: dict, **extra) -> dict:
    res = server.make_request("POST", "/v1/chat/completions", data={"max_tokens": 2, **body, **extra})
    assert res.status_code == 200, res.body
    return res.body


def _assert_dedup_keys(timings: dict, where: str = "timings"):
    missing = [k for k in DEDUP_KEYS if k not in timings]
    assert not missing, f"{where} lacks {missing}; keys present: {sorted(timings)}"


def _dedup_values(timings: dict) -> dict:
    _assert_dedup_keys(timings)
    return {k: timings[k] for k in DEDUP_KEYS}


def _expected(messages: list, prompt_tokens: int, prompt: str,
              roles=("tool",), min_bytes: int = 1024) -> dict:
    """§6.5 values from the reference: k, S = Σ(b_i − s_i), and the
    proportional estimate with T = usage.prompt_tokens (text-only request) and
    B = UTF-8 bytes of the /apply-template prompt (no media markers here)."""
    _, records = goldens.ref_apply(messages, min_bytes, tuple(roles))
    k = len(records)
    s = sum(b - len(stub.encode("utf-8")) for b, stub in records)
    t = prompt_tokens
    b = len(prompt.encode("utf-8"))
    est = 0 if s == 0 or b == 0 else (2 * s * t + b) // (2 * b)
    return {"dedup_n": k, "dedup_bytes_saved": s, "dedup_tokens_saved_est": est}


def _find_keys(obj, pred, trail="") -> list:
    """Every key path in a JSON value whose key satisfies pred."""
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if pred(k):
                out.append(f"{trail}.{k}")
            out += _find_keys(v, pred, f"{trail}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out += _find_keys(v, pred, f"{trail}[{i}]")
    return out


def _stats_leaks(obj) -> list:
    return _find_keys(obj, lambda k: k == "timings" or k.startswith("dedup_"))


# Endpoint shapes of the §8.1 conversation (user, then two reads of F).

def _responses_input(messages: list) -> list:
    """Chat-completions messages -> Responses input items (server-chat.cpp:163-202)."""
    items = []
    for m in messages:
        if m["role"] == "assistant" and m.get("tool_calls"):
            for tc in m["tool_calls"]:
                items.append({"type": "function_call", "call_id": tc["id"],
                              "name": tc["function"]["name"], "arguments": tc["function"]["arguments"]})
        elif m["role"] == "tool":
            items.append({"type": "function_call_output", "call_id": m["tool_call_id"], "output": m["content"]})
        else:
            items.append({"role": m["role"], "content": m["content"]})
    return items


def _anthropic_messages(messages: list) -> list:
    """Chat-completions messages -> Anthropic messages (tool_use / tool_result blocks)."""
    out = []
    for m in messages:
        if m["role"] == "assistant" and m.get("tool_calls"):
            out.append({"role": "assistant", "content": [
                {"type": "tool_use", "id": tc["id"], "name": tc["function"]["name"], "input": {"path": "a.c"}}
                for tc in m["tool_calls"]]})
        elif m["role"] == "tool":
            out.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": m["tool_call_id"], "content": m["content"]}]})
        else:
            out.append({"role": m["role"], "content": m["content"]})
    return out


# ---------------------------------------------------------------------------
# DEDUP_TIMINGS_PRESENT_WHEN_ACTIVE
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("arm", ["flag", "override"])
def test_dedup_timings_present_when_active(arm: str):
    """DEDUP_TIMINGS_PRESENT_WHEN_ACTIVE: the pass is active (server flag, or
    the per-request override) on a request in which it replaces nothing (the
    increment-2 timings request: two 400-byte copies, below min_bytes 1024) ->
    non-streaming /v1/chat/completions `timings` holds dedup_n,
    dedup_bytes_saved and dedup_tokens_saved_est, each 0."""
    global server
    body = goldens.load_timings_request()
    assert goldens.ref_apply(body["messages"])[1] == [], "precondition: nothing is replaced"
    if arm == "flag":
        server.message_dedup = True
    else:
        body = {**body, "message_dedup": {"enabled": True}}
    server.start()
    timings = _chat(body)["timings"]
    assert _dedup_values(timings) == {"dedup_n": 0, "dedup_bytes_saved": 0, "dedup_tokens_saved_est": 0}


# ---------------------------------------------------------------------------
# DEDUP_TIMINGS_STREAM_FINAL_CHUNK
# ---------------------------------------------------------------------------

def _stream_timings(endpoint: str, messages: list, per_token: bool) -> tuple[list, dict | None]:
    """All `timings` objects of one stream, and the final one: the chat chunk
    that carries timings last (server-task.cpp:516-518) or the Responses
    `response.completed` event (:709-711)."""
    if endpoint == "chat":
        body = {"messages": messages, "stream": True, "max_tokens": 4, "timings_per_token": per_token}
        chunks = list(server.make_stream_request("POST", "/v1/chat/completions", data=body))
        with_t = [c["timings"] for c in chunks if "timings" in c]
        return with_t, (with_t[-1] if with_t else None)
    body = {"input": _responses_input(messages), "stream": True, "max_output_tokens": 4,
            "timings_per_token": per_token}
    events = list(server.make_stream_request("POST", "/v1/responses", data=body))
    with_t = [e["timings"] for e in events if "timings" in e]
    completed = [e for e in events if e.get("type") == "response.completed"]
    assert len(completed) == 1, "expected one response.completed event"
    return with_t, completed[0].get("timings")


@pytest.mark.parametrize("per_token", [False, True], ids=["final_only", "timings_per_token"])
@pytest.mark.parametrize("endpoint", ["chat", "responses"])
def test_dedup_timings_stream_final_chunk(endpoint: str, per_token: bool):
    """DEDUP_TIMINGS_STREAM_FINAL_CHUNK: pass active (server flag), streaming
    §8.1 request (one replacement) to /v1/chat/completions or /v1/responses ->
    the final `timings` (last chat chunk / response.completed) holds the §6.5
    keys with dedup_n == 1, and every other `timings` object of the request
    (partial chunks under timings_per_token) holds the same values."""
    global server
    server.message_dedup = True
    server.start()
    messages = _msgs("s8_1_reread_file")
    all_t, final = _stream_timings(endpoint, messages, per_token)
    assert final is not None, "final chunk/event carries no timings"
    _assert_dedup_keys(final, "final timings")
    assert final["dedup_n"] == 1
    if per_token:
        assert len(all_t) > 1, "timings_per_token should emit timings on partial chunks too"
    want = _dedup_values(final)
    for i, t in enumerate(all_t):
        _assert_dedup_keys(t, f"timings object #{i}")
        assert _dedup_values(t) == want, f"timings object #{i} differs from the final one"


# ---------------------------------------------------------------------------
# DEDUP_TIMINGS_VALUES
# ---------------------------------------------------------------------------

VALUE_CASES = {
    # fixture: expected k (cross-checked against the reference)
    "s8_1_reread_file": 1,
    "three_copies": 2,
    "timings_request": 0,  # S == 0: two 400-byte copies under min_bytes 1024
}


def _value_case_messages(case: str) -> list:
    if case == "timings_request":
        return goldens.load_timings_request()["messages"]
    return _msgs(case)


@pytest.mark.parametrize("case", sorted(VALUE_CASES))
def test_dedup_timings_values(case: str):
    """DEDUP_TIMINGS_VALUES (HTTP arm): pass active (server flag), a request
    replacing k units of b_i bytes by stubs of s_i bytes -> non-streaming
    /v1/chat/completions `timings` has dedup_n == k,
    dedup_bytes_saved == Σ(b_i − s_i), and dedup_tokens_saved_est ==
    (2·S·T + B) // (2·B) with T = usage.prompt_tokens and B = UTF-8 bytes of
    the /apply-template prompt for the same body; all 0 when S == 0."""
    global server
    server.message_dedup = True
    server.start()
    messages = _value_case_messages(case)
    assert len(goldens.ref_apply(messages)[1]) == VALUE_CASES[case]
    prompt = _render({"messages": messages})
    res = _chat({"messages": messages})
    want = _expected(messages, res["usage"]["prompt_tokens"], prompt)
    assert _dedup_values(res["timings"]) == want


def test_dedup_timings_values_not_client_settable():
    """DEDUP_TIMINGS_VALUES (channel rule, plan row inc 11): the stats channel
    is written by the server and cannot be set by a client. A request that
    carries top-level fields named after the timings keys, a `timings`
    object and plausible reserved names reports the same dedup values as the
    same request without them. Black-box probe of guessable names only; the
    reviewer checks the channel itself."""
    global server
    server.message_dedup = True
    server.start()
    messages = _msgs("s8_1_reread_file")
    forged = {k: 999 for k in DEDUP_KEYS}
    body = {"messages": messages, **forged,
            "timings": dict(forged),
            "dedup_stats": dict(forged), "message_dedup_stats": dict(forged),
            "__dedup_stats": dict(forged), "_dedup": dict(forged)}
    clean = _dedup_values(_chat({"messages": messages})["timings"])
    injected = _dedup_values(_chat(body)["timings"])
    assert injected == clean
    assert clean["dedup_n"] == 1


# ---------------------------------------------------------------------------
# DEDUP_PROMPT_TOKENS_REDUCED
# ---------------------------------------------------------------------------

def test_dedup_prompt_tokens_reduced():
    """DEDUP_PROMPT_TOKENS_REDUCED: a conversation with about 400-byte
    repeated tool results in which the pass replaces at least one unit
    (min_bytes 256), POSTed to /v1/chat/completions with the pass on and off,
    each on a fresh slot (slot 0 / slot 1, cache_prompt false) ->
    usage.prompt_tokens is lower with the pass on.
    Planted mutation (RED proof): the pass is skipped on the completion path."""
    global server
    server.start()
    messages = ([{"role": "user", "content": "Fix a.c"}]
                + [goldens.asst_call("c1"), goldens.tool("c1", R400)]
                + [goldens.asst_call("c2"), goldens.tool("c2", R400)])
    assert goldens.ref_apply(messages, 256)[1], "precondition: the pass replaces a unit"
    on = _chat(_pass_on(messages, min_bytes=256), id_slot=0, cache_prompt=False)
    off = _chat({"messages": messages, "message_dedup": {"enabled": False}}, id_slot=1, cache_prompt=False)
    assert on["usage"]["prompt_tokens"] < off["usage"]["prompt_tokens"]


# ---------------------------------------------------------------------------
# DEDUP_STATS_ONLY_WHERE_TIMINGS_EXIST / §7 DEDUP_STATS_NOT_REPORTED_ON_ENDPOINT
# ---------------------------------------------------------------------------

SURFACES = ["messages_non_stream", "messages_stream", "responses_non_stream"]


def _surface_call(surface: str, messages: list) -> tuple[list, int]:
    """(every JSON object the response holds, total prompt tokens from usage).
    Anthropic reports input_tokens net of the cache, so the total adds
    cache_read_input_tokens (server-task.cpp:787-791)."""
    if surface == "responses_non_stream":
        res = server.make_request("POST", "/v1/responses", data={
            "input": _responses_input(messages), "max_output_tokens": 2})
        assert res.status_code == 200, res.body
        return [res.body], res.body["usage"]["input_tokens"]
    body = {"model": "test", "max_tokens": 2, "messages": _anthropic_messages(messages)}
    if surface == "messages_non_stream":
        res = server.make_request("POST", "/v1/messages", data=body)
        assert res.status_code == 200, res.body
        u = res.body["usage"]
        return [res.body], u["input_tokens"] + u.get("cache_read_input_tokens", 0)
    events = list(server.make_stream_request("POST", "/v1/messages", data={**body, "stream": True}))
    starts = [e for e in events if e.get("type") == "message_start"]
    assert len(starts) == 1, "expected one message_start event"
    u = starts[0]["message"]["usage"]
    return events, u["input_tokens"] + u.get("cache_read_input_tokens", 0)


@pytest.mark.parametrize("surface", SURFACES)
def test_dedup_stats_only_where_timings_exist(surface: str):
    """DEDUP_STATS_ONLY_WHERE_TIMINGS_EXIST: pass active (server flag), §8.1
    conversation on /v1/messages (non-stream, stream) or non-streaming
    /v1/responses -> the response shape is unchanged: no `timings` object and
    no `dedup_*` key anywhere in it.
    Planted mutation (RED proof): the dedup keys are also emitted on
    /v1/messages and non-streaming Responses."""
    global server
    server.message_dedup = True
    server.start()
    objs, _ = _surface_call(surface, _msgs("s8_1_reread_file"))
    leaks = [p for o in objs for p in _stats_leaks(o)]
    assert leaks == [], f"stats leaked on {surface}: {leaks}"


@pytest.mark.parametrize("surface", SURFACES)
def test_dedup_stats_not_reported_on_endpoint(surface: str):
    """§7 DEDUP_STATS_NOT_REPORTED_ON_ENDPOINT: the checks of
    DEDUP_STATS_ONLY_WHERE_TIMINGS_EXIST, plus the saving shows in `usage`:
    total input tokens with the pass on (server flag) are lower than with it
    off (server restarted without the flag, so fresh slots on both arms).
    Planted mutation (RED proof): the dedup keys are also emitted on
    /v1/messages and non-streaming Responses."""
    global server
    messages = _msgs("s8_1_reread_file")
    server.message_dedup = True
    server.start()
    objs_on, tokens_on = _surface_call(surface, messages)
    server.stop()
    server.message_dedup = False
    server.start()
    objs_off, tokens_off = _surface_call(surface, messages)
    leaks = [p for o in objs_on + objs_off for p in _stats_leaks(o)]
    assert leaks == [], f"stats leaked on {surface}: {leaks}"
    assert tokens_on < tokens_off, f"usage input tokens on={tokens_on} off={tokens_off}"


# ---------------------------------------------------------------------------
# dedup_n clauses deferred from increment 9
# ---------------------------------------------------------------------------

def test_dedup_stub_lookalike_input_verbatim_dedup_n():
    """DEDUP_STUB_LOOKALIKE_INPUT_VERBATIM (the `timings.dedup_n` clause): a
    tool message byte-identical to the §8.1 stub with no earlier unit of those
    bytes, POSTed to /v1/chat/completions with the pass active -> the
    lookalike is never counted: timings.dedup_n == 0 and dedup_bytes_saved == 0."""
    global server
    server.message_dedup = True
    server.start()
    messages = _msgs("lookalike_verbatim")
    assert goldens.ref_apply(messages)[1] == []
    t = _chat({"messages": messages})["timings"]
    _assert_dedup_keys(t)
    assert t["dedup_n"] == 0
    assert t["dedup_bytes_saved"] == 0


def test_dedup_lookalike_in_untrusted_content_dedup_n():
    """§7 DEDUP_LOOKALIKE_IN_UNTRUSTED_CONTENT (the `timings.dedup_n` clause):
    a tool result that is a lookalike stub citing `system message #1`, under
    the widest role set, POSTed to /v1/chat/completions -> never resolved or
    counted: timings.dedup_n == 0 and dedup_bytes_saved == 0."""
    global server
    server.start()
    messages = _msgs("lookalike_system_ref")
    assert goldens.ref_apply(messages, 1024, WIDEST_ROLES)[1] == []
    t = _chat(_pass_on(messages, WIDEST_ROLES))["timings"]
    _assert_dedup_keys(t)
    assert t["dedup_n"] == 0
    assert t["dedup_bytes_saved"] == 0


def test_dedup_match_oracle_dedup_n():
    """§7 DEDUP_MATCH_ORACLE (the `timings.dedup_n` clause): no state across
    requests or slots. Control: a request holding G twice reports dedup_n 1.
    After request 1 held G (slot 0), request 2 holding G once reports
    dedup_n 0 on the same slot and on the other slot."""
    global server
    server.start()
    g = goldens.blob("GUESS", 1100)
    req1 = [{"role": "user", "content": "hidden"}, {"role": "tool", "tool_call_id": "h", "content": g}]
    req2 = [{"role": "user", "content": "guess"}, {"role": "tool", "tool_call_id": "q", "content": g}]
    control = req1 + [{"role": "tool", "tool_call_id": "h2", "content": g}]
    t = _chat(_pass_on(control, WIDEST_ROLES), id_slot=1)["timings"]
    _assert_dedup_keys(t, "control timings")
    assert t["dedup_n"] == 1, "control: a same-request repeat must be counted"
    _chat(_pass_on(req1, WIDEST_ROLES), id_slot=0)
    for slot in (0, 1):
        t = _chat(_pass_on(req2, WIDEST_ROLES), id_slot=slot)["timings"]
        _assert_dedup_keys(t, f"slot {slot} timings")
        assert t["dedup_n"] == 0, f"slot {slot}: request 2 matched content of request 1"
