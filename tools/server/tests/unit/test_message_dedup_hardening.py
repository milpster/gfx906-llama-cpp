#!/usr/bin/env python
"""SPEC-0001 (server message dedup), increment 12: hardening over HTTP.

Contracts: DEDUP_OVERRIDE_MALFORMED_NEVER_500 (the HTTP arm; the ctest arm on
*resolve* is tests/test-server-message-dedup.cpp) and DEDUP_NO_CONTENT_IN_LOGS,
with their §7 failure modes DEDUP_OVERRIDE_MALFORMED_TYPE and
DEDUP_CONTENT_LOGGED, under §5 S1 (no content in logs) and S2 (malformed input
fails closed as 400).

Plan row: docs/graph/plans/grill/spec-0001-inc-12-malformed-and-logging.md.
Each test names, in its docstring, the planted defect that must turn it red.

Log-test design (spec §10 harness constraints, "Log test"):
- the server runs with `--verbose` (debug) and its stdout/stderr go to a file;
- R goes to /v1/chat/completions, never /apply-template, because the transport
  body log (server-http.cpp:69-70) would carry the rendered prompt;
- excluded lines (spec §9.3 AC_N03, by exact logger message prefix, nothing
  else): the two transport body lines (`request:  ` / `response: `,
  server-http.cpp:69-70, not installed today but excluded by contract), the
  `SRV_DBG` "converted request" lines (server-context.cpp) and the `SLT_DBG`
  "launching slot" line (launch_slot_with_task); those belong to
  crosscut.security, not to the pass;
- M1 spans several tokens, because the DBG "prompt token" lines print one
  token piece per line.

The peak-RSS bench of the plan note (orchestrator.42.reliability.2) is
test_dedup_pass_peak_rss_bench at the end of this file.
"""
import json
import os
import re
import sys
import time
from pathlib import Path

import pytest
import requests

# ensure grandparent path is in sys.path
path = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(path))

from utils import *  # noqa: E402,F403
from fixtures.message_dedup import dedup_goldens as goldens  # noqa: E402

SERVER_KEY = "tinyllama2_chatml"  # tinyllama2 + jinja + chatml (spec §10 test homes)


def _new_server(**attrs):
    server = goldens.make_server(SERVER_KEY)
    for k, v in attrs.items():
        setattr(server, k, v)
    return server


def _post_raw(server, path: str, raw: str, timeout: float = 60) -> requests.Response:
    """POST a JSON text as-is, so literals such as `1e3` or 2^63 reach the
    server byte for byte (requests' json= would re-serialize them)."""
    return requests.post(server.make_url(path), data=raw.encode("utf-8"),
                         headers={"Content-Type": "application/json"}, timeout=timeout)


# ---------------------------------------------------------------------------
# The seven JSON chat endpoints of §4.0, each with a minimal valid body.
# ---------------------------------------------------------------------------

_CHAT_BODY = {"messages": [{"role": "user", "content": "hi"}], "max_tokens": 2}
_RESPONSES_BODY = {"model": "test", "input": "hi", "max_output_tokens": 2}
_ANTHROPIC_BODY = {"model": "test", "max_tokens": 2, "messages": [{"role": "user", "content": "hi"}]}

JSON_CHAT_ENDPOINTS = {
    "/v1/chat/completions": _CHAT_BODY,
    "/v1/responses": _RESPONSES_BODY,
    "/v1/messages": _ANTHROPIC_BODY,
    "/apply-template": _CHAT_BODY,
    "/v1/chat/completions/input_tokens": _CHAT_BODY,
    "/v1/responses/input_tokens": _RESPONSES_BODY,
    "/v1/messages/count_tokens": _ANTHROPIC_BODY,
}

# ---------------------------------------------------------------------------
# §7 DEDUP_OVERRIDE_MALFORMED_TYPE inputs.
# Each case: (raw JSON text of the `message_dedup` value,
#             client values that must NOT appear in the error message / log,
#             fixed strings that MUST appear in the error message).
# Sent values are chosen distinctive, so a substring hit is an echo, not a
# coincidence with the fixed rule text.
# ---------------------------------------------------------------------------

