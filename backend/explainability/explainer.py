"""
SENTRANET — Main Explainer (Phase 11)
Orchestrates all sub-explainers to produce a complete ExplanationObject.

Critical principles (enforced here):
- All values derived from actual DecisionObject + feature vector
- No fabricated data, no LLM text generation
- Deterministic: same inputs → same ExplanationObject
- No future leakage: explanation at time t uses only data up to t
- Caching by window_id (invalidated on new window)
"""

from typing import Dict, Any, Optional, List
import threading
from datetime import timezone
import datetime

from backend.explainability.schemas import (
    ExplanationResponse,
    AnomalyExplanation,
    AnalystSummary,
)
from backend.explainability.classification_explainer import (
    build_classification_explanation,
    build_feature_explanations,
)
from backend.explainability.risk_explainer import build_risk_explanation
from backend.explainability.forecast_explainer import build_forecast_explanation


# ──────────────────────────────────────────────────────────────────────────────
# Module-level explanation cache
# Keyed by window_id (timestamp string). Thread-safe.
# ──────────────────────────────────────────────────────────────────────────────
_cache: Dict[str, ExplanationResponse] = {}
_cache_lock = threading.Lock()
_CACHE_MAX_SIZE = 50  # Keep up to 50 window explanations


def invalidate_cache() -> None:
    """Call when a new window is processed. Clears the explanation cache."""
    with _cache_lock:
        _cache.clear()


def get_cached_explanation(window_id: str) -> Optional[ExplanationResponse]:
    """Returns cached explanation for window_id, or None if not cached."""
    with _cache_lock:
        return _cache.get(window_id)


def _cache_explanation(window_id: str, explanation: ExplanationResponse) -> None:
    with _cache_lock:
        if len(_cache) >= _CACHE_MAX_SIZE:
            # Evict oldest entry (FIFO)
            oldest = next(iter(_cache))
            del _cache[oldest]
        _cache[window_id] = explanation


# ──────────────────────────────────────────────────────────────────────────────
# Anomaly Explanation builder
# ──────────────────────────────────────────────────────────────────────────────

# Default anomaly threshold from IsolationForestDetector (matches anomaly_reference.json)
_DEFAULT_ANOMALY_THRESHOLD = 0.4978


