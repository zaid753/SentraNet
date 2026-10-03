# CIC-IDS2017 Feature Contract & Dataset Coverage Audit

## A. Training Dataset Audit
- **Training Dataset**: `data/processed/sample/train.parquet` (Synthetically generated)
- **Training Samples**: 415,820 windows
- **Label Distribution**:
  - BENIGN: 207,816
  - DDOS: 104,188
  - BOTNET: 51,927
  - SCANNING: 51,889
- **Scaler Used**: `StandardScaler` (`data/processed/sample/artifacts/scaler.joblib`)

## B. CIC-IDS2017 Audit (Friday Morning)
- **Dataset**: `data/processed/cicids2017/Friday-WorkingHours-Morning.parquet`
- **Windows**: 241
- **Label Distribution**: BOTNET (163), BENIGN (78)

## C. 17-Feature Comparison (Synthetic vs CIC-IDS2017)
The structural shift in scale is extreme. Examples:
- **`flow_count`**: Synthetic (Mean 10.3, Max 16) vs CIC (Mean 216.5, Max 1066.0)
- **`avg_packet_rate`**: Synthetic (Mean 50.4, Max 234.0) vs CIC (Mean 131,234.8, Max 448,590,929.0)
- **`total_bytes`**: Synthetic (Mean 32,804) vs CIC (Mean 18,296,878)
- **`syn_flag_count`**: Synthetic (Mean 1.9) vs CIC (Mean 206.8)

## D. Semantic Compatibility
- **Unit and Type Match**: MATCH. Both pipelines use the exact same `WindowAggregator` which enforces identical 60-second temporal windows, rolling-5 history logic, and mathematical aggregation.
- **Domain Scale Match**: MISMATCH. Synthetic traffic was modeled on a low-volume micro-network or single endpoint, whereas CIC-IDS2017 represents a high-volume aggregation point (full switch/tap).

## E. Scaler Analysis
- **Scaler Type**: `StandardScaler` (fitted without feature names).
- **Transformation Outcome**: The scaler strictly normalizes values based on the synthetic training distribution (mean ≈ 0, std ≈ 1).
- **CIC-IDS2017 Transformed Ranges**:
  - `avg_packet_rate` transformed max is **57,946,269.0** (expected ~3.0).
  - `avg_byte_rate` transformed max is **958,029.0**.
  - `flow_count` transformed max is **982.8**.
- **Conclusion**: CIC-IDS2017 feature values fall violently outside the standardized distribution that the XGBoost model and Isolation Forest expect.

## F. Model Input Verification
- **Exact Path Verified**: CSV Flows → `WindowAggregator` (identically shaped 17 features) → `StandardScaler` (identically ordered via list iteration) → `XGBoost/IsolationForest`.
- **Finding**: There is no accidental column permutation, NaN injection, or type mismatch. The pipeline structure is perfectly preserved. The mathematical values simply explode post-scaling due to distribution shift.

## G. Label Coverage
CIC-IDS2017 provides 8 traffic capture files totaling **3,119,345 flow records**.
- `Monday-WorkingHours`: BENIGN
- `Tuesday-WorkingHours`: BENIGN, FTP-Patator, SSH-Patator (OTHER_ATTACK)
- `Wednesday-workingHours`: BENIGN, DoS Hulk, DoS slowloris, DoS Slowhttptest, DoS GoldenEye (DDOS), Heartbleed (OTHER_ATTACK)
- `Thursday-WorkingHours-Morning-WebAttacks`: BENIGN, Web Attacks (OTHER_ATTACK)
- `Thursday-WorkingHours-Afternoon-Infilteration`: BENIGN, Infiltration (OTHER_ATTACK)
- `Friday-WorkingHours-Morning`: BENIGN, Bot (BOTNET)
- `Friday-WorkingHours-Afternoon-PortScan`: BENIGN, PortScan (SCANNING)
- `Friday-WorkingHours-Afternoon-DDos`: BENIGN, DDoS (DDOS)

**Conclusion**: Friday Morning is **NOT** representative of all attack classes. It only contains `Bot` (Botnet) and `BENIGN`. The full CIC dataset comprehensively covers all SENTRANET categories.

## H. Temporal Coverage
- **Temporal Windows**: Spans 5 distinct working days (Monday - Friday) with clear chronological boundaries per day. Millions of flows map into thousands of dense 60-second temporal windows.

## I. Root-Cause Evidence
**Why does XGBoost predict everything as SCANNING?**
- **Evidence**: Extreme out-of-distribution feature scaling (Domain Shift). Decision tree splits (thresholds) in the frozen XGBoost model were learned on synthetic values bounded tightly between -3 and +3. Transformed CIC-IDS2017 features route to values in the tens of millions, driving every single leaf traversal into an extreme edge case node (which happens to be `SCANNING` in the current synthetic model topology).

**Why is Isolation Forest 100% Anomalous?**
- **Evidence**: The Isolation Forest computes anomaly scores based on path lengths in random trees fit on the synthetic data. A transformed feature value of `57,000,000` is immediately partitioned near the root of every tree, yielding an extremely short path length. Consequently, the model flags 100% of the windows as severe anomalies, regardless of whether they are BENIGN or ATTACK.

## J. Final Classification
**C. FEATURE CONTRACT COMPATIBLE BUT MAJOR DOMAIN SHIFT**

## K. Recommended Next Action
Do NOT modify the feature schemas, `WindowAggregator`, or frontend. The pipeline integration is structurally sound.
**Recommendation**: Retrain the ML models (XGBoost & Isolation Forest) and refit the `StandardScaler` natively on the comprehensive CIC-IDS2017 dataset to align the learned weights with real-world network traffic distributions.
