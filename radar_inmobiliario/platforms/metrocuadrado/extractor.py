"""Metrocuadrado extractor implementation.

Extracts properties from data.result.propertiesByFiltersQuery.properties
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...core.base import BaseExtractor
from ...core.io import read_json


class MetrocuadradoExtractor(BaseExtractor):
    """Extractor for Metrocuadrado raw JSON files."""

    def extract(self, input_path: str) -> List[Dict[str, Any]]:
        data = read_json(input_path)
        props: List[Dict[str, Any]] = []
        try:
            container = (
                data.get("data", {})
                .get("result", {})
                .get("propertiesByFiltersQuery", {})
            )
            candidates = container.get("properties", [])
            if isinstance(candidates, list):
                props = [p for p in candidates if isinstance(p, dict)]
        except Exception:
            props = []
        return props


