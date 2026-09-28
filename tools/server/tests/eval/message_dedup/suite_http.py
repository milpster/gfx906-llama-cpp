"""SPEC-0001 §9.4 suite: thin HTTP client for one running llama-server.

Tester-owned gate infrastructure (spawn `orchestrator.49.tester.g2`), shared
by the plant gates (increments 15 and 16) and usable by the increment-18
runner as its default client. It only wraps endpoints; it judges nothing.
It talks to an ALREADY RUNNING server by URL, so plant gates never go through
tools/server/tests/utils.py ServerProcess (which exports
LLAMA_SERVER_DEBUG_FAKE_TIMING to its child).

Uses `requests`, already in tools/server/tests/requirements.txt (no new
dependency).
"""
from __future__ import annotations

import time
from typing import Any

import requests


class SuiteHttpError(RuntimeError):
    def __init__(self, path: str, code: int, body: Any):
        super().__init__(f"POST {path} returned {code}: {body!r}"[:2000])
        self.path = path
        self.code = code
        self.body = body


class SuiteHttp:
    def __init__(self, base_url: str, timeout: float = 3600.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    # -- raw ------------------------------------------------------------------
    def post(self, path: str, body: dict) -> dict:
        res = self.session.post(self.base_url + path, json=body, timeout=self.timeout)
        try:
            payload = res.json()
        except ValueError:
            payload = res.text
        if res.status_code != 200:
            raise SuiteHttpError(path, res.status_code, payload)
        return payload

    def get(self, path: str) -> Any:
        res = self.session.get(self.base_url + path, timeout=self.timeout)
        res.raise_for_status()
        return res.json()

    # -- endpoints ------------------------------------------------------------
    def apply_template(self, body: dict) -> str:
        return self.post("/apply-template", body)["prompt"]

    def timed_apply_template(self, body: dict) -> tuple[str, float]:
        """(prompt, wall-clock seconds of the HTTP round trip)."""
        t0 = time.perf_counter()
        prompt = self.apply_template(body)
        return prompt, time.perf_counter() - t0

    def tokenize(self, text: str, parse_special: bool = True) -> list[int]:
        """Served vocab, no BOS (add_special false)."""
        toks = self.post("/tokenize", {"content": text, "add_special": False,
                                       "parse_special": parse_special})["tokens"]
        return [t["id"] if isinstance(t, dict) else t for t in toks]

    def chat(self, body: dict) -> dict:
        return self.post("/v1/chat/completions", body)

    def messages(self, body: dict) -> dict:
        return self.post("/v1/messages", body)

    def count_tokens_chat(self, body: dict) -> int:
        return int(self.post("/v1/chat/completions/input_tokens", body)["input_tokens"])

    def count_tokens_anthropic(self, body: dict) -> int:
        return int(self.post("/v1/messages/count_tokens", body)["input_tokens"])

    def total_slots(self) -> int:
        return int(self.get("/props").get("total_slots", 1))

    def erase_slots(self) -> None:
        """Erase every slot's KV (needs the server started with --slot-save-path)."""
        for i in range(self.total_slots()):
            self.post(f"/slots/{i}?action=erase", {})

    def reset_cache(self) -> None:
        """The runner's "every run starts from an empty prompt cache" (spec §9.4)."""
        self.erase_slots()
