"""SPEC-0001 §9.4 scenario suite: the deterministic tool simulator (live half).

Tool card: docs/graph/tools/message-dedup-scenario-suite.md.
Tests: tests/test_tool_simulator.py (increment 18, row test (1)).

- ``SNAPSHOTS_DIR``: where the synthetic repository snapshots of the real
  scenario set live (``<SUITE_DIR>/snapshots/<repo_snapshot id>/``), beside
  ``scenarios/``. Increment 17 fills it.
- ``ToolSimulator(snapshot_dir, time_limit_s=10.0)``: answers tool calls from
  ONE synthetic snapshot. Deterministic (no clock, no randomness in any
  answer), offline, time-limited per call. Edits are applied only to a
  private temporary copy of the snapshot; the snapshot itself never changes.
  ``call(name, arguments) -> str``: ``arguments`` is the tool call's JSON
  ``arguments`` string (or an already-parsed dict). ``close()`` removes the
  temporary copy. Also a context manager.
- ``UNKNOWN_TOOL_ERROR``: the one fixed response for any tool name outside
  ``TOOLS`` (spec §9.4 "deterministic tool simulator").

Tools, and the exact bytes they answer. They match the scripted-prefix tool
behaviour of the increment-17 generator (``gen_scenarios.py`` ``Conv.execute``),
so the live tail sees the same tool as the prefix did:

- ``read_file`` {path}: the file's text.
- ``grep`` {pattern[, path]}: Python regex, one ``path:line:text`` row per
  matching line over the files in path order, at most 60 rows, then ``\\n``;
  ``no matches for '<pattern>'\\n`` when none.
- ``run_tests`` {}: ``python -m unittest discover -s tests -t . -v`` in a
  fresh temporary copy of the working copy, normalised (temp path, run time,
  stdlib paths) so the report is a pure function of the files.
- ``edit_file`` {path, line, text}: replace 1-based line ``line`` (lines are
  the ``\\n``-split of the file) with ``text``; answers
  ``edited <path>: line <line> replaced\\n``.
- ``run_linter`` {[path]}: the synthetic linter (E501 > 79 chars, W291
  trailing whitespace, T100 ``TODO``) over the ``.py`` files under ``path``.
- ``fetch_url`` {url} (R1): the page text of ``<snapshot>/_web/<host>/<path>``
  (the URL without its scheme; increment-17 convention, PROVENANCE.md).

``_web/`` (simulator data) and the top-level ``SYNTHETIC.txt`` marker are not
part of the repository the prefix saw, so every repository tool (read_file,
grep, run_linter, run_tests, edit_file) ignores them. Any other failure is a
one-line ``error: ...\\n`` answer to the model, never an exception: a missing
file, a path outside the snapshot, bad arguments, an invalid regex, a line out
of range, a time limit hit.

``run_tests`` executes model-written code, so it runs inside a bubblewrap
sandbox (``BWRAP``, a host prerequisite, not a project dependency; security
note docs/graph/plans/spec-0001-inc-18-security-note.md): read-only ``/usr`` and
interpreter prefix, the repository copied onto a tmpfs working directory, a
fresh tmpfs ``/tmp``, no host ``/tmp``, ``$HOME`` (beyond the interpreter
prefix) or network, own PID namespace, killed with its parent, a process-count
cap, CPU/file-size/address-space limits and the per-call time limit; the whole
process group is killed on timeout. It fails closed: when bwrap is missing or
cannot start (preflight on every call), ``run_tests`` answers
``SANDBOX_UNAVAILABLE`` and runs nothing. The name screen on edited lines
(``_guard_edited``) is NOT a control; it only gives the transcript a stable
refusal answer for the obvious cases. ``edit_file`` refuses every control
character except tab, and a snapshot holding any symlink is refused at
construction (``ValueError``). ``grep`` runs in a forked child killed at the
time limit, so a catastrophic regex answers a fixed error.
"""
from __future__ import annotations

import ast
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path, PurePosixPath

SUITE_DIR = Path(__file__).resolve().parent
SNAPSHOTS_DIR = SUITE_DIR / "snapshots"

