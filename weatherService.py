"""
Live weather + forecast, backed by Open-Meteo (free, no API key, supports
explicit model selection e.g. models=gfs_seamless / ecmwf_ifs — this is how
the NWP model integration requirement from the SIH brief is satisfied
without having to run GFS/WRF yourself).
"""
from typing import Any, Dict, Optional

import httpx

from app.config import get_settings
from app.utils.wmo_codes import describe

settings = get_settings()


class WeatherServiceError(Exception):
    pass


async def get_current_weather(lat: float, lon: float, models: Optional[str] = None) -> Dict[str, Any]:
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ",".join(
            [
                "temperature_2m",
                "apparent_temperature",
                "relative_humidity_2m",
                "precipitation",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
            ]
        ),
        "timezone": "auto",
    }
    if models:
        params["models"] = models

    data = await _fetch(params)
    current = data.get("current", {})

    return {
        "latitude": data.get("latitude", lat),
        "longitude": data.get("longitude", lon),
        "temperature_c": current.get("temperature_2m"),
        "apparent_temperature_c": current.get("apparent_temperature"),
        "humidity_pct": current.get("relative_humidity_2m"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "wind_direction_deg": current.get("wind_direction_10m"),
        "precipitation_mm": current.get("precipitation"),
        "weather_code": current.get("weather_code"),
        "weather_description": describe(current.get("weather_code")),
        "observed_at": current.get("time"),
    }


async def get_forecast(lat: float, lon: float, days: int = 5, models: Optional[str] = None) -> Dict[str, Any]:
    days = max(1, min(days, 16))  # Open-Meteo supports up to 16 day forecasts
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ",".join(
            [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "precipitation_probability_max",
                "wind_speed_10m_max",
                "weather_code",
            ]
        ),
        "forecast_days": days,
        "timezone": "auto",
    }
    if models:
        params["models"] = models

    data = await _fetch(params)
    daily = data.get("daily", {})
    dates = daily.get("time", [])

    forecast_days = []
    for i, date in enumerate(dates):
        forecast_days.append(
            {
                "date": date,
                "temp_max_c": _at(daily.get("temperature_2m_max"), i),
                "temp_min_c": _at(daily.get("temperature_2m_min"), i),
                "precipitation_sum_mm": _at(daily.get("precipitation_sum"), i),
                "precipitation_probability_max_pct": _at(daily.get("precipitation_probability_max"), i),
                "wind_speed_max_kmh": _at(daily.get("wind_speed_10m_max"), i),
                "weather_code": _at(daily.get("weather_code"), i),
                "weather_description": describe(_at(daily.get("weather_code"), i)),
            }
        )

    return {
        "latitude": data.get("latitude", lat),
        "longitude": data.get("longitude", lon),
        "days": forecast_days,
    }


async def _fetch(params: Dict[str, Any]) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(settings.OPEN_METEO_FORECAST_URL, params=params)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPError as exc:
        raise WeatherServiceError(f"Open-Meteo request failed: {exc}") from exc
    except ValueError as exc:
        raise WeatherServiceError(f"Open-Meteo returned invalid JSON: {exc}") from exc


def _at(lst, i):
    if not lst or i >= len(lst):
        return None
    return lst[i]
