# SENTRANET — Phase 5 Data Leakage & Causality Audit

This document verifies the temporal and target leakage safeguards implemented across the Phase 5 Risk Fusion and Forecasting Engine.

---

## 1. Runtime Causality & Input Boundary Isolation

- **Zero Future Feature Access:** At temporal window $T$, the `ForecastEngine` processes exclusively the row or feature vector for $T$. No forward-looking features ($T+1, \dots, T+N$) are provided or accessible.
- **Causal Rolling History:** The `RiskTrajectoryTracker` maintains historical windows strictly in backward order $[T, T-1, T-2, \dots]$. Future values cannot enter the trajectory buffer.
- **Finite Difference Computation:** Derivatives $\Delta R$, velocity $v(T)$, and acceleration $a(T)$ use exclusively backward differences referencing $T$ and $T-1$.

---

## 2. Target Label Isolation

- **Runtime Label Independence:** Ground-truth labels (`label`, `label_encoded`) are strictly excluded from runtime model execution. Even if a target column is passed in a testing DataFrame, it is filtered out prior to inference.
- **Offline Evaluation Separation:** Ground-truth attack onsets and lead times are calculated strictly inside `ForecastEvaluator` for retrospective benchmark auditing. The runtime `ForecastEngine` possesses zero access to future onset timestamps.
- **Threshold Neutrality:** Risk state boundaries (`0.24`, `0.49`, `0.74`) and emergence thresholds are configuration constants derived from architectural specifications, not optimized against test partition labels.

---

## 3. Verdict

**LEAKAGE CHECK: PASSED. Zero temporal lookahead, target contamination, or retrospective leakage.**
