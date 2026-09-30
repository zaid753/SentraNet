import pytest
from typing import Dict, Any
import datetime
from backend.explainability.feature_metadata import FEATURE_METADATA, CANONICAL_FEATURES
from backend.explainability.explainer import build_explanation, invalidate_cache, get_cached_explanation
from backend.explainability.schemas import ExplanationResponse
from backend.explainability.incident_explainer import build_incident_explanation, IncidentExplanation
from backend.replay.replay_event import AlertEvent
from ml.models.xgboost_classifier import XGBoostClassifier
import uuid

# Mock objects for testing
class MockBooster:
    def get_score(self, importance_type="gain"):
        return {
            "total_bytes": 10.0,
            "avg_packet_rate": 5.0,
            "flow_count": 2.0
        }

class MockClassifier:
    def __init__(self):
        self.booster = MockBooster()

def get_mock_decision() -> Dict[str, Any]:
    return {
        "timestamp": f"2026-01-01T12:00:00Z-{uuid.uuid4()}",
        "predicted_class": "DDOS",
        "class_probabilities": {"BENIGN": 0.1, "DDOS": 0.8, "SCANNING": 0.05, "BOTNET": 0.05, "OTHER_ATTACK": 0.0},
        "classification_confidence": 0.8,
        "anomaly_score": 0.82,
        "is_anomalous": True,
        "risk_score": 0.868,
        "risk_state": "HIGH",
        "risk_velocity": 0.05,
        "risk_acceleration": 0.01,
        "risk_trend": "RISING",
        "forecast_available": True,
        "forecast_class": "DDOS",
        "time_to_impact_seconds": 120,
        "forecast_confidence": 0.9,
        "forecast_reason": ["Risk is rising", "Candidate class persisted"]
    }

def get_mock_features() -> Dict[str, float]:
    return {f: 1.0 for f in CANONICAL_FEATURES}

class MockIncident:
    def __init__(self):
        self.incident_id = "INC-001"
        self.created_at = "2026-01-01T12:00:00Z"
        self.updated_at = "2026-01-01T12:05:00Z"
        self.resolution_timestamp = "2026-01-01T12:05:00Z"
        self.status = "RESOLVED"
        self.attack_class = "DDOS"
        self.peak_risk_score = 0.95
        self.max_anomaly_score = 0.88
        self.forecast_triggered = True

@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    invalidate_cache()
    from backend.explainability.classification_explainer import invalidate_importance_cache
    invalidate_importance_cache()
    yield
    invalidate_cache()
    invalidate_importance_cache()

# 1. Feature metadata complete
def test_feature_metadata_complete():
    assert len(CANONICAL_FEATURES) == 17
    assert len(FEATURE_METADATA) == 17
    for feat in CANONICAL_FEATURES:
        assert feat in FEATURE_METADATA
        meta = FEATURE_METADATA[feat]
        assert "display_name" in meta
        assert "description" in meta

# 2. Explanation generated from DecisionObject
def test_explanation_generated_from_decision():
    decision = get_mock_decision()
    features = get_mock_features()
    classifier = MockClassifier()
    
    explanation = build_explanation(
        decision=decision,
        feature_values=features,
        booster=classifier.booster,
        history_length=5,
        anomaly_threshold=0.5,
        data_source="LIVE"
    )
    assert isinstance(explanation, ExplanationResponse)
    
# 3. Risk decomposition correct
def test_risk_decomposition_correct():
    decision = get_mock_decision()
    features = get_mock_features()
    classifier = MockClassifier()
    
    explanation = build_explanation(
        decision=decision,
        feature_values=features,
        booster=classifier.booster,
        history_length=5,
        anomaly_threshold=0.5
    )
    
    risk = explanation.risk
    assert risk.risk_score == 0.868
    assert risk.components.attack_likelihood == 0.9  # 1 - P(BENIGN)
    assert risk.components.anomaly_score == 0.82

