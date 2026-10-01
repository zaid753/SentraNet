from sqlalchemy import Column, String, DateTime, Float, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from backend.api.database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    status = Column(String, nullable=False, default="ACTIVE")
    attack_class = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    first_risk_score = Column(Float, nullable=False)
    current_risk_score = Column(Float, nullable=False)
    peak_risk_score = Column(Float, nullable=False)
    max_anomaly_score = Column(Float, nullable=False)
    forecast_triggered = Column(Boolean, default=False)
    estimated_eta_seconds = Column(Integer, nullable=True)

    workspace = relationship("Workspace", back_populates="incidents")
    alerts = relationship("Alert", back_populates="incident")
