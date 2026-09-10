import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, index=True, nullable=True)
    query = Column(Text, nullable=False)
    detected_language = Column(String, nullable=True)
    intent = Column(String, index=True, nullable=True)
    location = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    response = Column(Text, nullable=False)
    raw_data = Column(Text, nullable=True)  # JSON string of the underlying weather/tool payload
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=_uuid)
    location = Column(String, index=True, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    hazard = Column(String, index=True, nullable=False)  # flood, cyclone, heatwave, ...
    severity = Column(String, nullable=False)  # LOW, MODERATE, HIGH, SEVERE
    message = Column(Text, nullable=False)
    source = Column(String, default="internal_risk_engine")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(String, primary_key=True, default=_uuid)
    location = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    flood_score = Column(Integer, default=0)
    cyclone_score = Column(Integer, default=0)
    heatwave_score = Column(Integer, default=0)
    overall_level = Column(String, nullable=False)
    details = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class CropAdvisoryLog(Base):
    __tablename__ = "crop_advisory_log"

    id = Column(String, primary_key=True, default=_uuid)
    location = Column(String, nullable=False)
    crop = Column(String, nullable=True)
    advice = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