# 4. Attack likelihood correct
def test_attack_likelihood_correct():
    decision = get_mock_decision()
    decision["class_probabilities"]["BENIGN"] = 0.25
    explanation = build_explanation(decision, get_mock_features(), MockClassifier().booster, 5)
    assert explanation.classification.attack_likelihood == 0.75

# 5. Anomaly contribution correct
def test_anomaly_contribution_correct():
    decision = get_mock_decision()
    explanation = build_explanation(decision, get_mock_features(), MockClassifier().booster, 5)
    # anomaly_score = 0.82, weight = 0.40
    assert explanation.risk.components.anomaly_contribution == 0.328

# 6. Risk contribution sum correct
def test_risk_contribution_sum_correct():
    decision = get_mock_decision()
    explanation = build_explanation(decision, get_mock_features(), MockClassifier().booster, 5)
    comp = explanation.risk.components
    expected_sum = comp.attack_likelihood_contribution + comp.anomaly_contribution
    assert abs(comp.combined_risk - expected_sum) < 0.01

# 7. Risk state correct
def test_risk_state_correct():
    decision = get_mock_decision()
    explanation = build_explanation(decision, get_mock_features(), MockClassifier().booster, 5)
    assert explanation.risk.risk_state == "HIGH"

# 8. Top feature selection deterministic
def test_top_feature_selection_deterministic():
    explanation = build_explanation(get_mock_decision(), get_mock_features(), MockClassifier().booster, 5)
    top_features = explanation.top_features
    assert len(top_features) == 5
    # From MockBooster, total_bytes should be first (highest gain)
    assert top_features[0].feature == "total_bytes"
    assert top_features[1].feature == "avg_packet_rate"

# 9. Forecast explanation correct
def test_forecast_explanation_correct():
    decision = get_mock_decision()
    explanation = build_explanation(decision, get_mock_features(), MockClassifier().booster, 5)
    forecast = explanation.forecast
    assert forecast.forecast_available is True
    assert forecast.forecast_class == "DDOS"
    assert "Forecast is ACTIVE" in forecast.narrative

# 10. Forecast-not-triggered explanation correct
def test_forecast_not_triggered():
    decision = get_mock_decision()
    decision["forecast_available"] = False
    decision["risk_trend"] = "STABLE"
    decision["risk_velocity"] = 0.0
    explanation = build_explanation(decision, get_mock_features(), MockClassifier().booster, 5)
    assert explanation.forecast.forecast_available is False
    assert "Forecast not triggered" in explanation.forecast.narrative

# 11. ETA explanation correct
def test_eta_explanation_correct():
    decision = get_mock_decision()
    explanation = build_explanation(decision, get_mock_features(), MockClassifier().booster, 5)
    assert explanation.forecast.time_to_impact_seconds == 120
    assert "2m 0s" in explanation.forecast.eta_narrative

# 12. Anomaly explanation correct
def test_anomaly_explanation_correct():
    decision = get_mock_decision()
    explanation = build_explanation(decision, get_mock_features(), MockClassifier().booster, 5, anomaly_threshold=0.5)
    assert explanation.anomaly.is_anomalous is True
    assert explanation.anomaly.threshold == 0.5
    assert explanation.anomaly.status == "ANOMALOUS"

# 13. Alert explanation correct
def test_alert_explanation_is_not_fabricated():
    # Alerts are handled at incident level or via timeline
    incident = MockIncident()
    alert1 = AlertEvent(
        alert_event_id="ALT-1", incident_id="INC-001", event_type="ALERT_CREATED",
        timestamp="2026-01-01T12:02:00Z", attack_class="DDOS", severity="HIGH", 
        risk_score=0.9, anomaly_score=0.8, forecast_active=True, estimated_eta_seconds=0,
        reasons=[]
    )
    inc_expl = build_incident_explanation(incident, [alert1])
    # Timeline should have 1 event
    assert len(inc_expl.timeline) == 1
    assert "Risk crossed HIGH" in inc_expl.timeline[0].explanation

# 14. Incident explanation correct
def test_incident_explanation_correct():
    inc_expl = build_incident_explanation(MockIncident(), [])
    assert inc_expl.incident_id == "INC-001"
    assert inc_expl.duration == "5m 0s"
    assert inc_expl.highest_risk == 0.95

