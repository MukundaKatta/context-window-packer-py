"""context_window_packer -- pack chunks into a token budget by relevance and priority.

Public surface (mirrors the JS sibling, with Pythonic naming):

* ``pack(chunks, budget_tokens, model=None)`` -- greedy packer; returns a
  :class:`PackResult`.
* ``pack_context(chunks, *, max_tokens=...)`` -- alias matching the JS
  ``packContext({maxTokens})`` signature for callers porting from JS.
* ``estimate_tokens(text)`` -- ``ceil(len(text) / 4)`` heuristic.
* ``PackResult`` -- dataclass returned by :func:`pack`.
"""

from .pack import PackResult, estimate_tokens, pack, pack_context

__version__ = "0.1.0"
VERSION = __version__

__all__ = [
    "VERSION",
    "PackResult",
    "estimate_tokens",
    "pack",
    "pack_context",
]
