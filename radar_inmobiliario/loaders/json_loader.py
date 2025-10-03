"""JSON loader for standardized listings."""

from __future__ import annotations

from typing import Sequence

from ..core.base import BaseLoader
from ..core.io import write_json
from ..core.models import Listing
from ..core.schema import project_listing_to_row


class JsonLoader(BaseLoader):
    """Persist standardized listings to a JSON file."""

    def load(self, items: Sequence[Listing], output_stem: str) -> str:
        payload = [project_listing_to_row(i) for i in items]
        path = f"{output_stem}_processed.json"
        return write_json(path, payload)


