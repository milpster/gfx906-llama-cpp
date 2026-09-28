"""SPEC-0001 §9.4 scenario suite: scenario/manifest schema and validator.

Tool card: docs/graph/tools/message-dedup-scenario-suite.md.
Tests: tests/test_suite_schema.py (increment 14, row tests (1)-(3)).

A scenario is one JSON document ``scenarios/<ID>.json``::

    {
      "schema": "message_dedup.scenario/1",          # optional; if present, exactly this
      "id": "A1",                                     # == the file stem
      "provenance": {"kind": "synthetic" | "owner-authored", "source": "<generator or author>"},
      "endpoint": "/v1/chat/completions" | "/v1/responses" | "/v1/messages",
      "depth_class": "<non-empty string>",            # A1-A3: shallow / mid / deep (spec §9.4)
      "repo_snapshot": "<synthetic snapshot id>",
      "prefix": {"messages": [...], ...},             # the scripted prefix, a chat-completions body
      "manifest": {
        "dedup_roles": ["tool"] | ["tool", "user", "system"] | ...,   # non-empty subset
        "min_bytes": 1024,                            # optional, the arm's min_bytes (§6.1)
        "must_fire": [{"message": 7, "part": null, "reference": "tool result #1 (read_file)"}],  # the exact §6.4 REF
        "must_not_fire": [{"message": 11, "part": null}],
        "embedded_block": "<text>",                   # optional (B3): a block repeated INSIDE larger units
        "checker": {"kind": "<checker kind>", ...}    # judged by checkers.py (increment 18)
      }
    }

A unit (§6.3) is ``prefix.messages[message].content`` when ``part`` is null
(a non-empty string), or ``prefix.messages[message].content[part].text`` for a
``text`` part. Fields added by later increments (``turns``,
``anthropic_prefix``, ``manifest.enable_from_turn``, ``checker.answer_span``)
are not judged here.

Provenance is binding (kernel §4, spec §9.4): only synthetic or
owner-authored transcripts; captured proxy traffic or samples of real
sessions are refused whatever they are labelled.

Finding codes: ``PROVENANCE_MISSING``, ``PROVENANCE_KIND_FORBIDDEN``,
``FIELD_MISSING``, ``FIELD_INVALID``, ``SCHEMA_UNKNOWN``, ``ENDPOINT_INVALID``,
``ROLE_INVALID``, ``UNIT_INVALID``, ``MUST_FIRE_NOT_REPEATED``,
``REFERENCE_INVALID``, ``SCENARIO_SET_MISMATCH``.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

SUITE_DIR = Path(__file__).resolve().parent
SCENARIOS_DIR = SUITE_DIR / "scenarios"

REQUIRED_SCENARIO_IDS = frozenset(
    ["A1", "A2", "A3", "A4", "A5", "B1", "B2", "B3", "B4", "M1", "M2", "M3", "R1", "R2", "R3"]
)

SCHEMA_ID = "message_dedup.scenario/1"
PROVENANCE_KINDS = frozenset(["synthetic", "owner-authored"])
ENDPOINTS = frozenset(["/v1/chat/completions", "/v1/responses", "/v1/messages"])
DEDUP_ROLES = frozenset(["tool", "user", "system"])      # spec §6.2 role enum
DEFAULT_MIN_BYTES = 1024                                  # spec §6.1 default
ROLEWORD = {"tool": "tool result", "user": "user message", "system": "system message"}  # spec §6.4
_TOOLNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")                                # spec §6.4 TOOLNAME allowlist
_REF_RE = re.compile(r"^(tool result|user message|system message) #([1-9][0-9]*)(?: \(([A-Za-z0-9_.-]{1,64})\))?$")


@dataclass(frozen=True)
class Finding:
    code: str
    detail: str = ""


# ---------------------------------------------------------------------------
# shared helpers (also used by static_checks)
# ---------------------------------------------------------------------------

def messages_of(scenario: dict) -> list:
    return scenario["prefix"]["messages"]


def unit_text(scenario: dict, message: Any, part: Any) -> str | None:
    """The unit's text, or None when (message, part) names no §6.3 unit."""
    msgs = messages_of(scenario)
    if not isinstance(message, int) or isinstance(message, bool) or not 0 <= message < len(msgs):
        return None
    m = msgs[message]
    if not isinstance(m, dict):
        return None
    content = m.get("content")
    if part is None:
        return content if isinstance(content, str) and content else None
    if not isinstance(part, int) or isinstance(part, bool) or not isinstance(content, list) or not 0 <= part < len(content):
        return None
    p = content[part]
    if isinstance(p, dict) and p.get("type") == "text" and isinstance(p.get("text"), str) and p["text"]:
        return p["text"]
    return None