DEEP = 300
_DEEP_LEAF = '"zqdeepleaf4417"'
_DEEP_VALUE = "[" * DEEP + _DEEP_LEAF + "]" * DEEP

MALFORMED_CASES = {
    "min_bytes_float_1e3":     ('{"min_bytes": 1e3}', ["1e3", "1000"], []),
    "min_bytes_string_1024":   ('{"min_bytes": "1024"}', ["1024"], []),
    # above 2^63 reads as a negative long long; its wrapped reading must not leak either
    "min_bytes_above_2p63":    ('{"min_bytes": 9300000000000000017}', ["9300000000000000017", "9146744073709551599"], []),
    # range violations (§7 DEDUP_OVERRIDE_INVALID) share the §5 S1 no-echo rule; without them a
    # range message that echoes the number survives (planted mutant H9, increment 12 sweep)
    "min_bytes_above_int32":   ('{"min_bytes": 2147483648417}', ["2147483648417"], []),
    "min_bytes_negative":      ('{"min_bytes": -77731}', ["77731"], []),
    "min_bytes_above_2p64":    ('{"min_bytes": 18446744073709551627}', ["18446744073709551627", "1.8446"], []),
    "min_bytes_true":          ('{"min_bytes": true}', ["true"], []),
    "roles_number":            ('{"roles": 31337}', ["31337"], []),
    "roles_holding_number":    ('{"roles": ["tool", 31337]}', ["31337"], []),
    "roles_holding_object":    ('{"roles": [{"zqobjkey9051": "zqobjval9052"}]}', ["zqobjkey9051", "zqobjval9052"], []),
    "roles_nested_deep":       ('{"roles": ' + _DEEP_VALUE + '}', ["zqdeepleaf4417", "[[["], []),
    "enabled_nested_deep":     ('{"enabled": ' + _DEEP_VALUE + '}', ["zqdeepleaf4417", "[[["], []),
    "enabled_object_deep":     ('{"enabled": ' + '{"a":' * DEEP + _DEEP_LEAF + "}" * DEEP + "}", ["zqdeepleaf4417", '{"a"'], []),
    "roles_unknown_string":    ('{"roles": ["zqrole7713"]}', ["zqrole7713"], []),
    # unknown keys: `bad key!` fails ^[A-Za-z0-9_]{1,32}$ and is never echoed;
    # `ab_1` passes it and is echoed (S1), while its value is not.
    "unknown_key_not_echoed":  ('{"bad key!": "zqval3301"}', ["bad key", "zqval3301"], []),
    "unknown_key_echoed":      ('{"ab_1": "zqval3302"}', ["zqval3302"], ["ab_1"]),
}


def _raw_body(base: dict, dedup_raw: str) -> str:
    placeholder = "\"__DEDUP_PLACEHOLDER__\""
    text = json.dumps({**base, "message_dedup": "__DEDUP_PLACEHOLDER__"})
    assert text.count(placeholder) == 1
    return text.replace(placeholder, dedup_raw)