TOOLS = ("read_file", "grep", "run_tests", "edit_file", "run_linter", "fetch_url")

UNKNOWN_TOOL_ERROR = "error: unknown tool; available tools: " + ", ".join(TOOLS) + "\n"

WEB_DIR = "_web"                          # _web/<host>/<path>: fetch_url pages
HIDDEN = frozenset({WEB_DIR, "SYNTHETIC.txt"})  # top-level entries the repository tools never see
GREP_MAX_ROWS = 60
# edit_file text: one line; any control character but \t is refused (a lone \r is a
# Python line break that would shift line numbers; security note F2)
_CONTROL = re.compile(r"[\x00-\x08\x0a-\x1f\x7f]")
LINT_MAX = 79

# names a model-written line may not use (run_tests executes it)
_FORBIDDEN_NAMES = frozenset({
    "open", "exec", "eval", "compile", "__import__", "getattr", "setattr", "delattr", "globals",
    "locals", "vars", "breakpoint", "input", "memoryview", "__builtins__", "__loader__", "__spec__",
})


class _ToolError(Exception):
    pass


def _err(msg: str) -> str:
    return f"error: {msg}\n"


# ---------------------------------------------------------------------------
# pure tool behaviour over {posix path: text}
# Stable interface: gen_scenarios.py (increment 17) imports grep_repo,
# lint_repo, normalise_test_report and run_tests_repo so the scripted prefix
# and the live tail answer with the same bytes. Keep names and signatures.
# ---------------------------------------------------------------------------

def _under(p: str, path: str | None) -> bool:
    return not path or path in (".", "") or p == path or p.startswith(path.rstrip("/") + "/")


def grep_repo(repo: dict[str, str], pattern: str, path: str | None = None, deadline: float | None = None) -> str:
    rx = re.compile(pattern)
    rows = []
    for p in sorted(repo):
        if not _under(p, path):
            continue
        if deadline is not None and time.monotonic() > deadline:
            raise TimeoutError
        for i, line in enumerate(repo[p].split("\n"), 1):
            if rx.search(line):
                rows.append(f"{p}:{i}:{line}")
    return ("\n".join(rows[:GREP_MAX_ROWS]) + "\n") if rows else f"no matches for {pattern!r}\n"


def lint_repo(repo: dict[str, str], path: str | None = None) -> str:
    rows = []
    for p in sorted(repo):
        if not p.endswith(".py") or not _under(p, path):
            continue
        for i, line in enumerate(repo[p].split("\n"), 1):
            if len(line) > LINT_MAX:
                rows.append(f"{p}:{i}:{LINT_MAX + 1}: E501 line too long ({len(line)} > {LINT_MAX} characters)")
            stripped = line.rstrip(" \t")
            if line != stripped:
                rows.append(f"{p}:{i}:{len(stripped) + 1}: W291 trailing whitespace")
            if "TODO" in line:
                rows.append(f"{p}:{i}:{line.index('TODO') + 1}: T100 TODO marker left in code")
    return "\n".join(rows) + f"\nFound {len(rows)} problem(s).\n" if rows else "No problems found.\n"


_CARET_LINE = re.compile(r"^[ \t]*[\^~][ \t\^~]*$\n?", re.M)


def normalise_test_report(out: str, tmpdir: str) -> str:
    """The unittest report as a pure function of the files: the temp path, the
    run time and the stdlib paths are normalised, and traceback caret lines
    (only spaces, ``^`` and ``~``; their shape differs between Python 3.11 and
    3.13+) are dropped, so the report is the same on any interpreter.
    Stable interface: gen_scenarios.py imports it."""
    out = _CARET_LINE.sub("", out)
    out = out.replace(tmpdir + "/", "").replace(tmpdir, ".")
    out = re.sub(r"Ran (\d+) tests? in [0-9.]+s", r"Ran \1 tests in 0.004s", out)
    out = re.sub(r'File ".*?/(unittest|python3\.\d+)/', r'File "<stdlib>/', out)
    out = out.replace("<stdlib>", "stdlib")
    return out.strip("\n") + "\n"


# --- the run_tests sandbox (security note F1-F4: docs/graph/plans/spec-0001-inc-18-security-note.md)