def iter_units(scenario: dict):
    """Every §6.3 unit of the prefix, in message then part order: (message, part, role, text)."""
    for i, m in enumerate(messages_of(scenario)):
        if not isinstance(m, dict):
            continue
        content = m.get("content")
        if isinstance(content, str) and content:
            yield i, None, m.get("role"), content
        elif isinstance(content, list):
            for k, p in enumerate(content):
                if isinstance(p, dict) and p.get("type") == "text" and isinstance(p.get("text"), str) and p["text"]:
                    yield i, k, m.get("role"), p["text"]


def embedded_block_occurrences(scenario: dict, block: str) -> int:
    """How many times ``block`` occurs in the prefix's unit texts (§9.4 B3:
    the block embedded inside each user message's text)."""
    return sum(t.count(block) for _, _, _, t in iter_units(scenario))


def unit_order(message: int, part: Any) -> tuple[int, int]:
    return (message, -1 if part is None else part)


def first_occurrence(scenario: dict, message: int, part: Any) -> tuple[int, Any] | None:
    """§6.3 first_occurrence of the unit: the earliest EARLIER unit of the same
    role, in message then part order, with equal bytes. None if there is none."""
    text = unit_text(scenario, message, part)
    role = messages_of(scenario)[message].get("role")
    here = unit_order(message, part)
    for i, k, r, t in iter_units(scenario):
        if unit_order(i, k) >= here:
            return None
        if r == role and t == text:
            return i, k
    return None


def role_ordinal(scenario: dict, message: int) -> int:
    """§6.4 ORDINAL: 1 + the number of messages before ``message`` with its role."""
    msgs = messages_of(scenario)
    role = msgs[message].get("role")
    return 1 + sum(1 for m in msgs[:message] if isinstance(m, dict) and m.get("role") == role)


def role_toolname(scenario: dict, message: int) -> str | None:
    """§6.4 TOOLNAME of the tool message ``message``, or None when the group is
    omitted. Candidate: the function.name of the latest earlier assistant
    tool_call whose id == the message's tool_call_id; else the message's own
    string "name". Kept only if the whole candidate is on the allowlist."""
    msgs = messages_of(scenario)
    call_id = msgs[message].get("tool_call_id")
    candidate = None
    if isinstance(call_id, str):
        for m in msgs[:message]:
            if not isinstance(m, dict) or m.get("role") != "assistant" or not isinstance(m.get("tool_calls"), list):
                continue
            for tc in m["tool_calls"]:
                fn = tc.get("function") if isinstance(tc, dict) else None
                if isinstance(fn, dict) and tc.get("id") == call_id and isinstance(fn.get("name"), str):
                    candidate = fn["name"]
    if candidate is None and isinstance(msgs[message].get("name"), str):
        candidate = msgs[message]["name"]
    return candidate if candidate is not None and _TOOLNAME_RE.match(candidate) else None


def min_bytes_of(scenario: dict) -> int:
    return scenario["manifest"].get("min_bytes", DEFAULT_MIN_BYTES)


def parse_reference(reference: str) -> tuple[str, int, str | None] | None:
    """A §6.4 REF string -> (role, ordinal, toolname or None); None if malformed."""
    m = _REF_RE.match(reference) if isinstance(reference, str) else None
    if not m:
        return None
    role = next(r for r, w in ROLEWORD.items() if w == m.group(1))
    if m.group(3) is not None and role != "tool":
        return None
    return role, int(m.group(2)), m.group(3)


