from sqlalchemy import Column, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from backend.api.database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=False)
    alert_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="NEW")
    risk_score = Column(Float, nullable=True)
    anomaly_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    incident = relationship("Incident", back_populates="alerts")
