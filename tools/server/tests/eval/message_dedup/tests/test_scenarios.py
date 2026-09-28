#!/usr/bin/env python
"""SPEC-0001 increment 17 (RED): the 15 real §9.4 scenarios.

Row: docs/graph/plans/grill/spec-0001-inc-17-scenario-transcripts.md. The
increment-14 suite tests run over the REAL set (tests (1), (3)-(7) per
scenario), plus the scenario-specific assertions of the row, each taken from
the spec §9.4 table. Contracts (the must-fire / must-not-fire conditions each
manifest encodes; AC_Q05, AC_Q08): DEDUP_TOOL_RESULT_REPEAT_STUBBED,
DEDUP_LATER_REPEATS_REFERENCE_FIRST, DEDUP_USER_SYSTEM_OPT_IN,
DEDUP_TEXT_PART_REPEAT_STUBBED, DEDUP_NEAR_DUPLICATE_UNCHANGED,
DEDUP_ASSISTANT_NEVER_STUBBED, DEDUP_STUB_LOOKALIKE_INPUT_VERBATIM,
DEDUP_OVERRIDE_HONORED_ON_ALL_ENDPOINTS.

Test (2), "exactly the 15 IDs", is the increment-14 test
tests/test_suite_schema.py::test_spec0001_suite_real_set_is_exactly_the_15_scenarios
(strict xfail there); this increment removes its marker. Every test here is
parametrized over the FIXED 15 IDs (never over the loaded set), so an empty or
partial set fails instead of collecting nothing.

Provenance (binding): every scenario and snapshot is synthetic (data-ml) or
owner-authored for this suite; never production traffic or real sessions,
"anonymized" or not (kernel §4; spec §9.4). The suite's provenance record is
<SUITE_DIR>/PROVENANCE.md.

Server tests use tests/_suite_server.py (production-profile model and
template; CPU-only render path when the GPU lock is held elsewhere). A test
looks its scenario up BEFORE it asks for the server, so a missing scenario
fails without loading the model.

Schema fields beyond the increment-14 validator that these tests assume
(written against the increment-17 row, reported to data-ml / tool-smith):
- ``turns``: list of message counts, the request of each scripted turn is
  ``prefix.messages[:turns[k]]`` (strictly increasing, last = all messages).
- ``manifest.enable_from_turn`` (M2): the 1-based turn the pass turns on.
- ``manifest.checker.answer_span`` (A1-A4, M1): ``{message, part, start, end}``,
  the byte span inside a must-fire repeated unit that the answer depends on.
- ``anthropic_prefix`` (A4): the Anthropic /v1/messages body; ``prefix`` is
  its chat-completions twin.
"""
from __future__ import annotations

import pytest

from _paths import SUITE_DIR

import checkers  # noqa: E402
import static_checks  # noqa: E402
import suite_schema  # noqa: E402
import tool_simulator  # noqa: E402

ALL_IDS = sorted(suite_schema.REQUIRED_SCENARIO_IDS)
STUB_PREFIX = "[duplicate content omitted"
TOOL = ["tool"]
WIDEST = ["tool", "user", "system"]

# spec §9.4 scenario table: roles, stub count ("+" = at least), reference
TABLE = {
    "A1": (TOOL, 1, "tool result #1 (read_file)"),
    "A2": (TOOL, 1, None),
    "A3": (TOOL, 1, None),
    "A4": (TOOL, 4, "tool result #1"),
    "A5": (TOOL, 0, None),
    "B1": (WIDEST, 7, "user message #1"),  # spec §9.4 amended 2026-09-24 (orchestrator.86.product.1)
    "B2": (WIDEST, 7, "user message #1"),
    "B3": (WIDEST, 0, None),
    "B4": (TOOL, 5, "tool result #1 (run_linter)"),
    "M1": (TOOL, "+", None),
    "M2": (TOOL, "+", None),
    "M3": (TOOL, 0, None),
    "R1": (TOOL, "+", None),
    "R2": (TOOL, "+", None),
    "R3": (WIDEST, 1, "user message #1"),  # spec §9.4 amended 2026-09-24 (orchestrator.86.product.1)
}
DEPTH = {"A1": ("shallow", 3000, 5000), "A2": ("mid", 24000, 40000), "A3": ("deep", 64000, None)}
ANSWER_SPAN_IDS = ["A1", "A2", "A3", "A4", "M1"]
NOTHING_FIRES = ["A5", "B3", "M3"]
STATIC_CHECKS = ["manifest_check", "template_check", "fire_check", "must_not_fire_check"]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def render_server():
    from _suite_server import RenderServer
    srv = RenderServer()
    yield srv
    srv.stop()