@pytest.mark.parametrize("endpoint", sorted(JSON_CHAT_ENDPOINTS))
def test_dedup_override_malformed_never_500(endpoint: str):
    """DEDUP_OVERRIDE_MALFORMED_NEVER_500 (HTTP arm), §7 DEDUP_OVERRIDE_MALFORMED_TYPE:
    every malformed `message_dedup` of §7 (min_bytes 1e3 / "1024" / above 2^63 /
    true; roles holding a number or an object; a value nested 300 levels deep;
    plus the out-of-range integers 2147483648417 and -77731)
    POSTed to this JSON chat endpoint gives 400 with the §6.6 body, never 500;
    the error `message` holds none of the sent values; an unknown key
    `bad key!` is not echoed while `ab_1` is.
    Planted defect (RED proof): a `get<int>()` on `min_bytes` outside
    *resolve* (for example in the parser before `dedup_resolve`), which
    throws nlohmann::json::type_error -> 500."""
    server = _new_server()
    server.start()
    base = JSON_CHAT_ENDPOINTS[endpoint]
    failures = []
    for case, (dedup_raw, sent, must_echo) in sorted(MALFORMED_CASES.items()):
        res = _post_raw(server, endpoint, _raw_body(base, dedup_raw))
        try:
            body = res.json()
        except ValueError:
            body = None
        err = body.get("error", {}) if isinstance(body, dict) else {}
        message = err.get("message", "") if isinstance(err, dict) else ""
        problems = []
        if res.status_code != 400:
            problems.append(f"status {res.status_code}")
        if not isinstance(err, dict) or err.get("code") != 400 or err.get("type") != "invalid_request_error":
            problems.append("body is not the §6.6 invalid_request_error shape")
        if "message_dedup" not in message:
            problems.append("message does not name message_dedup")
        echoed = [v for v in sent if v in message]
        if echoed:
            problems.append(f"message echoes sent value(s) {echoed}")
        missing = [v for v in must_echo if v not in message]
        if missing:
            problems.append(f"message does not echo allowlisted key(s) {missing}")
        if problems:
            failures.append(f"{case}: {'; '.join(problems)} | body {res.text[:300]!r}")
    assert not failures, f"{endpoint}:\n  " + "\n  ".join(failures)


# ---------------------------------------------------------------------------
# Log helpers
# ---------------------------------------------------------------------------

# the lines DEDUP_NO_CONTENT_IN_LOGS excludes (spec §9.3 AC_N03, amended; §4/§7 aligned in 2f71dbe5f),
# matched only on the exact logger message prefix at the start of the line (after an optional
# colour code and the "<elapsed> <level> " prefix): SRV_DBG prints "srv  %12.*s: " with __func__, so
# log_server_request (server-http.cpp:69-70) shows as "log_server_r", the converted-request lambdas
# (server-context.cpp) as "  operator()", and SLT_DBG in launch_slot_with_task as
# "slot launch_slot_: id %2d | task %d | ". A line that merely contains one of those messages
# elsewhere is scored. Mirror of tools/server/tests/eval/message_dedup/plant_gates.py `_EXCLUDED`.
_EXCLUDED = re.compile(
    r"^(?:\x1b\[[0-9;]*m)*(?:\d+(?:\.\d+)* [A-Z] )?(?:\x1b\[[0-9;]*m)*"   # optional colour + "<elapsed> <level> "
    r"(?:srv  log_server_r: (?:request:  |response: )"                     # transport body lines
    r"|srv    operator\(\): converted request: "                            # converted request lines
    r"|slot launch_slot_: id +\d+ \| task -?\d+ \| launching slot : )")     # SLT_DBG launching slot
# ANSI colour codes and the logger's "<elapsed> <level> " prefix, stripped before
# comparing runs, so "only in the pass-on run" compares what was logged, not when
_ANSI = re.compile(r"\x1b\[[0-9;]*m")
_PREFIX = re.compile(r"^\d+\.\d+\.\d+\.\d+ [A-Z] ")


def _norm(line: str) -> str:
    return _PREFIX.sub("", _ANSI.sub("", line))


