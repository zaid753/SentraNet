"""
SENTRANET — Phase 5 Risk Fusion Unit Tests
Verifies mathematical bounds, weight configurations, edge-case behavior, and state mapping.
"""

import pytest
from ml.risk.risk_fusion import RiskFusionEngine

def test_risk_fusion_pure_benign():
    engine = RiskFusionEngine(classification_weight=0.6, anomaly_weight=0.4)
    # Pure normal: P(BENIGN) = 1.0, anomaly = 0.0
    probs = {"BENIGN": 1.0, "DDOS": 0.0, "SCANNING": 0.0, "BOTNET": 0.0, "OTHER_ATTACK": 0.0}
    risk, candidate, state = engine.calculate(probs, anomaly_score=0.0)

    assert risk == 0.0
    assert candidate == "BENIGN"
    assert state == "LOW"

def test_risk_fusion_pure_attack():
    engine = RiskFusionEngine(classification_weight=0.6, anomaly_weight=0.4)
    # High attack: P(DDOS) = 1.0, P(BENIGN) = 0.0, anomaly = 1.0
    probs = {"BENIGN": 0.0, "DDOS": 1.0, "SCANNING": 0.0, "BOTNET": 0.0, "OTHER_ATTACK": 0.0}
    risk, candidate, state = engine.calculate(probs, anomaly_score=1.0)

    assert risk == 1.0
    assert candidate == "DDOS"
    assert state == "HIGH"

def test_risk_fusion_classification_only():
    engine = RiskFusionEngine(classification_weight=0.6, anomaly_weight=0.4)
    # P(BENIGN) = 0.0, anomaly = 0.0
    probs = {"BENIGN": 0.0, "SCANNING": 0.9, "DDOS": 0.1, "BOTNET": 0.0, "OTHER_ATTACK": 0.0}
    risk, candidate, state = engine.calculate(probs, anomaly_score=0.0)

    # 0.6 * 1.0 + 0.4 * 0.0 = 0.60
    assert abs(risk - 0.60) < 1e-4
    assert candidate == "SCANNING"
    assert state == "ELEVATED"

def test_risk_fusion_anomaly_only():
    engine = RiskFusionEngine(classification_weight=0.6, anomaly_weight=0.4)
    # P(BENIGN) = 1.0 (classifier sees benign), but anomaly detector flags abnormal unusualness (1.0)
    probs = {"BENIGN": 1.0, "SCANNING": 0.0, "DDOS": 0.0, "BOTNET": 0.0, "OTHER_ATTACK": 0.0}
    risk, candidate, state = engine.calculate(probs, anomaly_score=1.0)

    # 0.6 * 0.0 + 0.4 * 1.0 = 0.40
    assert abs(risk - 0.40) < 1e-4
    assert candidate == "BENIGN"
    assert state == "GUARDED"

def test_risk_fusion_clamped_bounds():
    engine = RiskFusionEngine(classification_weight=0.6, anomaly_weight=0.4)
    probs = {"BENIGN": 0.0, "DDOS": 1.0}
    # Anomaly passed as > 1.0 or < 0.0 must be safely clamped
    risk_high, _, _ = engine.calculate(probs, anomaly_score=1.5)
    assert 0.0 <= risk_high <= 1.0

    risk_low, _, _ = engine.calculate(probs, anomaly_score=-0.5)
    assert 0.0 <= risk_low <= 1.0

def test_risk_fusion_weights_must_sum_to_one():
    with pytest.raises(ValueError, match="must sum to 1.0"):
        RiskFusionEngine(classification_weight=0.7, anomaly_weight=0.5)

def test_risk_state_boundaries():
    engine = RiskFusionEngine(classification_weight=0.6, anomaly_weight=0.4)
    assert engine.classify_state(0.00) == "LOW"
    assert engine.classify_state(0.24) == "LOW"
    assert engine.classify_state(0.25) == "GUARDED"
    assert engine.classify_state(0.49) == "GUARDED"
    assert engine.classify_state(0.50) == "ELEVATED"
    assert engine.classify_state(0.74) == "ELEVATED"
    assert engine.classify_state(0.75) == "HIGH"
    assert engine.classify_state(1.00) == "HIGH"
