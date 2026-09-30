# SENTRANET — Phase 5 Architecture Documentation

## 1. Architectural Overview

Phase 5 introduces the predictive core of **SENTRANET**, transforming the system from a static per-window IDS into a dynamic temporal attack forecasting engine.

```
                      Raw Network Traffic
                               │
                               ▼
                   Validated Temporal Features (17)
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
       Supervised Classifier         Unsupervised Detector
        (XGBoost Multi-Class)          (Isolation Forest)
                │                             │
          Attack Class                  Anomaly Score
          Probabilities                  Unusualness
                │                             │
                └──────────────┬──────────────┘
                               ▼
                       RISK FUSION ENGINE
                               │
                      Fused Risk Score & State
                               │
                               ▼
                   TEMPORAL TRAJECTORY TRACKER
                               │
                     Velocity & Acceleration
                               │
                               ▼
                    ATTACK EMERGENCE DETECTOR
                               │
                   Multi-Window Persistence Check
                               │
                               ▼
                        FORECAST ENGINE
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
          Emerging Attack               Estimated ETA
          Classification               (Time-to-Impact)
                │                             │
                └──────────────┬──────────────┘
                               ▼
                 EXTENDED DECISIONOBJECT PAYLOAD
```

---

## 2. Component Pipeline Responsibilities

1. **Feature Input Layer:** Consumes identical 17 causal numerical features without temporal lookahead or identifiers.
2. **Supervised Classification Engine (XGBoost):** Evaluates known attack resemblance (`multi:softprob`), outputting complete class probabilities ($P(\text{BENIGN}), P(\text{SCANNING}), \dots$).
3. **Unsupervised Anomaly Engine (Isolation Forest):** Evaluates deviation from learned normal baseline, outputting normalized anomaly score $A_t \in [0.0, 1.0]$.
4. **Risk Fusion Engine (`ml/risk/risk_fusion.py`):** Combines non-benign probability ($1 - P(\text{BENIGN})$) with anomaly score into unified security risk score $R_t \in [0.0, 1.0]$ and categorizes into 4 operational states (`LOW`, `GUARDED`, `ELEVATED`, `HIGH`).
5. **Temporal Trajectory Tracker (`ml/risk/risk_trajectory.py`):** Tracks rolling risk delta, first derivative (velocity per minute), second derivative (acceleration per minute$^2$), and categorizes trend (`STABLE`, `RISING`, `RAPIDLY_RISING`, `FALLING`).
6. **Attack Emergence Detector (`ml/forecast/emergence.py`):** Enforces multi-window evidence criteria (rising risk + class persistence + elevated anomaly) to suppress noisy single-window false alarms.
7. **Forecast Engine (`ml/forecast/forecast_engine.py`):** Computes time-to-impact ETA to critical risk threshold and heuristic forecast confidence.
8. **Extended DecisionObject Contract:** Produces the comprehensive, typed telemetry payload ready for future SOC streaming and automated response.
