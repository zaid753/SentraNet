# Phase 11: Explainability and SOC Analyst Experience

## Overview
Phase 11 adds a critical explainability layer to the SENTRANET pipeline. Given the high stakes of AI-driven cybersecurity incident response, the system must justify its risk classifications, anomalous detections, and predictive forecasts using grounded, observable telemetry data. 

We do not use hallucinatory generative models (LLMs) to invent evidence. Instead, the explainer interrogates the underlying XGBoost model's actual gain weights and decomposing the temporal risk fusion math deterministically.

## Architecture & Integration

The explainability module intercepts decisions coming out of the `SentranetService`. 
When the chronological pipeline executes a window:
1. `SentranetService` stores the `latest_decision` and `latest_features` locally (protected by `threading.Lock`).
2. The UI queries `GET /api/explanations/current` continuously (every 5 seconds).
3. The `Explainer` module extracts SHAP-like model-native gain from the active XGBoost booster and normalizes it to provide deterministic feature importance.
4. The Risk Engine's mathematical boundaries are introspected to justify precisely *why* a threat escalated (e.g., Anomaly contribution vs. Classification contribution).
5. The `ExplanationResponse` is cached in a thread-safe LRU mechanism (`@lru_cache`) to prevent redundant computation across clients.

## Key Components

### Backend Explainers
*   `explainer.py`: The root orchestrator that constructs `ExplanationResponse` schemas. Contains thread-safe caching.
*   `classification_explainer.py`: Queries XGBoost native `gain` for the `booster`.
*   `risk_explainer.py`: Decomposes risk formulas `risk = clip(0.60 * class_prob + 0.40 * anomaly_score, 0, 1)`.
*   `forecast_explainer.py`: Evaluates risk trajectory, velocity, and trend to explain the emergence trigger.
*   `incident_explainer.py`: Compiles an overarching `IncidentExplanation` that summarizes the lifecycle of an entire incident, providing a narrative summary based on actual transition states.

### APIs Exposed
*   `GET /api/explanations/current`: Detailed explanation of the live or replayed streaming window.
*   `GET /api/explanations/window/{window_id}`: Look up historical window explanations.
*   `GET /api/incidents/{incident_id}/explanation`: Retrieve a full narrative summary of a correlated incident.

### Frontend Enhancements
*   `ExplanationPanel.tsx`: A live view attached to the main dashboard. Shows:
    *   **RiskBreakdownCard**: Visualizes the math behind the risk score.
    *   **ForecastEvidenceCard**: Details why the predictive engine triggered.
    *   **TopSignalsCard**: Bar charts mapping the real-time feature contributions against the AI's classification.
*   `IncidentDetailModal.tsx`: Redesigned with tabs (OVERVIEW, EVIDENCE, RISK, FORECAST, TIMELINE) for deep-dive post-mortem investigations.

## Testing Integrity
The explainability layer is verified by a comprehensive 24-test suite (`tests/test_explainability.py`) enforcing:
*   No future leakage (chronological state separation).
*   No fabricated/hallucinated telemetry values (values must match canonical features strictly).
*   Correct risk math decomposition bounds.
*   Determinism across cache evictions.

All 178 system tests pass.
