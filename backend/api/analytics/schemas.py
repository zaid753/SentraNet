from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import datetime

class MetricTrend(BaseModel):
    timestamp: str
    value: float

class AnalyticsOverviewResponse(BaseModel):
    total_incidents: int
    active_incidents: int
    resolved_incidents: int
    total_alerts: int
    peak_risk: float
    average_resolution_seconds: Optional[float]
    threat_distribution: Dict[str, int]
    incident_trend: List[MetricTrend]
    alert_trend: List[MetricTrend]
    risk_trend: List[MetricTrend]

class ModelHealthDetail(BaseModel):
    status: str
    version: str = "Not tracked"
    feature_count: Optional[int] = None
    classes: Optional[List[str]] = None

class SystemHealthResponse(BaseModel):
    status: str
    api: str
    database: str
    realtime: str
    xgboost: ModelHealthDetail
    isolation_forest: ModelHealthDetail
    forecast_engine: ModelHealthDetail
    replay: str
