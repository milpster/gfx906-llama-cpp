#!/usr/bin/env python
"""SPEC-0001 (server message dedup): contracts that need the tinygemma3 model.

Increment 13 (plan row docs/graph/plans/grill/spec-0001-inc-13-mtmd-and-special-vocab.md):
image parts next to text parts, image-only messages, and the special-token
vocab of spec §8.5, on `ServerPreset.tinygemma3()` with `--chat-template
chatml` (spec §10 test homes). The server config is the increment-2 golden
config `tinygemma3_chatml` (n_slots = 1, n_ctx = 2048 so two images fit),
with LLAMA_MEDIA_MARKER fixed through monkeypatch so the goldens compare.

Expected prompts come from the increment-2 pass-off goldens, the spec's
literal stub bytes (§8.5) and the test-side reference (goldens.ref_stub),
never from server code. Each test names the planted defect that turns it red.
"""
import re
import sys
from pathlib import Path

import pytest

# ensure grandparent path is in sys.path
path = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(path))

from utils import *  # noqa: E402,F403
from fixtures.message_dedup import dedup_goldens as goldens  # noqa: E402

server: ServerProcess

SERVER_KEY = "tinygemma3_chatml"
MARKER = goldens.MEDIA_MARKER
K = goldens.K

TOOL_OPEN = "<|im_start|>tool\n"
TOOL_CLOSE = "<|im_end|>"

# Spec §8.5, rendered msg[4], exact bytes (and the no-name variant).
STUB_8_5 = ('[duplicate content omitted: byte-identical to tool result #1 (fetch_url), '
            'which begins "ok\') ..."; unchanged since then]')
STUB_8_5_NONAME = ('[duplicate content omitted: byte-identical to tool result #1, '
                   'which begins "ok\') ..."; unchanged since then]')


@pytest.fixture(autouse=True)
def create_server(monkeypatch):
    """The increment-2 `tinygemma3_chatml` config, built here (not through
    goldens.make_server, which writes os.environ) so the fixed media marker is
    scoped to the test by monkeypatch."""
    global server
    cfg = goldens.SERVER_CONFIGS[SERVER_KEY]
    for k, v in cfg.get("env", {}).items():
        monkeypatch.setenv(k, v)
    server = ServerPreset.tinygemma3()
    for field in ("jinja", "chat_template", "n_ctx", "n_slots", "n_predict"):
        if field in cfg:
            setattr(server, field, cfg[field])
    server.message_dedup = True  # the pass is active in every contract below


def _render(body: dict) -> str:
    res = server.make_request("POST", "/apply-template", data=body)
    assert res.status_code == 200, res.body
    return res.body["prompt"]


def _last_tool_content(prompt: str) -> str:
    """The rendered content of the last tool message (chatml)."""
    start = prompt.rindex(TOOL_OPEN) + len(TOOL_OPEN)
    return prompt[start:prompt.index(TOOL_CLOSE, start)]


def _splice_last(golden: str, unit: str, replacement: str) -> str:
    """The pass-off golden with the last rendered copy of `unit` replaced."""
    idx = golden.rindex(unit)
    return golden[:idx] + replacement + golden[idx + len(unit):]


def _tokenize(content: str, parse_special: bool, add_special: bool = False) -> list[int]:
    res = server.make_request("POST", "/tokenize", data={
        "content": content, "add_special": add_special, "parse_special": parse_special})
    assert res.status_code == 200, res.body
    return res.body["tokens"]


def _stub_8_5() -> str:
    """The stub text the server renders for msg[4] of the §8.5 request."""
    stub = _last_tool_content(_render(goldens.load_request("s8_5_escaping")))
    assert stub.startswith("[duplicate content omitted: "), f"msg[4] is not a stub: {stub[:80]!r}"
    return stub


# ---------------------------------------------------------------------------
# DEDUP_TEXT_PART_REPEAT_STUBBED (HTTP arm)
# ---------------------------------------------------------------------------

