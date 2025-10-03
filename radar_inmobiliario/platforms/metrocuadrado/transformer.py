"""Metrocuadrado transformer implementation.

Maps raw Metrocuadrado dictionaries into the standardized Listing model.
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


class MetrocuadradoTransformer(BaseTransformer):
    def __init__(self, platform_name: str = "metrocuadrado") -> None:
        self.platform_name = platform_name

    def transform(self, raw_items: List[Dict[str, Any]]) -> Sequence[Listing]:
        standardized: List[Listing] = []
        for item in raw_items:
            if not isinstance(item, dict):
                continue

            listing_id = str(item.get("id", ""))
            url = f"https://www.metrocuadrado.com.co{item.get('url', '')}"

            # Location
            country = item.get("country") if isinstance(item.get("country"), dict) else None
            region = item.get("region") if isinstance(item.get("region"), dict) else None
            city = item.get("city") if isinstance(item.get("city"), dict) else None
            neighborhood = item.get("neighborhood") if isinstance(item.get("neighborhood"), dict) else None
            address = item.get("address") or None

            country_name = country.get("name") if isinstance(country, dict) else None
            region_name = region.get("name") if isinstance(region, dict) else None
            city_name = city.get("name") if isinstance(city, dict) else None
            neighborhood_name = neighborhood.get("name") if isinstance(neighborhood, dict) else None

            # Coordinates
            location = item.get("location") if isinstance(item.get("location"), dict) else None
            latitude = _to_optional_float(location.get("lat")) if isinstance(location, dict) else None
            longitude = _to_optional_float(location.get("lon")) if isinstance(location, dict) else None

            # Property details
            property_type = item.get("propertyType") if isinstance(item.get("propertyType"), dict) else None
            property_type_name = property_type.get("name") if isinstance(property_type, dict) else None

            total_area_m2 = _to_optional_float(item.get("area"))
            bedrooms = _to_optional_int(item.get("roomsNumber"))
            bathrooms = _to_optional_float(item.get("bathroomsNumber"))
            parking_spaces = _to_optional_int(item.get("parkingNumber"))
            stratum = _to_optional_int(item.get("stratum"))
            condition = item.get("status") or None

            built_time = item.get("builtTime") if isinstance(item.get("builtTime"), dict) else None
            build_age = built_time.get("name") if isinstance(built_time, dict) else None

            # Pricing
            sale_price = _to_optional_float(item.get("salePrice"))
            admin_price = _to_optional_float(item.get("adminPrice"))
            deal_type = "sale" if sale_price is not None else None

            # Dates
            publish_date = item.get("publishedDate") or None
            update_date = item.get("updatedDate") or None
            ingestion_date = item.get("checkInDate") or None

            # Contact
            advertiser = item.get("advertiser") if isinstance(item.get("advertiser"), dict) else None
            seller = item.get("seller") if isinstance(item.get("seller"), dict) else None
            contact_name = None
            if isinstance(advertiser, dict) and advertiser.get("name"):
                contact_name = advertiser.get("name")
            elif isinstance(seller, dict) and seller.get("name"):
                contact_name = seller.get("name")

            # Remodel detection
            comments = _normalize_text(item.get("comments"))
            remodeled = any(
                p in comments
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
                country=country_name,
                region=region_name,
                city=city_name,
                neighborhood=neighborhood_name,
                address=address,
                latitude=latitude,
                longitude=longitude,
                property_type=property_type_name,
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


