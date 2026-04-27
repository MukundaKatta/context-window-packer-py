"""Pack chunks into a token budget by relevance and priority.

Mirrors the JS sibling's behavior:

1. Sort chunks by ``score`` (descending), with ``priority`` as the tiebreaker
   (descending).
2. Walk in that order; accept each chunk if it fits, else drop it.
3. Return the kept chunks in pack order plus token usage.

The Python API uses ``relevance`` as a more readable alias for ``score`` --
both are accepted; ``score`` wins if both are present, matching JS.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, List, Mapping, Optional


@dataclass
class PackResult:
    """Result of :func:`pack`.

    Attributes:
        chunks: Chunks that fit, in pack order.
        tokens: Total tokens consumed.
        dropped: Count of chunks that did not fit.
    """

    chunks: List[dict]
    tokens: int
    dropped: int


def estimate_tokens(text) -> int:
    """``ceil(len(text) / 4)`` -- matches the JS sibling's heuristic."""
    s = "" if text is None else str(text)
    if not s:
        return 0
    return math.ceil(len(s) / 4)


def _score_of(chunk: Mapping) -> float:
    if "score" in chunk and chunk["score"] is not None:
        return float(chunk["score"])
    if "relevance" in chunk and chunk["relevance"] is not None:
        return float(chunk["relevance"])
    return 0.0


def _priority_of(chunk: Mapping) -> float:
    p = chunk.get("priority") if isinstance(chunk, Mapping) else None
    return float(p) if p is not None else 0.0


def _tokens_of(chunk: Mapping) -> int:
    if not isinstance(chunk, Mapping):
        return 0
    t = chunk.get("tokens")
    if t is not None:
        return int(t)
    return estimate_tokens(chunk.get("text", ""))


def pack(
    chunks: Iterable[Mapping],
    budget_tokens: int,
    model: Optional[str] = None,
) -> PackResult:
    """Greedy packer.

    Sort by relevance (desc), then priority (desc). Accept each chunk if
    it fits the remaining budget, else drop it. ``model`` is reserved for
    future per-family token estimators.
    """
    if isinstance(budget_tokens, bool) or not isinstance(budget_tokens, (int, float)) or budget_tokens < 0:
        raise TypeError("pack: budget_tokens must be a non-negative number")
    items: List[dict] = []
    for chunk in chunks or []:
        if isinstance(chunk, Mapping):
            items.append(dict(chunk))
    # Stable sort: relevance desc, then priority desc.
    items.sort(key=lambda c: (-_score_of(c), -_priority_of(c)))

    used = 0
    kept: List[dict] = []
    total = len(items)
    for chunk in items:
        tokens = _tokens_of(chunk)
        if used + tokens <= budget_tokens:
            kept.append(chunk)
            used += tokens
    return PackResult(chunks=kept, tokens=used, dropped=total - len(kept))


def pack_context(
    chunks: Iterable[Mapping],
    *,
    max_tokens: int,
) -> PackResult:
    """JS-parity alias: ``packContext(chunks, {maxTokens})``."""
    return pack(chunks, budget_tokens=max_tokens)
