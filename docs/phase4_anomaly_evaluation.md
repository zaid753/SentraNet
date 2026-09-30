# SENTRANET — Phase 4 Isolation Forest Anomaly Evaluation Report

## 1. Experimental Overview

> [!IMPORTANT]
> **Scientific Honesty Statement:**  
> The current development results are based on a **Category B: Synthetic / Generated test fixture** and **must not be presented as benchmark performance on CICIDS2017, UNSW-NB15, or CIC-DDoS2019.**  
> The Isolation Forest was trained strictly on **BENIGN** windows from the training partition. Attack labels were used solely for post-hoc evaluation.

- **Model Type:** Scikit-Learn `IsolationForest` (`n_estimators=300`, `contamination='auto'`)
- **Feature Count:** 17 identical model features
- **Training Dataset:** `data/processed/sample/train.parquet`
- **Total Training Windows:** 142
- **Benign Training Windows:** 76 (53.52%)
- **Scaling:** Frozen `SafeFeatureScaler` (StandardScaler) fitted in Phase 2 on the training set

---

## 2. Anomaly Score Normalization Contract

```
Isolation Forest raw score s = decision_function(x)
                     │
                     ▼
Piecewise Linear Two-Span Clamping:
   anomaly_score = clip((s_high - s) / (s_high - s_low), 0.0, 1.0)
                     │
                     ▼
      0.0 ─────────────────────── 1.0
   deep normal                 anomalous
```

### Reference Calibration Parameters (Derived Exclusively from Benign Train):
- **$s_{high}$ (Max Benign Baseline):** `0.1056` $\rightarrow$ Normalizes to `0.0000`
- **$s_{min}$ (Min Benign Baseline):** `-0.0717` $\rightarrow$ Normalizes to `0.5000`
- **Span $\Delta = s_{high} - s_{min}$:** `0.1773`
- **$s_{low} = s_{min} - \Delta$ (Extreme Outlier Anchor):** `-0.2489` $\rightarrow$ Normalizes to `1.0000`

### Threshold Selection Strategy:
- **Selected Anomaly Threshold $\tau$:** `0.4978`
- **Methodology:** Quantile 0.99 ($P_{99}$) of the normalized benign training score distribution.
- **Label Usage:** `label_usage_for_threshold = false`. Strictly zero attack label usage.

---

## 3. Post-Hoc Anomaly Score Distribution Across Partitions

| Partition | Label | Count | Mean Score | Median Score | P95 Score | Anomalous Flag Rate ($\ge \tau$) |
|---|---|---|---|---|---|---|
| **Train** | `BENIGN` | 76 | 0.1819 | 0.1345 | 0.4525 | 1.3% |
| **Train** | `BOTNET` | 18 | 0.2524 | 0.2351 | 0.3529 | 0.0% |
| **Train** | `DDOS` | 24 | 0.5916 | 0.5993 | 0.6790 | 91.7% |
| **Train** | `SCANNING` | 24 | 0.7942 | 0.8007 | 0.8630 | 100.0% |
| **Validation** | `BENIGN` | 20 | 0.2123 | 0.2046 | 0.3863 | 0.0% |
| **Validation** | `SCANNING` | 11 | 0.7862 | 0.7945 | 0.8475 | 100.0% |
| **Test** | `DDOS` | 18 | 0.6049 | 0.5922 | 0.7052 | 100.0% |
| **Test** | `SCANNING` | 13 | 0.7624 | 0.7966 | 0.8258 | 100.0% |

---

## 4. Binary Separation Performance (Benign vs Attack)

| Partition | ROC-AUC | PR-AUC | Precision | Recall | False Positive Rate |
|---|---|---|---|---|---|
| **Train** | 0.9211 | 0.9253 | 0.9787 | 0.6970 | 1.32% |
| **Validation** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.00% |
| **Test** | N/A (single class) | N/A (single class) | 1.0000 | 1.0000 | 0.00% |

---

## 5. False-Positive & Anomaly Interpretation

- **Benign False-Positive Rate:** In validation, benign traffic produced a 0.00% false-positive rate under the $P_{99}$ threshold (maximum validation benign score was 0.4735 < 0.4978).
- **Attack Detection:** 100% of validation SCANNING, 100% of test DDOS, and 100% of test SCANNING windows exceeded the threshold.
- **Security Distinction:** An observation flagged as `is_anomalous = true` denotes behavioral deviation, not necessarily a cyber attack.
