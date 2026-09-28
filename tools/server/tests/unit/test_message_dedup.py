#!/usr/bin/env python
"""SPEC-0001 (server message dedup): HTTP-level contracts.

Increment 2 adds the pass-off characterization tests. They pin what a build
WITHOUT the feature renders and reports, using the golden fixtures in
tools/server/tests/fixtures/message_dedup/ (see PROVENANCE.md there). They are
green on the feature-free baseline by design; after the feature lands they
are the regression oracle for the off state (AC_F01).

Increment 3 adds the server-flag contracts (DEDUP_INVALID_FLAG_REFUSES_START,
§7 DEDUP_FLAG_INVALID) and the override arm of the off state
(DEDUP_OFF_BY_OVERRIDE_PROMPT_UNCHANGED, DEDUP_OFF_NO_TIMINGS_FIELDS).

Increment 8 adds the HTTP arms of the enabling, override and stub contracts
(server flag and override enable the pass, partial override inherits,
min_bytes/roles apply, the tool-result repeat is stubbed in the exact §6.4
format, equivalence to manual substitution, invalid override -> 400). The
Python reference `goldens.ref_stub`/`goldens.ref_apply` builds R' independently
of the server code.

Increment 9 adds the conformance slice over HTTP: matching (threshold,
near-duplicates, role sets, references, parts, the length rule), stub and
tool-name safety, lookalike input, determinism, prefix stability and the
cache bound across turns, plus the §7 rows of the same module. The behavior
was built behind the unit seam (increments 5-8), so each test's red proof is
a planted mutation of that seam; the per-test mutant list and the sweep
outcome are in docs/graph/plans/grill/spec-0001-inc-09-*.md.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

# ensure grandparent path is in sys.path
path = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(path))

from utils import *  # noqa: E402,F403
from fixtures.message_dedup import dedup_goldens as goldens  # noqa: E402

server: ServerProcess

SERVER_KEY = "tinyllama2_chatml"  # tinyllama2 + jinja + chatml (spec §10 test homes)

MANIFEST = goldens.load_manifest()

# Server-default arm: fixtures rendered on tinyllama2 whose request carries no
# `message_dedup` field. The override arm is test_dedup_off_by_override_prompt_unchanged.
DEFAULT_ARM_FIXTURES = sorted(
    name for name, entry in MANIFEST.items()
    if goldens.SERVER_CONFIGS[entry["server"]]["preset"] == "tinyllama2"
    and "message_dedup" not in goldens.load_request(name)
)


@pytest.fixture(autouse=True)
def create_server():
    global server
    server = goldens.make_server(SERVER_KEY)


@pytest.mark.parametrize("fixture", DEFAULT_ARM_FIXTURES)
def test_dedup_off_by_default_prompt_unchanged(fixture: str):
    """DEDUP_OFF_BY_DEFAULT_PROMPT_UNCHANGED: server started without
    --message-dedup, request without `message_dedup` -> /apply-template prompt
    is byte-identical to the feature-free golden. Characterization: green on
    the baseline build."""
    global server
    server = goldens.make_server(MANIFEST[fixture]["server"])
    server.start()
    res = server.make_request("POST", "/apply-template", data=goldens.load_request(fixture))
    assert res.status_code == 200
    expected = goldens.load_golden(fixture).encode("utf-8")
    actual = res.body["prompt"].encode("utf-8")
    assert actual == expected, (
        f"{fixture}: prompt differs from pass-off golden "
        f"(len {len(actual)} vs {len(expected)}; first difference at byte "
        f"{next((i for i, (a, b) in enumerate(zip(actual, expected)) if a != b), min(len(actual), len(expected)))})"
    )


@pytest.mark.parametrize("stream", [False, True], ids=["non_stream", "stream"])
@pytest.mark.parametrize("arm", ["server_default", "override"])
def test_dedup_off_no_timings_fields(arm: str, stream: bool):
    """DEDUP_OFF_NO_TIMINGS_FIELDS: with the pass not active, no `timings`
    object on /v1/chat/completions holds a `dedup_*` key, and its key set
    equals the feature-free build's (§8.4).
    - server_default: server without --message-dedup, request without
      `message_dedup` (characterization, green on the baseline build);
    - override: server with --message-dedup, request with
      `message_dedup: {"enabled": false}` (increment 3)."""
    global server
    body = goldens.load_timings_request()
    if arm == "override":
        server.message_dedup = True
        body = {**body, "message_dedup": {"enabled": False}}
    server.start()
    timings = goldens.collect_timings(server, body, stream)
    assert len(timings) >= 1, "expected at least one timings object"
    expected_keys = set(goldens.load_timings_keys()["stream" if stream else "non_stream"])
    for t in timings:
        assert not [k for k in t if k.startswith("dedup_")]
        assert set(t.keys()) == expected_keys


def test_dedup_off_by_override_prompt_unchanged():
    """DEDUP_OFF_BY_OVERRIDE_PROMPT_UNCHANGED: server started with
    --message-dedup, request carrying `"message_dedup": {"enabled": false}`
    with a repeated 1100-byte tool result -> /apply-template prompt is
    byte-identical to the pass-off golden (§8.4; the `s8_4_off_override`
    golden, which equals the DEDUP_OFF_BY_DEFAULT_PROMPT_UNCHANGED golden of
    `s8_1_reread_file`)."""
    global server
    server.message_dedup = True
    server.start()
    body = goldens.load_request("s8_4_off_override")
    assert body.get("message_dedup") == {"enabled": False}
    res = server.make_request("POST", "/apply-template", data=body)
    assert res.status_code == 200
    assert res.body["prompt"].encode("utf-8") == goldens.load_golden("s8_4_off_override").encode("utf-8")
    assert goldens.load_golden("s8_4_off_override") == goldens.load_golden("s8_1_reread_file")


# ---------------------------------------------------------------------------
# DEDUP_INVALID_FLAG_REFUSES_START / DEDUP_FLAG_INVALID
#
# The binary is run directly with `-m` pointing at a missing file. A valid
# flag set would get as far as the model load and fail there; an invalid flag
# value must stop the process in argument parsing, before the model load,
# with a message that names the flag in the parser's VALIDATION form. The
# unknown-flag form (`error: invalid argument: <flag>`, common/arg.cpp:824),
# which today's build prints, must not satisfy these tests.
# ---------------------------------------------------------------------------

MISSING_MODEL = "/nonexistent/spec-0001/missing-model.gguf"

FLAG_ENV = {
    "--message-dedup-min-bytes": "LLAMA_ARG_MESSAGE_DEDUP_MIN_BYTES",
    "--message-dedup-roles": "LLAMA_ARG_MESSAGE_DEDUP_ROLES",
}

# (id, flag, invalid value) per SPEC-0001 §6.1 and §7 DEDUP_FLAG_INVALID
REFUSES_START_CASES = [
    ("min_bytes_0", "--message-dedup-min-bytes", "0"),
    ("roles_assistant", "--message-dedup-roles", "assistant"),
    ("roles_unknown", "--message-dedup-roles", "bogus"),
]
FLAG_INVALID_CASES = [
    ("min_bytes_0", "--message-dedup-min-bytes", "0"),
    ("min_bytes_neg1", "--message-dedup-min-bytes", "-1"),
    ("min_bytes_2147483648", "--message-dedup-min-bytes", "2147483648"),
    ("min_bytes_abc", "--message-dedup-min-bytes", "abc"),
    # not a whole integer: std::stoi-style prefix parsing would accept these
    ("min_bytes_1024abc", "--message-dedup-min-bytes", "1024abc"),
    ("min_bytes_1.5", "--message-dedup-min-bytes", "1.5"),
    ("min_bytes_0x10", "--message-dedup-min-bytes", "0x10"),
    ("min_bytes_leading_space", "--message-dedup-min-bytes", " 1024"),
    ("roles_assistant", "--message-dedup-roles", "assistant"),
    ("roles_tool_assistant", "--message-dedup-roles", "tool,assistant"),
    ("roles_bogus", "--message-dedup-roles", "bogus"),
]


def _server_bin() -> str:
    return os.environ.get("LLAMA_SERVER_BIN_PATH", "../../../build/bin/llama-server")


def _port() -> int:
    return int(os.environ.get("PORT", "8080"))


def _run_server_with_flag(channel: str, flag: str, value: str, tmp_path: Path) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if not k.startswith("LLAMA_ARG_MESSAGE_DEDUP")}
    # isolate the user-level config.ini (common/arg.cpp:717-732)
    xdg = tmp_path / "xdg"
    (xdg / "llama.cpp").mkdir(parents=True)
    env["XDG_CONFIG_HOME"] = str(xdg)
    argv = [_server_bin(), "-m", MISSING_MODEL, "--port", str(_port()), "--host", "127.0.0.1"]
    if channel == "argv":
        argv += [flag, value]
    elif channel == "env":
        env[FLAG_ENV[flag]] = value
    elif channel == "config_ini":
        (xdg / "llama.cpp" / "config.ini").write_text(f"{flag.lstrip('-')} = {value}\n", encoding="utf-8")
    else:
        raise ValueError(channel)
    return subprocess.run(argv, env=env, capture_output=True, text=True, timeout=60)


def _port_is_bound(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        return s.connect_ex(("127.0.0.1", port)) == 0


def _assert_refused_before_model_load(channel: str, flag: str, value: str, proc: subprocess.CompletedProcess, xdg_ini: Path):
    out = proc.stdout + proc.stderr
    assert proc.returncode != 0, f"exit code {proc.returncode}"
    # never the unknown-flag form
    assert f"error: invalid argument: {flag}" not in out
    if channel == "argv":
        assert f'error while handling argument "{flag}"' in out, out[-2000:]
    elif channel == "env":
        assert f'error while handling environment variable "{FLAG_ENV[flag]}"' in out, out[-2000:]
    else:
        # the config file was read, the key was not ignored as unsupported,
        # and the rejection names the flag
        assert f"using config file: {xdg_ini}" in out, out[-2000:]
        assert "ignoring option" not in out, out[-2000:]
        assert flag.lstrip("-") in out.replace(str(xdg_ini), ""), out[-2000:]
    # refused in argument parsing: no model-load attempt, never listening
    assert "failed to load model" not in out, out[-2000:]
    assert "listening on" not in out, out[-2000:]
    assert not _port_is_bound(_port())


@pytest.mark.parametrize("case_id,flag,value", REFUSES_START_CASES, ids=[c[0] for c in REFUSES_START_CASES])
def test_dedup_invalid_flag_refuses_start(case_id: str, flag: str, value: str, tmp_path: Path):
    """DEDUP_INVALID_FLAG_REFUSES_START: `--message-dedup-min-bytes 0`, or
    `--message-dedup-roles` naming `assistant` or an unknown role, makes the
    process exit non-zero before loading the model, with an error naming the
    flag."""
    proc = _run_server_with_flag("argv", flag, value, tmp_path)
    _assert_refused_before_model_load("argv", flag, value, proc, tmp_path / "xdg" / "llama.cpp" / "config.ini")


# config.ini cannot carry a leading space in a value: the ini grammar consumes
# the whitespace after `=` (common/preset.cpp kv-line rule), so that case runs
# on argv and env only.
FLAG_INVALID_PARAMS = [
    pytest.param(case_id, flag, value, channel, id=f"{case_id}-{channel}")
    for (case_id, flag, value) in FLAG_INVALID_CASES
    for channel in ("argv", "env", "config_ini")
    if not (channel == "config_ini" and value != value.strip())
]


@pytest.mark.parametrize("case_id,flag,value,channel", FLAG_INVALID_PARAMS)
def test_dedup_flag_invalid(case_id: str, flag: str, value: str, channel: str, tmp_path: Path):
    """§7 DEDUP_FLAG_INVALID: an out-of-range or non-integer min-bytes, or a
    roles list naming `assistant` or an unknown role, is rejected whether it
    comes from argv, `LLAMA_ARG_*` or `config.ini`: non-zero exit, a message
    naming the flag, no model load, port unbound."""
    proc = _run_server_with_flag(channel, flag, value, tmp_path)
    _assert_refused_before_model_load(channel, flag, value, proc, tmp_path / "xdg" / "llama.cpp" / "config.ini")


# ---------------------------------------------------------------------------
# Increment 8: the pass wired into oaicompat_chat_params_parse, seen through
# /apply-template on tinyllama2 + chatml. Expected prompts come from the
# increment-2 pass-off goldens and the test-side reference pass
# (goldens.ref_stub / goldens.ref_apply), never from server code.
# ---------------------------------------------------------------------------

F = goldens.F


def _stubbed_8_1_prompt() -> str:
    """The §8.1 pass-off golden with the second copy of F rendered as the §8.1 stub."""
    golden = goldens.load_golden("s8_1_reread_file")
    assert golden.count(F) == 2
    idx = golden.rindex(F)
    return golden[:idx] + goldens.STUB_8_1 + golden[idx + len(F):]


def _render(body: dict) -> str:
    res = server.make_request("POST", "/apply-template", data=body)
    assert res.status_code == 200, res.body
    return res.body["prompt"]


def _s8_1_body(message_dedup: dict | None = None) -> dict:
    body = {"messages": goldens.load_request("s8_1_reread_file")["messages"]}
    if message_dedup is not None:
        body["message_dedup"] = message_dedup
    return body


def test_dedup_server_flag_enables_pass():
    """DEDUP_SERVER_FLAG_ENABLES_PASS: with --message-dedup and no override,
    the second 1100-byte tool message renders as the §6.4 stub and the first
    in full."""
    global server
    server.message_dedup = True
    server.start()
    prompt = _render(_s8_1_body())
    assert prompt.count(F) == 1, "F must render exactly once (the first occurrence)"
    assert prompt.count(goldens.STUB_8_1) == 1, "the second tool message must render as the §8.1 stub"
    assert prompt.index(F) < prompt.index(goldens.STUB_8_1)
    assert prompt == _stubbed_8_1_prompt()


def test_dedup_override_enables_pass():
    """DEDUP_OVERRIDE_ENABLES_PASS: without --message-dedup, `{"enabled": true}`
    gives the prompt of DEDUP_SERVER_FLAG_ENABLES_PASS (the §8.1 golden with the
    second F stubbed)."""
    global server
    server.start()
    assert _render(_s8_1_body({"enabled": True})) == _stubbed_8_1_prompt()


def test_dedup_override_partial_inherits_enabled():
    """DEDUP_OVERRIDE_PARTIAL_INHERITS_ENABLED (HTTP arm): without
    --message-dedup, `{"min_bytes": 16}` (no `enabled`) leaves the pass off, so
    the prompt equals the pass-off golden. Green before GREEN (an unwired pass
    renders in full); its red proof is the planted mutation "a present
    min_bytes or roles field turns the pass on"."""
    global server
    server.start()
    assert _render(_s8_1_body({"min_bytes": 16})) == goldens.load_golden("s8_1_reread_file")
    assert _render(_s8_1_body({"roles": ["tool"]})) == goldens.load_golden("s8_1_reread_file")


