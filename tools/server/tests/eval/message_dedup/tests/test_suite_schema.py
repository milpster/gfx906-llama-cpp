#!/usr/bin/env python
"""SPEC-0001 increment 14 (RED): scenario/manifest schema and validator.

Row: docs/graph/plans/grill/spec-0001-inc-14-eval-harness-and-transcripts.md,
tests (1)-(3). Spec §9.4 (scenario manifest; transcript provenance) and
kernel §4 (no production data). Pure Python: no server.

Fixtures are hand-made synthetic mini scenarios under tests/fixtures/, not
the real A1-R3 set (increment 17).
"""
import copy

import pytest

from _paths import load  # noqa: F401  (also sets sys.path)

import suite_schema  # noqa: E402

VALID = "valid_scenario.json"


def codes(findings) -> set[str]:
    return {f.code for f in findings}


# --- positive control (guards against a validator that rejects everything) --

def test_spec0001_suite_valid_mini_scenario_accepted():
    """§9.4 manifest schema: the hand-made valid mini scenario (endpoint, dedup
    role set, must-fire unit with its exact reference, must-not-fire unit,
    checker kind, provenance, depth class, repo snapshot id) validates clean.
    Positive control: passes on the RED stub by design."""
    assert suite_schema.validate(load(VALID)) == []


# --- (1) provenance -----------------------------------------------------------

def test_spec0001_suite_scenario_without_provenance_rejected():
    """Row test (1); §9.4 "Every transcript records its provenance"; kernel §4.
    Given a scenario with no `provenance` field, When validated, Then it is
    rejected with PROVENANCE_MISSING."""
    findings = suite_schema.validate(load("planted_no_provenance.json"))
    assert "PROVENANCE_MISSING" in codes(findings)


def test_spec0001_suite_scenario_captured_provenance_rejected():
    """Row test (1), provenance allow-list; §9.4 "Traffic captured from the
    owner's production proxy is never used". Given provenance kind
    `captured-proxy-traffic`, When validated, Then PROVENANCE_KIND_FORBIDDEN.
    Allowed kinds are exactly `synthetic` and `owner-authored`."""
    findings = suite_schema.validate(load("planted_provenance_captured.json"))
    assert "PROVENANCE_KIND_FORBIDDEN" in codes(findings)


@pytest.mark.parametrize("kind", ["synthetic-x", "xsynthetic", "owner", "owner-authored-x", "", None])
def test_spec0001_suite_provenance_kind_exact_membership(kind):
    """Row test (1): exact membership of the provenance kind (prefix- and
    suffix-extension mutants of the allowed values are rejected;
    protocol.test-first exact-membership rule)."""
    s = load(VALID)
    s["provenance"]["kind"] = kind
    assert "PROVENANCE_KIND_FORBIDDEN" in codes(suite_schema.validate(s))


# --- manifest fields (spec §9.4 manifest list; row "Files touched") ----------

REQUIRED_FIELDS = [
    ("endpoint",),
    ("depth_class",),
    ("repo_snapshot",),
    ("prefix",),
    ("manifest", "dedup_roles"),
    ("manifest", "must_fire"),
    ("manifest", "must_not_fire"),
    ("manifest", "checker"),
]


@pytest.mark.parametrize("path", REQUIRED_FIELDS, ids=lambda p: ".".join(p))
def test_spec0001_suite_manifest_required_field_missing_rejected(path):
    """§9.4 manifest: endpoint, role set of the dedup arm, must-fire units,
    must-not-fire units, checker; row: depth class and synthetic repository
    snapshot id. Given the valid scenario minus one required field, When
    validated, Then FIELD_MISSING."""
    s = load(VALID)
    node = s
    for key in path[:-1]:
        node = node[key]
    del node[path[-1]]
    assert "FIELD_MISSING" in codes(suite_schema.validate(s))


@pytest.mark.parametrize("endpoint", ["/v1/chat/completion", "/v1/chat/completions/x", "/completion", "/v1/messages/count_tokens"])
def test_spec0001_suite_endpoint_outside_scope_rejected(endpoint):
    """§9.4 manifest `endpoint`: one of the JSON chat endpoints a scenario is
    sent to (/v1/chat/completions, /v1/responses, /v1/messages; A4 uses
    /v1/messages). Anything else, including near-miss spellings, is
    ENDPOINT_INVALID."""
    s = load(VALID)
    s["endpoint"] = endpoint
    assert "ENDPOINT_INVALID" in codes(suite_schema.validate(s))


