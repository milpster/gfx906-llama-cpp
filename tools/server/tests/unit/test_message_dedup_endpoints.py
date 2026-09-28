#!/usr/bin/env python
"""SPEC-0001 (server message dedup), increment 10: every JSON chat endpoint.

The override `message_dedup` must reach the pass, and be validated, on all
seven JSON chat endpoints of spec §4.0: /v1/chat/completions, /v1/responses,
/v1/messages, /apply-template and the three count-tokens routes.
/v1/chat/completions and /apply-template are covered for the 400 contract by
test_message_dedup.py::test_dedup_override_invalid_returns_400; this module
covers the other five.

RED today: the Anthropic arms. server_chat_convert_anthropic_to_oai forwards
only an allowlist of top-level fields (server-chat.cpp:593), so
`message_dedup` is dropped before the parser sees it.

Conformance (green before GREEN; each names the planted mutation that must
turn it red): the chat and Responses arms, and
DEDUP_COUNT_TOKENS_MATCHES_COMPLETION.
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

SERVER_KEY = "tinyllama2_chatml"  # tinyllama2 + jinja + chatml (spec §10 test homes)

F = goldens.F  # 1100 bytes


@pytest.fixture(autouse=True)
def create_server():
    global server
    server = goldens.make_server(SERVER_KEY)


# ---------------------------------------------------------------------------
# One conversation (two identical 1100-byte tool results), three wire shapes.
# ---------------------------------------------------------------------------

def _chat_body(content: str = F) -> dict:
    return {"messages": [
        {"role": "user", "content": "Fix a.c"},
        goldens.asst_call("c1"), goldens.tool("c1", content),
        goldens.asst_call("c2"), goldens.tool("c2", content),
    ]}


def _responses_body(content: str = F) -> dict:
    def call(cid):
        return {"type": "function_call", "call_id": cid, "name": "read_file",
                "arguments": "{\"path\":\"a.c\"}"}

    def out(cid):
        return {"type": "function_call_output", "call_id": cid, "output": content}

    return {"model": "any", "input": [
        {"role": "user", "content": "Fix a.c"},
        call("c1"), out("c1"), call("c2"), out("c2"),
    ]}


def _anthropic_body(content: str = F) -> dict:
    def use(cid):
        return {"role": "assistant", "content": [
            {"type": "tool_use", "id": cid, "name": "read_file", "input": {"path": "a.c"}}]}

    def result(cid):
        return {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": cid, "content": content}]}

    return {"model": "any", "max_tokens": 8, "messages": [
        {"role": "user", "content": "Fix a.c"},
        use("c1"), result("c1"), use("c2"), result("c2"),
    ]}


COUNT_ROUTES = {
    "chat": ("/v1/chat/completions/input_tokens", _chat_body),
    "responses": ("/v1/responses/input_tokens", _responses_body),
    "anthropic": ("/v1/messages/count_tokens", _anthropic_body),
}


def _input_tokens(route: str, body: dict) -> int:
    res = server.make_request("POST", route, data=body)
    assert res.status_code == 200, f"{route}: status {res.status_code}, body {res.body}"
    return res.body["input_tokens"]


@pytest.mark.parametrize("arm", sorted(COUNT_ROUTES))
def test_dedup_override_honored_on_all_endpoints(arm: str):
    """DEDUP_OVERRIDE_HONORED_ON_ALL_ENDPOINTS: server without --message-dedup;
    the same two-identical-1100-byte-tool-result conversation as a chat body,
    a Responses body (`function_call_output` items) and an Anthropic body
    (`tool_result` blocks); on each count-tokens route, `input_tokens` with
    `"message_dedup": {"enabled": true}` is lower than without it.
    RED today: anthropic (the converter allowlist drops the field).
    Conformance: chat (mutation: handle_count_tokens erases `message_dedup`
    from the body before calling the parser) and responses (mutation:
    server_chat_convert_responses_to_chatcmpl erases `message_dedup`)."""
    global server
    server.start()
    route, make_body = COUNT_ROUTES[arm]
    body = make_body()
    without = _input_tokens(route, body)
    with_override = _input_tokens(route, {**body, "message_dedup": {"enabled": True}})
    assert with_override < without, (
        f"{route}: input_tokens with the override ({with_override}) is not below "
        f"the value without it ({without}); the override did not reach the pass")


# ---------------------------------------------------------------------------
# DEDUP_OVERRIDE_INVALID_RETURNS_400 on the five endpoints not covered in
# test_message_dedup.py.
# ---------------------------------------------------------------------------

def _hi_chat() -> dict:
    return {"messages": [{"role": "user", "content": "hi"}], "max_tokens": 2}


def _hi_responses() -> dict:
    return {"model": "any", "input": [{"role": "user", "content": "hi"}], "max_output_tokens": 2}


def _hi_anthropic() -> dict:
    return {"model": "any", "max_tokens": 2, "messages": [{"role": "user", "content": "hi"}]}


# endpoint -> (route, base body); /v1/chat/completions and /apply-template live
# in test_message_dedup.py::test_dedup_override_invalid_returns_400
INVALID_ENDPOINTS = {
    "responses": ("/v1/responses", _hi_responses),
    "messages": ("/v1/messages", _hi_anthropic),
    "chat_input_tokens": ("/v1/chat/completions/input_tokens", _hi_chat),
    "responses_input_tokens": ("/v1/responses/input_tokens", _hi_responses),
    "messages_count_tokens": ("/v1/messages/count_tokens", _hi_anthropic),
}

INVALID_OVERRIDES = {
    # §8.3 body (roles holding "assistant")
    "roles_assistant": {"enabled": True, "roles": ["tool", "assistant"]},
    "min_bytes_0": {"min_bytes": 0},
    "enabled_not_bool": {"enabled": "yes"},
    "not_an_object": "on",
    "unknown_key_null": {"enabled": True, "bogus": None},
}

ANTHROPIC_ENDPOINTS = {"messages", "messages_count_tokens"}


def _slot_tasks() -> dict:
    res = server.make_request("GET", "/slots")
    assert res.status_code == 200
    return {s["id"]: s.get("id_task") for s in res.body}


@pytest.mark.parametrize("case", sorted(INVALID_OVERRIDES))
@pytest.mark.parametrize("endpoint", sorted(INVALID_ENDPOINTS))
def test_dedup_override_invalid_returns_400(endpoint: str, case: str):
    """DEDUP_OVERRIDE_INVALID_RETURNS_400 (also §7 DEDUP_OVERRIDE_INVALID), on
    /v1/responses, /v1/messages and the three count-tokens routes: a
    §6.2-invalid `message_dedup` gives HTTP 400 with the §6.6 body whose
    message names `message_dedup`, and no task is queued (no slot's id_task
    changes). The `roles_assistant` case on `messages` is the §8.3 example.
    RED today: messages and messages_count_tokens (the Anthropic converter
    drops the field, so the request succeeds with 200).
    Conformance: responses and responses_input_tokens (mutation:
    server_chat_convert_responses_to_chatcmpl erases `message_dedup`),
    chat_input_tokens (mutation: handle_count_tokens erases `message_dedup`
    before calling the parser)."""
    global server
    server.server_slots = True
    server.start()
    # give every slot a task id first, so an unchanged id_task is meaningful
    for _ in range(2):
        warm = server.make_request("POST", "/v1/chat/completions", data=_hi_chat())
        assert warm.status_code == 200
    before = _slot_tasks()
    route, make_body = INVALID_ENDPOINTS[endpoint]
    body = {**make_body(), "message_dedup": INVALID_OVERRIDES[case]}
    res = server.make_request("POST", route, data=body)
    assert res.status_code == 400, f"{route}: status {res.status_code}, body {res.body}"
    err = res.body.get("error", {}) if isinstance(res.body, dict) else {}
    assert err.get("code") == 400
    assert err.get("type") == "invalid_request_error"
    assert "message_dedup" in err.get("message", "")
    if endpoint == "messages" and case == "roles_assistant":
        assert "assistant" in err["message"], "§8.3: the message names the rule broken"
    assert _slot_tasks() == before, "an invalid override must not queue a task"


# ---------------------------------------------------------------------------
# DEDUP_COUNT_TOKENS_MATCHES_COMPLETION
# ---------------------------------------------------------------------------

U400 = goldens.blob("U", 400)


def test_dedup_count_tokens_matches_completion():
    """DEDUP_COUNT_TOKENS_MATCHES_COMPLETION: with the pass active (override,
    `min_bytes: 256`, about 400-byte units), R POSTed to
    /v1/chat/completions/input_tokens and to /v1/chat/completions on a fresh
    slot: `input_tokens` equals `usage.prompt_tokens`.
    Conformance (green since increment 8 wired the shared parser); mutation:
    the pass is skipped when handle_count_tokens calls the parser, so the
    count-tokens route reports the unstubbed prompt."""
    global server
    server.start()
    base = _chat_body(U400)
    r = {**base, "message_dedup": {"enabled": True, "min_bytes": 256}}
    # the pass must actually change the prompt, or equality proves nothing
    unstubbed = _input_tokens("/v1/chat/completions/input_tokens", {**base, "message_dedup": {"enabled": False}})
    counted = _input_tokens("/v1/chat/completions/input_tokens", r)
    assert counted < unstubbed, "precondition: the pass must stub the repeated 400-byte unit"
    res = server.make_request("POST", "/v1/chat/completions", data={
        **r, "max_tokens": 2, "id_slot": 0, "cache_prompt": False})
    assert res.status_code == 200, res.body
    assert res.body["usage"]["prompt_tokens"] == counted
