"""Finca Raíz extractor implementation.

Supports the common Elasticsearch-like structure: data["hits"]["hits"][]._source.listing
falling back to _source when listing is not present.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...core.base import BaseExtractor
from ...core.io import read_json


class FincaRaizExtractor(BaseExtractor):
    """Extractor for Finca Raíz raw JSON files."""

    def extract(self, input_path: str) -> List[Dict[str, Any]]:
        data = read_json(input_path)
        listings: List[Dict[str, Any]] = []

        if not isinstance(data, dict):
            return listings

        hits = data.get("hits")
        if isinstance(hits, dict):
            hits_list = hits.get("hits", [])
            for hit in hits_list:
                if not isinstance(hit, dict):
                    continue
                source = hit.get("_source")
                if isinstance(source, dict):
                    listing = source.get("listing", source)
                    if isinstance(listing, dict):
                        listings.append(listing)

        return listings