@pytest.fixture(scope="session")
def special_texts() -> list[str]:
    """The §4.0 special-text list of the served qwen35 vocab, read once per
    session from the GGUF (stdlib-only reader, increment 14). fire_check needs
    it: a special text in the first 40 bytes of a must-fire unit changes the
    §6.4 stub."""
    from _suite_server import suite_model_path
    from vocab_special_texts import vocab_special_texts
    texts = vocab_special_texts(suite_model_path())
    assert texts, "served vocab yielded no special texts"
    return texts


def scenario(sid: str) -> dict:
    suite = suite_schema.load_suite()
    assert sid in suite, f"scenario {sid} missing from {suite_schema.SCENARIOS_DIR} (increment 17, data-ml)"
    return suite[sid]


def unit_text(s: dict, message: int, part) -> str:
    content = s["prefix"]["messages"][message]["content"]
    return content if part is None else content[part]["text"]


def arm_body(s: dict, arm: str) -> dict:
    body = {k: v for k, v in s["prefix"].items()}
    body["message_dedup"] = ({"enabled": False} if arm == "off"
                             else {"enabled": True, "roles": s["manifest"]["dedup_roles"]})
    return body


def client_of(request):
    return request.getfixturevalue("render_server").client


# ---------------------------------------------------------------------------
# (1)/(3): present, valid, provenance recorded — no server
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("sid", ALL_IDS)
def test_spec0001_suite_real_scenario_valid(sid):
    """Increment-14 tests (1) and (3) over the real set: the scenario exists
    and the validator returns no finding (provenance present and allowed,
    required fields, endpoint and roles in range, every must-fire unit a
    byte repeat of the same role at >= min_bytes)."""
    assert suite_schema.validate(scenario(sid)) == []


@pytest.mark.parametrize("sid", ALL_IDS)
def test_spec0001_suite_real_scenario_snapshot_and_provenance_recorded(sid):
    """Row "Transcript provenance (binding)" and gate "data-ml attests the
    provenance of every scenario and snapshot in the suite's provenance
    record": the scenario's synthetic snapshot exists beside the scenarios,
    and PROVENANCE.md names the scenario ID and its snapshot id."""
    s = scenario(sid)
    snap = tool_simulator.SNAPSHOTS_DIR / s["repo_snapshot"]
    assert snap.is_dir() and any(snap.iterdir()), f"snapshot {snap} missing or empty"
    record = SUITE_DIR / "PROVENANCE.md"
    assert record.is_file(), "suite provenance record missing"
    text = record.read_text(encoding="utf-8")
    assert sid in text and s["repo_snapshot"] in text


@pytest.mark.parametrize("sid", ALL_IDS)
def test_spec0001_suite_real_scenario_matches_table(sid):
    """Spec §9.4 table: the dedup arm's role set, the number of must-fire
    stubs and the reference each carries (A4: "4 stubs, all referencing
    `tool result #1`")."""
    s = scenario(sid)
    roles, count, ref = TABLE[sid]
    m = s["manifest"]
    assert sorted(m["dedup_roles"]) == sorted(roles)
    if count == "+":
        assert len(m["must_fire"]) >= 1
    else:
        assert len(m["must_fire"]) == count
    if ref is not None:
        # A4 names only the ordinal; its stubs may add the tool name "(read_file)"
        ok = (lambda r: r == ref or r.startswith(ref + " (")) if sid == "A4" else (lambda r: r == ref)
        assert all(ok(u["reference"]) for u in m["must_fire"]), [u["reference"] for u in m["must_fire"]]
    if sid in DEPTH:
        assert s["depth_class"] == DEPTH[sid][0]


@pytest.mark.parametrize("sid", ALL_IDS)
def test_spec0001_suite_real_scenario_checker_valid(sid):
    """Spec §9.4 "the checker, which is deterministic": every real
    scenario's checker object is valid under the increment-18 checker schema
    (checkers.py docstring, the one home of that schema), so no run can fail
    on an authoring bug (checkers.check raises ValueError on one)."""
    assert checkers.validate_checker(scenario(sid)["manifest"]["checker"]) == []


