"""
SENTRANET — Risk Explainer (Phase 11)
Generates traceable risk decomposition and state explanations.
Formula: risk = clip(0.60 × (1 - P(BENIGN)) + 0.40 × anomaly_score, 0, 1)
All thresholds and weights sourced from actual RiskFusionEngine config.
"""

from typing import Optional
from backend.explainability.schemas import RiskExplanation, RiskComponents


# Risk state thresholds (must match RiskFusionEngine defaults / config)
# These are documentation of the actual thresholds, not overrides.
STATE_THRESHOLDS = {
    "LOW": "0.00 – 0.24",
    "GUARDED": "0.25 – 0.49",
    "ELEVATED": "0.50 – 0.74",
    "HIGH": "0.75 – 1.00",
}


def _determine_primary_driver(
    attack_likelihood: float,
    anomaly_score: float,
    cls_weight: float,
    ano_weight: float,
    cls_contribution: float,
    ano_contribution: float,
) -> str:
    """
    Determines which component primarily drives the risk score.
    Returns: CLASSIFICATION | ANOMALY | BOTH | NEITHER
    """
    sig_cls = attack_likelihood >= 0.5
    sig_ano = anomaly_score >= 0.4
    if sig_cls and sig_ano:
        return "BOTH"
    if sig_cls:
        return "CLASSIFICATION"
    if sig_ano:
        return "ANOMALY"
    return "NEITHER"


def _build_risk_narrative(
    risk_state: str,
    primary_driver: str,
    attack_likelihood: float,
    anomaly_score: float,
) -> str:
    """
    Deterministic narrative template based on actual values.
    Templates are conditioned on whether conditions are actually satisfied.
    """
    if primary_driver == "BOTH":
        return (
            f"Risk is {risk_state} because both attack likelihood "
            f"({attack_likelihood:.2f}) and anomaly score ({anomaly_score:.2f}) are elevated."
        )
    if primary_driver == "CLASSIFICATION":
        return (
            f"Risk is {risk_state}, primarily driven by the supervised attack classification "
            f"(attack likelihood: {attack_likelihood:.2f}). "
            f"Anomaly score ({anomaly_score:.2f}) is below the elevated threshold."
        )
    if primary_driver == "ANOMALY":
        return (
            f"Risk is {risk_state}, primarily driven by anomalous deviation from the "
            f"benign reference (anomaly score: {anomaly_score:.2f}). "
            f"Supervised classification shows lower attack likelihood ({attack_likelihood:.2f})."
        )
    return (
        f"Current evidence remains below the elevated-risk conditions "
        f"(attack likelihood: {attack_likelihood:.2f}, anomaly score: {anomaly_score:.2f}). "
        f"Risk state is {risk_state}."
    )


def _build_velocity_narrative(
    risk_velocity: float,
    risk_acceleration: float,
    risk_trend: str,
) -> Optional[str]:
    """Deterministic trajectory narrative from actual derivative values."""
    if risk_velocity == 0.0 and risk_acceleration == 0.0:
        return None
    vel_str = f"+{risk_velocity:.4f}" if risk_velocity >= 0 else f"{risk_velocity:.4f}"
    parts = [f"Risk is {risk_trend.lower().replace('_', ' ')} at {vel_str} score units/min."]
    if abs(risk_acceleration) > 0.0:
        acc_str = f"+{risk_acceleration:.4f}" if risk_acceleration >= 0 else f"{risk_acceleration:.4f}"
        parts.append(f"Risk acceleration: {acc_str} score units/min².")
    return " ".join(parts)


def build_risk_explanation(
    risk_score: float,
    risk_state: str,
    risk_velocity: float,
    risk_acceleration: float,
    risk_trend: str,
    attack_likelihood: float,
    anomaly_score: float,
    cls_weight: float = 0.60,
    ano_weight: float = 0.40,
    eta_seconds: Optional[int] = None,
) -> RiskExplanation:
    """
    Builds risk decomposition explanation from actual engine values.
    All arithmetic is derived from the actual RiskFusionEngine formula.
    """
    cls_contribution = round(cls_weight * attack_likelihood, 4)
    ano_contribution = round(ano_weight * anomaly_score, 4)

    components = RiskComponents(
        attack_likelihood=round(attack_likelihood, 4),
        attack_likelihood_weight=cls_weight,
        attack_likelihood_contribution=cls_contribution,
        anomaly_score=round(anomaly_score, 4),
        anomaly_weight=ano_weight,
        anomaly_contribution=ano_contribution,
        combined_risk=round(risk_score, 4),
    )

    primary_driver = _determine_primary_driver(
        attack_likelihood, anomaly_score,
        cls_weight, ano_weight,
        cls_contribution, ano_contribution,
    )

    narrative = _build_risk_narrative(risk_state, primary_driver, attack_likelihood, anomaly_score)
    velocity_narrative = _build_velocity_narrative(risk_velocity, risk_acceleration, risk_trend)

    return RiskExplanation(
        risk_score=round(risk_score, 4),
        risk_state=risk_state,
        risk_velocity=round(risk_velocity, 6),
        risk_acceleration=round(risk_acceleration, 6),
        risk_trend=risk_trend,
        components=components,
        state_thresholds=STATE_THRESHOLDS,
        primary_driver=primary_driver,
        narrative=narrative,
        velocity_narrative=velocity_narrative,
        eta_seconds=eta_seconds,
    )
