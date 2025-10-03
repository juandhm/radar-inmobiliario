"""Standardized data models for real estate listings.

Models are intentionally simple and based on dataclasses to keep the codebase
easy to reason about and test. Optional fields use explicit Optional types.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Listing:
    """Standardized real estate listing model.

    This model captures the common denominator across platforms.
    """

    listing_id: str
    platform: str
    url: str

    country: Optional[str]
    region: Optional[str]
    city: Optional[str]
    neighborhood: Optional[str]
    address: Optional[str]

    latitude: Optional[float]
    longitude: Optional[float]

    property_type: Optional[str]
    total_area_m2: Optional[float]
    bedrooms: Optional[int]
    bathrooms: Optional[float]
    parking_spaces: Optional[int]
    stratum: Optional[int]
    condition: Optional[str]
    build_age: Optional[str]
    remodeled: bool

    sale_price: Optional[float]
    rent_price: Optional[float]
    admin_price: Optional[float]
    deal_type: Optional[str]

    publish_date: Optional[str]
    update_date: Optional[str]
    ingestion_date: Optional[str]

    contact_name: Optional[str]