def test_dedup_override_min_bytes_applies():
    """DEDUP_OVERRIDE_MIN_BYTES_APPLIES: with --message-dedup (default 1024),
    `{"min_bytes": 2048}` renders both 1100-byte tool results in full. Green
    before GREEN; its red proof is the planted mutation "the request's
    min_bytes is ignored in favor of the default"."""
    global server
    server.message_dedup = True
    server.start()
    assert _render(_s8_1_body({"min_bytes": 2048})) == goldens.load_golden("s8_1_reread_file")


def test_dedup_override_roles_applies():
    """DEDUP_OVERRIDE_ROLES_APPLIES: with --message-dedup (default roles tool),
    `{"roles": ["user"]}` stubs the second user message as `user message #1`
    and renders both tool results in full (the override replaces the set)."""
    global server
    server.message_dedup = True
    server.start()
    messages = goldens.load_request("user_and_tool_pairs")["messages"]
    user_text = messages[0]["content"]
    tool_text = messages[2]["content"]
    golden = goldens.load_golden("user_and_tool_pairs")
    assert golden.count(user_text) == 2 and golden.count(tool_text) == 2
    stub = goldens.ref_stub(user_text, "user", 1, None)
    assert stub is not None and stub.startswith("[duplicate content omitted: byte-identical to user message #1, ")
    idx = golden.rindex(user_text)
    expected = golden[:idx] + stub + golden[idx + len(user_text):]
    prompt = _render({"messages": messages, "message_dedup": {"roles": ["user"]}})
    assert prompt.count(tool_text) == 2, "both tool results must render in full"
    assert prompt == expected


