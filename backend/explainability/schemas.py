"""
SENTRANET — Explainability Pydantic Schemas (Phase 11)
Stable, frontend-friendly response schemas.
All values are derived from actual system data — no fabrication.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class FeatureExplanation(BaseModel):
    """Explanation for a single feature's role in the current prediction."""
    feature: str = Field(..., description="Canonical feature name")
    display_name: str = Field(..., description="Human-readable feature name")
    category: str = Field(..., description="Feature category")
    current_value: Optional[float] = Field(None, description="Current window value")
    unit: str = Field("", description="Measurement unit")
    global_importance: Optional[float] = Field(
        None,
        description="Model-level gain importance (normalized). Not prediction-specific."
    )
    importance_rank: Optional[int] = Field(None, description="Rank among all features by global importance")
    description: str = Field("", description="What this feature measures")


class RiskComponents(BaseModel):
    """Decomposition of the risk fusion formula."""
    attack_likelihood: float = Field(..., description="1 - P(BENIGN) = attack probability signal")
    attack_likelihood_weight: float = Field(..., description="Classification weight in fusion formula")
    attack_likelihood_contribution: float = Field(..., description="attack_likelihood × weight")
    anomaly_score: float = Field(..., description="Isolation Forest anomaly score [0, 1]")
    anomaly_weight: float = Field(..., description="Anomaly weight in fusion formula")
    anomaly_contribution: float = Field(..., description="anomaly_score × weight")
    combined_risk: float = Field(..., description="Fused risk score (clipped to [0, 1])")
    formula: str = Field(
        "risk = clip(cls_weight × (1 - P(BENIGN)) + ano_weight × anomaly_score, 0, 1)",
        description="Risk fusion formula"
    )


class ClassificationExplanation(BaseModel):
    """Explanation for the XGBoost classification result."""
    predicted_class: str
    confidence: float = Field(..., description="Max class probability (classification confidence)")
    all_probabilities: Dict[str, float] = Field(..., description="All 5-class probabilities")
    attack_likelihood: float = Field(..., description="1 - P(BENIGN)")
    p_benign: float = Field(..., description="P(BENIGN) as reported by XGBoost")
    model_name: str = Field("sentranet_xgboost", description="Model identifier")
    feature_schema: str = Field("17_features_v1", description="Feature schema version")
    note: str = Field(
        "confidence = max class probability; attack_likelihood = 1 - P(BENIGN)",
        description="Terminology note"
    )


class AnomalyExplanation(BaseModel):
    """Explanation for the Isolation Forest anomaly result."""
    anomaly_score: float = Field(..., description="Isolation Forest anomaly score [0, 1]")
    is_anomalous: bool = Field(..., description="Whether anomaly_score >= threshold")
    threshold: Optional[float] = Field(None, description="Operational anomaly threshold")
    status: str = Field(..., description="ANOMALOUS or NORMAL")
    interpretation: str = Field(
        ...,
        description="Factual statement about the anomaly score relative to threshold"
    )
    note: str = Field(
        "An anomaly score above threshold indicates deviation from the learned benign reference. "
        "It does not constitute proof of an attack.",
        description="Scientific honesty note"
    )


class RiskExplanation(BaseModel):
    """Risk score decomposition and state explanation."""
    risk_score: float
    risk_state: str
    risk_velocity: float = Field(..., description="Risk change rate per minute")
    risk_acceleration: float = Field(..., description="Risk velocity change per minute²")
    risk_trend: str = Field(..., description="RISING | FALLING | STABLE | RAPIDLY_RISING")
    components: RiskComponents
    state_thresholds: Dict[str, str] = Field(
        default_factory=lambda: {
            "LOW": "0.00 – 0.24",
            "GUARDED": "0.25 – 0.49",
            "ELEVATED": "0.50 – 0.74",
            "HIGH": "0.75 – 1.00",
        }
    )
    primary_driver: str = Field(
        ...,
        description="Which component drives the risk: CLASSIFICATION | ANOMALY | BOTH | NEITHER"
    )
    narrative: str = Field(..., description="Deterministic text explanation of risk state")
    velocity_narrative: Optional[str] = Field(None, description="Trajectory explanation")
    eta_seconds: Optional[int] = Field(None, description="Heuristic ETA to HIGH state (if applicable)")
    eta_note: str = Field(
        "ETA is a heuristic estimate derived from the current risk trajectory. "
        "It is not a calibrated probability or guaranteed attack time.",
        description="ETA disclaimer"
    )