@pytest.mark.parametrize("roles", [["assistant"], ["tool", "assistant"], ["tools"], ["too"], []])
def test_spec0001_suite_dedup_roles_outside_enum_rejected(roles):
    """§9.4 arms: the dedup arm's role set is `tool` or the widest
    `tool,user,system` (§6.2 enum: tool, user, system; `assistant` is never a
    participating role). An out-of-enum or empty role set is ROLE_INVALID."""
    s = load(VALID)
    s["manifest"]["dedup_roles"] = roles
    assert "ROLE_INVALID" in codes(suite_schema.validate(s))


# --- (3) must-fire unit must be byte-repeated in the prefix ------------------

def test_spec0001_suite_must_fire_unit_not_byte_repeated_rejected():
    """Row test (3), planted fixture "a unit changed by one byte"; §9.4 "the
    scripted prefix ... including every repeat the scenario is about";
    §6.3 equality is byte equality of the whole unit, same role. Given a
    manifest whose must-fire unit differs by one byte from its intended
    first occurrence, When validated, Then MUST_FIRE_NOT_REPEATED."""
    findings = suite_schema.validate(load("planted_must_fire_one_byte_changed.json"))
    assert "MUST_FIRE_NOT_REPEATED" in codes(findings)


def test_spec0001_suite_must_fire_unit_repeat_of_other_role_rejected():
    """Row test (3), same-role rule (§6.3 first_occurrence; DEDUP_REFERENCE_SAME_ROLE_ONLY):
    a must-fire tool unit whose only earlier byte-equal copy is a `user`
    message is not a repeat. Planted in-test: the first tool copy is moved
    into a user message."""
    s = load(VALID)
    msgs = s["prefix"]["messages"]
    msgs[1]["content"] = msgs[3]["content"]
    msgs[3]["content"] = "short and unrelated"
    assert "MUST_FIRE_NOT_REPEATED" in codes(suite_schema.validate(s))


def test_spec0001_suite_must_fire_unit_below_min_bytes_rejected():
    """Row test (3): a repeat that the pass can never stub (below the default
    min_bytes 1024, §6.1/§6.3 replace_if) is not a valid must-fire unit.
    Planted in-test: both copies shortened to 1023 bytes."""
    s = load(VALID)
    msgs = s["prefix"]["messages"]
    short = msgs[3]["content"][:1023]
    msgs[3]["content"] = short
    msgs[7]["content"] = short
    assert "MUST_FIRE_NOT_REPEATED" in codes(suite_schema.validate(s))


# --- (2) the suite set --------------------------------------------------------

ALL_IDS = ["A1", "A2", "A3", "A4", "A5", "B1", "B2", "B3", "B4", "M1", "M2", "M3", "R1", "R2", "R3"]


def test_spec0001_suite_id_set_exact_accepted():
    """Row test (2), positive control: exactly the 15 §9.4 IDs is accepted.
    Passes on the RED stub by design."""
    assert suite_schema.validate_suite_ids(ALL_IDS) == []


@pytest.mark.parametrize("ids", [
    ALL_IDS[:-1],                                   # 14: R3 missing
    ALL_IDS + ["R4"],                               # 16: extra ID
    [i if i != "A5" else "A6" for i in ALL_IDS],    # wrong ID
    [i if i != "A1" else "A10" for i in ALL_IDS],   # suffix-extension mutant
    [i if i != "M1" else "M" for i in ALL_IDS],     # prefix mutant
    ALL_IDS + ["A1"],                               # duplicate ID
], ids=["missing", "extra", "wrong", "suffix_ext", "prefix", "duplicate"])
def test_spec0001_suite_id_set_not_exact_rejected(ids):
    """Row test (2): the suite set must hold exactly A1-A5, B1-B4, M1-M3, R1-R3
    (§9.4 scenario table). Missing, extra, wrong, near-miss or duplicated IDs
    are SCENARIO_SET_MISMATCH."""
    assert "SCENARIO_SET_MISMATCH" in codes(suite_schema.validate_suite_ids(ids))


def test_spec0001_suite_loader_reads_scenarios_by_id(tmp_path):
    """Row test (2) support: load_suite reads every scenario JSON in a
    directory, keyed by its `id` (synthetic mini fixture copied to tmp)."""
    import json
    s = load(VALID)
    (tmp_path / "A1.json").write_text(json.dumps(s), encoding="utf-8")
    suite = suite_schema.load_suite(tmp_path)
    assert list(suite) == ["A1"] and suite["A1"]["endpoint"] == "/v1/chat/completions"