# The exclusion rule, pure (no server). Spec §9.3 AC_N03 amended 2026-09-25 (grill §12
# row 36): excluded are exactly the transport `request:`/`response:` lines, the `converted
# request` lines and the SLT_DBG `launching slot : %s` line (server-context.cpp:1784, in
# launch_slot_with_task, so "slot launch_slot_: id %2d | task %d | "). No other line. Same
# corpus as tools/server/tests/eval/message_dedup/tests/test_plant_gates.py
# (AC_N03_EXCLUDED_LINES / AC_N03_SCORED_LINES), synthetic.
_UNIT_X = "SECRET-UNIT-" + "q" * 64
_EXCLUDED_LINES = {
    "request": f'0.00.001.000 D srv  log_server_r: request:  {{"messages": "{_UNIT_X}"}}',
    "response": f'0.00.001.000 D srv  log_server_r: response: {{"prompt": "{_UNIT_X}"}}',
    "converted_request": f'0.00.001.000 D srv    operator(): converted request: {{"messages": "{_UNIT_X}"}}',
    "launching_slot": f'0.00.001.000 D slot launch_slot_: id  0 | task 7 | launching slot : {{"prompt": "{_UNIT_X}"}}',
    "launching_slot_wide_ids": f'0.00.001.000 D slot launch_slot_: id 12 | task 12345 | launching slot : '
                               f'{{"prompt": "{_UNIT_X}"}}',
}
_SCORED_LINES = {
    "dedup_launching_slot_ish": f"0.00.001.000 D srv  dedup_apply: launching slot-ish {_UNIT_X}",
    "launching_slot_not_message_start": f"0.00.001.000 D slot launch_slot_: id  0 | task 7 | dedup: launching slot : {_UNIT_X}",
    "launching_slot_other_function": f"0.00.001.000 D slot dedup_apply: id  0 | task 7 | launching slot : {_UNIT_X}",
    "dedup_response": f"0.00.001.000 D srv  dedup_apply: response: {_UNIT_X}",
    "dedup_converted_request": f"0.00.001.000 D srv  dedup_apply: converted request: {_UNIT_X}",
    "dedup_request": f"0.00.001.000 D srv  dedup_apply: request:  {_UNIT_X}",
}


@pytest.mark.parametrize("name", sorted(_EXCLUDED_LINES))
def test_dedup_no_content_in_logs_excluded_lines(name: str):
    """DEDUP_NO_CONTENT_IN_LOGS exclusion (spec §9.3 AC_N03, amended): the
    request/response, converted request and `launching slot` debug lines,
    with their exact logger prefixes, are excluded."""
    assert _EXCLUDED.search(_EXCLUDED_LINES[name])


@pytest.mark.parametrize("name", sorted(_SCORED_LINES))
def test_dedup_no_content_in_logs_lookalike_lines_scored(name: str):
    """DEDUP_NO_CONTENT_IN_LOGS control: a line that only contains one of the
    excluded messages under another logger prefix is not excluded."""
    assert not _EXCLUDED.search(_SCORED_LINES[name])


class _LogWindow:
    """Byte-offset window over the server's log file."""

    def __init__(self, log_path: Path):
        self.log_path = log_path

    def size(self) -> int:
        return self.log_path.stat().st_size if self.log_path.exists() else 0

    def settle(self, quiet_s: float = 0.6, timeout_s: float = 20.0) -> int:
        """Wait until the log stops growing (the logger has a worker thread)."""
        deadline = time.time() + timeout_s
        last = self.size()
        stable_since = time.time()
        while time.time() < deadline:
            time.sleep(0.1)
            cur = self.size()
            if cur != last:
                last, stable_since = cur, time.time()
            elif time.time() - stable_since >= quiet_s:
                break
        return last

    def lines(self, start: int, end: int) -> list[str]:
        with open(self.log_path, "rb") as f:
            f.seek(start)
            data = f.read(end - start)
        return data.decode("utf-8", errors="replace").splitlines()


def _logged_server(tmp_path: Path, debug: bool, **attrs):
    log_path = tmp_path / "server.log"
    server = _new_server(log_path=str(log_path), debug=debug, **attrs)
    server.start()
    return server, _LogWindow(log_path)


def _window(server, log: _LogWindow, method: str, path: str, raw: str | None = None, data=None):
    start = log.settle()
    if raw is not None:
        res = _post_raw(server, path, raw)
        status, text = res.status_code, res.text
    else:
        res = server.make_request(method, path, data=data)
        status, text = res.status_code, json.dumps(res.body) if not isinstance(res.body, str) else res.body
    end = log.settle()
    return status, text, log.lines(start, end)


