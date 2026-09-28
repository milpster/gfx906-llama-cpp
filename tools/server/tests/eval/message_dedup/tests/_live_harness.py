"""Shared helpers for the SPEC-0001 increment-18 (and 16) suite tests.

Synthetic only: the mini scenarios are built from the increment-14 hand-made
fixture `fixtures/valid_scenario.json`; the mini snapshot
`fixtures/snapshots/mini-snapshot-0001/` is byte-equal to its first reads
(see the PROVENANCE.md there). Written by `orchestrator.49.tester.g2`.
"""
from __future__ import annotations

import copy
import json

from _paths import FIXTURES, load  # also puts SUITE_DIR and SERVER_TESTS_DIR on sys.path

import runner  # noqa: E402
from suite_http import SuiteHttp  # noqa: E402

MINI_SNAPSHOT = FIXTURES / "snapshots" / "mini-snapshot-0001"
STUB_PREFIX = "[duplicate content omitted"


# ---------------------------------------------------------------------------
# mini scenarios
# ---------------------------------------------------------------------------

def _trimmed_valid() -> dict:
    """The increment-14 valid mini scenario cut to fit tinyllama2's 2048-token
    slot: system, user, read alpha.c, re-read alpha.c (the must-fire repeat,
    message 5). The beta.c messages are dropped; must_not_fire is empty."""
    s = load("valid_scenario.json")
    msgs = s["prefix"]["messages"]
    s["prefix"]["messages"] = [msgs[i] for i in (0, 1, 2, 3, 6, 7)]
    s["manifest"]["must_fire"] = [{"message": 5, "part": None, "reference": "tool result #1 (read_file)"}]
    s["manifest"]["must_not_fire"] = []
    return s


def mini_chat_scenario() -> dict:
    """A1-shaped mini (/v1/chat/completions) with two prefix turns:
    messages[:4] (no repeat yet) and [:6] (holds the must-fire repeat)."""
    s = _trimmed_valid()
    s["turns"] = [4, 6]
    return s


def mini_server_scenario() -> dict:
    """A1-shaped mini for the tinyllama2 server tests (its slot holds 2048
    tokens): read story.txt (1105 bytes, about 365 tinyllama2 tokens), read it
    again unchanged (the must-fire repeat, message 5). Two prefix turns:
    messages[:4] (no repeat yet) and [:6] (holds the repeat)."""
    s = _trimmed_valid()
    story = (MINI_SNAPSHOT / "story.txt").read_text(encoding="utf-8")
    msgs = s["prefix"]["messages"]
    for i in (2, 4):
        msgs[i]["tool_calls"][0]["function"]["arguments"] = json.dumps({"path": "story.txt"})
    msgs[3]["content"] = story
    msgs[5]["content"] = story
    s["manifest"]["checker"] = {"kind": "exact_answer", "answer": "dog"}
    s["turns"] = [4, 6]
    return s


def _to_anthropic(chat_messages: list[dict]) -> dict:
    system = None
    out: list[dict] = []
    for m in chat_messages:
        role = m["role"]
        if role == "system":
            system = m["content"]
        elif role == "user":
            out.append({"role": "user", "content": m["content"]})
        elif role == "assistant":
            blocks = []
            if m.get("content"):
                blocks.append({"type": "text", "text": m["content"]})
            for tc in m.get("tool_calls") or []:
                blocks.append({"type": "tool_use", "id": tc["id"], "name": tc["function"]["name"],
                               "input": json.loads(tc["function"]["arguments"])})
            out.append({"role": "assistant", "content": blocks})
        elif role == "tool":
            out.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": m["tool_call_id"], "content": m["content"]}]})
    body = {"messages": out, "max_tokens": 16}
    if system is not None:
        body["system"] = system
    return body


def mini_anthropic_scenario() -> dict:
    """A4-shaped mini: endpoint /v1/messages. `prefix` stays the chat twin (the
    static checks and /apply-template need it); `anthropic_prefix` is the
    Anthropic body the runner sends. One prefix turn (the whole prefix)."""
    s = mini_server_scenario()
    del s["turns"]
    s["id"] = "A4"
    s["endpoint"] = "/v1/messages"
    s["anthropic_prefix"] = _to_anthropic(s["prefix"]["messages"])
    return s


