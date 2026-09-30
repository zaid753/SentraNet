# SENTRANET — Phase 3 Model Evaluation Report

## 1. Experimental Overview

> [!IMPORTANT]
> **Scientific Honesty Statement:**  
> The current development results are based on a **synthetic/generated test fixture (Category B)** and **must not be presented as benchmark performance on CICIDS2017, UNSW-NB15, or CIC-DDoS2019.**

- **Model Type:** XGBoost Multi-Class Classifier (`multi:softprob`)
- **Number of Classes:** 5
- **Input Features:** 17 numerical flow attributes
- **Sample Weighting Strategy:** `compute_sample_weight("balanced", y_train)`
- **Dataset Partition Sizes:**
  - Training Split: 142 temporal windows
  - Validation Split: 31 temporal windows
  - Test Split: 31 temporal windows

---

## 2. Validation Metrics
- **Macro F1 Score:** 0.9654
- **Weighted F1 Score:** 0.968
- **Multi-class Log Loss:** 0.0981
- **Reference Accuracy:** 0.9677

---

## 3. Test Evaluation Metrics
- **Macro F1 Score:** 1.0
- **Weighted F1 Score:** 1.0
- **Macro PR-AUC:** 1.0 (Evaluated across 2/5 valid binary classes)
- **Multi-class Log Loss:** 0.073
- **Reference Accuracy:** 1.0

---

## 4. Per-Class Test Performance

| Class Name | Ground Truth Count | Predicted Count | Precision | Recall | F1-Score | Status |
|---|---|---|---|---|---|---|
| **BENIGN** | 0 | 0 | N/A | N/A | N/A | class_absent_in_ground_truth |
| **BOTNET** | 0 | 0 | N/A | N/A | N/A | class_absent_in_ground_truth |
| **DDOS** | 18 | 18 | 1.0000 | 1.0000 | 1.0000 | evaluated |
| **OTHER_ATTACK** | 0 | 0 | N/A | N/A | N/A | class_absent_in_ground_truth |
| **SCANNING** | 13 | 13 | 1.0000 | 1.0000 | 1.0000 | evaluated |

---

## 5. Confusion Matrix Observations
- Complete 5x5 confusion matrix persisted in `reports/phase3_confusion_matrix.json` and rendered in `reports/phase3_confusion_matrix.png`.
- The axes preserve all canonical classes (`BENIGN`, `DDOS`, `SCANNING`, `BOTNET`, `OTHER_ATTACK`).

---

## 6. Limitations & Next Steps
- Real benchmark validation on actual CICIDS2017 captures will be performed once raw dumps are placed into `data/raw/`.
- Phase 4 will introduce unsupervised anomaly detection (Isolation Forest) and risk fusion.