def test_spec0001_suite_real_set_is_exactly_the_15_scenarios():
    """Row test (2) over the REAL set: the suite's scenarios directory holds
    exactly the 15 §9.4 IDs, each valid. It was a strict expected failure in
    increment 14 (empty set); increment 17 filled the set and removed the
    marker, so it must pass."""
    suite = suite_schema.load_suite()
    assert set(suite) == set(ALL_IDS)
    assert suite_schema.validate_suite_ids(list(suite)) == []
    for sid, scenario in suite.items():
        assert suite_schema.validate(scenario) == [], sid


# --- review fixes (orchestrator.81.reviewer.1): validator codes pinned -------
# Characterization tests for validator paths that existed untested after
# increment 14 GREEN. Each was shown able to fail by a planted edit of
# suite_schema.py in a scratch copy (orchestrator.83.tester.2).

def test_spec0001_suite_reference_wrong_ordinal_rejected():
    """§6.4 ORDINAL; DEDUP_STUB_FORMAT_EXACT. Planted fixture: the must-fire
    reference says `tool result #2 (read_file)` where the first occurrence
    (message 3) is tool result #1. Then REFERENCE_INVALID."""
    findings = suite_schema.validate(load("planted_wrong_ordinal.json"))
    assert "REFERENCE_INVALID" in codes(findings)


@pytest.mark.parametrize("reference", [
    "tool result 1 (read_file)",         # no '#'
    "tool result #01 (read_file)",       # padded ordinal
    "tool result #1 (read:file)",        # name outside ^[A-Za-z0-9_.-]{1,64}$
    "user message #1 (read_file)",       # a name on a non-tool role
    "tool results #1",                   # ROLEWORD near miss
    None,                                # no reference at all
], ids=["no_hash", "padded", "bad_name_char", "name_on_user", "roleword_near_miss", "missing"])
def test_spec0001_suite_reference_outside_ref_grammar_rejected(reference):
    """§6.4 REF grammar: ROLEWORD " #" ORDINAL [ " (" TOOLNAME ")" ]. A
    must-fire reference that does not parse is REFERENCE_INVALID."""
    s = load(VALID)
    s["manifest"]["must_fire"][0]["reference"] = reference
    assert "REFERENCE_INVALID" in codes(suite_schema.validate(s))


def test_spec0001_suite_reference_wrong_role_rejected():
    """§6.4 ROLEWORD is the role shared by the stubbed unit and its first
    occurrence (DEDUP_REFERENCE_SAME_ROLE_ONLY). `user message #1` for a tool
    repeat is REFERENCE_INVALID."""
    s = load(VALID)
    s["manifest"]["must_fire"][0]["reference"] = "user message #1"
    assert "REFERENCE_INVALID" in codes(suite_schema.validate(s))


# Optional fields (turns, manifest.enable_from_turn, checker.answer_span,
# anthropic_prefix), used by increments 17/18. The valid mini prefix has 12
# messages; message 3 is a 1112-byte tool unit.
VALID_OPTIONALS = {
    "turns": [4, 12],
    "enable_from_turn": 2,
    "answer_span": {"message": 3, "part": None, "start": 0, "end": 5},
    "anthropic_prefix": {"messages": [{"role": "user", "content": "synthetic"}]},
}


def with_optionals(**override):
    s = load(VALID)
    o = {**VALID_OPTIONALS, **override}
    s["turns"] = o["turns"]
    s["manifest"]["enable_from_turn"] = o["enable_from_turn"]
    s["manifest"]["checker"]["answer_span"] = o["answer_span"]
    s["anthropic_prefix"] = o["anthropic_prefix"]
    return s


def test_spec0001_suite_optional_fields_valid_accepted():
    """Positive control for the optional-field checks: well-formed turns,
    enable_from_turn, answer_span and anthropic_prefix validate clean."""
    assert suite_schema.validate(with_optionals()) == []