@pytest.mark.parametrize("case", sorted(MALFORMED_CASES))
def test_dedup_override_malformed_type(case: str, tmp_path: Path):
    """§7 DEDUP_OVERRIDE_MALFORMED_TYPE (the log side; contract
    DEDUP_OVERRIDE_MALFORMED_NEVER_500): a malformed `message_dedup` on
    /v1/chat/completions writes exactly one WRN "got exception" line
    (tools/server/server.cpp:79), and that line holds no sent value (an
    allowlisted unknown key such as `ab_1` may appear).
    Planted defect (RED proof): the error message echoes the sent value
    (for example `"message_dedup.min_bytes must be an integer, got " + value.dump()`)."""
    server, log = _logged_server(tmp_path, debug=False)
    dedup_raw, sent, _ = MALFORMED_CASES[case]
    status, text, lines = _window(server, log, "POST", "/v1/chat/completions",
                                  raw=_raw_body(_CHAT_BODY, dedup_raw))
    assert status == 400, f"status {status}, body {text[:300]!r}"
    wrn = [ln for ln in lines if "got exception" in ln]
    assert len(wrn) == 1, f"expected one WRN line, got {len(wrn)}: {wrn}"
    echoed = [v for v in sent if v in wrn[0]]
    assert not echoed, f"WRN line echoes sent value(s) {echoed}: {wrn[0][:300]!r}"


# ---------------------------------------------------------------------------
# DEDUP_NO_CONTENT_IN_LOGS: R with the pass on, then R with the pass off.
# Units are ~400 bytes with min_bytes 256 (tinyllama2 slots hold 2048 tokens).
# ---------------------------------------------------------------------------

M1 = "ZQXmarkONEkappa7731"          # multi-token marker at the head of the stubbed unit
M2 = "zqm2_probe_tool_4471"          # unique name, matches ^[A-Za-z0-9_.-]{1,64}$
UNIT = goldens.blob("U", 400, head=M1 + " opens this synthetic tool result.\n")
OTHER = goldens.blob("V", 400, head="An unrelated synthetic tool result.\n")


def _r_messages() -> list:
    return [
        {"role": "user", "content": "Read the file twice."},
        goldens.asst_call("c1", M2),
        goldens.tool("c1", UNIT),
        goldens.asst_call("c2", "read_file"),
        goldens.tool("c2", OTHER),
        goldens.asst_call("c3", M2),
        goldens.tool("c3", UNIT),
    ]


def _r_body(enabled: bool) -> dict:
    return {"messages": _r_messages(), "max_tokens": 4, "cache_prompt": False,
            "message_dedup": {"enabled": enabled, "roles": ["tool"], "min_bytes": 256}}


def _units() -> list[str]:
    return [m["content"] for m in _r_messages() if isinstance(m.get("content"), str) and m["content"]]


def _windows32(s: str) -> set[bytes]:
    b = s.encode("utf-8")
    return {b[i:i + 32] for i in range(0, max(0, len(b) - 31))}


def _content_hits(line: str, windows: set[bytes]) -> list[str]:
    hits = [m for m in (M1, M2) if m in line]
    lb = line.encode("utf-8", errors="replace")
    if any(w in lb for w in windows):
        hits.append("32-byte unit substring")
    return hits


