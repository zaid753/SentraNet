# SENTRANET — Phase 2.5 Data Readiness Review

This document audits the data pipeline status, temporal structures, class representation, and data integrity prior to Phase 3 (Attack Classification & Dual-Model AI Core).

---

## 1. Current Dataset Summary

| Property | Value | Audit Notes |
|---|---|---|
| **Active Dataset** | `sample` | Synthetic NetFlow fixture structured with CICIDS2017 schema |
| **Source** | Local fixture generated via `scripts/generate_sample_data.py` | Strictly for pipeline and interface validation |
| **Raw Rows** | **3,502** | Flow events across ~4 simulated operational hours |
| **Clean Rows** | **3,500** | 2 duplicate records removed during cleaning |
| **Temporal Windows** | **204** | Grouped into 60-second non-overlapping buckets ($T = 60\text{s}$) |
| **Model Features** | **17** | Normalized numerical behavioral and rolling features |

---

## 2. BENIGN Class Investigation

### Findings:
1. **Raw Level:** BENIGN traffic is present in the raw sample data (~50% of raw flow events).
2. **Window Level Analysis:** 
   - Previously, BENIGN windows fell to 0 because the window label aggregator applied a strict `if len(attack_labels) > 0` condition, meaning that even a single stray attack flow in a window of 20 benign flows converted the whole window to an attack label. Furthermore, random sampling without temporal clustering meant attack flows were uniformly scattered across all minutes.
3. **Pipeline Fix & Resolution:**
   - Updated `TemporalWindowAggregator` to evaluate the attack proportion (`attack_threshold = 0.35`). When attack activity is below the threshold, the window remains `BENIGN`.
   - Structured the sample generator into realistic operational cycles (alternating between normal business baseline, scanning probes, DDoS surges, and botnet activity).
4. **Current Status:**
   - **`BENIGN` is present and active**: **96 windows (47.1% of all windows)**.
   - Training split contains **76 BENIGN windows**, Validation contains **20 BENIGN windows**.

---

## 3. Timestamp Provenance Audit

- **Classification:** **Synthetic / Generated Timestamps** (Category B).
- **Source:** Generated programmatically by `scripts/generate_sample_data.py` starting from `2026-09-30 08:00:00` with Poisson/exponential inter-arrival distributions.
- **Integrity Rule:** These timestamps validate pipeline mechanics (sorting, windowing, rolling lookbacks, chronological splitting), but **must not be used to claim real-world attack lead-time or forecasting accuracy**. Real temporal performance must be evaluated on real benchmark captures (CICIDS2017 / UNSW-NB15).

---

## 4. Real Benchmark Dataset Availability

- **Inspection Target:** `data/raw/` (`cicids2017/`, `unsw_nb15/`, `cic_ddos2019/`).
- **Inspection Result:** **Benchmark dataset not available locally.**
- **Status:** The modular adapters (`CICIDS2017Loader`, `UNSWNB15Loader`, `CICDDoS2019Loader`) and `DatasetRegistry` are implemented and validated. Once real CSV/PCAP partitions are downloaded into `data/raw/<dataset>/`, the pipeline can process them immediately without code changes.

---

## 5. Feature & Leakage Status

- **Feature Count:** Exactly 17 numerical model inputs.
- **NaNs / Infs:** Exactly 0 across all partitions.
- **Scaling Isolation:** `StandardScaler` is fitted **exclusively on the training split** (first 70% chronologically). Validation and test sets are transformed without updating scaler statistics.
- **Rolling Features:** Causal 5-window lookback ($K = 5$) references only $[T-4, T]$. Zero future leakage.
- **Chronological Split:**
  - **Train:** `08:00:00` to `10:21:00` (142 windows)
  - **Validation:** `10:22:00` to `10:52:00` (31 windows)
  - **Test:** `10:53:00` to `11:23:00` (31 windows)
  - No temporal overlap between partitions.

---

## 6. Current Limitations

1. **Synthetic Data Constraint:** The pipeline has been validated on a high-fidelity synthetic fixture. Reported ML metrics derived from this sample represent functional verification of the pipeline, not empirical network defense capability.
2. **Local Storage Constraint:** Gigabyte-scale PCAP archives are not bundled in Git to adhere to repository hygiene.

---

## 7. Phase 3 Readiness Verdict

| Requirement | Status |
|---|---|
| BENIGN Baseline Representation | **VERIFIED** (47.1% of windows) |
| Multi-Class Attack Coverage | **VERIFIED** (DDOS, SCANNING, BOTNET, OTHER_ATTACK) |
| Zero Data Leakage | **VERIFIED** (Fit on train only, strict chronological split) |
| Serialized Pipeline Artifacts | **SAVED** (`scaler.joblib`, `label_encoder.joblib`, `schema.json`) |
| Real Benchmark Integration Ready | **READY** (Adapters implemented in `ml/data/`) |

**Ready for Phase 3 Architecture Initialization:** We can proceed to construct the Phase 3 dual-model architecture (XGBoost Attack Classifier + Isolation Forest Anomaly Detector interfaces and evaluation harness).