BWRAP = "/usr/bin/bwrap"   # host prerequisite (bubblewrap); read at every run_tests call
SANDBOX_UNAVAILABLE = "run_tests refused: the test sandbox (bubblewrap) is unavailable, so nothing was run\n"
SANDBOX_WORK = "/work"     # the one read-write directory inside the sandbox (a tmpfs)
SANDBOX_SRC = "/src"       # the repository copy, bound read-only, copied into SANDBOX_WORK
NPROC_HEADROOM = 128       # tasks the sandbox may add to the owner's current count (fork-bomb cap)
PREFLIGHT_TIMEOUT_S = 10.0
STATUS_FD_PLACEHOLDER = "{status-fd}"   # replaced by _run_group with a pipe bwrap reports "child-pid" on
SANDBOX_RESOURCE_EXHAUSTED = ("run_tests failed: the host is out of process slots (EAGAIN), so the tests "
                              "could not run; this is an infrastructure error\n")
_EAGAIN_TEXT = "Resource temporarily unavailable"


class SandboxResourceError(BlockingIOError):
    """The sandbox could not start or fork for lack of host resources (EAGAIN,
    e.g. the RLIMIT_NPROC cap hit by host load): not a model outcome."""


def _interpreter() -> tuple[str, str]:
    """(real interpreter path, its installation prefix): the venv's base
    interpreter, so only that prefix has to be visible in the sandbox."""
    exe = getattr(sys, "_base_executable", None) or sys.executable
    return str(Path(exe).resolve()), str(Path(sys.base_prefix).resolve())


def _bwrap_argv(bwrap: str, src: str | None) -> list[str]:
    """Read-only system and interpreter, a tmpfs /tmp and SANDBOX_WORK, no host
    /tmp, $HOME or network, own PID/IPC/UTS/user namespaces, killed with its parent."""
    _, prefix = _interpreter()
    argv = [bwrap, "--unshare-all", "--unshare-net", "--unshare-pid", "--die-with-parent", "--new-session",
            "--cap-drop", "ALL", "--json-status-fd", STATUS_FD_PLACEHOLDER,
            "--ro-bind", "/usr", "/usr"]
    for link in ("bin", "sbin", "lib", "lib64"):
        p = Path("/") / link
        if p.is_symlink():
            argv += ["--symlink", str(Path(p.readlink())), str(p)]
        elif p.is_dir():
            argv += ["--ro-bind", str(p), str(p)]
    if not prefix.startswith("/usr/"):
        argv += ["--ro-bind", prefix, prefix]
    argv += ["--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp", "--tmpfs", SANDBOX_WORK]
    if src is not None:
        argv += ["--ro-bind", src, SANDBOX_SRC]
    argv += ["--chdir", SANDBOX_WORK, "--clearenv",
             "--setenv", "PATH", "/usr/bin:/bin", "--setenv", "PYTHONDONTWRITEBYTECODE", "1",
             "--setenv", "PYTHONHASHSEED", "0", "--setenv", "LANG", "C.UTF-8", "--setenv", "HOME", SANDBOX_WORK,
             "--"]
    return argv


def _owner_tasks() -> int:
    """The owner's current task (thread) count: RLIMIT_NPROC is counted per
    user across the host, even inside the sandbox's user namespace."""
    n, uid = 0, __import__("os").getuid()
    for d in Path("/proc").iterdir():
        if d.name.isdigit():
            try:
                if d.stat().st_uid == uid:
                    n += sum(1 for _ in (d / "task").iterdir())
            except OSError:
                pass
    return n


def _limits(cpu_s: int, nproc: int | None):
    def apply():
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_s, cpu_s))
        resource.setrlimit(resource.RLIMIT_FSIZE, (16 << 20, 16 << 20))
        resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))
        if nproc is not None:
            resource.setrlimit(resource.RLIMIT_NPROC, (nproc, nproc))
    return apply