@pytest.mark.parametrize("override", [
    {"turns": [4, 11]},                                   # last != len(prefix.messages)
    {"turns": [12, 4, 12]},                               # not strictly increasing
    {"turns": [0, 12]},                                   # a count < 1
    {"turns": []},                                        # empty
    {"turns": [4, 12], "enable_from_turn": 3},            # beyond the turns
    {"enable_from_turn": 0},                              # not 1-based
    {"enable_from_turn": True},                           # bool is not an int
    {"answer_span": {"message": 3, "part": None, "start": 5, "end": 5}},     # empty span
    {"answer_span": {"message": 3, "part": None, "start": 0, "end": 1113}},  # past the unit
    {"answer_span": {"message": 99, "part": None, "start": 0, "end": 1}},    # not a unit
    {"anthropic_prefix": {"messages": []}},               # no messages
    {"anthropic_prefix": ["not", "an", "object"]},
], ids=["turns_last", "turns_order", "turns_zero", "turns_empty", "eft_beyond", "eft_zero",
        "eft_bool", "span_empty", "span_past_end", "span_not_unit", "anthropic_empty",
        "anthropic_not_object"])
def test_spec0001_suite_optional_field_malformed_rejected(override):
    """Increment 17/18 optional fields: a malformed value is FIELD_INVALID
    (checked only when present)."""
    assert "FIELD_INVALID" in codes(suite_schema.validate(with_optionals(**override)))


@pytest.mark.parametrize("schema", ["message_dedup.scenario/2", "message_dedup.scenario/1x",
                                    "message_dedup.scenario", "", None])
def test_spec0001_suite_schema_id_unknown_rejected(schema):
    """Scenario document `schema`: optional, but if present exactly
    `message_dedup.scenario/1`. Anything else (near misses included) is
    SCHEMA_UNKNOWN."""
    s = load(VALID)
    s["schema"] = schema
    assert "SCHEMA_UNKNOWN" in codes(suite_schema.validate(s))


@pytest.mark.parametrize("key,units", [
    ("must_not_fire", [{"message": 99, "part": None}]),         # index past the prefix
    ("must_not_fire", [{"message": 11, "part": 0}]),            # a part of string content
    ("must_not_fire", [{"message": 2, "part": None}]),          # empty content: no §6.3 unit
    ("must_not_fire", [{"part": None}]),                        # no 'message'
    ("must_not_fire", [{"message": 11, "part": None}, {"message": 11, "part": None}]),  # listed twice
    ("must_fire", [{"message": 7, "part": None, "reference": "tool result #1 (read_file)"},
                   {"message": 7, "part": None, "reference": "tool result #1 (read_file)"}]),
], ids=["bad_index", "part_on_string", "empty_content", "no_message", "twice_not_fire", "twice_fire"])
def test_spec0001_suite_manifest_unit_invalid_rejected(key, units):
    """§6.3 unit: prefix.messages[message].content (part null) or a text part.
    A manifest entry that names no unit, or names one twice, is UNIT_INVALID."""
    s = load(VALID)
    s["manifest"][key] = units
    assert "UNIT_INVALID" in codes(suite_schema.validate(s))


def test_spec0001_suite_unit_both_must_fire_and_must_not_fire_rejected():
    """A unit cannot be both must-fire and must-not-fire: message 7 listed in
    both lists is UNIT_INVALID."""
    s = load(VALID)
    s["manifest"]["must_not_fire"].append({"message": 7, "part": None})
    assert "UNIT_INVALID" in codes(suite_schema.validate(s))


# --- review Minor 1 (RED): the TOOLNAME of a reference is checked -------------
# §6.4 TOOLNAME (DEDUP_TOOLNAME_ALLOWLIST): only for "tool result". Candidate:
# the function.name of the latest earlier assistant tool_call whose id == the
# first occurrence's tool_call_id; else the tool message's own string "name".
# Rendered only if the whole candidate matches ^[A-Za-z0-9_.-]{1,64}$, else the
# group is omitted. The manifest reference must carry exactly that group.
# In the valid mini scenario the first occurrence is message 3 (call_1), paired
# with message 2's call_1 `read_file`.

def _unpair_first_occurrence(s, own_name=None):
    """Message 3 no longer pairs with any call; optionally give it its own name."""
    s["prefix"]["messages"][3]["tool_call_id"] = "call_unpaired"
    if own_name is not None:
        s["prefix"]["messages"][3]["name"] = own_name
    return s


@pytest.mark.parametrize("case", ["wrong_name", "name_omitted_from_call", "name_omitted_from_own_name",
                                  "name_where_none_determined", "call_name_over_own_name"])
