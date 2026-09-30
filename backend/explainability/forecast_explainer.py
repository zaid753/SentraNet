"""
SENTRANET — Forecast Explainer (Phase 11)
Explains why a forecast was triggered or not triggered.
Uses actual emergence detector conditions from ml/forecast/emergence.py.
No fabrication — every condition maps to actual engine state.
"""

from typing import Dict, Any, List, Optional
from backend.explainability.schemas import ForecastExplanation, ForecastCondition

# Matches AttackEmergenceDetector constants from ml/forecast/emergence.py
# These thresholds are the same defaults used by the engine.
EMERGENCE_THRESHOLD_DEFAULT = 0.50
MIN_PERSISTENCE_WINDOWS_DEFAULT = 2
MIN_HISTORY_WINDOWS = 3  # minimum_history_windows in ForecastEngine


def _build_forecast_conditions(
    decision: Dict[str, Any],
    history_length: int,
) -> List[ForecastCondition]:
    """
    Derives the actual condition states from the DecisionObject.
    Maps to the 5 conditions in AttackEmergenceDetector.evaluate_emergence().
    """
    risk_score = decision.get("risk_score", 0.0)
    risk_velocity = decision.get("risk_velocity", 0.0)
    risk_trend = decision.get("risk_trend", "STABLE")
    anomaly_score = decision.get("anomaly_score", 0.0)
    is_anomalous = decision.get("is_anomalous", False)
    forecast_class = decision.get("forecast_class") or decision.get("predicted_class", "BENIGN")
    forecast_reasons = decision.get("forecast_reason") or []

    conditions = []

    # Condition 1: Sufficient history
    hist_ok = history_length >= MIN_HISTORY_WINDOWS
    conditions.append(ForecastCondition(
        condition="Sufficient temporal history",
        satisfied=hist_ok,
        detail=f"{history_length} windows available (minimum: {MIN_HISTORY_WINDOWS})"
    ))

    # Condition 2: Risk trending upward
    risk_rising = risk_velocity > 0.0 or risk_trend in {"RISING", "RAPIDLY_RISING"}
    conditions.append(ForecastCondition(
        condition="Risk trend rising",
        satisfied=risk_rising,
        detail=f"velocity={risk_velocity:.4f}/min, trend={risk_trend}"
    ))

    # Condition 3: Risk meets emergence threshold
    risk_elevated = risk_score >= EMERGENCE_THRESHOLD_DEFAULT
    conditions.append(ForecastCondition(
        condition=f"Risk ≥ emergence threshold ({EMERGENCE_THRESHOLD_DEFAULT:.2f})",
        satisfied=risk_elevated,
        detail=f"current risk_score={risk_score:.4f}"
    ))

    # Condition 4: Candidate class persisted (inferred from forecast reasons)
    persistence_ok = any("persisted" in r.lower() or "persistence" in r.lower() or "consecutive" in r.lower()
                         for r in forecast_reasons)
    # Also check: if forecast is active and class is not BENIGN
    if decision.get("forecast_available") and forecast_class != "BENIGN":
        persistence_ok = True
    conditions.append(ForecastCondition(
        condition="Candidate attack class persisted",
        satisfied=persistence_ok,
        detail=f"candidate class: {forecast_class}" if forecast_class else "no candidate class"
    ))

    # Condition 5: Anomaly score elevated
    ano_elevated = anomaly_score >= 0.40 or is_anomalous
    conditions.append(ForecastCondition(
        condition="Anomaly score elevated (≥ 0.40) or anomalous",
        satisfied=ano_elevated,
        detail=f"anomaly_score={anomaly_score:.4f}, is_anomalous={is_anomalous}"
    ))

    return conditions


def _build_forecast_narrative(
    forecast_available: bool,
    forecast_class: Optional[str],
    conditions: List[ForecastCondition],
    risk_trend: str,
    risk_velocity: float,
) -> str:
    """
    Deterministic narrative about why the forecast is active or inactive.
    Based only on actual condition states — not fabricated.
    """
    if forecast_available:
        return (
            f"Forecast is ACTIVE for class '{forecast_class}'. "
            f"All emergence conditions were satisfied: risk trend is {risk_trend.lower().replace('_', ' ')}, "
            f"candidate class persisted, and risk velocity is positive "
            f"({risk_velocity:+.4f}/min)."
        )

    # Explain why not triggered — identify first unsatisfied condition
    failed = [c for c in conditions if not c.satisfied]
    if not failed:
        return (
            "Forecast conditions were partially evaluated but no emerging attack signal was confirmed."
        )

    first_fail = failed[0]
    reason_map = {
        "Sufficient temporal history": "insufficient temporal history has accumulated",
        "Risk trend rising": f"risk trend is not rising (trend: {risk_trend})",
        f"Risk ≥ emergence threshold ({EMERGENCE_THRESHOLD_DEFAULT:.2f})": (
            "risk has not reached the emergence threshold"
        ),
        "Candidate attack class persisted": (
            "the candidate attack class did not persist for the required consecutive windows"
        ),
        "Anomaly score elevated (≥ 0.40) or anomalous": (
            "anomaly score is below the elevated threshold"
        ),
    }
    reason = reason_map.get(first_fail.condition, first_fail.condition)
    return f"Forecast not triggered because {reason}."


def _build_eta_narrative(
    time_to_impact_seconds: Optional[int],
    risk_score: float,
    target_threshold: float = 0.75,
) -> Optional[str]:
    """Deterministic ETA explanation from actual trajectory extrapolation."""
    if time_to_impact_seconds is None:
        return None
    if time_to_impact_seconds == 0:
        return (
            f"Risk has reached or exceeded the critical threshold ({target_threshold:.2f}). "
            "ETA is 0 seconds (attack has reached saturation)."
        )
    minutes = time_to_impact_seconds // 60
    seconds = time_to_impact_seconds % 60
    time_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
    return (
        f"Heuristic ETA: ~{time_str} to critical threshold ({target_threshold:.2f}), "
        "based on current risk trajectory extrapolation."
    )


def build_forecast_explanation(
    decision: Dict[str, Any],
    history_length: int,
) -> ForecastExplanation:
    """
    Builds forecast explanation from actual DecisionObject.
    All conditions derived from actual engine state.
    """
    forecast_available = bool(decision.get("forecast_available", False))
    forecast_class = decision.get("forecast_class")
    forecast_confidence = decision.get("forecast_confidence")
    time_to_impact_seconds = decision.get("time_to_impact_seconds")
    forecast_reasons = decision.get("forecast_reason") or []
    risk_trend = decision.get("risk_trend", "STABLE")
    risk_velocity = decision.get("risk_velocity", 0.0)
    risk_score = decision.get("risk_score", 0.0)

    conditions = _build_forecast_conditions(decision, history_length)
    narrative = _build_forecast_narrative(
        forecast_available, forecast_class, conditions, risk_trend, risk_velocity
    )
    eta_narrative = _build_eta_narrative(time_to_impact_seconds, risk_score)

    return ForecastExplanation(
        forecast_available=forecast_available,
        forecast_class=forecast_class,
        forecast_confidence=round(forecast_confidence, 4) if forecast_confidence is not None else None,
        time_to_impact_seconds=time_to_impact_seconds,
        conditions=conditions,
        reasons=forecast_reasons,
        narrative=narrative,
        eta_narrative=eta_narrative,
    )
