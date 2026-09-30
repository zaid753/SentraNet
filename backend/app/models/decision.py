from pydantic import BaseModel
from typing import Optional

class DecisionObject(BaseModel):
    timestamp: str
    attack_class: str
    attack_probability: float
    risk_score: float
    confidence: float
    anomaly_score: float
    time_to_impact_seconds: Optional[float] = None
    forecast_status: str
    explanation: str
