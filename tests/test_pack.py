"""Tests for ``context_window_packer.pack``."""

import pytest

from context_window_packer import PackResult, estimate_tokens, pack, pack_context


def test_pack_returns_PackResult():
    result = pack([], budget_tokens=100)
    assert isinstance(result, PackResult)
    assert result.chunks == []
    assert result.tokens == 0
    assert result.dropped == 0


def test_pack_keeps_under_budget():
    chunks = [
        {"text": "a" * 40, "relevance": 1.0},  # 10 tokens
        {"text": "b" * 40, "relevance": 0.5},  # 10 tokens
    ]
    result = pack(chunks, budget_tokens=20)
    assert len(result.chunks) == 2
    assert result.tokens == 20
    assert result.dropped == 0


def test_pack_drops_overflow():
    chunks = [
        {"text": "x" * 40, "relevance": 1.0, "tokens": 10},
        {"text": "y" * 40, "relevance": 0.5, "tokens": 10},
        {"text": "z" * 40, "relevance": 0.1, "tokens": 10},
    ]
    result = pack(chunks, budget_tokens=15)
    assert result.tokens == 10
    assert result.dropped == 2


def test_pack_orders_by_relevance_desc():
    chunks = [
        {"text": "low", "relevance": 0.1, "tokens": 1},
        {"text": "high", "relevance": 0.9, "tokens": 1},
        {"text": "mid", "relevance": 0.5, "tokens": 1},
    ]
    result = pack(chunks, budget_tokens=100)
    assert [c["text"] for c in result.chunks] == ["high", "mid", "low"]


def test_pack_priority_breaks_score_ties():
    chunks = [
        {"text": "low-p", "relevance": 1.0, "priority": 0, "tokens": 1},
        {"text": "high-p", "relevance": 1.0, "priority": 5, "tokens": 1},
    ]
    result = pack(chunks, budget_tokens=100)
    assert result.chunks[0]["text"] == "high-p"


def test_pack_uses_estimate_when_tokens_missing():
    chunks = [{"text": "x" * 200, "relevance": 1.0}]  # 50 tokens
    result = pack(chunks, budget_tokens=100)
    assert result.tokens == 50


def test_pack_score_alias_takes_precedence_over_relevance():
    chunks = [
        {"text": "via-relevance", "relevance": 0.1, "tokens": 1},
        {"text": "via-score", "score": 0.9, "tokens": 1},
    ]
    result = pack(chunks, budget_tokens=100)
    assert result.chunks[0]["text"] == "via-score"


def test_pack_negative_budget_raises():
    with pytest.raises(TypeError):
        pack([], budget_tokens=-1)


def test_pack_context_alias_works():
    chunks = [{"text": "hello", "tokens": 1}]
    result = pack_context(chunks, max_tokens=10)
    assert result.chunks == chunks
    assert result.tokens == 1


def test_estimate_tokens_basic():
    assert estimate_tokens("") == 0
    assert estimate_tokens(None) == 0
    assert estimate_tokens("abcd") == 1
    assert estimate_tokens("abcdefgh") == 2
