from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------- Shared ----------

class LocationQuery(BaseModel):
    location: Optional[str] = Field(None, description="Free-text place name, e.g. 'Kurukshetra'")
    lat: Optional[float] = None
    lon: Optional[float] = None


# ---------- Chat ----------

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language user question")
    location: Optional[str] = Field(None, description="Optional explicit location override")
    lat: Optional[float] = None
    lon: Optional[float] = None
    language: Optional[str] = Field(None, description="BCP-47 code; auto-detected if omitted")
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    intent: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    detected_language: str
    response: str
    data: Dict[str, Any] = {}
    risk: Optional[Dict[str, Any]] = None


# ---------- Weather ----------

class CurrentWeather(BaseModel):
    location: str
    latitude: float
    longitude: float
    temperature_c: Optional[float]
    apparent_temperature_c: Optional[float]
    humidity_pct: Optional[float]
    wind_speed_kmh: Optional[float]
    wind_direction_deg: Optional[float]
    precipitation_mm: Optional[float]
    weather_code: Optional[int]
    weather_description: Optional[str]
    observed_at: Optional[str]


class ForecastDay(BaseModel):
    date: str
    temp_max_c: Optional[float]
    temp_min_c: Optional[float]
    precipitation_sum_mm: Optional[float]
    precipitation_probability_max_pct: Optional[float]
    wind_speed_max_kmh: Optional[float]
    weather_code: Optional[int]
    weather_description: Optional[str]


class ForecastResponse(BaseModel):
    location: str
    latitude: float
    longitude: float
    days: List[ForecastDay]


# ---------- Historical / climate ----------

class ClimateTrendResponse(BaseModel):
    location: str
    latitude: float
    longitude: float
    variable: str
    period_years: int
    yearly_averages: Dict[str, float]
    trend_per_year: float
    trend_summary: str


# ---------- Aviation ----------

class AviationWeatherResponse(BaseModel):
    icao: str
    raw_metar: Optional[str]
    parsed: Dict[str, Any] = {}
    fetched_at: Optional[str]


# ---------- Alerts ----------

class AlertOut(BaseModel):
    id: str
    location: str
    hazard: str
    severity: str
    message: str
    source: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Risk ----------

class RiskAssessRequest(BaseModel):
    location: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


class RiskAssessResponse(BaseModel):
    location: str
    latitude: float
    longitude: float
    flood_score: int
    cyclone_score: int
    heatwave_score: int
    overall_level: str
    details: Dict[str, Any]


# ---------- Crop advisory ----------

class CropAdvisoryRequest(BaseModel):
    location: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    crop: Optional[str] = None
    language: Optional[str] = None


class CropAdvisoryResponse(BaseModel):
    location: str
    crop: Optional[str]
    advice: str
    weather_summary: Dict[str, Any]
