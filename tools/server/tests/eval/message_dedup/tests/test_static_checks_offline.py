#!/usr/bin/env python
"""SPEC-0001 increment 14 review fixes (RED): static-check gaps, no server.

Review orchestrator.81.reviewer.1, Minors 2 and 3 of increment 14
(docs/graph/plans/grill/spec-0001-inc-14-eval-harness-and-transcripts.md).
Contracts: DEDUP_OFF_BY_OVERRIDE_PROMPT_UNCHANGED (AC_Q04 (iii)),
DEDUP_FIRST_OCCURRENCE_UNCHANGED (AC_Q04 (ii); §7
DEDUP_FIRST_OCCURRENCE_NOT_RENDERED), DEDUP_NEAR_DUPLICATE_UNCHANGED (AC_Q08,
/apply-template part).

The checks take ``render`` as a callable, so these tests feed a pure-Python
fake of /apply-template: a chatml-like renderer that can drop given messages
(a template bug) and, on the dedup arm, replace given messages with a stub
(what the server's pass did). Synthetic mini fixture only.

- Minor 2: manifest_check and must_not_fire_check count full copies only up to
  the unit, so a later unstubbed full copy hides a wrongly dropped or stubbed
  unit. The required count is the whole-prefix count of copies (on the dedup
  arm: of copies that are not must-fire units).
- Minor 3: template_check tests ``text in prompt``, which an unstubbed repeat
  (the pass did not fire) or a copy under another role satisfies when the
  template dropped the first occurrence.
"""
import pytest

from _paths import load  # noqa: F401  (also sets sys.path)

import static_checks  # noqa: E402

VALID = "valid_scenario.json"
FAKE_STUB = "[duplicate content omitted: fake stub]"


def codes(findings) -> set[str]:
    return {f.code for f in findings}


def fake_render(drop=(), stub=()):
    """A fake /apply-template. ``drop``: message indices the "template" never
    renders (on either arm). ``stub``: message indices the "pass" replaces with
    a stub on the dedup arm. Everything else renders its content in full."""
    def render(body: dict) -> str:
        dedup_on = bool(body.get("message_dedup", {}).get("enabled"))
        out = []
        for i, m in enumerate(body["messages"]):
            if i in drop:
                continue
            c = m.get("content")
            if isinstance(c, list):
                c = "".join(p.get("text", "") for p in c if isinstance(p, dict))
            if dedup_on and i in stub:
                c = FAKE_STUB
            out.append(f"<|im_start|>{m['role']}\n{c or ''}<|im_end|>\n")
        return "".join(out) + "<|im_start|>assistant\n"
    return render


def with_later_copy(s, of_message: int, call_id: str = "call_6"):
    """Append an assistant call and a tool result that is a full copy of
    ``of_message`` (messages 12 and 13), unlisted in the manifest."""
    msgs = s["prefix"]["messages"]
    msgs.append({"role": "assistant", "content": "", "tool_calls": [
        {"id": call_id, "type": "function", "function": {"name": "read_file", "arguments": "{}"}}]})
    msgs.append({"role": "tool", "tool_call_id": call_id, "content": msgs[of_message]["content"]})
    return s


# --- Minor 2: manifest_check (off arm) ---------------------------------------

def test_spec0001_suite_manifest_check_later_copy_valid_passes():
    """Positive control: every copy rendered on the off arm -> no finding."""
    s = with_later_copy(load(VALID), of_message=7)
    assert static_checks.manifest_check(s, fake_render()) == []


def test_spec0001_suite_manifest_check_dropped_unit_hidden_by_later_copy_reported():
    """Review Minor 2 (RED). AC_Q04 (iii) / DEDUP_OFF_BY_OVERRIDE_PROMPT_UNCHANGED:
    the off-arm render holds every manifest unit in full. Given the must-fire
    unit (message 7) with a later full copy (message 13), When the template
    drops message 7, Then MANIFEST_UNIT_NOT_RENDERED: the render holds 2
    copies of the text, the whole prefix holds 3."""
    s = with_later_copy(load(VALID), of_message=7)
    findings = static_checks.manifest_check(s, fake_render(drop={7}))
    assert "MANIFEST_UNIT_NOT_RENDERED" in codes(findings)


