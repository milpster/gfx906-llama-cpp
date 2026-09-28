"""SPEC-0001 plant gates: shared measurement plumbing (increments 15 and 16).

Tester-owned (spawn `orchestrator.49.tester.g2`). Request builders over the
increment-17 scenarios, a byte-offset window over a server log file, and JSON
result records. Decisions live in plant_gates.py.

Scenario fields used (see tests/test_scenarios.py for the schema
assumptions): ``prefix`` (chat body), ``turns`` (message counts per scripted
turn), ``manifest.dedup_roles``, ``manifest.enable_from_turn`` (M2),
``anthropic_prefix`` (A4).
"""
from __future__ import annotations

import copy
import datetime as _dt
import json
import re
import time
from pathlib import Path

SUITE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = SUITE_DIR / "results"
STUB_PREFIX = "[duplicate content omitted"
STUB_RE = re.compile(r"\[duplicate content omitted: byte-identical to [^\]]*?; unchanged since then\]")

OFF = {"enabled": False}


def on_override(scenario: dict) -> dict:
    return {"enabled": True, "roles": list(scenario["manifest"]["dedup_roles"])}


def turns_of(scenario: dict) -> list[int]:
    return list(scenario.get("turns") or [len(scenario["prefix"]["messages"])])


def turn_body(scenario: dict, k: int, override: dict | None, **extra) -> dict:
    """The chat body of scripted turn k (0-based): prefix.messages[:turns[k]].
    ``override`` None sends no `message_dedup` field (server-default arm, the
    only form the feature-free baseline build understands)."""
    body = copy.deepcopy({kk: v for kk, v in scenario["prefix"].items() if kk != "messages"})
    body["messages"] = copy.deepcopy(scenario["prefix"]["messages"][:turns_of(scenario)[k]])
    if override is not None:
        body["message_dedup"] = dict(override)
    body.update(extra)
    return body


def prefix_body(scenario: dict, override: dict | None, **extra) -> dict:
    return turn_body(scenario, len(turns_of(scenario)) - 1, override, **extra)


def units(scenario: dict) -> list[str]:
    """Every text unit of the scripted prefix (string content and text parts)."""
    out = []
    for m in scenario["prefix"]["messages"]:
        c = m.get("content")
        if isinstance(c, str) and c:
            out.append(c)
        elif isinstance(c, list):
            out += [p["text"] for p in c if isinstance(p, dict) and p.get("type") == "text" and p.get("text")]
    return out


class LogWindow:
    """Byte-offset window over a server log file (the logger writes from a
    worker thread, so settle() waits for the file to stop growing)."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def size(self) -> int:
        return self.path.stat().st_size if self.path.exists() else 0

    def settle(self, quiet_s: float = 0.5, timeout_s: float = 30.0) -> int:
        deadline = time.time() + timeout_s
        last, since = self.size(), time.time()
        while time.time() < deadline:
            time.sleep(0.1)
            cur = self.size()
            if cur != last:
                last, since = cur, time.time()
            elif time.time() - since >= quiet_s:
                break
        return last

    def text(self, start: int, end: int) -> str:
        with open(self.path, "rb") as f:
            f.seek(start)
            return f.read(max(0, end - start)).decode("utf-8", errors="replace")


def write_record(name: str, payload: dict, out: str | Path | None = None) -> Path:
    path = Path(out) if out else RESULTS_DIR / f"{name}-{_dt.datetime.now().strftime('%Y%m%dT%H%M%S')}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=1, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    return path


def read_record(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def gate_payload(results: dict) -> dict:
    """{gate: GateResult} -> JSON-able dict with an overall `passed`."""
    return {"passed": all(r.passed for r in results.values()),
            "gates": {k: {"passed": r.passed, "failures": r.failures, "details": r.details}
                      for k, r in results.items()}}
