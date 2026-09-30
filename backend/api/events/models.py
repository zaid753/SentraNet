import datetime
import uuid
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class EventEnvelope(BaseModel):
    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex}")
    event_type: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    source: str = "sentranet"
    payload: Dict[str, Any]

class EventTypes:
    TELEMETRY_WINDOW_CREATED = "telemetry.window.created"
    RISK_UPDATED = "risk.updated"
    FORECAST_UPDATED = "forecast.updated"
    ALERT_CREATED = "alert.created"
    ALERT_UPDATED = "alert.updated"
    INCIDENT_CREATED = "incident.created"
    INCIDENT_UPDATED = "incident.updated"
    INCIDENT_RESOLVED = "incident.resolved"
    SYSTEM_STATUS_CHANGED = "system.status.changed"
    REPLAY_STATUS_CHANGED = "replay.status.changed"
