"""SPEC-0001 §9.4 scenario suite: static checks through /apply-template.

Tool card: docs/graph/tools/message-dedup-scenario-suite.md.
Tests: tests/test_static_checks.py (increment 14, row tests (4)-(7)).

Every check takes a scenario document (the shape suite_schema.validate
accepts) and ``render``, a callable that POSTs a request body to the served
model's ``/apply-template`` and returns its ``prompt`` string (for example
``SuiteHttp.apply_template`` or ``dedup_goldens.render`` bound to a server).
Each check builds its arm bodies with ``suite_schema.arm_body``:

- off arm:   prefix + ``"message_dedup": {"enabled": false}``
- dedup arm: prefix + ``"message_dedup": {"enabled": true, "roles": manifest.dedup_roles}``
  (+ ``min_bytes`` when the manifest sets it)

A check returns ``list[suite_schema.Finding]``; empty == pass. The checks do
NOT re-run suite_schema.validate (run it first); a manifest unit that names
no §6.3 unit is reported as ``UNIT_INVALID``. Errors from ``render`` propagate.

Copy counts are whole-prefix: a unit's text must be in the render as many
times as the whole prefix holds it (any role), so a later full copy cannot
hide a dropped or stubbed unit.

- ``manifest_check`` (AC_Q04 (iii)): on the off arm every manifest unit is in
  the render in full, as many times as the whole prefix holds it. Code
  ``MANIFEST_UNIT_NOT_RENDERED``.
- ``template_check`` (AC_Q04 (ii)): the first occurrence (§6.3) of every
  must-fire unit is in the render of the manual substitution (the off arm of
  the prefix with each must-fire unit replaced by its stub, the render the
  dedup arm must equal) as many times as the whole prefix holds it outside
  must-fire units. The repeats are stubs there, so only the first occurrence
  (and copies under other roles, which are counted) can supply the text: a
  template that drops the first occurrence is caught whether or not the pass
  fired. Code ``DEDUP_FIRST_OCCURRENCE_NOT_RENDERED`` (§7).
- ``fire_check`` (AC_Q05 (i)): the dedup-arm render equals, byte for byte, the
  render of the manual substitution (DEDUP_EQUIVALENT_TO_MANUAL_SUBSTITUTION).
  That is "exactly the manifest's stubs, each at its unit's position". The
  expected stub is built from the manifest's reference by the test-side
  builder ``dedup_goldens.ref_stub``. Code ``STUB_MISMATCH``.
- ``must_not_fire_check`` (AC_Q08, /apply-template part): on the dedup arm every
  must-not-fire unit is in the render in full, as many times as the whole
  prefix holds it outside must-fire units. Code ``MUST_NOT_FIRE_STUBBED``.

Special texts: ``template_check`` and ``fire_check`` take the served
vocab's §4.0 special-text list explicitly. Get it with
``vocab_special_texts.vocab_special_texts(<model.gguf>)``. The default, an
empty list, is right only for a vocab whose special texts cannot occur in a
stub or in the first 40 bytes of a stubbed unit (the tinyllama2 mini
fixtures). In ``fire_check`` a wrong list shows up as ``STUB_MISMATCH``, never
as a pass. ``template_check`` counts only first-occurrence text, which the
stub text does not change, so its default is always safe.
"""
from __future__ import annotations

import copy
import sys
from typing import Callable, Sequence

import suite_schema
from suite_schema import Finding

# dedup_goldens lives under tools/server/tests; the tests put it on sys.path
# themselves (tests/_paths.py), this makes the module importable on its own.
_SERVER_TESTS_DIR = suite_schema.SUITE_DIR.parents[1]      # tools/server/tests
if str(_SERVER_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SERVER_TESTS_DIR))
from fixtures.message_dedup import dedup_goldens  # noqa: E402  (the §6.4 reference stub builder)

Render = Callable[[dict], str]


def _where(message: int, part) -> str:
    return f"message {message}" + ("" if part is None else f" part {part}")


def _units(scenario: dict, key: str, out: list[Finding]) -> list[tuple[int, object, str]]:
    """(message, part, text) of every manifest unit under ``key``; bad ones -> UNIT_INVALID."""
    units = []
    for n, u in enumerate(scenario["manifest"][key]):
        msg, part = (u.get("message"), u.get("part")) if isinstance(u, dict) else (None, None)
        text = suite_schema.unit_text(scenario, msg, part)
        if text is None:
            out.append(Finding("UNIT_INVALID", f"manifest.{key}[{n}]: message {msg!r} part {part!r} is not a unit"))
            continue
        units.append((msg, part, text))
    return units


def _copies(scenario: dict, text: str, exclude: set = frozenset()) -> int:
    """How many units of the whole prefix (any role), outside ``exclude``, have exactly ``text``."""
    return sum(1 for i, k, _r, t in suite_schema.iter_units(scenario) if t == text and (i, k) not in exclude)


def _must_fire_keys(scenario: dict) -> set:
    return {(u.get("message"), u.get("part")) for u in scenario["manifest"]["must_fire"] if isinstance(u, dict)}


