"""Output schema and projector for standardized listings.

This module defines the required output columns (order-sensitive) and a
projector that maps a Listing instance to a dict matching the schema. Any
fields not available are emitted as empty strings.
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence

from .models import Listing


HEADERS: List[str] = [
    "#",
    "id_inmueble",
    "Plataforma",
    "Link",
    "Duplicado",
    #"pais",
    #"departamento",
    "Ciudad",
    #"barrios",
    "Barrio",
    "Está en el barrio?",
    "Dónde está?",
    #"Estrato",
    "Direccion",
    #"latitud",
    #"longitud",
    #"Antigüedad",
    "Tipo propiedad",
    #"Precio Admon",
    "Precio venta",
    "área m2",
    "Valor m2",
    "Valor m2 actualizado",
    "Remodelado",
    "Desv reformados",
    "Resultado",
    "Propiedad horizontal",
    "Piso",
    "Ascensor",
    "# Habitaciones",
    "# baños",
    #"Balcón",
    "Red gas",
    "Zona ropas",
    #"Util",
    "# Parquead",
    "Fecha actual",
    # "estado",
    "Fecha publicación",
    #"fecha_actualizacion",
    #"fecha_ingreso",
    "Agencia",
    "Contacto",
    "COMENTARIOS",
]


def _safe_number(value: Any) -> Any:
    return "" if value is None else value


def project_listing_to_row(listing: Listing) -> Dict[str, Any]:
    """Project a Listing into a dict matching the required schema."""
    valor_m2 = ""
    if listing.sale_price is not None and listing.total_area_m2 not in (None, 0):
        try:
            valor_m2 = float(listing.sale_price) / float(listing.total_area_m2)
        except Exception:
            valor_m2 = ""

    row: Dict[str, Any] = {
        "id_inmueble": listing.listing_id,
        "Plataforma": listing.platform,
        "Link": listing.url,
        "Duplicado": "",
        #"pais": listing.country or "",
        #"departamento": listing.region or "",
        "Ciudad": listing.city or "",
        #"barrios": listing.neighborhood or "",
        "Barrio": listing.neighborhood or "",
        "Está en el barrio?": "",
        "Dónde está?": "",
        #"Estrato": _safe_number(listing.stratum),
        "Direccion": listing.address or "",
        #"latitud": _safe_number(listing.latitude),
        #"longitud": _safe_number(listing.longitude),
        #"Antigüedad": listing.build_age or "",
        "Tipo propiedad": listing.property_type or "",
        #"Precio Admon": _safe_number(listing.admin_price),
        "Precio venta": _safe_number(listing.sale_price),
        "área m2": _safe_number(listing.total_area_m2),
        "Valor m2": valor_m2,
        "Valor m2 actualizado": "",
        "Remodelado": listing.remodeled,
        "Desv reformados": "",
        "Resultado": "",
        "Propiedad horizontal": "",
        "Piso": "",
        "Ascensor": "",
        "# Habitaciones": _safe_number(listing.bedrooms),
        "# baños": _safe_number(listing.bathrooms),
        #"Balcón": "",
        "Red gas": "",
        "Zona ropas": "",
        #"Util": "",
        "# Parquead": _safe_number(listing.parking_spaces),
        "Fecha actual": "",
        #"estado": listing.condition or "",
        "Fecha publicación": listing.publish_date or "",
        #"fecha_actualizacion": listing.update_date or "",
        #"fecha_ingreso": listing.ingestion_date or "",
        "Agencia": "",
        "Contacto": listing.contact_name or "",
        "COMENTARIOS": "",
    }

    return row