def test_dedup_tool_result_repeat_stubbed():
    """DEDUP_TOOL_RESULT_REPEAT_STUBBED (HTTP arm): the §4 five-message list
    renders its fifth message as stub(tool result #1, read_file, F)."""
    global server
    server.message_dedup = True
    server.start()
    stub = goldens.ref_stub(F, "tool", 1, "read_file")
    assert stub == goldens.STUB_8_1
    prompt = _render(_s8_1_body())
    # the fifth message is the last tool block before the generation prompt
    last_tool = prompt.rindex("<|im_start|>tool\n")
    assert prompt[last_tool:].startswith("<|im_start|>tool\n" + stub + "<|im_end|>")


def test_dedup_first_occurrence_unchanged():
    """DEDUP_FIRST_OCCURRENCE_UNCHANGED: with the pass on, messages 1-4 render
    byte-identically to their pass-off rendering (the increment-2 golden) up to
    where the fifth message's content starts."""
    global server
    server.message_dedup = True
    server.start()
    golden = goldens.load_golden("s8_1_reread_file")
    cut = golden.rindex(F)
    prompt = _render(_s8_1_body())
    assert prompt[:cut] == golden[:cut]
    assert prompt[cut:cut + len(F)] != F, "the fifth message must not render F in full"


def test_dedup_stub_format_exact():
    """DEDUP_STUB_FORMAT_EXACT (HTTP arm, tinyllama2): the stubbed unit renders
    as exactly the §8.1 stub, 155 bytes."""
    global server
    server.message_dedup = True
    server.start()
    assert len(goldens.STUB_8_1.encode("utf-8")) == 155
    prompt = _render(_s8_1_body())
    golden = goldens.load_golden("s8_1_reread_file")
    start = golden.rindex(F)
    tail = golden[start + len(F):]
    assert prompt.endswith(tail)
    assert prompt[start:len(prompt) - len(tail)] == goldens.STUB_8_1


# every tinyllama2/chatml pass-on fixture, under the default roles and the widest set
EQUIV_FIXTURES = sorted(
    name for name, entry in MANIFEST.items()
    if entry["server"] == SERVER_KEY and "message_dedup" not in goldens.load_request(name)
)
EQUIV_ARMS = {"roles_tool": ["tool"], "roles_all": ["tool", "user", "system"]}


