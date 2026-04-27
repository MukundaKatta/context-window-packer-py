# context-window-packer-py

[![PyPI](https://img.shields.io/pypi/v/context-window-packer-py.svg)](https://pypi.org/project/context-window-packer-py/)
[![Python](https://img.shields.io/pypi/pyversions/context-window-packer-py.svg)](https://pypi.org/project/context-window-packer-py/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Pack context chunks into a budget by relevance and priority.** Sort by `score` (descending), break ties by `priority`, accept each chunk if it fits, otherwise drop. Zero runtime dependencies.

Python port of [@mukundakatta/context-window-packer](https://www.npmjs.com/package/@mukundakatta/context-window-packer).

## Install

```bash
pip install context-window-packer-py
```

## Quick start

```python
from context_window_packer import pack

chunks = [
    {"text": "Pluto was reclassified...", "priority": 1, "relevance": 0.9},
    {"text": "Mars is the fourth planet...", "priority": 0, "relevance": 0.4},
    {"text": "Cats are independent...", "priority": 0, "relevance": 0.1},
]

result = pack(chunks, budget_tokens=20)

result.chunks   # list of dicts that fit
result.tokens   # int -- tokens consumed by kept chunks
result.dropped  # int -- count of chunks not kept
```

## API

### `pack(chunks, budget_tokens, model=None) -> PackResult`

Each chunk is a mapping with at minimum `text`. Optional fields:

| Field | Default | Meaning |
|---|---|---|
| `text` | `""` | The chunk content. |
| `tokens` | `ceil(len(text)/4)` | Pre-counted tokens (skips estimator). |
| `relevance` / `score` | `0` | Higher = more relevant; primary sort key (descending). |
| `priority` | `0` | Tie-breaker for relevance (descending). |

`PackResult` is a dataclass with:

* `chunks: list[dict]` -- chunks that fit, in pack order.
* `tokens: int` -- total tokens consumed.
* `dropped: int` -- count of chunks dropped.

`model` is reserved for future per-family token estimators (currently uses the standard `ceil(chars/4)` heuristic, matching the JS sibling).

## License

MIT
