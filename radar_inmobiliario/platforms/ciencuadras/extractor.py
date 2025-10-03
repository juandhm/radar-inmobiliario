"""Ciencuadras extractor implementation.

Reads the platform raw JSON and extracts the list of property dictionaries.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...core.base import BaseExtractor
from ...core.io import read_json


class CiencuadrasExtractor(BaseExtractor):
    """Extractor for Ciencuadras raw JSON files."""

    def extract(self, input_path: str) -> List[Dict[str, Any]]:
        data = read_json(input_path)
        container = data.get("data", {}) if isinstance(data, dict) else {}

        listings: List[Dict[str, Any]] = []
        for key in ("highlights", "results"):
            maybe_list = container.get(key, [])
            if isinstance(maybe_list, list):
                listings.extend([x for x in maybe_list if isinstance(x, dict)])

        return listings


