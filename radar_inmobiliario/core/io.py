"""Basic IO helpers for reading and writing files.

These functions are intentionally small wrappers around standard library IO to
centralize encoding and error handling conventions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_json(path: str) -> Any:
    """Read a JSON file and return its contents."""
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str, data: Any) -> str:
    """Write data to a JSON file and return the path as string."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return str(p)


def write_text(path: str, content: str) -> str:
    """Write plain text content to a file and return the path as string."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return str(p)