def test_dedup_no_content_in_logs(tmp_path: Path):
    """DEDUP_NO_CONTENT_IN_LOGS (§5 S1): at debug verbosity with a log file,
    R (the pass on, stubbing a unit that opens with the multi-token marker M1,
    first paired with the allowlisted tool name M2) is sent to
    /v1/chat/completions, then R with `message_dedup.enabled: false`. No line
    that appears only in the pass-on run holds M1, M2 or a 32-byte substring
    of any unit (excluding, by exact logger message prefix, the
    server-http.cpp:69-70 request/response body lines, the SRV_DBG
    "converted request" lines and the SLT_DBG "launching slot" line).
    Planted defect (RED proof): a DBG line in dedup_apply that prints the
    excerpt (for example `SRV_DBG("dedup stub: %s\\n", stub.c_str())`)."""
    # Given: the reference stub for R carries M1 and M2, so a line printing
    # the stub, its excerpt or its tool name would be caught.
    ref_messages, records = goldens.ref_apply(_r_messages(), 256, ("tool",))
    assert len(records) == 1, f"R must stub exactly one unit, the reference made {len(records)}"
    stub = ref_messages[-1]["content"]
    assert M1 in stub and M2 in stub, f"reference stub must carry M1 and M2: {stub!r}"

    server, log = _logged_server(tmp_path, debug=True)
    status_on, text_on, on_lines = _window(server, log, "POST", "/v1/chat/completions", data=_r_body(True))
    assert status_on == 200, text_on[:300]
    status_off, text_off, off_lines = _window(server, log, "POST", "/v1/chat/completions", data=_r_body(False))
    assert status_off == 200, text_off[:300]
    assert on_lines, "debug log wrote nothing for the pass-on run"

    off_set = {_norm(ln) for ln in off_lines}
    windows = set().union(*(_windows32(u) for u in _units()))
    offending = []
    for ln in on_lines:
        if _norm(ln) in off_set or _EXCLUDED.search(ln):
            continue
        hits = _content_hits(ln, windows)
        if hits:
            offending.append(f"{hits}: {ln[:200]!r}")
    assert not offending, "pass-on-only log lines carry content:\n  " + "\n  ".join(offending)


# invalid overrides that carry M1 in a client value (or a non-echo-safe key)
CONTENT_OVERRIDES = {
    "roles_element":       {"roles": [M1]},
    "min_bytes_string":    {"min_bytes": M1},
    "enabled_string":      {"enabled": M1},
    "echoable_key_value":  {"ab_1": M1},
    "unsafe_key":          {M1 + " !": 1},
    "not_an_object":       M1,
}


@pytest.mark.parametrize("case", sorted(CONTENT_OVERRIDES))
def test_dedup_content_logged(case: str, tmp_path: Path):
    """§7 DEDUP_CONTENT_LOGGED (contract DEDUP_NO_CONTENT_IN_LOGS, §5 S1): at
    debug verbosity, an invalid override on /v1/chat/completions that carries
    the marker M1 in a value (or in a key that fails the echo allowlist) gives
    400 and writes no log line with M1 (excluded, by exact logger message
    prefix: the server-http.cpp:69-70 request/response body lines, the SRV_DBG
    "converted request" lines and the SLT_DBG "launching slot" line).
    Planted defect (RED proof): the invalid-override path logs the raw value
    (for example `SRV_WRN("bad message_dedup: %s\\n", body.at("message_dedup").dump().c_str())`)."""
    server, log = _logged_server(tmp_path, debug=True)
    body = {**_CHAT_BODY, "message_dedup": CONTENT_OVERRIDES[case]}
    status, text, lines = _window(server, log, "POST", "/v1/chat/completions", data=body)
    assert status == 400, f"status {status}, body {text[:300]!r}"
    assert M1 not in text, f"error body echoes M1: {text[:300]!r}"
    offending = [ln for ln in lines if M1 in ln and not _EXCLUDED.search(ln)]
    assert not offending, "log lines carry M1:\n  " + "\n  ".join(ln[:200] for ln in offending)


# ---------------------------------------------------------------------------
# Peak-RSS bench (plan note 2026-09-23, orchestrator.42.reliability.2; grill
# §11 concurrency row). CPU-only by design: the harness env hides the GPUs.
# ---------------------------------------------------------------------------

# ~100 MiB, kept under cpp-httplib's CPPHTTPLIB_PAYLOAD_MAX_LENGTH (100 MiB,
# vendor/cpp-httplib/httplib.h:130), above which the server answers 413
RSS_BODY_MIB = float(os.environ.get("SPEC0001_RSS_BODY_MIB", "98"))
RSS_UNIT_BYTES = 4096
HTTPLIB_PAYLOAD_MAX = 100 * 1024 * 1024