@pytest.mark.parametrize("arm", sorted(EQUIV_ARMS))
@pytest.mark.parametrize("fixture", EQUIV_FIXTURES)
def test_dedup_equivalent_to_manual_substitution(fixture: str, arm: str):
    """DEDUP_EQUIVALENT_TO_MANUAL_SUBSTITUTION (HTTP arm): R with the pass on
    renders byte-identically to R' (pass off, each stubbed unit replaced by the
    test-side §6.4 stub). Fixtures where the reference pass stubs nothing guard
    only after GREEN."""
    global server
    server.start()
    body = goldens.load_request(fixture)
    roles = EQUIV_ARMS[arm]
    r_on = {**body, "message_dedup": {"enabled": True, "roles": roles}}
    ref_messages, _records = goldens.ref_apply(body["messages"], 1024, tuple(roles))
    r_prime = {**body, "messages": ref_messages, "message_dedup": {"enabled": False}}
    assert _render(r_on) == _render(r_prime)


INVALID_OVERRIDES = {
    "roles_assistant": {"enabled": True, "roles": ["tool", "assistant"]},
    "min_bytes_0": {"min_bytes": 0},
    "enabled_not_bool": {"enabled": "yes"},
    "not_an_object": "on",
}


@pytest.mark.parametrize("case", sorted(INVALID_OVERRIDES))
@pytest.mark.parametrize("endpoint", ["/v1/chat/completions", "/apply-template"])
def test_dedup_override_invalid_returns_400(endpoint: str, case: str):
    """DEDUP_OVERRIDE_INVALID_RETURNS_400 (chat completions and /apply-template;
    the remaining JSON chat endpoints are in unit/test_message_dedup_endpoints.py, increment 10): a §6.2-invalid
    `message_dedup` gives 400 with the §6.6 body naming `message_dedup`, and no
    task is queued (no slot's id_task changes)."""
    global server
    server.server_slots = True
    server.start()
    # give every slot a task id first, so an unchanged id_task is meaningful
    for _ in range(2):
        warm = server.make_request("POST", "/v1/chat/completions", data={
            "max_tokens": 2, "messages": [{"role": "user", "content": "hello"}]})
        assert warm.status_code == 200
    before = server.make_request("GET", "/slots")
    assert before.status_code == 200
    body = {"messages": [{"role": "user", "content": "hi"}], "max_tokens": 2,
            "message_dedup": INVALID_OVERRIDES[case]}
    res = server.make_request("POST", endpoint, data=body)
    assert res.status_code == 400, f"status {res.status_code}, body {res.body}"
    err = res.body.get("error", {}) if isinstance(res.body, dict) else {}
    assert err.get("code") == 400
    assert err.get("type") == "invalid_request_error"
    assert "message_dedup" in err.get("message", "")
    after = server.make_request("GET", "/slots")
    assert {s["id"]: s.get("id_task") for s in after.body} == {s["id"]: s.get("id_task") for s in before.body}


# ---------------------------------------------------------------------------
# Increment 9: matching, stub and cache contracts over HTTP (conformance).
# Each test's RED proof is the planted seam mutation named in its docstring
# (plan row spec-0001-inc-09-http-matching-conformance.md). Expected prompts
# come from the pass-off render of the test-side reference (ref_apply).
# ---------------------------------------------------------------------------

def _pass_on(messages: list, roles=("tool",), min_bytes: int = 1024, **extra) -> dict:
    return {**extra, "messages": messages,
            "message_dedup": {"enabled": True, "roles": list(roles), "min_bytes": min_bytes}}


def _check_equiv(messages: list, roles=("tool",), min_bytes: int = 1024, expect_stubs: int | None = None, **extra):
    """Render R (pass on through the override) and R' (the reference rewrite,
    pass off); assert they are byte-identical. Returns (prompt, records)."""
    ref_messages, records = goldens.ref_apply(messages, min_bytes, tuple(roles))
    if expect_stubs is not None:
        assert len(records) == expect_stubs, f"reference made {len(records)} replacements, the contract expects {expect_stubs}"
    got = _render(_pass_on(messages, roles, min_bytes, **extra))
    want = _render({**extra, "messages": ref_messages, "message_dedup": {"enabled": False}})
    assert got == want
    return got, records


def _msgs(fixture: str) -> list:
    return goldens.load_request(fixture)["messages"]


def test_dedup_threshold_boundary_inclusive():
    """DEDUP_THRESHOLD_BOUNDARY_INCLUSIVE (HTTP): the second 1024-byte copy is
    stubbed and both 1023-byte copies render in full. Mutation: `>=` becomes `>`."""
    global server
    server.start()
    prompt, records = _check_equiv(_msgs("threshold_1024_1023"), expect_stubs=1)
    g1023 = _msgs("threshold_1024_1023")[0]["content"]
    assert prompt.count(g1023) == 2
    assert "byte-identical to tool result #3, which begins" in prompt


@pytest.mark.parametrize("fixture", ["near_dup_one_byte", "near_dup_trailing_newline", "near_dup_crlf_lf", "near_dup_nfc_nfd"])
def test_dedup_near_duplicate_unchanged(fixture: str):
    """DEDUP_NEAR_DUPLICATE_UNCHANGED (HTTP): two 1100-byte tool results that
    differ in one byte, a trailing newline, CRLF/LF or NFC/NFD both render in
    full. Mutation: compare after trimming trailing whitespace and normalizing CRLF."""
    global server
    server.message_dedup = True
    server.start()
    assert _render({"messages": _msgs(fixture)}) == goldens.load_golden(fixture)


def test_dedup_user_system_excluded_by_default():
    """DEDUP_USER_SYSTEM_EXCLUDED_BY_DEFAULT: with the flag and default roles,
    two identical user and two identical system messages all render in full.
    Mutation: default roles {tool,user,system}."""
    global server
    server.message_dedup = True
    server.start()
    assert _render({"messages": _msgs("user_system_pairs")}) == goldens.load_golden("user_system_pairs")


@pytest.mark.parametrize("arm", ["flag", "override"])
def test_dedup_user_system_opt_in(arm: str):
    """DEDUP_USER_SYSTEM_OPT_IN (flag / override): with roles ["user","system"]
    the second user copy and the second system copy render as `user message #1`
    and `system message #1`. Mutation: the `roles` override is ignored."""
    global server
    messages = _msgs("user_system_pairs")
    if arm == "flag":
        server.message_dedup = True
        server.message_dedup_roles = "user,system"
        server.start()
        prompt = _render({"messages": messages})
    else:
        server.start()
        prompt = _render(_pass_on(messages, ("user", "system")))
    ref_messages, records = goldens.ref_apply(messages, 1024, ("user", "system"))
    assert len(records) == 2
    assert prompt == _render({"messages": ref_messages, "message_dedup": {"enabled": False}})
    assert "byte-identical to user message #1, " in prompt and "byte-identical to system message #1, " in prompt


