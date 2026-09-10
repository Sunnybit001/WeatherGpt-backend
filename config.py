"""
Central configuration for the WeatherGPT backend.

Everything here is overridable via environment variables or a `.env`
file in the project root (see `.env.example`). Nothing is hard-coded
so the same code can run locally on a Mac, in Docker, or on a cloud
server during the SIH evaluation.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- General ---
    APP_NAME: str = "WeatherGPT Backend"
    APP_VERSION: str = "1.0.0"
    ENV: str = "development"
    DEBUG: bool = True

    # --- CORS (mobile app / web frontend origins) ---
    CORS_ORIGINS: List[str] = ["*"]

    # --- Database ---
    # Defaults to a local SQLite file so the project runs with zero setup.
    # For production, point this at Postgres/PostGIS, e.g.:
    # postgresql+psycopg2://weathergpt:weathergpt@localhost:5432/weathergpt
    DATABASE_URL: str = "sqlite:///./weathergpt.db"

    # --- LLM / intent routing ---
    # "none"   -> fast, offline, rule-based intent parsing + template responses (default, zero setup)
    # "ollama" -> use a locally running fine-tuned Llama model via Ollama (http://localhost:11434)
    # "openai" -> use the OpenAI Chat Completions API (requires OPENAI_API_KEY)
    LLM_PROVIDER: str = "none"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "weathergpt"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # --- Weather data providers (Open-Meteo requires no API key) ---
    OPEN_METEO_FORECAST_URL: str = "https://api.open-meteo.com/v1/forecast"
    OPEN_METEO_HISTORICAL_URL: str = "https://archive-api.open-meteo.com/v1/archive"
    OPEN_METEO_GEOCODING_URL: str = "https://geocoding-api.open-meteo.com/v1/search"
    OPEN_METEO_AIR_QUALITY_URL: str = "https://air-quality-api.open-meteo.com/v1/air-quality"

    # --- Aviation weather (METAR/TAF, no API key required) ---
    AVIATION_WEATHER_API_URL: str = "https://aviationweather.gov/api/data/metar"

    # --- Translation / multilingual ---
    ENABLE_TRANSLATION: bool = True
    DEFAULT_LANGUAGE: str = "en"

    # --- Voice (optional, heavy deps installed separately) ---
    ENABLE_VOICE: bool = False

    # --- MQTT / WIS2.0 style real-time alert ingestion (optional) ---
    ENABLE_MQTT: bool = False
    MQTT_BROKER_HOST: str = ""
    MQTT_BROKER_PORT: int = 1883
    MQTT_TOPIC: str = "weather/alerts/india"

    # --- Risk engine thresholds ---
    FLOOD_RAIN_MM_HIGH: float = 64.5   # IMD "very heavy rain" 24h threshold (mm)
    FLOOD_RAIN_MM_SEVERE: float = 204.4  # IMD "extremely heavy rain" threshold (mm)
    CYCLONE_WIND_KMH_HIGH: float = 62.0   # gale force
    CYCLONE_WIND_KMH_SEVERE: float = 118.0  # severe cyclonic storm
    HEATWAVE_TEMP_C_HIGH: float = 40.0
    HEATWAVE_TEMP_C_SEVERE: float = 45.0

    # --- Simple API key protection (optional; empty disables it) ---
    API_KEY: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