def _run_group(argv: list[str], timeout: float, preexec) -> subprocess.CompletedProcess:
    """Run in its own session; on timeout SIGKILL the whole process group
    (bwrap's PID namespace then takes every sandboxed process with it).
    When ``argv`` holds STATUS_FD_PLACEHOLDER (bwrap ``--json-status-fd``), it
    becomes a pipe, and the result's ``child_started`` says whether bwrap
    reported ``child-pid``, i.e. whether the sandboxed child ever ran."""
    import os
    import signal
    r = w = None
    if STATUS_FD_PLACEHOLDER in argv:
        r, w = os.pipe()
        argv = [str(w) if a == STATUS_FD_PLACEHOLDER else a for a in argv]
    try:
        proc = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, start_new_session=True, preexec_fn=preexec,
                                pass_fds=(w,) if w is not None else ())
    except BaseException:
        if r is not None:
            os.close(r)
            os.close(w)
        raise
    if w is not None:
        os.close(w)
    try:
        try:
            out, err = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.communicate()
            raise
        status = b""
        if r is not None:
            os.set_blocking(r, False)
            try:
                while chunk := os.read(r, 1 << 16):
                    status += chunk
            except BlockingIOError:
                pass
    finally:
        if r is not None:
            os.close(r)
    res = subprocess.CompletedProcess(argv, proc.returncode, out, err)
    res.child_started = b'"child-pid"' in status
    return res


def _eagain(res: subprocess.CompletedProcess) -> bool:
    """bwrap could not start its sandbox for lack of host resources: no child
    ever started (bwrap never reported child-pid) and bwrap itself said EAGAIN.
    Anything a started child writes is the model's test report, never this."""
    if getattr(res, "child_started", False):
        return False
    return res.returncode != 0 and any(line.startswith("bwrap:") and _EAGAIN_TEXT in line
                                       for line in (res.stderr or "").splitlines())


def _sandbox_starts(bwrap: str) -> bool:
    """Preflight: bwrap exists and can build this exact sandbox (fail closed).
    Raises SandboxResourceError when it fails for lack of host resources."""
    if not Path(bwrap).is_file():
        return False
    try:
        r = _run_group(_bwrap_argv(bwrap, None) + ["/usr/bin/true"], PREFLIGHT_TIMEOUT_S, None)
    except BlockingIOError as e:
        raise SandboxResourceError(e.errno, f"sandbox preflight: {e.strerror or e}") from e
    except (OSError, subprocess.SubprocessError):
        return False
    if _eagain(r):
        raise SandboxResourceError(11, f"sandbox preflight: {r.stderr.strip()}")
    return r.returncode == 0


def run_tests_repo(repo: dict[str, str], time_limit_s: float) -> str:
    """The repository's unittest report, run inside the bubblewrap sandbox,
    normalised. Stable interface: gen_scenarios.py imports it. Returns
    SANDBOX_UNAVAILABLE (and runs nothing) when bwrap is missing or cannot
    start; raises TimeoutError when the run exceeds ``time_limit_s``, and
    SandboxResourceError (a BlockingIOError) when the host is out of process
    slots (EAGAIN) before or while starting the sandbox."""
    bwrap = BWRAP
    if not _sandbox_starts(bwrap):
        return SANDBOX_UNAVAILABLE
    interp, _ = _interpreter()
    with tempfile.TemporaryDirectory(prefix="dedup-sim-") as d:
        for p, text in repo.items():
            f = Path(d) / p
            f.parent.mkdir(parents=True, exist_ok=True)
            with open(f, "w", encoding="utf-8", newline="") as fh:
                fh.write(text)
        inner = (f'cp -a {SANDBOX_SRC}/. {SANDBOX_WORK}/ && cd {SANDBOX_WORK} && '
                 'exec "$0" -m unittest discover -s tests -t . -v')
        argv = _bwrap_argv(bwrap, d) + ["/usr/bin/sh", "-c", inner, interp]
        try:
            res = _run_group(argv, time_limit_s,
                             _limits(max(1, int(time_limit_s) + 1), _owner_tasks() + NPROC_HEADROOM))
        except subprocess.TimeoutExpired:
            raise TimeoutError
        except BlockingIOError as e:
            raise SandboxResourceError(e.errno, f"sandbox start: {e.strerror or e}") from e
    if _eagain(res):
        raise SandboxResourceError(11, f"sandbox start: {res.stderr.strip()}")
    return normalise_test_report(res.stdout + res.stderr, SANDBOX_WORK)