def arm_body(scenario: dict, arm: str) -> dict:
    """The request body of one §9.4 arm: the prefix plus the message_dedup override."""
    body = dict(scenario["prefix"])
    if arm == "off":
        body["message_dedup"] = {"enabled": False}
    elif arm == "dedup":
        override = {"enabled": True, "roles": list(scenario["manifest"]["dedup_roles"])}
        if "min_bytes" in scenario["manifest"]:
            override["min_bytes"] = scenario["manifest"]["min_bytes"]
        body["message_dedup"] = override
    else:
        raise ValueError(f"unknown arm {arm!r} (expected 'off' or 'dedup')")
    return body


# ---------------------------------------------------------------------------
# validator
# ---------------------------------------------------------------------------

def _nonempty_str(v: Any) -> bool:
    return isinstance(v, str) and v != ""


def _validate_provenance(s: dict, out: list[Finding]) -> None:
    if "provenance" not in s or s["provenance"] is None:
        out.append(Finding("PROVENANCE_MISSING", "scenario has no provenance (kernel §4, spec §9.4)"))
        return
    prov = s["provenance"]
    kind = prov.get("kind") if isinstance(prov, dict) else None
    if not isinstance(kind, str) or kind not in PROVENANCE_KINDS:
        out.append(Finding("PROVENANCE_KIND_FORBIDDEN",
                           f"provenance.kind {kind!r} not in {sorted(PROVENANCE_KINDS)}"))
    if isinstance(prov, dict) and not _nonempty_str(prov.get("source")):
        out.append(Finding("FIELD_MISSING", "provenance.source (the generator or the author) is required"))


def _validate_units(s: dict, key: str, out: list[Finding]) -> list[tuple[int, Any]]:
    units = s["manifest"][key]
    if not isinstance(units, list):
        out.append(Finding("FIELD_INVALID", f"manifest.{key} must be a list"))
        return []
    seen: list[tuple[int, Any]] = []
    for n, u in enumerate(units):
        where = f"manifest.{key}[{n}]"
        if not isinstance(u, dict) or "message" not in u:
            out.append(Finding("UNIT_INVALID", f"{where}: needs 'message' (and 'part', null for string content)"))
            continue
        msg, part = u["message"], u.get("part")
        if unit_text(s, msg, part) is None:
            out.append(Finding("UNIT_INVALID", f"{where}: message {msg!r} part {part!r} is not a §6.3 unit of the prefix"))
            continue
        if (msg, part) in seen:
            out.append(Finding("UNIT_INVALID", f"{where}: unit listed twice"))
            continue
        seen.append((msg, part))
    return seen


def _validate_must_fire(s: dict, roles: set[str], min_bytes: int, out: list[Finding]) -> None:
    for n, u in enumerate(s["manifest"]["must_fire"]):
        if not isinstance(u, dict):
            continue
        msg, part = u.get("message"), u.get("part")
        text = unit_text(s, msg, part)
        if text is None:
            continue  # already UNIT_INVALID
        where = f"manifest.must_fire[{n}] (message {msg}, part {part})"
        role = messages_of(s)[msg].get("role")
        if role not in roles:
            out.append(Finding("MUST_FIRE_NOT_REPEATED", f"{where}: role {role!r} is not in dedup_roles"))
            continue
        nbytes = len(text.encode("utf-8"))
        if nbytes < min_bytes:
            out.append(Finding("MUST_FIRE_NOT_REPEATED", f"{where}: {nbytes} bytes < min_bytes {min_bytes}"))
            continue
        first = first_occurrence(s, msg, part)
        if first is None:
            out.append(Finding("MUST_FIRE_NOT_REPEATED",
                               f"{where}: no earlier {role!r} unit with equal bytes (§6.3, same role only)"))
            continue
        ref = u.get("reference")
        parsed = parse_reference(ref)
        if parsed is None:
            out.append(Finding("REFERENCE_INVALID", f"{where}: reference {ref!r} does not match the §6.4 REF grammar"))
            continue
        want_ord = role_ordinal(s, first[0])
        want_name = role_toolname(s, first[0]) if role == "tool" else None
        if parsed != (role, want_ord, want_name):
            want_ref = f"{ROLEWORD[role]} #{want_ord}" + ("" if want_name is None else f" ({want_name})")
            out.append(Finding("REFERENCE_INVALID",
                               f"{where}: reference {ref!r}, but the first occurrence (message {first[0]}) "
                               f"is {want_ref!r}"))


