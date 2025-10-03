"""Finca Raíz transformer implementation.

Maps raw Finca Raíz dictionaries into the standardized Listing model.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from ...core.base import BaseTransformer
from ...core.models import Listing


def _to_optional_float(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_optional_int(value: Any) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _normalize_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    text = value.lower()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u")):
        text = text.replace(a, b)
    return text


class FincaRaizTransformer(BaseTransformer):
    def __init__(self, platform_name: str = "fincaraiz") -> None:
        self.platform_name = platform_name

    def transform(self, raw_items: List[Dict[str, Any]]) -> Sequence[Listing]:
        standardized: List[Listing] = []
        for item in raw_items:
            if not isinstance(item, dict):
                continue

            # Identification and URL
            listing_id = str(item.get("id", ""))
            url = f"https://www.fincaraiz.com.co{item.get('link', '')}"

            # Location
            locations = item.get("locations", {}) if isinstance(item.get("locations", {}), dict) else {}
            country = None
            region = None
            city = None
            neighborhood = None
            if isinstance(locations.get("country"), list) and locations["country"]:
                country = locations["country"][0].get("name") or None
            if isinstance(locations.get("state"), list) and locations["state"]:
                region = locations["state"][0].get("name") or None
            if isinstance(locations.get("city"), list) and locations["city"]:
                city = locations["city"][0].get("name") or None
            if isinstance(locations.get("neighbourhood"), list) and locations["neighbourhood"]:
                neighborhood = (locations["neighbourhood"][0].get("name") or "").lower()
                for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u")):
                    neighborhood = neighborhood.replace(a, b)
                neighborhood = neighborhood or None

            # Coordinates
            latitude = _to_optional_float(item.get("latitude"))
            longitude = _to_optional_float(item.get("longitude"))

            # Property details
            property_type_data = item.get("property_type", {})
            property_type = property_type_data.get("name") if isinstance(property_type_data, dict) else None
            total_area_m2 = _to_optional_float(item.get("m2"))
            bedrooms = _to_optional_int(item.get("bedrooms"))
            bathrooms = _to_optional_float(item.get("bathrooms"))
            parking_spaces = _to_optional_int(item.get("garage"))
            stratum = _to_optional_int(item.get("stratum"))

            # Condition and age
            antiquity = item.get("antiquity")
            condition = None
            if isinstance(antiquity, (int, float)):
                if antiquity > 3:
                    condition = "Used"
                elif antiquity > 0:
                    condition = "Semi-New"
                else:
                    condition = "New"
            build_age = str(antiquity) if antiquity is not None else None

            # Pricing
            sale_price = None
            admin_price = None
            deal_type = None
            price_data = item.get("price", {})
            if isinstance(price_data, dict):
                sale_price = _to_optional_float(price_data.get("amount"))
                admin_included = _to_optional_float(price_data.get("admin_included"))
                if sale_price is not None and admin_included is not None and admin_included >= sale_price:
                    admin_price = admin_included - sale_price
                deal_type = "sale" if sale_price is not None else None

            # Dates
            publish_date = item.get("created_at") or None
            update_date = item.get("updated_at") or None
            ingestion_date = publish_date

            # Address and contact
            address = item.get("address") or None
            owner = item.get("owner") if isinstance(item.get("owner"), dict) else None
            contact_name = owner.get("name") if isinstance(owner, dict) else None

            # Remodel detection
            title = _normalize_text(item.get("title"))
            description = _normalize_text(item.get("description"))
            remodeled = any(
                p in f"{title} {description}"
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
                country=country,
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
                condition=condition,
                build_age=build_age,
                remodeled=bool(remodeled),
                sale_price=sale_price,
                rent_price=None,
                admin_price=admin_price,
                deal_type=deal_type,
                publish_date=publish_date,
                update_date=update_date,
                ingestion_date=ingestion_date,
                contact_name=contact_name,
            )

            standardized.append(listing)

        return standardized