def test_spec0001_suite_a4_anthropic_body_and_chat_twin():
    """Row: "A4's manifest carries both the Anthropic body and its
    chat-completions equivalent"; endpoint /v1/messages."""
    s = scenario("A4")
    assert s["endpoint"] == "/v1/messages"
    assert isinstance(s.get("anthropic_prefix"), dict) and s["anthropic_prefix"].get("messages")
    assert s["prefix"].get("messages")


def test_spec0001_suite_m1_is_the_reference_transcript_shape():
    """Row: M1 has >= 40 turns and >= 4 tools (read_file, grep, run_tests,
    edit_file); its two identical assistant turns (content >= 1024 bytes, so
    only the assistant rule keeps them in full) are listed must-not-fire."""
    s = scenario("M1")
    assert len(s["turns"]) >= 40
    names = {tc["function"]["name"] for msg in s["prefix"]["messages"] if msg["role"] == "assistant"
             for tc in msg.get("tool_calls") or []}
    assert {"read_file", "grep", "run_tests", "edit_file"} <= names, names
    by_content: dict[str, list[int]] = {}
    for i, msg in enumerate(s["prefix"]["messages"]):
        c = msg.get("content")
        if msg["role"] == "assistant" and isinstance(c, str) and len(c.encode("utf-8")) >= 1024:
            by_content.setdefault(c, []).append(i)
    groups = [ix for ix in by_content.values() if len(ix) >= 2]
    assert groups, "no pair of identical assistant turns of >= 1024 bytes"
    mnf = {u["message"] for u in s["manifest"]["must_not_fire"]}
    assert all(set(ix) <= mnf for ix in groups)


def test_spec0001_suite_m2_split_marked():
    """Row: "M2: the turn-7/turn-8 split is marked"; 15 turns, pass off
    through turn 7 and on from turn 8."""
    s = scenario("M2")
    assert len(s["turns"]) == 15
    assert s["manifest"]["enable_from_turn"] == 8


@pytest.mark.parametrize("sid", ANSWER_SPAN_IDS)
def test_spec0001_suite_answer_span_beyond_excerpt(sid):
    """Row + AC_Q01: the checkers of A1-A4 and M1 need bytes beyond the
    40-byte excerpt of the stubbed unit. The manifest records the byte span
    inside a must-fire repeated unit that the answer depends on; it starts at
    byte 40 or later and lies inside the unit (exact answers occur in it)."""
    s = scenario(sid)
    ck = s["manifest"]["checker"]
    span = ck.get("answer_span")
    assert span, f"{sid}: checker has no answer_span"
    assert any(u["message"] == span["message"] and u.get("part") == span.get("part")
               for u in s["manifest"]["must_fire"]), f"{sid}: answer_span not in a must-fire unit"
    raw = unit_text(s, span["message"], span.get("part")).encode("utf-8")
    assert 40 <= span["start"] < span["end"] <= len(raw), (span, len(raw))
    if ck["kind"] == "exact_answer":
        assert ck["answer"].encode("utf-8") in raw[span["start"]:span["end"]]


@pytest.mark.parametrize("sid", ["R1", "R2"])
def test_spec0001_suite_lookalike_listed_must_not_fire(sid):
    """Spec §9.4 R1/R2: a tool result carries a fake stub; the manifest
    lists that unit as must-not-fire (it renders verbatim, is not counted)."""
    s = scenario(sid)
    msgs = s["prefix"]["messages"]
    look = [i for i, m in enumerate(msgs) if m["role"] == "tool" and STUB_PREFIX in str(m.get("content"))]
    assert look, f"{sid}: no lookalike in any tool result"
    mnf = {u["message"] for u in s["manifest"]["must_not_fire"]}
    assert set(look) <= mnf


