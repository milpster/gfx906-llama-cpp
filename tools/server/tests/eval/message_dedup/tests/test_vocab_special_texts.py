#!/usr/bin/env python
"""SPEC-0001 increment 14 (tool-smith): the special-text list for fire_check.

Pins vocab_special_texts, the dependency-free source of the §4.0
special-text match set that static_checks.fire_check needs on a real vocab
(the increment-14 open item). Spec §4.0: the set is every vocab token with the
CONTROL, USER_DEFINED or UNKNOWN attribute, by its raw text; the server builds
it in tools/server/server-message-dedup.cpp dedup_special_text_predicate_from_vocab.
Pure Python, vocab-only GGUF files in models/ (no server, no GPU).
"""
import struct

import pytest

from _paths import SERVER_TESTS_DIR

import vocab_special_texts as vst  # noqa: E402

MODELS = SERVER_TESTS_DIR.parents[2] / "models"


def test_spec0001_suite_special_texts_qwen35_holds_control_and_pad_tokens():
    """Spec §4.0 and the SPEC-0001 DEDUP_STUB_NO_CONTROL_TOKENS row: in
    ggml-vocab-qwen35.gguf, `<|im_end|>` and `[PAD151646]` are special texts;
    ordinary words are not."""
    texts = vst.vocab_special_texts(MODELS / "ggml-vocab-qwen35.gguf")
    assert "<|im_end|>" in texts and "<|im_start|>" in texts
    assert "[PAD151646]" in texts
    assert "the" not in texts and "hello" not in texts
    assert "" not in texts


def test_spec0001_suite_special_texts_spm_holds_unknown_token():
    """Spec §4.0: UNKNOWN is part of the set (`<unk>` in ggml-vocab-llama-spm.gguf)."""
    texts = vst.vocab_special_texts(MODELS / "ggml-vocab-llama-spm.gguf")
    assert "<unk>" in texts and "<s>" in texts and "</s>" in texts


def _gguf(path, kvs):
    """Write a tiny GGUF v3 header holding only string-array / int32-array KVs."""
    out = bytearray(b"GGUF") + struct.pack("<IQQ", 3, 0, len(kvs))
    for key, (etype, values) in kvs.items():
        k = key.encode()
        out += struct.pack("<Q", len(k)) + k + struct.pack("<I", 9) + struct.pack("<IQ", etype, len(values))
        for v in values:
            if etype == 8:
                b = v.encode()
                out += struct.pack("<Q", len(b)) + b
            else:
                out += struct.pack("<i", v)
    path.write_bytes(bytes(out))


def test_spec0001_suite_special_texts_type_membership_exact(tmp_path):
    """Exact membership over llama.cpp token types (src/llama-vocab.cpp token
    type -> attribute): 2 UNKNOWN, 3 CONTROL, 4 USER_DEFINED are in; 1 NORMAL,
    5 UNUSED, 6 BYTE, 0 UNDEFINED are out; empty texts are skipped."""
    p = tmp_path / "v.gguf"
    toks = ["n", "unk", "ctl", "usr", "unused", "byte", "undef", ""]
    types = [1, 2, 3, 4, 5, 6, 0, 3]
    _gguf(p, {"tokenizer.ggml.tokens": (8, toks), "tokenizer.ggml.token_type": (5, types)})
    assert vst.vocab_special_texts(p) == ["ctl", "unk", "usr"]


def test_spec0001_suite_special_texts_missing_token_type_fails_loudly(tmp_path):
    """method.contract-posture §1: a vocab without token types is an error,
    never an empty list (an empty list would silently disable the §6.4 cut)."""
    p = tmp_path / "v.gguf"
    _gguf(p, {"tokenizer.ggml.tokens": (8, ["a"])})
    with pytest.raises(vst.VocabError, match="tokenizer.ggml.token_type"):
        vst.vocab_special_texts(p)


def test_spec0001_suite_special_texts_not_gguf_fails_loudly(tmp_path):
    p = tmp_path / "v.gguf"
    p.write_bytes(b"NOPE" + b"\0" * 32)
    with pytest.raises(vst.VocabError, match="not a GGUF"):
        vst.vocab_special_texts(p)
