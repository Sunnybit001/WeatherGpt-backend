"""
Aviation weather briefings (METAR), backed by the free public
aviationweather.gov data API — no API key required. Use ICAO airport
codes, e.g. VIDP (Delhi), VABB (Mumbai), VOBL (Bengaluru), KJFK (JFK).
"""
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import httpx

from app.config import get_settings

settings = get_settings()


class AviationServiceError(Exception):
    pass


async def get_metar(icao: str) -> Dict[str, Any]:
    icao = icao.strip().upper()
    params = {"ids": icao, "format": "json"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(settings.AVIATION_WEATHER_API_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as exc:
        raise AviationServiceError(f"Aviation weather request failed: {exc}") from exc
    except ValueError as exc:
        raise AviationServiceError(f"Aviation weather returned invalid JSON: {exc}") from exc

    if not data:
        return {
            "icao": icao,
            "raw_metar": None,
            "parsed": {},
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    report = data[0] if isinstance(data, list) else data
    raw = report.get("rawOb") or report.get("raw_text")

    parsed = {
        "temperature_c": report.get("temp"),
        "dewpoint_c": report.get("dewp"),
        "wind_direction_deg": report.get("wdir"),
        "wind_speed_kt": report.get("wspd"),
        "wind_gust_kt": report.get("wgst"),
        "visibility_sm": report.get("visib"),
        "altimeter_hpa": report.get("altim"),
        "flight_category": report.get("fltCat") or report.get("flight_category"),
        "clouds": report.get("clouds"),
    }

    return {
        "icao": icao,
        "raw_metar": raw,
        "parsed": {k: v for k, v in parsed.items() if v is not None},
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
