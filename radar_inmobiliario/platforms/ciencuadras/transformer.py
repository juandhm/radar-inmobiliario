"""Ciencuadras transformer implementation.

Maps raw Ciencuadras dictionaries into the standardized Listing model.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Sequence

from ...core.base import BaseTransformer
from ...core.models import Listing


def _to_optional_float(value: Any) -> Optional[float]:
    """Best-effort conversion to float."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_optional_int(value: Any) -> Optional[int]:
    """Best-effort conversion to int."""
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _normalize_text(value: Any) -> str:
    """Lowercased ascii-like text (basic accent stripping)."""
    if not isinstance(value, str):
        return ""
    text = value.lower()
    replacements = (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"))
    for a, b in replacements:
        text = text.replace(a, b)
    return text


class CiencuadrasTransformer(BaseTransformer):
    """Transformer for Ciencuadras raw items."""

    def __init__(self, platform_name: str = "ciencuadras") -> None:
        self.platform_name = platform_name

    def transform(self, raw_items: List[Dict[str, Any]]) -> Sequence[Listing]:
        standardized: List[Listing] = []
        for item in raw_items:
            if not isinstance(item, dict):
                continue

            coordinates = item.get("coordinates", {}) if isinstance(item.get("coordinates", {}), dict) else {}

            # Basic fields
            listing_id = str(item.get("id", ""))
            url = f"https://www.ciencuadras.com{item.get('url', '')}"
            region = item.get("department") or None
            city = item.get("city") or None
            neighborhood = item.get("neighborhood") or None
            address = item.get("address") or None
            latitude = _to_optional_float(coordinates.get("latitude"))
            longitude = _to_optional_float(coordinates.get("longitude"))
            property_type = item.get("realEstateType") or None
            total_area_m2 = _to_optional_float(item.get("area"))
            bedrooms = _to_optional_int(item.get("rooms"))
            bathrooms = _to_optional_float(item.get("baths"))
            parking_spaces = _to_optional_int(item.get("garages"))
            stratum = _to_optional_int(item.get("stratum"))

            # Economic information
            sale_price = _to_optional_float(item.get("salePrice"))
            admin_price = _to_optional_float(item.get("adminValue"))
            deal_type = "sale" if sale_price is not None else None

            # Dates
            created = item.get("createdAt") or None

            # Contact
            contact_name = item.get("userName") or None

            # Remodel detection
            comments = item.get("comments") or ""
            normalized = _normalize_text(comments)
            remodeled = any(
                p in normalized
                for p in (
                    "remodelado",
                    "remodelada",
                    "remodelacion",
                    "renovado",
                    "renovada",
                    "reformado",
                    "reformada",
                    "actualizado",
                    "actualizada",
                    "modernizado",
                    "modernizada",
                    "cocina remodelada",
                    "banos remodelados",
                    "bano remodelado",
                    "baño remodelado",
                )
            )

            listing = Listing(
                listing_id=listing_id,
                platform=self.platform_name,
                url=url,
                country=None,
                region=region,
                city=city,
                neighborhood=neighborhood,
                address=address,
                latitude=latitude,
                longitude=longitude,
                property_type=property_type,
                total_area_m2=total_area_m2,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                parking_spaces=parking_spaces,
                stratum=stratum,
                condition=None,
                build_age=None,
                remodeled=bool(remodeled),
                sale_price=sale_price,
                rent_price=None,
                admin_price=admin_price,
                deal_type=deal_type,
                publish_date=created,
                update_date=created,
                ingestion_date=created,
                contact_name=contact_name,
            )

            standardized.append(listing)

        return standardized