# --- Minor 2: must_not_fire_check (dedup arm) --------------------------------

def _exact_repeat_not_fire():
    """Message 11 made an exact repeat of message 5 (the planted shape of
    planted_must_not_fire_exact_repeat.json) and a later copy at message 13."""
    s = load(VALID)
    msgs = s["prefix"]["messages"]
    msgs[11]["content"] = msgs[5]["content"]
    return with_later_copy(s, of_message=5)


def test_spec0001_suite_must_not_fire_check_later_copy_valid_passes():
    """Positive control: the pass stubs only the must-fire unit (message 7);
    must-not-fire message 11 and the later copy render in full."""
    s = _exact_repeat_not_fire()
    assert static_checks.must_not_fire_check(s, fake_render(stub={7})) == []


def test_spec0001_suite_must_not_fire_stubbed_hidden_by_later_copy_reported():
    """Review Minor 2 (RED). AC_Q08: every must-not-fire unit renders in full on
    the dedup arm. Given must-not-fire message 11 (an exact repeat of message
    5) and a later unstubbed copy (message 13), When the pass stubs message 11,
    Then MUST_NOT_FIRE_STUBBED: the render holds 2 copies, the prefix holds 3
    that are not must-fire units."""
    s = _exact_repeat_not_fire()
    findings = static_checks.must_not_fire_check(s, fake_render(stub={7, 11}))
    assert "MUST_NOT_FIRE_STUBBED" in codes(findings)


# --- Minor 3: template_check (dedup arm) -------------------------------------

def test_spec0001_suite_template_check_offline_valid_passes():
    """Positive control: the first occurrence (message 3) renders and the pass
    stubs the must-fire repeat (message 7)."""
    assert static_checks.template_check(load(VALID), fake_render(stub={7})) == []


def test_spec0001_suite_template_check_dropped_first_occurrence_pass_not_fired_reported():
    """Review Minor 3 (RED). AC_Q04 (ii) / DEDUP_FIRST_OCCURRENCE_UNCHANGED; §7
    DEDUP_FIRST_OCCURRENCE_NOT_RENDERED. Given a template that drops the first
    occurrence (message 3), When the pass does not fire (message 7 renders in
    full on the dedup arm), Then the check still reports
    DEDUP_FIRST_OCCURRENCE_NOT_RENDERED: the unstubbed repeat is not the first
    occurrence. (A copy count alone cannot tell the two apart here: one copy
    either way. The check must tie the text to the first occurrence, e.g. by
    rendering the body with each must-fire unit replaced by its stub.)"""
    findings = static_checks.template_check(load(VALID), fake_render(drop={3}))
    assert "DEDUP_FIRST_OCCURRENCE_NOT_RENDERED" in codes(findings)


def test_spec0001_suite_template_check_dropped_first_occurrence_other_role_copy_reported():
    """Review Minor 3 (RED), copy-count case. Given the first occurrence's text
    also sent earlier as a user message (message 1; §6.3 same-role rule, so
    message 3 stays the first occurrence), When the template drops message 3
    and the pass stubs message 7, Then DEDUP_FIRST_OCCURRENCE_NOT_RENDERED: the
    render holds 1 copy, the expected count of copies that are not must-fire
    units is 2."""
    s = load(VALID)
    msgs = s["prefix"]["messages"]
    msgs[1]["content"] = msgs[3]["content"]
    findings = static_checks.template_check(s, fake_render(drop={3}, stub={7}))
    assert "DEDUP_FIRST_OCCURRENCE_NOT_RENDERED" in codes(findings)