def test_dedup_assistant_never_stubbed():
    """DEDUP_ASSISTANT_NEVER_STUBBED (HTTP): identical 1100-byte assistant
    content, reasoning_content and tool-call arguments render as with the pass
    off under the widest role set (a user message follows the second
    assistant). Mutation: `assistant` is added to every role set."""
    global server
    server.start()
    body = _pass_on(_msgs("assistant_pair"), ("tool", "user", "system"), 1)
    assert _render(body) == goldens.load_golden("assistant_pair")


def test_dedup_non_participating_role_not_a_reference():
    """DEDUP_NON_PARTICIPATING_ROLE_NOT_A_REFERENCE: a user F followed by a tool F
    both render in full under the default roles. Mutation: non-participating
    units are indexed."""
    global server
    server.message_dedup = True
    server.start()
    assert _render({"messages": _msgs("non_participating_role")}) == goldens.load_golden("non_participating_role")


def test_dedup_reference_same_role_only():
    """DEDUP_REFERENCE_SAME_ROLE_ONLY (HTTP): tool F, user F, tool F under roles
    ["tool","user"]: the tool and user messages render in full, the second tool
    message as stub(tool result #1). Mutation: the role is dropped from the key."""
    global server
    server.start()
    prompt, _ = _check_equiv(_msgs("same_role_only"), ("tool", "user"), expect_stubs=1)
    assert prompt.count(F) == 2
    assert "byte-identical to tool result #1, which begins" in prompt


def test_dedup_later_repeats_reference_first():
    """DEDUP_LATER_REPEATS_REFERENCE_FIRST: tool results #2 and #3 (copies of #1)
    both reference `tool result #1`, never #2. Mutation: the index keeps the latest copy."""
    global server
    server.message_dedup = True
    server.start()
    prompt = _render({"messages": _msgs("three_copies")})
    assert prompt.count(goldens.STUB_8_1) == 2
    assert "tool result #2" not in prompt
    _check_equiv(_msgs("three_copies"), expect_stubs=2)


def test_dedup_first_copy_dropped_next_is_full():
    """DEDUP_FIRST_COPY_DROPPED_NEXT_IS_FULL: with the first of three copies (and
    its call) removed, the new first copy (tool result #1 by ordinal) renders in
    full and the other references it. Mutation: ORDINAL counts earlier messages
    of every role."""
    global server
    server.message_dedup = True
    server.start()
    prompt = _render({"messages": _msgs("truncated_history")})
    assert prompt.count(F) == 1
    assert prompt.count(goldens.STUB_8_1) == 1


def test_dedup_same_message_parts():
    """DEDUP_SAME_MESSAGE_PARTS (HTTP): one user message [text P, text P] under
    roles ["user"]: the first part in full, the second a stub referencing that
    same message. Mutation: parts of the current message are not indexed."""
    global server
    server.start()
    prompt, _ = _check_equiv(_msgs("same_message_parts"), ("user",), expect_stubs=1)
    assert "byte-identical to user message #1, " in prompt


def test_dedup_stub_not_longer_than_content():
    """DEDUP_STUB_NOT_LONGER_THAN_CONTENT (HTTP): two identical 60-byte tool
    results under min_bytes 1 both render in full. Mutation: the length check is dropped."""
    global server
    server.start()
    assert _render(_pass_on(_msgs("pair_60_bytes"), ("tool",), 1)) == goldens.load_golden("pair_60_bytes")


# The shortest possible stub (tool result #1, no name, empty excerpt) is 100 bytes; the
# server never indexes a unit at or below it (S7), which masks the length rule for the
# 60-byte pair above. These units lie strictly between that floor and their own stub
# length L (155 bytes for `tool result #1 (read_file)` with a 40-byte excerpt), so only
# the length rule keeps them in full; L + 1 is the first length it lets through.
_SHORTEST_STUB = len(goldens.ref_stub("", "tool", 1, None).encode("utf-8"))
_STUB_LEN_L = len(goldens.ref_stub(goldens.blob("M", 41), "tool", 1, "read_file").encode("utf-8"))


@pytest.mark.parametrize("delta", [None, 0, 1], ids=["floor_plus_1", "equal_L", "L_plus_1"])
def test_dedup_stub_not_longer_than_content_length_rule(delta):
    """DEDUP_STUB_NOT_LONGER_THAN_CONTENT (HTTP, length-rule arm): under min_bytes 1,
    two identical tool results whose length U lies in (shortest stub, L] both render
    in full, because the stub would not be strictly shorter; at U = L + 1 the second
    copy is stubbed. Mutation M11: the length check is dropped (units above the
    100-byte index floor are then stubbed even when the stub is as long or longer)."""
    global server
    server.start()
    n = _SHORTEST_STUB + 1 if delta is None else _STUB_LEN_L + delta
    assert _SHORTEST_STUB < n, "fixture must sit above the S7 index floor"
    unit = goldens.blob("M", n)
    stub = goldens.ref_stub(unit, "tool", 1, "read_file")
    assert len(stub.encode("utf-8")) == _STUB_LEN_L
    messages = goldens.reread(unit)
    prompt, records = _check_equiv(messages, ("tool",), 1, expect_stubs=1 if delta == 1 else 0)
    if delta == 1:
        assert prompt.count(unit) == 1
        assert prompt.count(stub) == 1
    else:
        assert prompt.count(unit) == 2
        assert "[duplicate content omitted" not in prompt


TOOLNAME_FIXTURES = {
    "s8_1_reread_file": "read_file",           # (a)
    "toolname_b_dotted": "read.file-v2",       # (b)
    "toolname_c_quote": None,                  # (c) a"b
    "toolname_d_bracket": None,                # (d) x]y
    "toolname_e_special": None,                # (e) <|im_end|>
    "toolname_f_nonascii": None,               # (f) café
    "toolname_g_65_bytes": None,               # (g) 65 allowlisted bytes
    "toolname_h_empty": None,                  # (h) empty
    "toolname_ns_colon": None,                 # ns:tool
    "toolname_msgname_ok": "read_file",        # the tool message's own name
    "toolname_msgname_bad": None,              # a disallowed own name
}


