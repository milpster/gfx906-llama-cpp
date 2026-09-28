"""SPEC-0001 §9.4 scenario suite: the served vocab's special-text list.

Tool card: docs/graph/tools/message-dedup-scenario-suite.md.
Tests: tests/test_vocab_special_texts.py.

static_checks.fire_check builds the expected §6.4 stub with the test-side
builder ``dedup_goldens.ref_stub``, whose steps 2 and 6 need the §4.0
special-text match set: the raw text of every vocab token with the CONTROL,
USER_DEFINED or UNKNOWN attribute (the server's own copy is
tools/server/server-message-dedup.cpp dedup_special_text_predicate_from_vocab).

This module reads that set straight from a GGUF file with the standard library
only: the ``tokenizer.ggml.tokens`` and ``tokenizer.ggml.token_type`` arrays of
the KV header. gguf-py is not used because it needs pyyaml, which the test
venv does not have (no new dependency; protocol.ingest-library). Reading the
file, and not asking the server, keeps the oracle independent of the code it
judges.

Token type -> attribute follows src/llama-vocab.cpp (the token_type switch):
2 UNKNOWN, 3 CONTROL, 4 USER_DEFINED are in the set. Not mirrored: the
load-time attribute fix-ups llama-vocab.cpp applies for particular vocabs
(gpt-oss channel tokens set USER_DEFINED; gemma4's ``</s>`` set NORMAL when
``<|tool_response>`` is an EOG token). None of them applies to the qwen35
production vocab. For a vocab they do apply to, compare with the server
before trusting the list.

Usage::

    python3 vocab_special_texts.py <model.gguf>     # one special text per line (JSON strings)
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path
from typing import BinaryIO

SPECIAL_TOKEN_TYPES = frozenset([2, 3, 4])   # UNKNOWN, CONTROL, USER_DEFINED

_SCALAR = {0: "<B", 1: "<b", 2: "<H", 3: "<h", 4: "<I", 5: "<i", 6: "<f", 7: "<?", 10: "<Q", 11: "<q", 12: "<d"}
_STRING, _ARRAY = 8, 9
_WANTED = ("tokenizer.ggml.tokens", "tokenizer.ggml.token_type")


class VocabError(ValueError):
    pass


def _read(f: BinaryIO, n: int) -> bytes:
    b = f.read(n)
    if len(b) != n:
        raise VocabError(f"{f.name}: truncated GGUF header")
    return b


def _u32(f: BinaryIO) -> int:
    return struct.unpack("<I", _read(f, 4))[0]


def _u64(f: BinaryIO) -> int:
    return struct.unpack("<Q", _read(f, 8))[0]


def _string(f: BinaryIO) -> bytes:
    return _read(f, _u64(f))


def _value(f: BinaryIO, vtype: int, keep: bool):
    if vtype in _SCALAR:
        fmt = _SCALAR[vtype]
        v = struct.unpack(fmt, _read(f, struct.calcsize(fmt)))[0]
        return v if keep else None
    if vtype == _STRING:
        s = _string(f)
        return s if keep else None
    if vtype == _ARRAY:
        etype, count = _u32(f), _u64(f)
        if etype in _SCALAR and not keep:
            f.seek(struct.calcsize(_SCALAR[etype]) * count, 1)
            return None
        values = [_value(f, etype, keep) for _ in range(count)]
        return values if keep else None
    raise VocabError(f"{f.name}: unknown GGUF value type {vtype}")


def _read_kv(path: Path) -> dict[str, object]:
    found: dict[str, object] = {}
    with open(path, "rb") as f:
        if f.read(4) != b"GGUF":
            raise VocabError(f"{path}: not a GGUF file (bad magic)")
        version = _u32(f)
        if version not in (2, 3):
            raise VocabError(f"{path}: GGUF version {version} not supported (little-endian v2/v3 only)")
        _u64(f)                       # tensor count
        n_kv = _u64(f)
        for _ in range(n_kv):
            key = _string(f).decode("utf-8")
            vtype = _u32(f)
            keep = key in _WANTED
            v = _value(f, vtype, keep)
            if keep:
                found[key] = v
            if len(found) == len(_WANTED):
                break
    return found


def vocab_special_texts(gguf_path: str | Path) -> list[str]:
    """The §4.0 special-text list of a GGUF vocab, sorted, without empty texts.

    Raises VocabError when the file is not a GGUF, is truncated, or lacks
    the token or token-type arrays (never an empty list in their place)."""
    path = Path(gguf_path)
    kv = _read_kv(path)
    for key in _WANTED:
        if key not in kv:
            raise VocabError(f"{path}: no {key} array in the GGUF header")
    tokens, types = kv["tokenizer.ggml.tokens"], kv["tokenizer.ggml.token_type"]
    if len(tokens) != len(types):
        raise VocabError(f"{path}: {len(tokens)} tokens but {len(types)} token types")
    texts = {t.decode("utf-8", errors="surrogateescape") for t, ty in zip(tokens, types) if ty in SPECIAL_TOKEN_TYPES and t}
    return sorted(texts)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: vocab_special_texts.py <model.gguf>", file=sys.stderr)
        return 2
    for t in vocab_special_texts(argv[1]):
        print(json.dumps(t, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