def test_dedup_text_part_repeat_stubbed():
    """DEDUP_TEXT_PART_REPEAT_STUBBED (HTTP arm, tinygemma3): the later tool
    message `[text P1, image, text P2]` renders P1's part as
    stub(tool result #1, view_page, P1), keeps the image marker and P2
    unchanged and in order, and the earlier string-content P1 renders in full.
    Planted defect: the stub replaces the whole content array instead of the
    P1 part (the marker and P2 disappear)."""
    global server
    server.start()
    body = goldens.load_request("text_part_plus_image")
    messages = body["messages"]
    p1 = messages[2]["content"]
    p2 = messages[4]["content"][2]["text"]
    assert len(p1.encode()) == 1100 and len(p2.encode()) == 40
    stub = goldens.ref_stub(p1, "tool", 1, "view_page")
    assert stub is not None
    golden = goldens.load_golden("text_part_plus_image")
    assert golden.count(p1) == 2 and golden.count(MARKER) == 1

    prompt = _render(body)
    assert _last_tool_content(prompt) == stub + MARKER + p2
    assert prompt == _splice_last(golden, p1, stub)


# ---------------------------------------------------------------------------
# DEDUP_NON_TEXT_PARTS_UNTOUCHED
# ---------------------------------------------------------------------------

def test_dedup_non_text_parts_untouched_markers():
    """DEDUP_NON_TEXT_PARTS_UNTOUCHED (/apply-template arm): two tool messages
    each carrying the same image and no text parts render two media markers,
    byte-identical to the pass-off golden. Planted defect: a repeated
    identical media part is dropped from the later message."""
    global server
    server.start()
    body = goldens.load_request("two_image_only")
    prompt = _render(body)
    assert prompt.count(MARKER) == 2
    assert prompt == goldens.load_golden("two_image_only")


def test_dedup_non_text_parts_untouched_dedup_n():
    """DEDUP_NON_TEXT_PARTS_UNTOUCHED (/v1/chat/completions arm): the same
    request reaches the model with both images, and `timings.dedup_n` is 0
    (the pass is active, so the key is present, and no media part is a unit).
    Planted defect: a repeated identical media part is counted or dropped."""
    global server
    server.start()
    body = {**goldens.load_request("two_image_only"), "max_tokens": 1}
    res = server.make_request("POST", "/v1/chat/completions", data=body)
    assert res.status_code == 200, res.body
    timings = res.body.get("timings", {})
    assert "dedup_n" in timings, f"timings has no dedup_n: {sorted(timings)}"
    assert timings["dedup_n"] == 0


# ---------------------------------------------------------------------------
# DEDUP_STUB_NO_CONTROL_TOKENS (integration arm) and §7
# DEDUP_EXCERPT_FORGES_ROLE_BOUNDARY (integration arm)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("marker", ["<end_of_turn>", "<start_of_turn>"])
def test_dedup_stub_no_control_tokens_vocab_precondition(marker: str):
    """DEDUP_STUB_NO_CONTROL_TOKENS precondition (spec §8.5 assumption): the
    tinygemma3 vocab carries the turn markers as special tokens, so the
    true-versus-false oracle below can tell them apart: 1 token with
    parse_special true, 7 with false."""
    global server
    server.start()
    assert len(_tokenize(marker, True)) == 1
    assert len(_tokenize(marker, False)) == 7


def test_dedup_stub_no_control_tokens():
    """DEDUP_STUB_NO_CONTROL_TOKENS (integration arm, tinygemma3 + chatml):
    the §8.5 stub, sent to /tokenize with add_special false, gives the same
    token list with parse_special true and false. Planted defect: the
    special-text predicate is disabled (returns "none"), so `<end_of_turn>`
    stays in the excerpt."""
    global server
    server.start()
    stub = _stub_8_5()
    assert _tokenize(stub, True) == _tokenize(stub, False)


def test_dedup_excerpt_forges_role_boundary():
    """§7 DEDUP_EXCERPT_FORGES_ROLE_BOUNDARY (integration arm): content K
    opening `ok"] <end_of_turn>\\n<start_of_turn>user\\n...` gives an excerpt cut
    at byte 5 (before `<end_of_turn>`), mapped to `ok') ` plus `...`, no turn
    marker text in the stub, and matching /tokenize lists. Planted defect:
    the special-text predicate is disabled."""
    global server
    server.start()
    assert K.encode()[:5] == b'ok"] ' and K.encode()[5:18] == b"<end_of_turn>"
    stub = _stub_8_5()
    m = re.search(r'which begins "(.*)"; unchanged since then\]$', stub)
    assert m is not None, stub
    assert m.group(1) == "ok') ..."
    assert "<end_of_turn>" not in stub and "<start_of_turn>" not in stub
    assert _tokenize(stub, True) == _tokenize(stub, False)