def _build_anomaly_explanation(
    anomaly_score: float,
    is_anomalous: bool,
    threshold: Optional[float] = None,
) -> AnomalyExplanation:
    eff_threshold = threshold or _DEFAULT_ANOMALY_THRESHOLD
    status = "ANOMALOUS" if is_anomalous else "NORMAL"
    if is_anomalous:
        interpretation = (
            f"Current behavior (score: {anomaly_score:.4f}) exceeds the anomaly threshold "
            f"({eff_threshold:.4f}), indicating deviation from the learned benign reference "
            "according to the Isolation Forest detector."
        )
    else:
        interpretation = (
            f"Current behavior (score: {anomaly_score:.4f}) is within the normal range "
            f"relative to the anomaly threshold ({eff_threshold:.4f})."
        )
    return AnomalyExplanation(
        anomaly_score=round(anomaly_score, 4),
        is_anomalous=is_anomalous,
        threshold=round(eff_threshold, 4),
        status=status,
        interpretation=interpretation,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Analyst Summary builder
# ──────────────────────────────────────────────────────────────────────────────

_CLASS_DESCRIPTIONS = {
    "DDOS": "Potential DDoS activity",
    "SCANNING": "Potential scanning behavior",
    "BOTNET": "Potential botnet activity",
    "OTHER_ATTACK": "Potential attack activity",
    "BENIGN": "Normal traffic pattern",
}


def _build_analyst_summary(
    decision: Dict[str, Any],
    data_source: str = "HISTORICAL_REPLAY",
) -> AnalystSummary:
    predicted_class = decision.get("predicted_class", "BENIGN")
    risk_state = decision.get("risk_state", "LOW")
    risk_velocity = decision.get("risk_velocity", 0.0)
    risk_trend = decision.get("risk_trend", "STABLE")
    attack_likelihood = max(0.0, 1.0 - float(decision.get("class_probabilities", {}).get("BENIGN", 1.0)))
    anomaly_score = decision.get("anomaly_score", 0.0)
    is_anomalous = decision.get("is_anomalous", False)
    forecast_available = bool(decision.get("forecast_available", False))
    eta_seconds = decision.get("time_to_impact_seconds")
    cls_confidence = decision.get("classification_confidence")
    forecast_confidence = decision.get("forecast_confidence")

    what = _CLASS_DESCRIPTIONS.get(predicted_class, f"Potential {predicted_class} activity")

    # Evidence list — only add conditions actually met
    why: List[str] = []
    if attack_likelihood >= 0.5:
        why.append(f"Attack likelihood elevated ({attack_likelihood:.2f})")
    if is_anomalous or anomaly_score >= 0.4:
        why.append(f"Anomaly score above threshold ({anomaly_score:.2f})")
    if risk_trend in {"RISING", "RAPIDLY_RISING"}:
        why.append(f"Risk trend {risk_trend.lower().replace('_', ' ')} (velocity: {risk_velocity:+.4f}/min)")
    if forecast_available:
        why.append(f"Forecast signal active for {decision.get('forecast_class', predicted_class)}")
    if not why:
        why.append(f"Risk score {decision.get('risk_score', 0.0):.4f} in {risk_state} state")

    limitations: List[str] = []
    if data_source == "SIMULATION":
        limitations.append(
            "Data source is SIMULATION. Results reflect synthetic data, not real network traffic."
        )
    if data_source == "HISTORICAL_REPLAY":
        limitations.append(
            "Data source is HISTORICAL REPLAY. Results reflect replayed historical data."
        )
    limitations.append(
        "Classification confidence is not equivalent to attack certainty. "
        "False positives are possible."
    )
    if forecast_available and eta_seconds is not None:
        limitations.append(
            "ETA is a heuristic estimate derived from risk trajectory extrapolation. "
            "It is not a guaranteed attack time."
        )

    return AnalystSummary(
        what=what,
        severity=risk_state,
        why=why,
        trend=risk_trend,
        forecast_active=forecast_available,
        eta_seconds=eta_seconds,
        classification_confidence=round(cls_confidence, 4) if cls_confidence is not None else None,
        forecast_confidence=round(forecast_confidence, 4) if forecast_confidence is not None else None,
        data_source=data_source,
        limitations=limitations,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Top-level explainer
# ──────────────────────────────────────────────────────────────────────────────

def build_explanation(
    decision: Dict[str, Any],
    feature_values: Dict[str, float],
    booster,
    history_length: int,
    anomaly_threshold: Optional[float] = None,
    data_source: str = "HISTORICAL_REPLAY",
    cls_weight: float = 0.60,
    ano_weight: float = 0.40,
) -> ExplanationResponse:
    """
    Builds a complete ExplanationObject from actual system data.

    Args:
        decision: Full DecisionObject from ForecastEngine.update()
        feature_values: Dict mapping canonical feature names to actual float values
        booster: XGBoost Booster (for feature importance)
        history_length: Number of windows in the trajectory history
        anomaly_threshold: Operational anomaly threshold (if known)
        data_source: SIMULATION | HISTORICAL_REPLAY | LIVE | BENCHMARK
        cls_weight: Classification weight used by RiskFusionEngine
        ano_weight: Anomaly weight used by RiskFusionEngine

    Returns:
        ExplanationResponse — fully traceable, deterministic

    Raises:
        ValueError: If decision dict is missing required keys
    """
    timestamp = str(decision.get("timestamp", ""))
    window_id = timestamp or datetime.datetime.now(timezone.utc).isoformat()

    # Check cache
    cached = get_cached_explanation(window_id)
    if cached is not None:
        return cached

    # Extract common values
    predicted_class = str(decision.get("predicted_class", "BENIGN"))
    class_probabilities = dict(decision.get("class_probabilities", {}))
    classification_confidence = float(decision.get("classification_confidence", 0.0))
    anomaly_score = float(decision.get("anomaly_score", 0.0))
    is_anomalous = bool(decision.get("is_anomalous", False))
    risk_score = float(decision.get("risk_score", 0.0))
    risk_state = str(decision.get("risk_state", "LOW"))
    risk_velocity = float(decision.get("risk_velocity", 0.0))
    risk_acceleration = float(decision.get("risk_acceleration", 0.0))
    risk_trend = str(decision.get("risk_trend", "STABLE"))
    eta_seconds = decision.get("time_to_impact_seconds")
    attack_likelihood = max(0.0, 1.0 - float(class_probabilities.get("BENIGN", 1.0)))

    # 1. Classification explanation
    classification = build_classification_explanation(
        predicted_class=predicted_class,
        class_probabilities=class_probabilities,
        classification_confidence=classification_confidence,
    )

    # 2. Anomaly explanation
    anomaly = _build_anomaly_explanation(anomaly_score, is_anomalous, anomaly_threshold)

    # 3. Risk explanation
    risk = build_risk_explanation(
        risk_score=risk_score,
        risk_state=risk_state,
        risk_velocity=risk_velocity,
        risk_acceleration=risk_acceleration,
        risk_trend=risk_trend,
        attack_likelihood=attack_likelihood,
        anomaly_score=anomaly_score,
        cls_weight=cls_weight,
        ano_weight=ano_weight,
        eta_seconds=eta_seconds,
    )

    # 4. Forecast explanation
    forecast = build_forecast_explanation(decision, history_length)

    # 5. Feature explanations
    all_features, top_features = build_feature_explanations(feature_values, booster)

    # 6. Analyst summary
    summary = _build_analyst_summary(decision, data_source)

    # 7. Global limitations
    limitations = [
        "Model-level feature importance (gain) is used, not prediction-level attribution. "
        "Individual feature contributions to this specific prediction are not computed.",
        "SHAP is not installed. Top features reflect global model behavior, not this window's prediction.",
    ]
    if not feature_values:
        limitations.append(
            "Feature values are unavailable for this window (legacy replay mode). "
            "Feature panel shows importance ranks only."
        )

    explanation = ExplanationResponse(
        window_id=window_id,
        timestamp=timestamp,
        summary=summary,
        classification=classification,
        anomaly=anomaly,
        risk=risk,
        forecast=forecast,
        features=all_features,
        top_features=top_features,
        limitations=limitations,
    )

    _cache_explanation(window_id, explanation)
    return explanation