def _int(v: Any) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _validate_optional(s: dict, out: list[Finding]) -> None:
    """Shape of the optional fields the increment-17/18 tests use, only when present."""
    n_msgs = len(messages_of(s))
    turns = s.get("turns")
    if "turns" in s:
        if (not isinstance(turns, list) or not turns or not all(_int(t) and t >= 1 for t in turns)
                or any(b <= a for a, b in zip(turns, turns[1:])) or turns[-1] != n_msgs):
            out.append(Finding("FIELD_INVALID", "turns: strictly increasing message counts >= 1, "
                                                f"the last == len(prefix.messages) ({n_msgs})"))
            turns = None
    man = s["manifest"]
    if "enable_from_turn" in man:
        eft = man["enable_from_turn"]
        if not _int(eft) or eft < 1 or not isinstance(turns, list) or eft > len(turns):
            out.append(Finding("FIELD_INVALID", "manifest.enable_from_turn: a 1-based turn number within turns"))
    ck = man.get("checker")
    if isinstance(ck, dict) and "answer_span" in ck:
        sp = ck["answer_span"]
        text = unit_text(s, sp.get("message"), sp.get("part")) if isinstance(sp, dict) else None
        if (text is None or not _int(sp.get("start")) or not _int(sp.get("end"))
                or not 0 <= sp["start"] < sp["end"] <= len(text.encode("utf-8"))):
            out.append(Finding("FIELD_INVALID", "manifest.checker.answer_span: {message, part, start, end}, "
                                                "a non-empty byte span inside a prefix unit"))
    if "embedded_block" in man:
        blk = man["embedded_block"]
        if not isinstance(blk, str) or not blk or embedded_block_occurrences(s, blk) == 0:
            out.append(Finding("FIELD_INVALID", "manifest.embedded_block: a non-empty string that occurs "
                                                "in the prefix message text"))
    if "anthropic_prefix" in s:
        ap = s["anthropic_prefix"]
        if not isinstance(ap, dict) or not isinstance(ap.get("messages"), list) or not ap["messages"]:
            out.append(Finding("FIELD_INVALID", "anthropic_prefix: an Anthropic /v1/messages body with messages"))


