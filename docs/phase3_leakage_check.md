# SENTRANET — Phase 3 Data Leakage & Integrity Verification

This report documents the safeguards preventing data leakage throughout Phase 3 training.

## 1. Preprocessing Isolation
- `SafeFeatureScaler` (StandardScaler) was **fitted exclusively on the training split** (first 70% chronologically).
- Validation and test splits were transformed using frozen parameters $\mu$ and $\sigma$ learned from train.
- Scaler artifact: `data/processed/sample/artifacts/scaler.joblib`.

## 2. Feature Filtering & Privacy Safety
- Identifiers (`source_ip`, `destination_ip`) are **strictly excluded** from the input feature vector.
- Temporal sequence markers (`timestamp`, `window_id`, `window_start`, `window_end`) are excluded from model inputs.
- Ground truth target labels (`label`, `original_label`, `label_encoded`) are excluded from $X$.

## 3. Temporal Causality & Window Independence
- Chronological splitting:
  - Train: `08:00:00` to `10:21:00`
  - Validation: `10:22:00` to `10:52:00`
  - Test: `10:53:00` to `11:23:00`
  - Overlap: **0 seconds**.
- Rolling features ($K = 5$) at time $T$ reference only $[T-4, T]$. No future windows are referenced.

## Verdict
**LEAKAGE CHECK: PASSED. Zero temporal or target contamination present.**