def _manual_substitution(scenario: dict, fire_units: list, special_texts: Sequence[str],
                         out: list[Finding]) -> dict:
    """A copy of the scenario with each must-fire unit (``_units(scenario,
    "must_fire", ...)``) replaced by the §6.4 stub built from its manifest
    reference; a unit with no stub -> STUB_MISMATCH."""
    expected = copy.deepcopy(scenario)
    msgs = suite_schema.messages_of(expected)
    for msg, part, text in fire_units:
        unit = next(u for u in scenario["manifest"]["must_fire"]
                    if isinstance(u, dict) and u.get("message") == msg and u.get("part") == part)
        parsed = suite_schema.parse_reference(unit.get("reference"))
        if parsed is None:
            out.append(Finding("STUB_MISMATCH", f"{_where(msg, part)}: reference {unit.get('reference')!r} "
                                                f"is not a §6.4 REF"))
            continue
        role, ordinal, toolname = parsed
        stub = dedup_goldens.ref_stub(text, role, ordinal, toolname, list(special_texts))
        if stub is None:
            out.append(Finding("STUB_MISMATCH", f"{_where(msg, part)}: no conforming §6.4 stub exists for this unit"))
            continue
        if part is None:
            msgs[msg]["content"] = stub
        else:
            msgs[msg]["content"][part]["text"] = stub
    return expected


def manifest_check(scenario: dict, render: Render) -> list[Finding]:
    out: list[Finding] = []
    units = _units(scenario, "must_fire", out) + _units(scenario, "must_not_fire", out)
    if not units:
        return out
    prompt = render(suite_schema.arm_body(scenario, "off"))
    for msg, part, text in units:
        need = _copies(scenario, text)
        have = prompt.count(text)
        if have < need:
            out.append(Finding("MANIFEST_UNIT_NOT_RENDERED",
                               f"{_where(msg, part)} ({len(text.encode('utf-8'))} bytes): off-arm render holds "
                               f"{have} full copies, the whole prefix has {need}"))
    return out


def template_check(scenario: dict, render: Render, special_texts: Sequence[str] = ()) -> list[Finding]:
    out: list[Finding] = []
    firsts = []
    fire_units = _units(scenario, "must_fire", out)
    for msg, part, _text in fire_units:
        first = suite_schema.first_occurrence(scenario, msg, part)
        if first is None:
            out.append(Finding("MUST_FIRE_NOT_REPEATED", f"{_where(msg, part)}: no earlier same-role copy"))
            continue
        if first not in [f for f, _ in firsts]:
            firsts.append((first, msg))
    if not firsts:
        return out
    n_before = len(out)
    expected = _manual_substitution(scenario, fire_units, special_texts, out)
    if len(out) > n_before:
        return out      # no stub to stand in for a repeat: nothing to render
    prompt = render(suite_schema.arm_body(expected, "off"))
    fire = _must_fire_keys(scenario)
    for (fm, fp), repeat in firsts:
        text = suite_schema.unit_text(scenario, fm, fp)
        need = _copies(scenario, text, exclude=fire)
        have = prompt.count(text)
        if have < need:
            out.append(Finding("DEDUP_FIRST_OCCURRENCE_NOT_RENDERED",
                               f"first occurrence {_where(fm, fp)} (of the repeat at message {repeat}) is not "
                               f"rendered byte for byte: the manual-substitution render holds {have} full copies, "
                               f"the whole prefix has {need} outside must-fire units"))
    return out


def _first_difference(a: str, b: str) -> str:
    n = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
    return (f"first difference at char {n} of {len(a)} (expected) / {len(b)} (rendered): "
            f"expected {a[n:n + 60]!r}, rendered {b[n:n + 60]!r}")


def fire_check(scenario: dict, render: Render, special_texts: Sequence[str] = ()) -> list[Finding]:
    out: list[Finding] = []
    expected = _manual_substitution(scenario, _units(scenario, "must_fire", out), special_texts, out)
    if out:
        return out
    want = render(suite_schema.arm_body(expected, "off"))
    got = render(suite_schema.arm_body(scenario, "dedup"))
    if want != got:
        stub_prefix = "[duplicate content omitted"
        out.append(Finding("STUB_MISMATCH",
                           f"dedup-arm render differs from the manual substitution of the manifest's "
                           f"{len(scenario['manifest']['must_fire'])} stub(s) "
                           f"(stub prefixes: expected {want.count(stub_prefix)}, rendered {got.count(stub_prefix)}); "
                           + _first_difference(want, got)))
    return out


def must_not_fire_check(scenario: dict, render: Render) -> list[Finding]:
    out: list[Finding] = []
    units = _units(scenario, "must_not_fire", out)
    if not units:
        return out
    fire = _must_fire_keys(scenario)
    prompt = render(suite_schema.arm_body(scenario, "dedup"))
    for msg, part, text in units:
        need = _copies(scenario, text, exclude=fire)
        have = prompt.count(text)
        if have < need:
            out.append(Finding("MUST_NOT_FIRE_STUBBED",
                               f"{_where(msg, part)} ({len(text.encode('utf-8'))} bytes): dedup-arm render holds "
                               f"{have} full copies, {need} expected (the unit was stubbed)"))
    return out
