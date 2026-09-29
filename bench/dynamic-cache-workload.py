#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx2[http2,brotli,zstd]",
#     "pydantic>=2,<3",
# ]
# ///

# How to run:
# 1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run: uv run bench/dynamic-cache-workload.py PORT
# 3. Set DYNAMIC_WORKLOAD_MODE=train or eval (default: eval).

from __future__ import annotations

import hashlib
import logging
import os
import socket
import sys
import time
from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar, Final, Literal, assert_never

import httpx2
from pydantic import BaseModel, ConfigDict

DEFAULT_PORT: Final = 8013
HEALTH_ATTEMPTS: Final = 900
HTTP_OK: Final = 200
TRAIN_PREDICT: Final = 4
PORT_NAME: Final = "port"
MODE_NAME: Final = "DYNAMIC_WORKLOAD_MODE"
LOGGER: Final = logging.getLogger("dynamic-cache-workload")


class WorkloadMode(StrEnum):
    TRAIN = "train"
    EVAL = "eval"


class ConfigError(ValueError):
    name: str
    value: str

    def __init__(self, name: str, value: str) -> None:
        self.name = name
        self.value = value
        super().__init__(f"invalid {name}: {value}")


class HealthTimeoutError(TimeoutError):
    def __init__(self) -> None:
        super().__init__("llama-server health check timed out")


@dataclass(frozen=True, slots=True)
class Config:
    port: int
    mode: WorkloadMode
    train_lines: int
    eval_tokens: int