def _bounded(fn, limit_s: float) -> str:
    """fn() in a forked child, killed at ``limit_s``: a regex match cannot be
    interrupted in-process (a catastrophic pattern on one long line would
    ignore any deadline). Raises TimeoutError at the bound."""
    import os
    import select
    import signal
    r, w = os.pipe()
    pid = os.fork()
    if pid == 0:  # child
        code = 0
        try:
            os.close(r)
            data = fn().encode("utf-8")
            while data:
                data = data[os.write(w, data):]
        except BaseException:  # noqa: BLE001
            code = 1
        finally:
            os._exit(code)
    os.close(w)
    chunks, deadline = [], time.monotonic() + limit_s
    try:
        while True:
            left = deadline - time.monotonic()
            if left <= 0 or not select.select([r], [], [], left)[0]:
                os.kill(pid, signal.SIGKILL)
                raise TimeoutError
            chunk = os.read(r, 1 << 16)
            if not chunk:
                break
            chunks.append(chunk)
    finally:
        os.close(r)
        _, status = os.waitpid(pid, 0)
    if os.waitstatus_to_exitcode(status) != 0:
        raise _ToolError("grep failed")
    return b"".join(chunks).decode("utf-8")


# ---------------------------------------------------------------------------
# the simulator
# ---------------------------------------------------------------------------