# ---------------------------------------------------------------------------
# clients
# ---------------------------------------------------------------------------

def tool_call_msg(turn: int, name: str = "read_file", args: dict | None = None) -> dict:
    args = {"path": "alpha.c"} if args is None else args
    return {"role": "assistant", "content": "", "tool_calls": [{
        "id": f"tail_{turn}", "type": "function",
        "function": {"name": name, "arguments": json.dumps(args)}}]}


def answer_msg(text: str) -> dict:
    return {"role": "assistant", "content": text}


class ScriptedClient:
    """Recorded/scripted model responses; no server. `script(turn)` returns
    the assistant message of live-tail model turn `turn` (1-based). The turn
    is derived from the request itself (messages beyond the scripted prefix),
    so the client is stateless across runs and arms. Requests that are a
    strict slice of the prefix (prefix turns) get an empty answer."""

    def __init__(self, scenario: dict, script):
        self.prefix_len = len(scenario["prefix"]["messages"])
        self.script = script
        self.bodies: list[dict] = []
        self.resets = 0

    def _response(self, body: dict) -> dict:
        self.bodies.append(copy.deepcopy(body))
        msgs = body.get("messages", [])
        n = len(msgs)
        if n < self.prefix_len:
            msg = answer_msg("")
        else:
            extra = msgs[self.prefix_len:]
            turn = 1 + sum(1 for m in extra if m.get("role") == "assistant")
            msg = self.script(turn)
        dedup = 1 if body.get("message_dedup", {}).get("enabled") else 0
        ptoks = 1000 - 400 * dedup
        return {"choices": [{"index": 0, "message": msg,
                             "finish_reason": "tool_calls" if msg.get("tool_calls") else "stop"}],
                "usage": {"prompt_tokens": ptoks, "completion_tokens": 1, "total_tokens": ptoks + 1},
                "timings": {"cache_n": 0, "prompt_n": ptoks, "prompt_ms": 1.0,
                            "dedup_n": dedup, "dedup_bytes_saved": 1000 * dedup}}

    def chat(self, body: dict) -> dict:
        return self._response(body)

    def messages(self, body: dict) -> dict:
        raise AssertionError("mini chat scenario must not hit /v1/messages")

    def count_tokens_chat(self, body: dict) -> int:
        return 600 if body.get("message_dedup", {}).get("enabled") else 1000

    def count_tokens_anthropic(self, body: dict) -> int:
        return self.count_tokens_chat(body)

    def reset_cache(self) -> None:
        self.resets += 1


class CountingHttpClient(SuiteHttp):
    """SuiteHttp against a real test server; records every generation
    request that reaches the server (chat and messages)."""

    def __init__(self, base_url: str):
        super().__init__(base_url, timeout=600)
        self.generation_bodies: list[tuple[str, dict]] = []

    def chat(self, body: dict) -> dict:
        self.generation_bodies.append(("/v1/chat/completions", copy.deepcopy(body)))
        return super().chat(body)

    def messages(self, body: dict) -> dict:
        self.generation_bodies.append(("/v1/messages", copy.deepcopy(body)))
        return super().messages(body)


def start_tinyllama(slot_dir, server_key: str = "tinyllama2_chatml"):
    """tinyllama2 + chatml, ONE slot (so a stale cache from the previous run
    is visible as cache_n > 0), --slot-save-path set so slot erase is
    available, started WITHOUT --message-dedup (the dedup arm enables the
    pass through the per-request override). Returns (server, client)."""
    from fixtures.message_dedup import dedup_goldens as goldens

    server = goldens.make_server(server_key)
    server.n_slots = 1
    server.server_slots = True  # the preset passes --no-slots, which disables /slots actions
    server.slot_save_path = str(slot_dir)
    server.start()
    client = CountingHttpClient(f"http://{server.server_host}:{server.server_port}")
    return server, client


def run_mini(scenario: dict, client, **kw) -> "runner.ScenarioResult":
    kw.setdefault("snapshot_dir", MINI_SNAPSHOT)
    return runner.run_scenario(scenario, client, **kw)
