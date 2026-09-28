#!/usr/bin/env python
"""SPEC-0001 increment 18 (RED): the tool simulator sandboxes ``run_tests``.

Security note: docs/graph/plans/spec-0001-inc-18-security-note.md
(findings F1-F4, fix direction). ``run_tests`` executes model-written code,
the name screen (``_guard_edited``) is a denylist and not a control (F1), so
the control is a bubblewrap sandbox that fails closed.

Every probe is benign: it only touches pytest ``tmp_path`` locations, a
loopback listener on an ephemeral port that this test opens, and a
``sleep`` child tagged with a unique marker that a finalizer kills whatever
the outcome. No owner files, no external network.

Each escape probe is delivered two ways:
- ``edit``: a model-written line through ``edit_file`` that passes today's
  name screen (the F1 pattern ``unittest.loader.os...``);
- ``baseline``: the same line already in the snapshot, which the name screen
  never looks at. This keeps the probe a test of the sandbox, not of the
  screen: extending the denylist cannot make these tests pass.

Seams the GREEN (tool-smith) must provide in ``tool_simulator``:
- ``BWRAP``: module attribute, the path of the bubblewrap executable, read
  at every ``run_tests`` call (not captured at import), so a test can point
  it at a missing file or at a program that cannot start a sandbox.
- ``SANDBOX_UNAVAILABLE``: the one fixed ``run_tests`` answer when bwrap is
  missing or cannot start; nothing runs in that case.
- ``ToolSimulator(snapshot)`` raises ``ValueError`` (message names
  "symlink") when the snapshot contains any symlink.

Synthetic snapshots are built in ``tmp_path``; no server.
"""
import json
import os
import signal
import socket
import time
import uuid
from pathlib import Path

import pytest

import _paths  # noqa: F401  (sys.path)

import tool_simulator  # noqa: E402
from tool_simulator import ToolSimulator  # noqa: E402

PROBE_FILE = "tests/test_probe.py"
PROBE_LINE = 2   # the "X = 1" line of the probe test module

PROBE_MODULE = (
    "import unittest\n"
    "X = 1\n"
    "\n"
    "\n"
    "class ProbeTest(unittest.TestCase):\n"
    "    def test_x(self):\n"
    "        self.assertEqual(X, 1)\n"
)

DELIVERY = ("edit", "baseline")


def make_snapshot(root: Path, line2: str | None = None) -> Path:
    """A synthetic snapshot with one unittest module; ``line2`` (if given)
    replaces its line 2 in the snapshot itself (baseline delivery)."""
    snap = root / "snapshot"
    (snap / "tests").mkdir(parents=True)
    (snap / "tests" / "__init__.py").write_text("", encoding="utf-8")
    text = PROBE_MODULE
    if line2 is not None:
        lines = text.split("\n")
        lines[PROBE_LINE - 1] = line2
        text = "\n".join(lines)
    (snap / PROBE_FILE).write_text(text, encoding="utf-8")
    (snap / "SYNTHETIC.txt").write_text("synthetic probe snapshot\n", encoding="utf-8")
    return snap


def run_probe(tmp_path: Path, line: str, delivery: str, time_limit_s: float = 10.0) -> str:
    """Deliver ``line`` as line 2 of the probe module, then call run_tests."""
    snap = make_snapshot(tmp_path, line if delivery == "baseline" else None)
    with ToolSimulator(snap, time_limit_s=time_limit_s) as sim:
        if delivery == "edit":
            ans = sim.call("edit_file", json.dumps({"path": PROBE_FILE, "line": PROBE_LINE, "text": line}))
            assert ans == f"edited {PROBE_FILE}: line {PROBE_LINE} replaced\n", ans
        return sim.call("run_tests", "{}")


def pids_with_marker(marker: str) -> list[int]:
    out = []
    for d in Path("/proc").iterdir():
        if not d.name.isdigit():
            continue
        try:
            cmd = (d / "cmdline").read_bytes()
        except OSError:
            continue
        if marker.encode() in cmd:
            out.append(int(d.name))
    return out


# ---------------------------------------------------------------------------
# F1: no write outside the private temporary copy
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("delivery", DELIVERY)
def test_spec0001_suite_simulator_run_tests_cannot_write_outside_temp_copy(tmp_path, delivery):
    """F1: a line that reaches ``os.system`` through an already-imported
    module writes a marker in tmp_path (outside the snapshot copy); after
    run_tests the marker must not exist."""
    marker = tmp_path / "outside" / "escaped.marker"
    marker.parent.mkdir()
    line = f"X = unittest.loader.os.system('touch {marker}') * 0 + 1"
    run_probe(tmp_path, line, delivery)
    assert not marker.exists(), "run_tests wrote outside its private temporary copy"


# ---------------------------------------------------------------------------
# F4: owner files outside the snapshot are not readable
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("delivery", DELIVERY)
def test_spec0001_suite_simulator_run_tests_cannot_read_outside_canary(tmp_path, delivery):
    """F4: a canary file in tmp_path outside the snapshot; a line prints its
    content at import time; the content must not appear in the report."""
    canary_value = "CANARY-" + uuid.uuid4().hex
    canary = tmp_path / "outside" / "canary.txt"
    canary.parent.mkdir()
    canary.write_text(canary_value + "\n", encoding="utf-8")
    line = f"X = print(unittest.loader.os.popen('cat {canary}').read()) or 1"
    report = run_probe(tmp_path, line, delivery)
    assert canary_value not in report, "run_tests read a file outside the snapshot"