class ToolSimulator:
    def __init__(self, snapshot_dir: Path, time_limit_s: float = 10.0):
        self.snapshot_dir = Path(snapshot_dir)
        self.time_limit_s = time_limit_s
        if not self.snapshot_dir.is_dir():
            raise FileNotFoundError(f"snapshot {self.snapshot_dir} does not exist")
        links = sorted(p.relative_to(self.snapshot_dir).as_posix()
                       for p in self.snapshot_dir.rglob("*") if p.is_symlink())
        if links:
            raise ValueError(f"snapshot {self.snapshot_dir} contains a symlink ({links[0]}); refused")
        self._tmp = tempfile.mkdtemp(prefix="dedup-sim-work-")
        self.root = Path(self._tmp) / "repo"
        shutil.copytree(self.snapshot_dir, self.root, symlinks=False)
        self._edited: dict[str, set[int]] = {}   # path -> 1-based lines written by edit_file
        self.infra_errors: list[str] = []         # host-side failures (not model outcomes), in call order

    # -- repository view ------------------------------------------------------
    def _rel(self, path) -> str:
        if not isinstance(path, str) or not path:
            raise _ToolError("argument 'path' must be a non-empty string")
        pp = PurePosixPath(path)
        parts = [x for x in pp.parts if x not in (".",)]
        if pp.is_absolute() or ".." in parts or not parts:
            raise _ToolError(f"path outside the repository: {path}")
        if parts[0] in HIDDEN:
            raise _ToolError(f"file not found: {path}")
        return "/".join(parts)

    def _file(self, path) -> Path:
        rel = self._rel(path)
        f = self.root / rel
        if not f.is_file() or f.is_symlink():
            raise _ToolError(f"file not found: {path}")
        return f

    def _read(self, f: Path) -> str:
        try:
            return f.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            raise _ToolError(f"not a UTF-8 text file: {f.relative_to(self.root).as_posix()}")

    def repo(self) -> dict[str, str]:
        out = {}
        for f in sorted(self.root.rglob("*")):
            rel = f.relative_to(self.root)
            if rel.parts[0] in HIDDEN or not f.is_file() or f.is_symlink():
                continue
            try:
                out[rel.as_posix()] = f.read_bytes().decode("utf-8")
            except UnicodeDecodeError:
                continue
        return out

    # -- tools ----------------------------------------------------------------
    def _read_file(self, a: dict) -> str:
        return self._read(self._file(a.get("path")))

    def _grep(self, a: dict) -> str:
        pattern = a.get("pattern")
        if not isinstance(pattern, str) or not pattern:
            raise _ToolError("argument 'pattern' must be a non-empty string")
        path = a.get("path")
        if path is not None:
            path = self._rel(path)
        try:
            re.compile(pattern)
        except re.error as e:
            raise _ToolError(f"invalid pattern: {e}")
        return _bounded(lambda: grep_repo(self.repo(), pattern, path), self.time_limit_s)

    def _edit_file(self, a: dict) -> str:
        f = self._file(a.get("path"))
        line, text = a.get("line"), a.get("text")
        if not isinstance(line, int) or isinstance(line, bool):
            raise _ToolError("argument 'line' must be an integer")
        if not isinstance(text, str) or _CONTROL.search(text):
            raise _ToolError("argument 'text' must be one line of text")
        lines = self._read(f).split("\n")
        if not 1 <= line <= len(lines):
            raise _ToolError(f"line {line} out of range (1..{len(lines)})")
        lines[line - 1] = text
        with open(f, "w", encoding="utf-8", newline="") as fh:
            fh.write("\n".join(lines))
        rel = f.relative_to(self.root).as_posix()
        self._edited.setdefault(rel, set()).add(line)
        return f"edited {a['path']}: line {line} replaced\n"

    def _run_linter(self, a: dict) -> str:
        path = a.get("path")
        if path is not None and path not in (".", ""):
            path = self._rel(path)
        return lint_repo(self.repo(), path)

    def _guard_edited(self, repo: dict[str, str]) -> str | None:
        for rel in sorted(self._edited):
            if not rel.endswith(".py") or rel not in repo:
                continue
            try:
                tree = ast.parse(repo[rel])
            except SyntaxError:
                continue  # an unparsable module cannot be imported, so nothing of it runs
            lines = self._edited[rel]
            for node in ast.walk(tree):
                ln = getattr(node, "lineno", None)
                if ln not in lines:
                    continue
                what = None
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    what = "an import"
                elif isinstance(node, ast.Name) and (node.id in _FORBIDDEN_NAMES or node.id.startswith("__")):
                    what = f"the name {node.id}"
                elif isinstance(node, ast.Attribute) and node.attr.startswith("__"):
                    what = f"the attribute {node.attr}"
                if what:
                    return (f"run_tests refused: line {ln} of {rel} uses {what}, "
                            f"which the simulator does not execute\n")
        return None

    def _run_tests(self, a: dict) -> str:
        repo = self.repo()
        refused = self._guard_edited(repo)
        if refused:
            return refused
        try:
            out = run_tests_repo(repo, self.time_limit_s)
        except SandboxResourceError as e:
            self.infra_errors.append(f"run_tests: {e.strerror or e}")
            return SANDBOX_RESOURCE_EXHAUSTED
        if out == SANDBOX_UNAVAILABLE:
            self.infra_errors.append("run_tests: the bubblewrap sandbox is unavailable")
        return out

    def _fetch_url(self, a: dict) -> str:
        url = a.get("url")
        if not isinstance(url, str) or not url:
            raise _ToolError("argument 'url' must be a non-empty string")
        rest = url.split("://", 1)[1] if "://" in url else ""
        parts = PurePosixPath(rest).parts
        page = self.root / WEB_DIR / rest if rest and ".." not in parts and not rest.startswith("/") else None
        if page is None or not page.is_file() or page.is_symlink():
            raise _ToolError(f"fetch failed: no page at {url}")
        return self._read(page)

    # -- entry ----------------------------------------------------------------
    def call(self, name: str, arguments) -> str:
        if name not in TOOLS:
            return UNKNOWN_TOOL_ERROR
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments) if arguments.strip() else {}
            except json.JSONDecodeError:
                return _err("arguments are not valid JSON")
        if arguments is None:
            arguments = {}
        if not isinstance(arguments, dict):
            return _err("arguments must be a JSON object")
        try:
            return getattr(self, "_" + name)(arguments)
        except _ToolError as e:
            return _err(str(e))
        except TimeoutError:
            return _err(f"{name} exceeded the {self.time_limit_s:g}s time limit")

    def close(self) -> None:
        if getattr(self, "_tmp", None):
            shutil.rmtree(self._tmp, ignore_errors=True)
            self._tmp = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def __del__(self):
        self.close()
