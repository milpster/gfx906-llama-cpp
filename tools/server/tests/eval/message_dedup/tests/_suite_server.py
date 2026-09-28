"""The render server for the SPEC-0001 real-set suite tests (increments 17, 16).

The real scenarios are judged under the production profile's model and chat
template (spec §9.4; the profile's fields have one home,
docs/graph/product/production-profile.md). Two modes:

- ``DEDUP_SUITE_URL`` set: use that ALREADY RUNNING server (the gate path:
  the production-profile server in GPU mode, started by whoever holds the GPU
  lock, `PORT` not 8080).
- unset: start ``$LLAMA_SERVER_BIN_PATH`` here, render-only: the model from
  ``LLAMA_DEDUP_SUITE_GGUF`` (REQUIRED, no default: the path is an owner
  configuration fact whose one home is docs/graph/product/production-profile.md,
  field `model`; unset -> the test fails loudly), the chat
  template from ``DEDUP_SUITE_TEMPLATE`` (default
  models/templates/Qwen3.5-4B.jinja, the in-repo stand-in the increment-14
  tests use as "the profile's chat template"; the profile's own
  qwen36_chat_template.jinja is not in this repo), ``--no-warmup``, mmap,
  ``-ngl $N_GPU_LAYERS`` or ``-ngl 0`` when unset (the CPU-only render path
  of the increment-17 row: nothing here decodes). ``PORT`` from the env.

Only /apply-template, /tokenize and the count-token routes are used; no
completion is ever requested through this helper.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
import time
from pathlib import Path

import requests

from _paths import SERVER_TESTS_DIR
from suite_http import SuiteHttp

REPO_ROOT = SERVER_TESTS_DIR.parents[2]
# The served GGUF is the production profile's `model` field; its one home is
# docs/graph/product/production-profile.md. It is an owner-machine path, so it
# is read from the environment and never hard-coded here.
MODEL_ENV = "LLAMA_DEDUP_SUITE_GGUF"
DEFAULT_TEMPLATE = REPO_ROOT / "models" / "templates" / "Qwen3.5-4B.jinja"


def suite_model_path() -> str:
    """The served GGUF from $LLAMA_DEDUP_SUITE_GGUF (set it to the production
    profile's `model`, docs/graph/product/production-profile.md). With
    DEDUP_SUITE_URL the external server must serve this same file (its
    special-text list feeds fire_check). Unset or missing file -> RuntimeError,
    so a real-set run can never pass without the profile's model."""
    path = os.environ.get(MODEL_ENV, "")
    if not path:
        raise RuntimeError(f"{MODEL_ENV} is not set: point it at the production profile's model "
                           "(docs/graph/product/production-profile.md, field `model`)")
    if not Path(path).is_file():
        raise RuntimeError(f"{MODEL_ENV}={path!r} is not a file")
    return path


class RenderServer:
    def __init__(self):
        self.proc: subprocess.Popen | None = None
        self.log_path: Path | None = None
        url = os.environ.get("DEDUP_SUITE_URL")
        if url:
            self.client = SuiteHttp(url)
            return
        port = os.environ.get("PORT", "18080")
        binary = os.environ.get("LLAMA_SERVER_BIN_PATH", str(REPO_ROOT / "build" / "bin" / "llama-server"))
        args = [binary, "--host", "127.0.0.1", "--port", port,
                "-m", suite_model_path(),
                "--jinja", "--chat-template-file", os.environ.get("DEDUP_SUITE_TEMPLATE", str(DEFAULT_TEMPLATE)),
                "-c", "8192", "--parallel", "1", "--no-warmup",
                "-ngl", os.environ.get("N_GPU_LAYERS", "0")]
        fd, log = tempfile.mkstemp(prefix="dedup-suite-render-", suffix=".log")
        os.close(fd)
        self.log_path = Path(log)
        self._log = open(self.log_path, "w")
        self.proc = subprocess.Popen(args, stdout=self._log, stderr=subprocess.STDOUT)
        self.client = SuiteHttp(f"http://127.0.0.1:{port}")
        deadline = time.time() + float(os.environ.get("DEDUP_SUITE_START_TIMEOUT", "900"))
        while time.time() < deadline:
            if self.proc.poll() is not None:
                raise RuntimeError(f"render server exited {self.proc.returncode}; log {self.log_path}")
            try:
                if requests.get(f"http://127.0.0.1:{port}/health", timeout=2).status_code == 200:
                    return
            except requests.RequestException:
                pass
            time.sleep(0.5)
        self.stop()
        raise TimeoutError(f"render server not healthy; log {self.log_path}")

    def stop(self) -> None:
        if self.proc is not None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                self.proc.kill()
            self.proc = None
            self._log.close()