# ---------------------------------------------------------------------------
# (4)-(7) static checks over the real set — render server
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("check", STATIC_CHECKS)
@pytest.mark.parametrize("sid", ALL_IDS)
def test_spec0001_suite_real_scenario_static_check(sid, check, request):
    """Increment-14 tests (4)-(7) over the real set, under the profile's
    model and chat template: AC_Q04 (iii) manifest_check, AC_Q04 (ii)
    template_check, AC_Q05 (i) fire_check (A5, B3 and M3: no stubs expected),
    AC_Q08 must_not_fire_check. Each returns no finding. fire_check gets the
    served vocab's special texts (session fixture `special_texts`)."""
    s = scenario(sid)
    client = client_of(request)
    if check == "fire_check":
        findings = static_checks.fire_check(s, client.apply_template,
                                            special_texts=request.getfixturevalue("special_texts"))
    else:
        findings = getattr(static_checks, check)(s, client.apply_template)
    assert findings == []


@pytest.mark.parametrize("sid", sorted(DEPTH))
def test_spec0001_suite_depth_class_measured(sid, request):
    """Row: A1 ~4k, A2 ~32k, A3 >= 64k tokens (target 96k): the /tokenize
    count (served vocab, parse_special true, no BOS) of the pass-off
    /apply-template text between the end of the first occurrence and the
    start of the repeat. "~" is read as +-25% (assumption; spec gives no
    tolerance)."""
    s = scenario(sid)
    client = client_of(request)
    u = s["manifest"]["must_fire"][0]
    text = unit_text(s, u["message"], u.get("part"))
    prompt = client.apply_template(arm_body(s, "off"))
    p1 = prompt.find(text)
    assert p1 >= 0
    p2 = prompt.find(text, p1 + len(text))
    assert p2 > p1
    n = len(client.tokenize(prompt[p1 + len(text):p2], parse_special=True))
    _, lo, hi = DEPTH[sid]
    assert n >= lo and (hi is None or n <= hi), f"{sid}: depth {n} tokens outside [{lo}, {hi}]"


def test_spec0001_suite_m1_prompt_at_least_100k_tokens(request):
    """Row + §9.3: M1's pass-off prompt (the whole scripted prefix, rendered
    with the pass off) is >= 100k tokens."""
    s = scenario("M1")
    client = client_of(request)
    n = len(client.tokenize(client.apply_template(arm_body(s, "off")), parse_special=True))
    assert n >= 100_000, n


@pytest.mark.parametrize("sid", NOTHING_FIRES)
def test_spec0001_suite_nothing_fires(sid, request):
    """Row: "A5, B3, ... and M3: nothing fires" (AC_Q08;
    DEDUP_NEAR_DUPLICATE_UNCHANGED): the dedup-arm render holds no stub
    prefix beyond the off arm's, and it is byte-identical to the off arm
    (nothing was replaced)."""
    s = scenario(sid)
    client = client_of(request)
    on = client.apply_template(arm_body(s, "dedup"))
    off = client.apply_template(arm_body(s, "off"))
    assert on.count(STUB_PREFIX) == off.count(STUB_PREFIX)
    assert on.encode("utf-8") == off.encode("utf-8")


@pytest.mark.parametrize("sid", ["R1", "R2"])
def test_spec0001_suite_lookalike_renders_verbatim(sid, request):
    """Row: "R1 and R2: the lookalike stays verbatim"
    (DEDUP_STUB_LOOKALIKE_INPUT_VERBATIM): every tool result holding the stub
    prefix appears byte for byte in the dedup-arm render."""
    s = scenario(sid)
    client = client_of(request)
    on = client.apply_template(arm_body(s, "dedup"))
    look = [m["content"] for m in s["prefix"]["messages"] if m["role"] == "tool" and STUB_PREFIX in str(m.get("content"))]
    assert look and all(c in on for c in look)


def test_spec0001_suite_a4_count_tokens_override(request):
    """Row A4 (DEDUP_OVERRIDE_HONORED_ON_ALL_ENDPOINTS): on
    /v1/messages/count_tokens the Anthropic body with the override counts
    fewer input_tokens than without it, and equals its chat twin's count on
    /v1/chat/completions/input_tokens (same override)."""
    s = scenario("A4")
    client = client_of(request)
    roles = s["manifest"]["dedup_roles"]
    on = client.count_tokens_anthropic({**s["anthropic_prefix"], "message_dedup": {"enabled": True, "roles": roles}})
    off = client.count_tokens_anthropic({**s["anthropic_prefix"], "message_dedup": {"enabled": False}})
    twin = client.count_tokens_chat(arm_body(s, "dedup"))
    assert on < off, (on, off)
    assert on == twin, (on, twin)
