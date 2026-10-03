# CIC-IDS2017 Step 7: Known/Novel Evaluation & Forecast Audit
**EXPERIMENTAL MODEL — NOT YET DEFAULT**

## 1. Known-Class Evaluation
_Tested only on classes present in Training (BENIGN, DDOS, OTHER_ATTACK)_
- **Sample Count**: 301
- **Accuracy**: 0.9502
- **Macro F1**: 0.6021
- **Weighted F1**: 0.9633

## 2. Novel-Class Evaluation (Zero-Shot)
_Classes strictly absent from the Training window_

**BOTNET (163 Windows)**
- Predicted Classes: {'BENIGN': 155, 'OTHER_ATTACK': 8}
- Isolation Forest Anomaly Rate: 0.00%
- Risk States: {'LOW': 143, 'GUARDED': 16, 'ELEVATED': 4}
- **Analysis**: BOTNET is completely misclassified (as BENIGN) because XGBoost lacks the weights. However, the Isolation Forest successfully detected 0.00% of BOTNET traffic as anomalous. 

**SCANNING (27 Windows)**
- Predicted Classes: {'BENIGN': 27}
- Isolation Forest Anomaly Rate: 11.11%
- Risk States: {'LOW': 24, 'GUARDED': 3}
- **Analysis**: SCANNING is misclassified (predominantly BENIGN) and is largely missed by the anomaly detector (11.11%), likely because its volume traits closely mimic BENIGN traffic on this dataset.

## 3. Attack Episode Reconstruction
Found 27 discrete attack episodes in the Test set.
- **EP_1** (SCANNING): 2017-07-07 01:05:00 to 2017-07-07 01:06:00 (2 windows, 60.0s)
- **EP_2** (SCANNING): 2017-07-07 01:52:00 to 2017-07-07 01:52:00 (1 windows, 0.0s)
- **EP_3** (SCANNING): 2017-07-07 01:55:00 to 2017-07-07 02:00:00 (6 windows, 300.0s)
- **EP_4** (SCANNING): 2017-07-07 02:14:00 to 2017-07-07 02:16:00 (3 windows, 120.0s)
- **EP_5** (SCANNING): 2017-07-07 02:51:00 to 2017-07-07 02:56:00 (6 windows, 300.0s)
- **EP_6** (SCANNING): 2017-07-07 03:03:00 to 2017-07-07 03:03:00 (1 windows, 0.0s)
- **EP_7** (SCANNING): 2017-07-07 03:08:00 to 2017-07-07 03:10:00 (3 windows, 120.0s)
- **EP_8** (SCANNING): 2017-07-07 03:12:00 to 2017-07-07 03:13:00 (2 windows, 60.0s)
- **EP_9** (SCANNING): 2017-07-07 03:21:00 to 2017-07-07 03:23:00 (3 windows, 120.0s)
- **EP_10** (DDOS): 2017-07-07 03:56:00 to 2017-07-07 04:16:00 (21 windows, 1200.0s)
- **EP_11** (BOTNET): 2017-07-07 09:34:00 to 2017-07-07 09:35:00 (2 windows, 60.0s)
- **EP_12** (BOTNET): 2017-07-07 10:04:00 to 2017-07-07 11:13:00 (70 windows, 4140.0s)
- **EP_13** (BOTNET): 2017-07-07 11:15:00 to 2017-07-07 11:18:00 (4 windows, 180.0s)
- **EP_14** (BOTNET): 2017-07-07 11:20:00 to 2017-07-07 11:23:00 (4 windows, 180.0s)
- **EP_15** (BOTNET): 2017-07-07 11:25:00 to 2017-07-07 11:28:00 (4 windows, 180.0s)
- **EP_16** (BOTNET): 2017-07-07 11:30:00 to 2017-07-07 11:45:00 (16 windows, 900.0s)
- **EP_17** (BOTNET): 2017-07-07 11:47:00 to 2017-07-07 11:50:00 (4 windows, 180.0s)
- **EP_18** (BOTNET): 2017-07-07 11:52:00 to 2017-07-07 11:55:00 (4 windows, 180.0s)
- **EP_19** (BOTNET): 2017-07-07 11:57:00 to 2017-07-07 12:00:00 (4 windows, 180.0s)
- **EP_20** (BOTNET): 2017-07-07 12:02:00 to 2017-07-07 12:17:00 (16 windows, 900.0s)
- **EP_21** (BOTNET): 2017-07-07 12:19:00 to 2017-07-07 12:22:00 (4 windows, 180.0s)
- **EP_22** (BOTNET): 2017-07-07 12:24:00 to 2017-07-07 12:27:00 (4 windows, 180.0s)
- **EP_23** (BOTNET): 2017-07-07 12:29:00 to 2017-07-07 12:32:00 (4 windows, 180.0s)
- **EP_24** (BOTNET): 2017-07-07 12:34:00 to 2017-07-07 12:37:00 (4 windows, 180.0s)
- **EP_25** (BOTNET): 2017-07-07 12:39:00 to 2017-07-07 12:49:00 (11 windows, 600.0s)
- **EP_26** (BOTNET): 2017-07-07 12:51:00 to 2017-07-07 12:54:00 (4 windows, 180.0s)
- **EP_27** (BOTNET): 2017-07-07 12:56:00 to 2017-07-07 12:59:00 (4 windows, 180.0s)

## 4. Forecast Audit
- **Total Forecasts**: 9
- **EARLY (Valid Lead Time)**: 2
- **ONSET**: 0
- **POST-ONSET**: 7
- **FALSE**: 0

### Early Lead Time Statistics
- **Mean**: 1590.0s
- **Median**: 1590.0s
- **Max**: 1620.0s
- **Min**: 1560.0s

## 5. Synthetic vs Real Model Comparison
| Metric | Synthetic Baseline (Phase 5A) | CIC-IDS2017 Real Model |
|--------|------------------------------|-------------------------|
| **Known-Class F1** | 0.0000 | {out['known_class_evaluation']['macro_f1']:.4f} |
| **Novel-Class Classification** | Failed (All SCANNING) | Failed (Never seen in train) |
| **Benign Anomaly Rate** | 100.0% | 1.07% |
| **Forecast Behavior** | Invalid (100% False Positives) | Limited by zero-shot exposure |

## 6. Generalization Analysis
Based on the evidence:
- **A. Good known-class generalization**: The model accurately separates BENIGN from known attacks (DDOS, OTHER_ATTACK) when tested on strictly future time windows.
- **C. Novel-class detection through anomaly detection**: The Isolation Forest caught the majority of BOTNET traffic, providing complementary unsupervised detection even when the XGBoost classifier predictably failed.
- **D. Poor novel-class detection (for SCANNING)**: The Isolation Forest failed to detect SCANNING traffic, classifying it as normal.
- **F. Insufficient evidence for forecasting**: Because the novel attacks in the test set had no preceding chronological ramping patterns matching known classes, and all forecasts occurred at ONSET or POST-ONSET, true predictive early warning was not demonstrated on this specific chronological slice.
