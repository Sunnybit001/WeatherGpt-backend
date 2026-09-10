"""
Early-warning alerts.

There is no open, keyless API for official IMD/NDMA cyclone & flood
warnings, so this module *derives* alerts from the forecast + risk engine
(same data everything else in the app uses) and persists them. The
function `ingest_external_alert()` is the seam where a real IMD/WIS2.0/
MQTT feed can be wired in later without touching any calling code —
see `app/services/mqtt_listener.py`.
"""
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app import models
from app.services import risk_engine, weather_service


HAZARD_MESSAGES = {
    "flood": "Heavy to very heavy rainfall expected — risk of local flooding.",
    "cyclone": "Strong/damaging winds expected — cyclonic conditions possible.",
    "heatwave": "Dangerously high temperatures expected — heatwave conditions likely.",
}


async def generate_alerts_for_location(db: Session, location: str, lat: float, lon: float) -> List[models.Alert]:
    forecast = await weather_service.get_forecast(lat, lon, days=5)
    assessment = risk_engine.assess(forecast["days"])

    created: List[models.Alert] = []

    for hazard, score_key in (("flood", "flood_score"), ("cyclone", "cyclone_score"), ("heatwave", "heatwave_score")):
        score = assessment[score_key]
        if score < 50:
            continue  # only HIGH/SEVERE become alerts
        severity = "SEVERE" if score >= 75 else "HIGH"
        alert = models.Alert(
            location=location,
            latitude=lat,
            longitude=lon,
            hazard=hazard,
            severity=severity,
            message=f"{severity}: {HAZARD_MESSAGES[hazard]} (risk score {score}/100)",
            source="internal_risk_engine",
        )
        db.add(alert)
        created.append(alert)

    if created:
        db.commit()
        for a in created:
            db.refresh(a)

    return created


def ingest_external_alert(
    db: Session,
    location: str,
    hazard: str,
    severity: str,
    message: str,
    source: str,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
) -> models.Alert:
    """Insertion point for a real external feed (IMD bulletin, WIS2.0/MQTT message, etc.)."""
    alert = models.Alert(
        location=location,
        latitude=lat,
        longitude=lon,
        hazard=hazard,
        severity=severity,
        message=message,
        source=source,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def list_recent_alerts(db: Session, location: Optional[str] = None, limit: int = 50) -> List[models.Alert]:
    query = db.query(models.Alert)
    if location:
        query = query.filter(models.Alert.location.ilike(f"%{location}%"))
    return query.order_by(models.Alert.created_at.desc()).limit(limit).all()