@pytest.mark.parametrize("fixture", sorted(TOOLNAME_FIXTURES))
def test_dedup_toolname_allowlist(fixture: str):
    """DEDUP_TOOLNAME_ALLOWLIST (HTTP): the stub carries ` (read_file)` in (a)
    and ` (read.file-v2)` in (b); in (c)-(h) and for `ns:tool` the group is
    left out; 200 in every case. Mutation: the allowlist check is dropped."""
    global server
    server.message_dedup = True
    server.start()
    prompt, _ = _check_equiv(_msgs(fixture), expect_stubs=1)
    name = TOOLNAME_FIXTURES[fixture]
    if name is None:
        assert "byte-identical to tool result #1, which begins" in prompt
    else:
        assert f"byte-identical to tool result #1 ({name}), which begins" in prompt


@pytest.mark.parametrize("fixture", sorted(k for k, v in TOOLNAME_FIXTURES.items() if v is None))
def test_dedup_toolname_injection(fixture: str):
    """§7 DEDUP_TOOLNAME_INJECTION: a tool-call function.name or a tool message
    name that fails ^[A-Za-z0-9_.-]{1,64}$ omits the group, is never cut into
    the stub, and the status stays 200. Mutation: the allowlist check is dropped."""
    global server
    server.message_dedup = True
    server.start()
    res = server.make_request("POST", "/apply-template", data={"messages": _msgs(fixture)})
    assert res.status_code == 200
    prompt = res.body["prompt"]
    assert "byte-identical to tool result #1, which begins" in prompt
    assert "byte-identical to tool result #1 (" not in prompt


def test_dedup_tool_pairing_preserved():
    """DEDUP_TOOL_PAIRING_PRESERVED: the §4 request with `tools` declared
    returns 200 on /v1/chat/completions (the stub also brings it under
    tinyllama2's 2048-token slot), and /apply-template shows the stubbed
    message with the same role rendering as pass-off manual substitution.
    Mutation: the stubbed message's role is rewritten to `user`."""
    global server
    server.message_dedup = True
    server.start()
    body = goldens.load_request("tool_repeat_with_tools")
    res = server.make_request("POST", "/v1/chat/completions", data={**body, "max_tokens": 2})
    assert res.status_code == 200, res.body
    _check_equiv(body["messages"], expect_stubs=1, tools=body["tools"])
    prompt = _render(body)
    assert prompt.count("<|im_start|>tool\n") == 2


def test_dedup_stub_lookalike_input_verbatim():
    """DEDUP_STUB_LOOKALIKE_INPUT_VERBATIM (/apply-template; the dedup_n clause
    joins in increment 11): a tool message byte-identical to the §8.1 stub, with
    no earlier unit of those bytes, renders verbatim and is never resolved.
    Mutation: stub-shaped content is replaced by the content of the message it names."""
    global server
    server.message_dedup = True
    server.start()
    prompt = _render({"messages": _msgs("lookalike_verbatim")})
    assert prompt == goldens.load_golden("lookalike_verbatim")
    assert prompt.count(F) == 1


def test_dedup_stub_lookalike_input():
    """§7 DEDUP_STUB_LOOKALIKE_INPUT: a lookalike that repeats an earlier
    participating unit above the threshold is itself stubbed like any content.
    Mutation: stub-shaped content is replaced by the content of the message it names."""
    global server
    server.message_dedup = True
    server.start()
    prompt, _ = _check_equiv(_msgs("lookalike_repeat"), expect_stubs=1)
    lookalike = _msgs("lookalike_repeat")[1]["content"]
    assert prompt.count(lookalike) == 1
    assert F not in prompt


def _interleaved_renders(body: dict, n: int) -> list:
    """n renders of body, interleaved with other requests across two slots."""
    other_render = {"messages": _msgs("user_system_pairs")}
    other_chat = {"max_tokens": 2, "messages": [{"role": "user", "content": "hello"}]}
    calls = []
    for i in range(n):
        calls.append((server.make_request, ("POST", "/apply-template", body)))
        calls.append((server.make_request, ("POST", "/apply-template", other_render)))
        if i % 3 == 0:
            calls.append((server.make_request, ("POST", "/v1/chat/completions", other_chat)))
    results = parallel_function_calls(calls)
    renders = []
    for (fn, args), res in zip(calls, results):
        if args[1] == "/apply-template" and args[2] is body:
            assert res.status_code == 200
            renders.append(res.body["prompt"])
    return renders


def test_dedup_deterministic():
    """DEDUP_DETERMINISTIC (HTTP): a fixed request rendered 20 times across 2
    restarts, with --parallel 2, interleaved with other requests, gives one
    byte-identical prompt. Mutation: among equal copies, the referenced copy is
    picked in an order that depends on the per-process seed."""
    global server
    body = _pass_on(_msgs("three_copies") + _msgs("user_system_pairs"), ("tool", "user", "system"))
    renders = []
    for _restart in range(2):
        server = goldens.make_server(SERVER_KEY)
        server.n_slots = 2
        server.start()
        renders += _interleaved_renders(body, 10)
        server.stop()
    assert len(renders) == 20
    assert len(set(renders)) == 1
    ref_messages, records = goldens.ref_apply(body["messages"], 1024, ("tool", "user", "system"))
    assert len(records) >= 3
    server = goldens.make_server(SERVER_KEY)
    server.start()
    assert renders[0] == _render({"messages": ref_messages, "message_dedup": {"enabled": False}})


PREFIX_FIXTURES = ["three_copies", "user_and_tool_pairs", "user_system_pairs", "same_role_only", "lookalike_repeat"]


@pytest.mark.parametrize("fixture", PREFIX_FIXTURES)
def test_dedup_prefix_stable_on_append(fixture: str):
    """DEDUP_PREFIX_STABLE_ON_APPEND (HTTP): with add_generation_prompt false,
    the prompt of every prefix L (a cut at every message boundary, except after
    an assistant tool call, which the server refuses as a prefill) is a byte
    prefix of the prompt of the full list. Mutation: the ordinal counts every
    message with that role in the whole list."""
    global server
    server.start()
    messages = _msgs(fixture)
    roles = ("tool", "user", "system")
    full = _render({**_pass_on(messages, roles), "add_generation_prompt": False})
    _, records = goldens.ref_apply(messages, 1024, roles)
    assert records, "the fixture must exercise stubbing"
    n_cuts = 0
    for k in range(1, len(messages)):
        # a list ending in an assistant tool call is a prefill the server refuses (400), so no cut there
        if messages[k - 1]["role"] == "assistant" and messages[k - 1].get("tool_calls"):
            continue
        part = _render({**_pass_on(messages[:k], roles), "add_generation_prompt": False})
        assert full.startswith(part), f"cut {k}: not a prefix"
        n_cuts += 1
    assert n_cuts >= 1


