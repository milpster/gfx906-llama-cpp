#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx2[http2,brotli,zstd]==2.12.0",
#     "pydantic>=2.11,<3",
# ]
# ///

# --- How to run ---
# 1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Start llama-server with one slot and context checkpoints enabled.
# 3. Run: uv run --script bench/checkpoint-eviction-probe.py [PORT]
# ------------------

from __future__ import annotations

import hashlib
import socket
import sys
from dataclasses import dataclass
from typing import ClassVar, Final, Literal

import httpx2
from pydantic import BaseModel, ConfigDict

Role = Literal["system", "user", "assistant"]

MAX_TOKENS: Final = 32
SYSTEM_PROMPT: Final = " ".join(
    f"Rule {index}: answer precisely, preserve prior facts, and use concise technical language."
    for index in range(1, 41)
)
USER_TURNS: Final = (
    "Define a deterministic cache in two sentences.",
    "Give one practical use for that cache.",
    "Explain how a cache key should be chosen.",
    "Describe one safe eviction policy.",
    "Name one metric for cache effectiveness.",
    "Summarize the design in one sentence.",
)
EDITED_TURN: Final = "Replace turn four: describe a checkpoint-based rewind policy."

_LIMITS: Final = httpx2.Limits(
    max_connections=50,
    max_keepalive_connections=20,
    keepalive_expiry=30.0,
)
_TIMEOUT: Final = httpx2.Timeout(connect=5.0, read=300.0, write=10.0, pool=10.0)
_SOCKET_OPTIONS: Final = [(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)]


class ProbeResponseError(RuntimeError):
    detail: str

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class Message(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    role: Role
    content: str


class ResponseMessage(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    content: str


class Choice(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    message: ResponseMessage


class Timings(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    prompt_n: int
    cache_n: int = 0
    prompt_ms: float


class ChatResponse(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    choices: tuple[Choice, ...]
    timings: Timings


class TurnMetrics(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    prompt_n: int
    cache_n: int
    prompt_ms: float
    output_sha: str


class ProbeSummary(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    warm_prompt_n: tuple[int, ...]
    warm_cache_n: tuple[int, ...]
    edit: TurnMetrics
    regenerate: TurnMetrics
    regenerate_matches: bool


@dataclass(frozen=True, slots=True)
class Completion:
    content: str
    metrics: TurnMetrics


def log_response(response: httpx2.Response) -> None:
    print(
        f"HTTP {response.request.method} {response.request.url.path} -> {response.status_code}",
        file=sys.stderr,
    )


def create_client(base_url: str) -> httpx2.Client:
    transport = httpx2.HTTPTransport(
        http2=True,
        retries=3,
        limits=_LIMITS,
        socket_options=_SOCKET_OPTIONS,
    )
    return httpx2.Client(
        base_url=base_url,
        transport=transport,
        timeout=_TIMEOUT,
        follow_redirects=True,
        event_hooks={"response": [log_response]},
    )


def complete(
    client: httpx2.Client,
    messages: tuple[Message, ...],
    max_tokens: int,
) -> Completion:
    response = client.post(
        "/v1/chat/completions",
        json={
            "messages": [message.model_dump() for message in messages],
            "max_tokens": max_tokens,
            "temperature": 0.0,
            "top_k": 1,
            "seed": 0,
            "cache_prompt": True,
            "id_slot": 0,
            "stream": False,
        },
    )
    _ = response.raise_for_status()
    parsed = ChatResponse.model_validate(response.json())
    if len(parsed.choices) != 1:
        raise ProbeResponseError(f"expected one choice, received {len(parsed.choices)}")

    content = parsed.choices[0].message.content
    timings = parsed.timings
    return Completion(
        content=content,
        metrics=TurnMetrics(
            prompt_n=timings.prompt_n,
            cache_n=timings.cache_n,
            prompt_ms=timings.prompt_ms,
            output_sha=hashlib.sha256(content.encode()).hexdigest()[:12],
        ),
    )


def run_probe(client: httpx2.Client) -> ProbeSummary:
    messages = (Message(role="system", content=SYSTEM_PROMPT),)
    states: list[tuple[Message, ...]] = []
    warm: list[TurnMetrics] = []

    for user_text in USER_TURNS:
        request_messages = messages + (Message(role="user", content=user_text),)
        completion = complete(client, request_messages, MAX_TOKENS)
        messages = request_messages + (Message(role="assistant", content=completion.content),)
        states.append(messages)
        warm.append(completion.metrics)

    edited_request = states[2] + (Message(role="user", content=EDITED_TURN),)
    edited = complete(client, edited_request, MAX_TOKENS)
    regenerated = complete(client, edited_request, MAX_TOKENS)

    return ProbeSummary(
        warm_prompt_n=tuple(result.prompt_n for result in warm),
        warm_cache_n=tuple(result.cache_n for result in warm),
        edit=edited.metrics,
        regenerate=regenerated.metrics,
        regenerate_matches=edited.content == regenerated.content,
    )


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8018
    with create_client(f"http://127.0.0.1:{port}") as client:
        print(run_probe(client).model_dump_json())


if __name__ == "__main__":
    main()