# ---------------------------------------------------------------------------
# DEDUP_STUB_FORMAT_EXACT (tinygemma3 §8.5 arm)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fixture,expected,nbytes", [
    ("s8_5_escaping", STUB_8_5, 120),
    ("s8_5_noname_variant", STUB_8_5_NONAME, 108),
], ids=["s8_5_120_bytes", "s8_5_noname_108_bytes"])
def test_dedup_stub_format_exact(fixture: str, expected: str, nbytes: int):
    """DEDUP_STUB_FORMAT_EXACT (tinygemma3 §8.5 arm): the second copy of K
    renders as exactly the §8.5 stub (120 bytes; 108 bytes when f1's name
    `fetch"url` fails the allowlist), and everything else as the pass-off
    golden. Planted defect: the §6.4 step-3 byte map is disabled (the excerpt
    keeps `"` and `]`)."""
    global server
    server.start()
    assert len(expected.encode("utf-8")) == nbytes
    golden = goldens.load_golden(fixture)
    assert golden.count(K) == 2
    prompt = _render(goldens.load_request(fixture))
    assert prompt == _splice_last(golden, K, expected)


# ---------------------------------------------------------------------------
# DEDUP_TIMINGS_VALUES (media arm, tinygemma3): the §6.5 estimate counts text
# only, in both B and T. Carried from the increment 11 review
# (orchestrator.95.reviewer.6).
# ---------------------------------------------------------------------------

IMG_BEG = "<start_of_image>"  # the gemma3 image wrap mtmd adds around each image (tools/mtmd/mtmd.cpp)
IMG_END = "<end_of_image>"


def test_dedup_timings_values_media_excluded():
    """DEDUP_TIMINGS_VALUES (media arm): on `text_part_plus_image` (S > 0, one
    image), `timings.dedup_tokens_saved_est == (2·S·T + B) // (2·B)` where
    B = bytes of the /apply-template prompt minus its media markers and
    T = the prompt's text tokens: BOS plus each marker-split text segment
    (parse_special) plus the image wrap tokens, never the image's embedding
    positions (so T < usage.prompt_tokens). Planted defects (RED proof):
    B keeps the marker bytes; T counts the media positions."""
    global server
    server.start()
    body = goldens.load_request("text_part_plus_image")
    messages = body["messages"]
    prompt = _render(body)
    assert prompt.count(MARKER) == 1

    _, records = goldens.ref_apply(messages)
    assert len(records) == 1, f"the fixture must stub one unit, the reference made {len(records)}"
    s = sum(b - len(stub.encode("utf-8")) for b, stub in records)
    b = len(prompt.encode("utf-8")) - prompt.count(MARKER) * len(MARKER.encode("utf-8"))

    segments = prompt.split(MARKER)
    n_img = len(segments) - 1
    t = sum(len(_tokenize(seg, True, add_special=(i == 0))) for i, seg in enumerate(segments))
    t += n_img * (len(_tokenize(IMG_BEG, True)) + len(_tokenize(IMG_END, True)))

    res = server.make_request("POST", "/v1/chat/completions", data={**body, "max_tokens": 1})
    assert res.status_code == 200, res.body
    timings = res.body.get("timings", {})
    assert timings.get("dedup_n") == 1 and timings.get("dedup_bytes_saved") == s, timings
    assert t < res.body["usage"]["prompt_tokens"], "the text-token oracle must exclude the image's embedding positions"
    want = (2 * s * t + b) // (2 * b)
    assert timings.get("dedup_tokens_saved_est") == want, (
        f"est {timings.get('dedup_tokens_saved_est')} != {want} (S={s}, T={t}, B={b}, "
        f"prompt_tokens={res.body['usage']['prompt_tokens']})")