# ---- cache and mid-conversation (chat completions on tinyllama2: ~400-byte units, min_bytes 256) ----

R400 = goldens.blob("R", 400)
S400 = goldens.blob("S", 400)


def _tool_turn(call_id: str, content: str) -> list:
    return [{"role": "assistant", "content": "", "tool_calls": [
                {"id": call_id, "type": "function", "function": {"name": "read_file", "arguments": "{\"path\":\"a.c\"}"}}]},
            {"role": "tool", "tool_call_id": call_id, "content": content}]


def _gen_prompt_tokens(body: dict) -> int:
    with_gp = _render({**body, "add_generation_prompt": True})
    without = _render({**body, "add_generation_prompt": False})
    assert with_gp.startswith(without)
    tail = with_gp[len(without):]
    res = server.make_request("POST", "/tokenize", data={"content": tail, "add_special": False, "parse_special": True})
    assert res.status_code == 200
    return len(res.body["tokens"])


def _chat(body: dict) -> dict:
    res = server.make_request("POST", "/v1/chat/completions", data={**body, "cache_prompt": True, "id_slot": 0, "max_tokens": 4})
    assert res.status_code == 200, res.body
    return res.body


def _assert_cache_bound(turn1: dict, turn2: dict, r1: dict, r2: dict):
    bound = r1["timings"]["cache_n"] + r1["timings"]["prompt_n"] - _gen_prompt_tokens(turn1)
    assert r2["timings"]["cache_n"] >= bound, f"cache_n {r2['timings']['cache_n']} < bound {bound}"


def _next_turn(turn: dict, reply: dict, call_id: str, content: str) -> dict:
    assistant = {"role": "assistant", "content": reply["choices"][0]["message"].get("content") or ""}
    return {**turn, "messages": turn["messages"] + [assistant, {"role": "user", "content": "continue"}] + _tool_turn(call_id, content)}


def test_dedup_cache_hit_across_turns():
    """DEDUP_CACHE_HIT_ACROSS_TURNS: turn 1 holds a stubbed repeat; turn 2 is
    turn 1 + the returned assistant message + a new tool result repeating an
    earlier one; on slot 0 turn 2's cache_n >= turn 1's cache_n + prompt_n
    minus turn 1's generation-prompt tokens. Mutation: the ordinal counts every
    message with that role in the whole list."""
    global server
    server.start()
    turn1 = {"messages": [{"role": "user", "content": "Fix a.c"}] + _tool_turn("c1", R400) + _tool_turn("c2", R400),
             "message_dedup": {"enabled": True, "min_bytes": 256}}
    assert goldens.ref_apply(turn1["messages"], 256)[1], "turn 1 must hold a stubbed repeat"
    r1 = _chat(turn1)
    turn2 = _next_turn(turn1, r1, "c3", R400)
    r2 = _chat(turn2)
    _assert_cache_bound(turn1, turn2, r1, r2)


def test_dedup_enable_midconversation_diverges_at_first_stub():
    """DEDUP_ENABLE_MIDCONVERSATION_DIVERGES_AT_FIRST_STUB: turn 1 rendered with
    the pass off (add_generation_prompt false) and turn 2 (turn 1 + new
    messages) with the pass on agree up to the rendered start of the earliest
    stubbed unit U, and first differ inside U; turn 2 also equals the reference
    rewrite. Mutation: the ordinal counts every message with that role in the
    whole list (caught by the reference equality)."""
    global server
    server.start()
    turn1 = [{"role": "user", "content": "Fix a.c"}] + _tool_turn("c1", R400) + _tool_turn("c2", R400)
    turn2 = turn1 + [{"role": "user", "content": "again"}] + _tool_turn("c3", S400)
    ref = _render({"messages": turn1, "add_generation_prompt": False})
    on = _render({**_pass_on(turn2, ("tool",), 256), "add_generation_prompt": False})
    pos = ref.index(R400, ref.index(R400) + 1)  # U: the second occurrence of R
    d = next((i for i, (a, b) in enumerate(zip(ref, on)) if a != b), None)
    assert d is not None, "turn 2 with the pass on must differ from turn 1 rendered with the pass off"
    assert on[:pos] == ref[:pos]
    assert pos <= d < pos + len(R400), f"first difference at {d}, U spans [{pos}, {pos + len(R400)})"
    ref_messages, _ = goldens.ref_apply(turn2, 256)
    assert on == _render({"messages": ref_messages, "message_dedup": {"enabled": False}, "add_generation_prompt": False})


U300 = goldens.blob("U", 300)  # a repeated user unit, >= min_bytes 256

# (before, after, user_repeat). Every after-setting that keeps the pass on still stubs at
# turns k+1 and k+2, so the k+2 cache bound runs over stubbed prompts: min_bytes 384 still
# qualifies the 400-byte tool units, and roles ["tool","user"] adds a repeated 300-byte
# user unit to the tool repeats.
MIDCONV_CHANGES = {
    "on":        ({"enabled": False},                                     {"enabled": True, "min_bytes": 256}, False),
    "off":       ({"enabled": True, "min_bytes": 256},                    {"enabled": False}, False),
    "min_bytes": ({"enabled": True, "min_bytes": 256},                    {"enabled": True, "min_bytes": 384}, False),
    "roles":     ({"enabled": True, "min_bytes": 256, "roles": ["tool"]}, {"enabled": True, "min_bytes": 256, "roles": ["tool", "user"]}, True),
}


def _midconv_expected_stubs(messages: list, setting: dict) -> list:
    if not setting.get("enabled"):
        return []
    return goldens.ref_apply(messages, setting.get("min_bytes", 1024), tuple(setting.get("roles", ["tool"])))[1]