# ---------------------------------------------------------------------------
# F3: no process survives run_tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("delivery", DELIVERY)
def test_spec0001_suite_simulator_run_tests_leaves_no_surviving_process(tmp_path, delivery):
    """F3: a line detaches a ``sleep`` child tagged with a unique argv[0];
    once run_tests has returned, no process carrying the tag remains (a 2 s
    grace covers asynchronous namespace teardown)."""
    tag = "dedupsimprobe" + uuid.uuid4().hex
    line = (f"X = unittest.loader.os.system(\"setsid bash -c 'exec -a {tag} sleep 300' "
            f"</dev/null >/dev/null 2>&1 &\") * 0 + 1")
    try:
        run_probe(tmp_path, line, delivery)
        deadline = time.monotonic() + 2.0
        while pids_with_marker(tag) and time.monotonic() < deadline:
            time.sleep(0.05)
        survivors = pids_with_marker(tag)
        assert not survivors, f"processes survived run_tests: {survivors}"
    finally:
        for pid in pids_with_marker(tag):
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass


# ---------------------------------------------------------------------------
# no network: host loopback is unreachable
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("delivery", DELIVERY)
def test_spec0001_suite_simulator_run_tests_cannot_reach_host_loopback(tmp_path, delivery):
    """No network: the test listens on 127.0.0.1 (ephemeral port); a line
    connects to it through bash /dev/tcp; no connection is accepted."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        port = srv.getsockname()[1]
        line = (f"X = unittest.loader.os.system(\"bash -c 'echo probe > /dev/tcp/127.0.0.1/{port}' "
                f"</dev/null >/dev/null 2>&1\") * 0 + 1")
        run_probe(tmp_path, line, delivery)
        srv.settimeout(0.5)
        try:
            conn, _ = srv.accept()
        except (socket.timeout, TimeoutError):
            conn = None
        if conn is not None:
            conn.close()
        assert conn is None, "run_tests reached a host loopback listener"
    finally:
        srv.close()


# ---------------------------------------------------------------------------
# fail closed without bwrap
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bwrap", ("missing", "cannot-start"))
def test_spec0001_suite_simulator_run_tests_fails_closed_without_bwrap(tmp_path, monkeypatch, bwrap):
    """Fail closed: with ``tool_simulator.BWRAP`` pointing at a missing file,
    or at a program that cannot start a sandbox (/bin/false), run_tests
    answers exactly ``SANDBOX_UNAVAILABLE`` and runs nothing (the snapshot's
    own marker-writing line leaves no marker)."""
    marker = tmp_path / "outside" / "ran.marker"
    marker.parent.mkdir()
    target = str(tmp_path / "no-such-bwrap") if bwrap == "missing" else "/bin/false"
    monkeypatch.setattr(tool_simulator, "BWRAP", target, raising=False)
    line = f"X = unittest.loader.os.system('touch {marker}') * 0 + 1"
    ans = run_probe(tmp_path, line, "baseline")
    refusal = getattr(tool_simulator, "SANDBOX_UNAVAILABLE", None)
    assert isinstance(refusal, str) and refusal, "tool_simulator.SANDBOX_UNAVAILABLE is not defined"
    assert ans == refusal
    assert not marker.exists(), "run_tests ran the tests without a sandbox"


# ---------------------------------------------------------------------------
# F2: edit_file rejects control characters
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ctrl", ("\r", "\x00", "\x0b", "\x0c", "\x1b", "\x7f"),
                         ids=("cr", "nul", "vt", "ff", "esc", "del"))
def test_spec0001_suite_simulator_edit_file_rejects_control_characters(tmp_path, ctrl):
    """F2: a text containing a control character (a lone carriage return is a
    Python line break that shifts line numbers past the screen) gets the one
    fixed error the newline case gets, and the file is unchanged."""
    snap = make_snapshot(tmp_path)
    with ToolSimulator(snap) as sim:
        before = sim.call("read_file", {"path": PROBE_FILE})
        fixed = sim.call("edit_file", {"path": PROBE_FILE, "line": PROBE_LINE, "text": "X = 1\nY = 2"})
        ans = sim.call("edit_file", {"path": PROBE_FILE, "line": PROBE_LINE, "text": f"X = 1{ctrl}Y = 2"})
        after = sim.call("read_file", {"path": PROBE_FILE})
    assert fixed.startswith("error: ")
    assert ans == fixed
    assert after == before


def test_spec0001_suite_simulator_edit_file_keeps_tab_indentation(tmp_path):
    """F2 boundary: a tab is indentation, not a line break; it stays accepted."""
    snap = make_snapshot(tmp_path)
    with ToolSimulator(snap) as sim:
        ans = sim.call("edit_file", {"path": PROBE_FILE, "line": 6, "text": "\tdef test_x(self):"})
    assert ans == f"edited {PROBE_FILE}: line 6 replaced\n"


# ---------------------------------------------------------------------------
# symlinks in a snapshot are refused at construction
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("where", ("outside", "inside"))
def test_spec0001_suite_simulator_refuses_snapshot_with_symlink(tmp_path, where):
    """A snapshot containing any symlink (to a canary outside it, or to a file
    inside it) is refused when the simulator is constructed."""
    snap = make_snapshot(tmp_path)
    if where == "outside":
        target = tmp_path / "canary.txt"
        target.write_text("CANARY\n", encoding="utf-8")
    else:
        target = snap / PROBE_FILE
    (snap / "link.txt").symlink_to(target)
    with pytest.raises(ValueError, match="symlink"):
        sim = ToolSimulator(snap)
        sim.close()
