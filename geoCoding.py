"""
Resolve a free-text place name to latitude/longitude using Open-Meteo's
geocoding API. No API key required.
"""
from typing import Optional, Tuple

import httpx

from app.config import get_settings

settings = get_settings()


async def geocode(place_name: str) -> Optional[Tuple[float, float, str]]:
    """Returns (lat, lon, resolved_display_name) or None if not found."""
    if not place_name or not place_name.strip():
        return None

    params = {"name": place_name.strip(), "count": 1, "language": "en", "format": "json"}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(settings.OPEN_METEO_GEOCODING_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
    except (httpx.HTTPError, ValueError):
        return None

    results = data.get("results") or []
    if not results:
        return None

    top = results[0]
    display_parts = [top.get("name")]
    if top.get("admin1"):
        display_parts.append(top["admin1"])
    if top.get("country"):
        display_parts.append(top["country"])
    display_name = ", ".join(p for p in display_parts if p)

    return float(top["latitude"]), float(top["longitude"]), display_name