@pytest.mark.parametrize("change", sorted(MIDCONV_CHANGES))
def test_dedup_midconversation_setting_change(change: str):
    """§7 DEDUP_MIDCONVERSATION_SETTING_CHANGE (on, off, min_bytes, roles): after
    a setting change at turn k+1 (one divergence), turn k+2 with unchanged
    settings meets the cache bound against turn k+1. Where the after-setting
    keeps the pass on, turns k+1 and k+2 hold stubs (min_bytes 256 -> 384 over
    400-byte units; roles ["tool"] -> ["tool","user"] with a repeated 300-byte
    user unit). Mutation: the ordinal counts every message with that role in
    the whole list."""
    global server
    server.start()
    before, after, user_repeat = MIDCONV_CHANGES[change]
    base = [{"role": "user", "content": U300 if user_repeat else "Fix a.c"}] + _tool_turn("c1", R400)
    if user_repeat:
        base += [{"role": "user", "content": U300}]
    base += _tool_turn("c2", R400)
    turn_k = {"messages": base, "message_dedup": before}
    r_k = _chat(turn_k)
    turn_k1 = {**_next_turn(turn_k, r_k, "c3", R400), "message_dedup": after}
    r_k1 = _chat(turn_k1)
    turn_k2 = {**_next_turn(turn_k1, r_k1, "c4", R400), "message_dedup": after}
    for turn in (turn_k1, turn_k2):
        stubs = _midconv_expected_stubs(turn["messages"], after)
        if after.get("enabled"):
            assert stubs, f"{change}: the after-setting must still stub"
        if user_repeat:
            assert any("byte-identical to user message #" in st for _, st in stubs), "roles arm must stub a user unit"
    r_k2 = _chat(turn_k2)
    _assert_cache_bound(turn_k1, turn_k2, r_k1, r_k2)


def test_dedup_first_occurrence_removed():
    """§7 DEDUP_FIRST_OCCURRENCE_REMOVED: after history truncation no stub
    ordinal or tool name points at a message missing from the request.
    Mutation: ORDINAL counts earlier messages of every role."""
    global server
    server.message_dedup = True
    server.start()
    messages = _msgs("truncated_history")
    prompt = _render({"messages": messages})
    n_tool = sum(1 for m in messages if m["role"] == "tool")
    for ordinal in re.findall(r"byte-identical to tool result #(\d+)", prompt):
        assert 1 <= int(ordinal) <= n_tool
    names = {tc["function"]["name"] for m in messages for tc in m.get("tool_calls") or []}
    for name in re.findall(r"byte-identical to tool result #\d+ \(([^)]*)\)", prompt):
        assert name in names
    _check_equiv(messages, expect_stubs=1)


def test_dedup_first_occurrence_not_rendered():
    """§7 DEDUP_FIRST_OCCURRENCE_NOT_RENDERED: under a fixture template that
    renders only the last tool message, the request returns 200, the stub is
    present and equivalence with manual substitution holds. Mutation: the
    stubbed message's role is rewritten to `user`."""
    global server
    server.chat_template = None
    server.chat_template_file = "fixtures/message_dedup/last_tool_only.jinja"
    server.start()
    messages = _msgs("s8_1_reread_file")
    prompt, _ = _check_equiv(messages, expect_stubs=1)
    assert goldens.STUB_8_1 in prompt
    assert F not in prompt, "the template drops the first occurrence"


def test_dedup_cross_role_authority_relocation():
    """§7 DEDUP_CROSS_ROLE_AUTHORITY_RELOCATION: under roles
    ["tool","user","system"], tool results reproducing a later user message
    and a later system message leave both in full. Mutation: the role is
    dropped from the key."""
    global server
    server.start()
    body = _pass_on(_msgs("cross_role_relocation"), ("tool", "user", "system"))
    assert _render(body) == goldens.load_golden("cross_role_relocation")


def test_dedup_repeated_instruction_suppressed():
    """§7 DEDUP_REPEATED_INSTRUCTION_SUPPRESSED (server side; the model side is
    AC_Q07): with `system` opted in, a re-sent system reminder is stubbed as
    `system message #1`, the behavior as specified. Mutation: `system` is never indexed."""
    global server
    server.start()
    prompt, _ = _check_equiv(_msgs("system_reminder_repeat"), ("system",), expect_stubs=1)
    assert "byte-identical to system message #1, " in prompt


def test_dedup_stub_alters_template_control_flow():
    """§7 DEDUP_STUB_ALTERS_TEMPLATE_CONTROL_FLOW: under
    models/templates/Qwen3.5-4B.jinja with `user` opted in, a repeated
    <tool_response> user message is stubbed; the request returns 200 and
    equivalence with manual substitution holds. Mutation: the stubbed
    message's role is rewritten to `user`, which breaks the equivalence.
    Red proof: M13 (role rewritten to `user`) is EQUIVALENT here — the stubbed
    message already has role `user`, so the rewrite is a no-op; the planted red
    proof is M09 (ORDINAL counted over every role), which changes the stub's
    `user message #N` and breaks the equivalence. And (the documented response):
    the stub moves the template's last query, so the earlier assistant reasoning
    that the pass-off render shows is no longer rendered."""
    global server
    server = goldens.make_server("tinyllama2_qwen35_template")
    server.start()
    messages = _msgs("qwen35_user_wrap")
    prompt, _ = _check_equiv(messages, ("user",), expect_stubs=1)
    off = _render({"messages": messages, "message_dedup": {"enabled": False}})
    assert "Need the file." in off
    assert "Need the file." not in prompt


def test_dedup_lookalike_in_untrusted_content():
    """§7 DEDUP_LOOKALIKE_IN_UNTRUSTED_CONTENT (server side, /apply-template;
    the dedup_n clause joins in increment 11): a tool result that is a
    lookalike citing `system message #1` renders verbatim under the widest
    role set. Mutation: stub-shaped content is replaced by the content of the
    message it names."""
    global server
    server.start()
    body = _pass_on(_msgs("lookalike_system_ref"), ("tool", "user", "system"))
    assert _render(body) == goldens.load_golden("lookalike_system_ref")


def test_dedup_match_oracle():
    """§7 DEDUP_MATCH_ORACLE (/apply-template; the dedup_n clause joins in
    increment 11): no state across requests. After request 1 held unit G, a
    request 2 holding G once renders G in full. Mutation: the index is a
    function-static that survives across requests."""
    global server
    server.start()
    g = goldens.blob("GUESS", 1100)
    req1 = [{"role": "user", "content": "hidden"}, {"role": "tool", "tool_call_id": "h", "content": g}]
    req2 = [{"role": "user", "content": "guess"}, {"role": "tool", "tool_call_id": "q", "content": g}]
    _render(_pass_on(req1, ("tool", "user", "system")))
    for _ in range(2):
        prompt = _render(_pass_on(req2, ("tool", "user", "system")))
        assert prompt.count(g) == 1
        assert "duplicate content omitted" not in prompt