class ForecastCondition(BaseModel):
    """One condition checked by the forecast engine."""
    condition: str = Field(..., description="Condition name")
    satisfied: bool = Field(..., description="Whether this condition was met")
    detail: str = Field("", description="Specific value or reason")


class ForecastExplanation(BaseModel):
    """Explanation for forecast active/inactive state."""
    forecast_available: bool
    forecast_class: Optional[str]
    forecast_confidence: Optional[float]
    time_to_impact_seconds: Optional[int]
    conditions: List[ForecastCondition] = Field(
        ...,
        description="All conditions checked (both satisfied and unsatisfied)"
    )
    reasons: List[str] = Field(default_factory=list, description="Engine-provided reason strings")
    narrative: str = Field(
        ...,
        description="Why forecast is active or not active"
    )
    eta_narrative: Optional[str] = Field(
        None,
        description="Heuristic ETA explanation (only when forecast is active)"
    )
    eta_note: str = Field(
        "ETA is a heuristic estimate derived from the current risk trajectory. "
        "It is not a calibrated probability or guaranteed attack time.",
        description="ETA disclaimer"
    )


class AnalystSummary(BaseModel):
    """Deterministic, structured analyst-facing summary."""
    what: str = Field(..., description="What was observed (neutral technical wording)")
    severity: str = Field(..., description="Current risk state")
    why: List[str] = Field(..., description="Evidence list (factual, derived from actual values)")
    trend: str = Field(..., description="RISING | FALLING | STABLE | RAPIDLY_RISING")
    forecast_active: bool
    eta_seconds: Optional[int]
    classification_confidence: Optional[float]
    forecast_confidence: Optional[float]
    data_source: str = Field("HISTORICAL_REPLAY", description="SIMULATION | HISTORICAL_REPLAY | LIVE | BENCHMARK")
    limitations: List[str] = Field(
        default_factory=list,
        description="Known limitations of this explanation"
    )


class ExplanationResponse(BaseModel):
    """
    Complete Phase 11 ExplanationObject.
    All values are derived from actual DecisionObject and feature vector.
    No fabricated data.
    """
    # Traceability
    window_id: str = Field(..., description="Window identifier (timestamp-based)")
    timestamp: str = Field(..., description="Window timestamp (ISO 8601)")
    model_version: str = Field("sentranet_xgboost_v1", description="Model identifier")
    feature_schema: str = Field("17_features_v1", description="Feature schema")

    # Core
    summary: AnalystSummary
    classification: ClassificationExplanation
    anomaly: AnomalyExplanation
    risk: RiskExplanation
    forecast: ForecastExplanation

    # Feature panel (all 17 features)
    features: List[FeatureExplanation] = Field(
        ...,
        description="All 17 canonical features with values and importance"
    )

    # Top signals (up to 5, by global importance)
    top_features: List[FeatureExplanation] = Field(
        ...,
        description="Top 5 features by model-level gain importance. "
                    "Labeled 'Model-level feature importance', not prediction explanation."
    )

    # Limitations
    limitations: List[str] = Field(
        default_factory=list,
        description="Scientific limitations of this explanation"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "window_id": "2026-01-01T08:00:00",
                "timestamp": "2026-01-01T08:00:00",
                "model_version": "sentranet_xgboost_v1",
                "feature_schema": "17_features_v1",
            }
        }