def test_spec0001_suite_reference_toolname_mismatch_rejected(case):
    """Review Minor 1 (RED). §6.4 TOOLNAME: the manifest reference's
    ` (TOOLNAME)` group must be exactly the one the prefix determines for the
    first occurrence. A wrong name, an omitted name that is determined, or a
    name where none is determined is REFERENCE_INVALID."""
    s = load(VALID)
    ref = s["manifest"]["must_fire"][0]
    if case == "wrong_name":
        ref["reference"] = "tool result #1 (grep)"                # determined: read_file
    elif case == "name_omitted_from_call":
        ref["reference"] = "tool result #1"                       # determined: read_file
    elif case == "name_omitted_from_own_name":
        _unpair_first_occurrence(s, own_name="grep")
        ref["reference"] = "tool result #1"                       # determined: grep (own name)
    elif case == "name_where_none_determined":
        _unpair_first_occurrence(s)
        ref["reference"] = "tool result #1 (read_file)"           # nothing determined
    elif case == "call_name_over_own_name":
        s["prefix"]["messages"][3]["name"] = "grep"
        ref["reference"] = "tool result #1 (grep)"                # the paired call wins: read_file
    assert "REFERENCE_INVALID" in codes(suite_schema.validate(s))


@pytest.mark.parametrize("case", ["from_call", "from_own_name", "disallowed_name_omitted",
                                  "later_call_with_same_id_ignored", "none_determined"])
def test_spec0001_suite_reference_toolname_determined_accepted(case):
    """Review Minor 1, positive controls (pass now; they pin the GREEN against
    over-rejection). The correct group is accepted: the paired call's name,
    the tool message's own name when no call pairs, the group omitted for a
    name outside the allowlist, a call with the same id AFTER the first
    occurrence ignored ("latest earlier"), and no group when nothing is
    determined."""
    s = load(VALID)
    msgs = s["prefix"]["messages"]
    ref = s["manifest"]["must_fire"][0]
    if case == "from_call":
        ref["reference"] = "tool result #1 (read_file)"
    elif case == "from_own_name":
        _unpair_first_occurrence(s, own_name="grep")
        ref["reference"] = "tool result #1 (grep)"
    elif case == "disallowed_name_omitted":
        msgs[2]["tool_calls"][0]["function"]["name"] = "ns:read_file"
        ref["reference"] = "tool result #1"
    elif case == "later_call_with_same_id_ignored":
        msgs[4]["tool_calls"][0]["id"] = "call_1"
        msgs[4]["tool_calls"][0]["function"]["name"] = "grep"
        msgs[5]["tool_call_id"] = "call_1"
        ref["reference"] = "tool result #1 (read_file)"
    elif case == "none_determined":
        _unpair_first_occurrence(s)
        ref["reference"] = "tool result #1"
    assert suite_schema.validate(s) == []


# --- increment-18 re-review (orchestrator.91.reviewer.5): manifest.embedded_block (B3)

def test_spec0001_suite_b3_embedded_block_in_every_user_message():
    """§9.4 B3 "the same 2 KiB block embedded inside each user message's
    single text string": the real B3 manifest names the block as
    ``embedded_block`` (a string of 2055 UTF-8 bytes, gen_scenarios
    ``reminder(...)``), and it occurs verbatim exactly once in each of the 8
    user messages of the B3 prefix."""
    s = suite_schema.load_suite()["B3"]
    block = s["manifest"].get("embedded_block")
    assert isinstance(block, str), "B3 manifest has no string embedded_block"
    assert len(block.encode("utf-8")) == 2055
    users = [m["content"] for m in s["prefix"]["messages"] if m["role"] == "user"]
    assert len(users) == 8
    assert [u.count(block) for u in users] == [1] * 8


def with_embedded_block(block):
    s = load(VALID)
    s["manifest"]["embedded_block"] = block
    return s


def test_spec0001_suite_embedded_block_present_accepted():
    """Positive control: an ``embedded_block`` that is text of the prefix
    (here a user message's own content) validates clean."""
    s = load(VALID)
    user = next(m["content"] for m in s["prefix"]["messages"] if m["role"] == "user")
    assert isinstance(user, str) and user
    assert suite_schema.validate(with_embedded_block(user)) == []


@pytest.mark.parametrize("block", [123, None, ["a"], "", "text that is nowhere in the prefix 7f3a"],
                         ids=["int", "null", "list", "empty", "absent_text"])
def test_spec0001_suite_embedded_block_malformed_rejected(block):
    """``manifest.embedded_block`` (optional): a non-string, an empty string,
    or text that does not occur in the prefix is FIELD_INVALID."""
    assert "FIELD_INVALID" in codes(suite_schema.validate(with_embedded_block(block)))