class TokenizeRequest(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    content: str


class TokenizeResponse(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")

    tokens: list[int]


class CompletionRequest(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    prompt: str
    n_predict: int
    temperature: float = 0.0
    top_k: int = 1
    seed: int = 1
    cache_prompt: bool = False
    id_slot: int = 0
    stream: bool = False
    ignore_eos: bool = True


class Timings(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")

    predicted_n: int
    predicted_per_second: float
    draft_n: int = 0
    draft_n_accepted: int = 0


class CompletionResponse(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")

    content: str
    timings: Timings


class TrainResult(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    mode: Literal["train"] = "train"
    training_lines: int
    prompt_tokens: int
    predicted_n: int
    output_sha: str


class EvalResult(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    mode: Literal["eval"] = "eval"
    requested_n: int
    predicted_n: int
    tg_tps: float
    draft_n: int
    draft_n_accepted: int
    accepted_per_generated: float
    accepted_per_draft: float
    output_sha: str
    output_lines: int
    template_matches: int
    content: str


def parse_positive_int(name: str, default: int) -> int:
    raw = os.environ.get(name, str(default))
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigError(name, raw) from exc
    if value < 1:
        raise ConfigError(name, raw)
    return value


def parse_config() -> Config:
    port_raw = sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_PORT)
    try:
        port = int(port_raw)
    except ValueError as exc:
        raise ConfigError(PORT_NAME, port_raw) from exc

    mode_raw = os.environ.get(MODE_NAME, WorkloadMode.EVAL.value)
    try:
        mode = WorkloadMode(mode_raw)
    except ValueError as exc:
        raise ConfigError(MODE_NAME, mode_raw) from exc

    return Config(
        port=port,
        mode=mode,
        train_lines=parse_positive_int("DYNAMIC_TRAIN_LINES", 512),
        eval_tokens=parse_positive_int("DYNAMIC_EVAL_TOKENS", 512),
    )


def log_request(request: httpx2.Request) -> None:
    request.extensions["request_start"] = time.perf_counter()


def log_response(response: httpx2.Response) -> None:
    started = response.request.extensions.get("request_start")
    elapsed = time.perf_counter() - started if isinstance(started, float) else 0.0
    LOGGER.info(
        "HTTP %s %s -> %d (%.3fs)",
        response.request.method,
        response.request.url,
        response.status_code,
        elapsed,
    )


def create_client(port: int) -> httpx2.Client:
    limits = httpx2.Limits(
        max_connections=200,
        max_keepalive_connections=40,
        keepalive_expiry=30.0,
    )
    timeout = httpx2.Timeout(connect=10.0, read=None, write=10.0, pool=10.0)
    transport = httpx2.HTTPTransport(
        http2=True,
        retries=3,
        limits=limits,
        socket_options=[(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)],
    )
    return httpx2.Client(
        transport=transport,
        timeout=timeout,
        base_url=f"http://127.0.0.1:{port}",
        event_hooks={"request": [log_request], "response": [log_response]},
        follow_redirects=True,
    )


def wait_for_health(client: httpx2.Client) -> None:
    for _ in range(HEALTH_ATTEMPTS):
        try:
            response = client.get("/health")
        except (httpx2.ConnectError, httpx2.ConnectTimeout, httpx2.ReadTimeout):
            time.sleep(2)
            continue
        if response.status_code == HTTP_OK:
            return
        time.sleep(2)
    raise HealthTimeoutError


def tokenize(client: httpx2.Client, content: str) -> TokenizeResponse:
    payload = TokenizeRequest(content=content).model_dump()
    response = client.post("/tokenize", json=payload)
    _ = response.raise_for_status()
    return TokenizeResponse.model_validate_json(response.content)


def complete(client: httpx2.Client, request: CompletionRequest) -> CompletionResponse:
    response = client.post("/completion", json=request.model_dump())
    _ = response.raise_for_status()
    return CompletionResponse.model_validate_json(response.content)


def make_training_corpus(lines: int) -> str:
    return "".join(
        f'{{"record":"T{index:05d}","status":"success","retry":false,"value":{100000 + index}}}\n'
        for index in range(lines)
    )


def run_train(client: httpx2.Client, config: Config) -> TrainResult:
    corpus = make_training_corpus(config.train_lines)
    prompt_tokens = len(tokenize(client, corpus).tokens)
    response = complete(
        client,
        CompletionRequest(prompt=corpus, n_predict=TRAIN_PREDICT),
    )
    return TrainResult(
        training_lines=config.train_lines,
        prompt_tokens=prompt_tokens,
        predicted_n=response.timings.predicted_n,
        output_sha=hashlib.sha256(response.content.encode()).hexdigest()[:12],
    )


def make_eval_prompt() -> str:
    return (
        "Return only compact JSON Lines. "
        "Use fields in this order: record, status, retry, value. "
        "Set status to success and retry to false. "
        "Start record at E9000. "
        "Increment its numeric suffix and value by one on every line. "
        "Output no prose. Continue until stopped.\n"
        '{"record":"E9000"'
    )


def run_eval(client: httpx2.Client, config: Config) -> EvalResult:
    request = CompletionRequest(
        prompt=make_eval_prompt(),
        n_predict=config.eval_tokens,
    )
    response = complete(client, request)
    timings = response.timings
    accepted_per_generated = timings.draft_n_accepted / max(timings.predicted_n, 1)
    accepted_per_draft = timings.draft_n_accepted / max(timings.draft_n, 1)
    compact_matches = response.content.count('"status":"success"')
    spaced_matches = response.content.count('"status": "success"')
    return EvalResult(
        requested_n=config.eval_tokens,
        predicted_n=timings.predicted_n,
        tg_tps=round(timings.predicted_per_second, 3),
        draft_n=timings.draft_n,
        draft_n_accepted=timings.draft_n_accepted,
        accepted_per_generated=round(accepted_per_generated, 6),
        accepted_per_draft=round(accepted_per_draft, 6),
        output_sha=hashlib.sha256(response.content.encode()).hexdigest()[:12],
        output_lines=response.content.count("\n") + 1,
        template_matches=compact_matches + spaced_matches,
        content=response.content,
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    config = parse_config()
    result: TrainResult | EvalResult
    with create_client(config.port) as client:
        wait_for_health(client)
        match config.mode:
            case WorkloadMode.TRAIN:
                result = run_train(client, config)
            case WorkloadMode.EVAL:
                result = run_eval(client, config)
            case unreachable:
                assert_never(unreachable)
    _ = sys.stdout.write(result.model_dump_json() + "\n")


if __name__ == "__main__":
    main()