def _rss_body() -> tuple[str, int]:
    """~RSS_BODY_MIB MiB of tool results: half unique units, half repeats of
    earlier ones, so the pass indexes and stubs at scale."""
    target = int(RSS_BODY_MIB * 1024 * 1024)
    probe = goldens.blob("P000000", RSS_UNIT_BYTES)
    per_msg = len(json.dumps({"role": "tool", "tool_call_id": "c000000", "content": probe}).encode()) + 2
    n = max(4, target // per_msg)
    pool = [goldens.blob(f"P{i:06d}", RSS_UNIT_BYTES) for i in range(n // 2)]
    messages = [{"role": "user", "content": "bench"}]
    for i in range(n):
        messages.append({"role": "tool", "tool_call_id": f"c{i}", "content": pool[i % len(pool)]})
    raw = json.dumps({"messages": messages, "message_dedup": {"enabled": True}})
    size = len(raw.encode("utf-8"))
    assert size < HTTPLIB_PAYLOAD_MAX, f"bench body {size} B would be refused with 413"
    return raw, size


def _vm_kib(pid: int, field: str) -> int:
    with open(f"/proc/{pid}/status") as f:
        for ln in f:
            if ln.startswith(field + ":"):
                return int(ln.split()[1])
    raise AssertionError(f"{field} not in /proc/{pid}/status")


def _mem_available_kib() -> int:
    with open("/proc/meminfo") as f:
        for ln in f:
            if ln.startswith("MemAvailable:"):
                return int(ln.split()[1])
    raise AssertionError("MemAvailable not in /proc/meminfo")


def _peak_rss_after(raw: str, flag: bool) -> tuple[int, int]:
    server = _new_server(message_dedup=flag)
    server.start()
    try:
        # the override is always `enabled: true` in the body; the off arm turns it off
        body = raw if flag else raw.replace('"message_dedup": {"enabled": true}', '"message_dedup": {"enabled": false}')
        res = _post_raw(server, "/apply-template", body, timeout=900)
        assert res.status_code == 200, f"status {res.status_code}: {res.text[:300]!r}"
        prompt_len = len(res.json()["prompt"])
        return _vm_kib(server.process.pid, "VmHWM"), prompt_len
    finally:
        server.stop()


@pytest.mark.skipif(sys.platform != "linux", reason="reads /proc/<pid>/status VmHWM")
def test_dedup_pass_peak_rss_bench():
    """DEDUP_PASS_COST_WITHIN_BUDGET, memory arm (plan note of increment 12,
    orchestrator.42.reliability.2): a ~100 MiB /apply-template request, the
    pass on vs off (tinyllama2, GPUs hidden). Pass when the VmHWM difference
    is <= 4x the body and 15x the difference is < 25% of MemAvailable.
    What it can see: the difference is on minus off, and the pass-on prompt is
    much smaller (at 98 MiB the stubs save ~630 MB of peak), so extra pass memory
    below that saving is masked; the bench catches retention that grows with the
    number of stubbed units, not a constant or linear extra copy. The index's one
    owning copy of each unit is by design (spec §5 S7), not a defect.
    Conformance; planted defect (RED proof): dedup_apply keeps a deep copy of the
    whole message array per stubbed unit, alive until the pass returns. Planted at
    SPEC0001_RSS_BODY_MIB=2 (at 98 MiB the defect would exhaust host memory)."""
    raw, body_bytes = _rss_body()
    hwm_off, len_off = _peak_rss_after(raw, flag=False)
    hwm_on, len_on = _peak_rss_after(raw, flag=True)
    assert len_on < len_off, "the pass stubbed nothing; the bench did not exercise it"
    diff_bytes = max(0, hwm_on - hwm_off) * 1024
    mem_avail = _mem_available_kib() * 1024
    print(f"[rss-bench] body={body_bytes} B, VmHWM off={hwm_off} KiB on={hwm_on} KiB, "
          f"diff={diff_bytes} B, MemAvailable={mem_avail} B, prompt off={len_off} on={len_on}")
    assert diff_bytes <= 4 * body_bytes, f"VmHWM difference {diff_bytes} B > 4x body {body_bytes} B"
    assert 15 * diff_bytes < 0.25 * mem_avail, f"15 x {diff_bytes} B >= 25% of MemAvailable {mem_avail} B"