def validate(scenario: dict) -> list[Finding]:
    """Validate ONE scenario document. Empty list == valid."""
    out: list[Finding] = []
    if not isinstance(scenario, dict):
        return [Finding("FIELD_INVALID", "a scenario is a JSON object")]
    s = scenario
    if "schema" in s and s["schema"] != SCHEMA_ID:
        out.append(Finding("SCHEMA_UNKNOWN", f"schema {s['schema']!r}, expected {SCHEMA_ID!r}"))
    _validate_provenance(s, out)

    for key in ("id", "endpoint", "depth_class", "repo_snapshot", "prefix", "manifest"):
        if key not in s:
            out.append(Finding("FIELD_MISSING", key))
    for key in ("id", "depth_class", "repo_snapshot"):
        if key in s and not _nonempty_str(s[key]):
            out.append(Finding("FIELD_INVALID", f"{key} must be a non-empty string"))
    if "endpoint" in s and s["endpoint"] not in ENDPOINTS:
        out.append(Finding("ENDPOINT_INVALID", f"endpoint {s['endpoint']!r} not in {sorted(ENDPOINTS)}"))

    prefix_ok = False
    if "prefix" in s:
        msgs = s["prefix"].get("messages") if isinstance(s["prefix"], dict) else None
        if not isinstance(msgs, list) or not msgs:
            out.append(Finding("FIELD_INVALID", "prefix.messages must be a non-empty list"))
        elif not all(isinstance(m, dict) and _nonempty_str(m.get("role")) for m in msgs):
            out.append(Finding("FIELD_INVALID", "every prefix message is an object with a string role"))
        else:
            prefix_ok = True

    if "manifest" not in s:
        return out
    man = s["manifest"]
    if not isinstance(man, dict):
        out.append(Finding("FIELD_INVALID", "manifest must be an object"))
        return out
    for key in ("dedup_roles", "must_fire", "must_not_fire", "checker"):
        if key not in man:
            out.append(Finding("FIELD_MISSING", f"manifest.{key}"))

    roles_ok = False
    if "dedup_roles" in man:
        roles = man["dedup_roles"]
        if (not isinstance(roles, list) or not roles
                or not all(isinstance(r, str) and r in DEDUP_ROLES for r in roles)
                or len(set(roles)) != len(roles)):
            out.append(Finding("ROLE_INVALID", f"dedup_roles {roles!r}: a non-empty subset of {sorted(DEDUP_ROLES)}"))
        else:
            roles_ok = True

    min_bytes_ok = True
    if "min_bytes" in man:
        mb = man["min_bytes"]
        if not isinstance(mb, int) or isinstance(mb, bool) or mb < 1:
            out.append(Finding("FIELD_INVALID", f"manifest.min_bytes {mb!r} must be a positive integer"))
            min_bytes_ok = False

    if "checker" in man:
        ck = man["checker"]
        if not isinstance(ck, dict) or not _nonempty_str(ck.get("kind")):
            out.append(Finding("FIELD_INVALID", "manifest.checker must be an object with a non-empty 'kind'"))

    if not prefix_ok:
        return out
    _validate_optional(s, out)
    fire = _validate_units(s, "must_fire", out) if "must_fire" in man else []
    not_fire = _validate_units(s, "must_not_fire", out) if "must_not_fire" in man else []
    for u in set(fire) & set(not_fire):
        out.append(Finding("UNIT_INVALID", f"message {u[0]} part {u[1]} is listed as both must-fire and must-not-fire"))
    if "must_fire" in man and isinstance(man["must_fire"], list) and roles_ok and min_bytes_ok:
        _validate_must_fire(s, set(man["dedup_roles"]), min_bytes_of(s), out)
    return out


def validate_suite_ids(ids: Iterable[str]) -> list[Finding]:
    """The suite set must be exactly REQUIRED_SCENARIO_IDS, each once."""
    ids = list(ids)
    out: list[Finding] = []
    dup = sorted(i for i, n in Counter(ids).items() if n > 1)
    if dup:
        out.append(Finding("SCENARIO_SET_MISMATCH", f"duplicate ids {dup}"))
    got = set(ids)
    missing = sorted(REQUIRED_SCENARIO_IDS - got)
    extra = sorted(got - REQUIRED_SCENARIO_IDS, key=str)
    if missing or extra:
        out.append(Finding("SCENARIO_SET_MISMATCH", f"missing {missing}, unexpected {extra}"))
    return out


def load_suite(directory: Path = SCENARIOS_DIR) -> dict[str, dict]:
    """Every ``*.json`` scenario in ``directory`` (sorted by file name), keyed
    by its ``id``. Raises on a missing directory, unparsable JSON, a missing
    id, an id that differs from the file stem, or a duplicate id."""
    directory = Path(directory)
    if not directory.is_dir():
        raise FileNotFoundError(f"scenario directory {directory} does not exist")
    suite: dict[str, dict] = {}
    for path in sorted(directory.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            try:
                doc = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"{path}: not valid JSON: {e}") from e
        sid = doc.get("id") if isinstance(doc, dict) else None
        if not _nonempty_str(sid):
            raise ValueError(f"{path}: scenario has no string 'id'")
        if sid != path.stem:
            raise ValueError(f"{path}: id {sid!r} differs from the file name")
        if sid in suite:
            raise ValueError(f"{path}: duplicate scenario id {sid!r}")
        suite[sid] = doc
    return suite
