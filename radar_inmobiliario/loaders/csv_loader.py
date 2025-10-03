"""CSV loader for standardized listings."""

from __future__ import annotations

import csv
from typing import Any, Dict, Sequence

from ..core.base import BaseLoader
from ..core.models import Listing
from ..core.schema import HEADERS, project_listing_to_row


def _none_to_empty(value: Any) -> Any:
    return "" if value is None else value


class CsvLoader(BaseLoader):
    """Persist standardized listings to a CSV file."""

    def load(self, items: Sequence[Listing], output_stem: str) -> str:
        path = f"{output_stem}_standardized.csv"
        fieldnames = list(HEADERS)
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for idx, item in enumerate(items, 1):
                row: Dict[str, Any] = {k: _none_to_empty(v) for k, v in project_listing_to_row(item).items()}
                if "#" in fieldnames:
                    row["#"] = idx
                writer.writerow(row)
        return path