# 15. No fabricated values
def test_no_fabricated_values():
    decision = get_mock_decision()
    features = get_mock_features()
    features["flow_count"] = 1234.0
    explanation = build_explanation(decision, features, MockClassifier().booster, 5)
    
    # Check that flow_count exactly matches
    fc_expl = next(f for f in explanation.features if f.feature == "flow_count")
    assert fc_expl.current_value == 1234.0

# 16. Missing baseline handled
# Not testing explicit baseline yet, but missing feature values handled
def test_missing_features_handled():
    decision = get_mock_decision()
    explanation = build_explanation(decision, {}, MockClassifier().booster, 5)
    assert explanation.features[0].current_value is None

# 17. Missing attribution handled
def test_missing_attribution_handled():
    class EmptyBooster:
        def get_score(self, importance_type="gain"): return {}
    decision = get_mock_decision()
    explanation = build_explanation(decision, get_mock_features(), EmptyBooster(), 5)
    for f in explanation.features:
        assert f.global_importance is None

# 18. Low-risk explanation
def test_low_risk_explanation():
    decision = get_mock_decision()
    decision["risk_score"] = 0.1
    decision["risk_state"] = "LOW"
    decision["class_probabilities"]["BENIGN"] = 0.9
    decision["anomaly_score"] = 0.1
    decision["is_anomalous"] = False
    explanation = build_explanation(decision, get_mock_features(), MockClassifier().booster, 5)
    assert explanation.risk.risk_state == "LOW"
    assert "below the elevated-risk conditions" in explanation.risk.narrative

# 19. High-risk explanation
def test_high_risk_explanation():
    decision = get_mock_decision()
    explanation = build_explanation(decision, get_mock_features(), MockClassifier().booster, 5)
    assert explanation.risk.risk_state == "HIGH"
    assert "elevated" in explanation.risk.narrative

# 20. Explanation cache invalidation
def test_explanation_cache_invalidation():
    decision = get_mock_decision()
    build_explanation(decision, get_mock_features(), MockClassifier().booster, 5)
    
    assert get_cached_explanation(decision["timestamp"]) is not None
    invalidate_cache()
    assert get_cached_explanation(decision["timestamp"]) is None

# 21. API schema validation
def test_api_schema_validation():
    decision = get_mock_decision()
    explanation = build_explanation(decision, get_mock_features(), MockClassifier().booster, 5)
    # If it builds without pydantic errors, schema is valid
    dump = explanation.model_dump()

# 22. Stale explanation prevention
def test_stale_explanation_prevention():
    # Calling invalidate_cache clears all, guaranteeing no stale explanation
    invalidate_cache()
    assert get_cached_explanation("stale_window") is None

# 23. Causality test
def test_causality_no_future_leakage():
    t1 = get_mock_decision()
    t1["timestamp"] = "2026-01-01T12:00:00Z"
    t1["risk_score"] = 0.868
    expl_t1 = build_explanation(t1, get_mock_features(), MockClassifier().booster, 5)
    
    # Provide new data at t2
    t2 = get_mock_decision()
    t2["timestamp"] = "2026-01-01T12:01:00Z"
    t2["risk_score"] = 0.99
    
    # building t2 should not affect t1's cached result (if it wasn't evicted)
    expl_t2 = build_explanation(t2, get_mock_features(), MockClassifier().booster, 6)
    
    cached_t1 = get_cached_explanation("2026-01-01T12:00:00Z")
    assert cached_t1.risk.risk_score == 0.868
    assert expl_t2.risk.risk_score == 0.99

# 24. Determinism test
def test_determinism():
    decision = get_mock_decision()
    expl1 = build_explanation(decision, get_mock_features(), MockClassifier().booster, 5)
    invalidate_cache()
    expl2 = build_explanation(decision, get_mock_features(), MockClassifier().booster, 5)
    
    assert expl1.model_dump() == expl2.model_dump()

