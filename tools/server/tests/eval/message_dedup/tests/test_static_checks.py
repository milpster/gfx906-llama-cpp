#!/usr/bin/env python
"""SPEC-0001 increment 14 (RED): static stub checks through /apply-template.

Row: docs/graph/plans/grill/spec-0001-inc-14-eval-harness-and-transcripts.md,
tests (4)-(7). Spec §9.4 AC_Q04 (ii)/(iii), AC_Q05 (i), AC_Q08
(/apply-template part); contracts DEDUP_FIRST_OCCURRENCE_UNCHANGED,
DEDUP_EQUIVALENT_TO_MANUAL_SUBSTITUTION, DEDUP_OFF_BY_OVERRIDE_PROMPT_UNCHANGED,
DEDUP_STUB_FORMAT_EXACT; failure mode §7 DEDUP_FIRST_OCCURRENCE_NOT_RENDERED.

Each check is shown red on a planted fixture: a wrong ordinal in the
manifest (6), a unit that is an exact repeat where the manifest says
must-not-fire (7), and a template that drops `tool` messages (4)/(5)
(tools/server/tests/fixtures/message_dedup/last_tool_only.jinja). The valid
mini scenario is the positive control for every check (it passes on the RED
stub by design).

Server: tinyllama2 (ServerPreset, the SPEC-0001 test model), started without
--message-dedup; the dedup arm enables the pass through the per-request
`message_dedup` override. Run from tools/server/tests.
"""
import pytest

from _paths import SERVER_TESTS_DIR, load

from utils import *  # noqa: E402,F403
from fixtures.message_dedup import dedup_goldens as goldens  # noqa: E402

import static_checks  # noqa: E402

VALID = "valid_scenario.json"
DROP_TOOL_TEMPLATE = str(SERVER_TESTS_DIR / "fixtures" / "message_dedup" / "last_tool_only.jinja")

server: ServerProcess  # noqa: F405


def codes(findings) -> set[str]:
    return {f.code for f in findings}


def start(server_key: str = "tinyllama2_chatml", template_file: str | None = None):
    global server
    server = goldens.make_server(server_key)
    if template_file is not None:
        server.chat_template = None
        server.chat_template_file = template_file
    server.start()
    return lambda body: goldens.render(server, body)


# --- (4) AC_Q04 (iii) manifest check -----------------------------------------

def test_spec0001_suite_manifest_check_valid_passes():
    """Row test (4), positive control. AC_Q04 (iii): with the pass off,
    /apply-template of the prefix holds every manifest unit in full."""
    render = start()
    assert static_checks.manifest_check(load(VALID), render) == []


def test_spec0001_suite_manifest_check_unit_missing_reported():
    """Row test (4); AC_Q04 (iii) maps to DEDUP_OFF_BY_OVERRIDE_PROMPT_UNCHANGED.
    Planted: a template that drops `tool` messages (renders only the last),
    so the must-fire unit (message 7) is absent from the off-arm render.
    Then MANIFEST_UNIT_NOT_RENDERED."""
    render = start(template_file=DROP_TOOL_TEMPLATE)
    findings = static_checks.manifest_check(load(VALID), render)
    assert "MANIFEST_UNIT_NOT_RENDERED" in codes(findings)


# --- (5) AC_Q04 (ii) template check ------------------------------------------

@pytest.mark.parametrize("server_key", ["tinyllama2_chatml", "tinyllama2_qwen35_template"])
def test_spec0001_suite_template_check_valid_passes(server_key):
    """Row test (5), positive control, under chatml and under the profile's
    chat template (models/templates/Qwen3.5-4B.jinja). AC_Q04 (ii): every
    first occurrence appears byte for byte in the /apply-template output."""
    render = start(server_key)
    assert static_checks.template_check(load(VALID), render) == []


def test_spec0001_suite_template_check_first_occurrence_not_rendered_reported():
    """Row test (5); AC_Q04 (ii) maps to DEDUP_FIRST_OCCURRENCE_UNCHANGED,
    DEDUP_EQUIVALENT_TO_MANUAL_SUBSTITUTION; §7 DEDUP_FIRST_OCCURRENCE_NOT_RENDERED.
    Planted: the drop-tool template hides the first occurrence (message 3).
    Then the check reports DEDUP_FIRST_OCCURRENCE_NOT_RENDERED."""
    render = start(template_file=DROP_TOOL_TEMPLATE)
    findings = static_checks.template_check(load(VALID), render)
    assert "DEDUP_FIRST_OCCURRENCE_NOT_RENDERED" in codes(findings)


# --- (6) AC_Q05 (i) static fire check ----------------------------------------

def test_spec0001_suite_fire_check_valid_passes():
    """Row test (6), positive control. AC_Q05 (i): on the dedup arm,
    /apply-template holds exactly the manifest's stubs, each at its unit's
    position and byte-identical to the §6.4 stub (dedup_goldens.ref_stub)."""
    render = start()
    assert static_checks.fire_check(load(VALID), render) == []


def test_spec0001_suite_fire_check_wrong_ordinal_reported():
    """Row test (6); AC_Q05 (i) maps to DEDUP_STUB_FORMAT_EXACT. Planted: the
    manifest's reference says `tool result #2 (read_file)` where the server
    (correctly) renders `tool result #1 (read_file)`. The expected stub built
    from the manifest differs from the render, so STUB_MISMATCH."""
    render = start()
    findings = static_checks.fire_check(load("planted_wrong_ordinal.json"), render)
    assert "STUB_MISMATCH" in codes(findings)


def test_spec0001_suite_fire_check_missing_manifest_stub_reported():
    """Row test (6), "exactly the manifest's stubs": the server stubs message 7
    but the manifest lists no must-fire unit (planted in-test by emptying
    must_fire). An unlisted stub in the render is STUB_MISMATCH."""
    render = start()
    s = load(VALID)
    s["manifest"]["must_fire"] = []
    assert "STUB_MISMATCH" in codes(static_checks.fire_check(s, render))


# --- (7) AC_Q08 must-not-fire, /apply-template part --------------------------

def test_spec0001_suite_must_not_fire_check_valid_passes():
    """Row test (7), positive control: the near-duplicate re-read (message 11,
    one byte changed from message 5) renders in full on the dedup arm
    (DEDUP_NEAR_DUPLICATE_UNCHANGED via AC_Q08)."""
    render = start()
    assert static_checks.must_not_fire_check(load(VALID), render) == []


def test_spec0001_suite_must_not_fire_check_exact_repeat_reported():
    """Row test (7); AC_Q08. Planted: the manifest lists message 11 as
    must-not-fire, but it is an exact >= 1024-byte repeat of message 5, so the
    pass stubs it on the dedup arm. Then MUST_NOT_FIRE_STUBBED."""
    render = start()
    findings = static_checks.must_not_fire_check(load("planted_must_not_fire_exact_repeat.json"), render)
    assert "MUST_NOT_FIRE_STUBBED" in codes(findings)
