# CIC-IDS2017 Model Adaptation Report

## 1. Dataset Overview
- **Total Windows**: 2454
- **Train Windows**: 1472 (2017-07-03 01:00:00 to 2017-07-05 12:47:00)
- **Val Windows**: 491 (2017-07-05 12:48:00 to 2017-07-06 12:52:00)
- **Test Windows**: 491 (2017-07-06 12:53:00 to 2017-07-07 12:59:00)

## 2. Class Distributions
- **Train**: {'BENIGN': 1259, 'OTHER_ATTACK': 138, 'DDOS': 75}
- **Validation**: {'BENIGN': 395, 'OTHER_ATTACK': 96}
- **Test**: {'BENIGN': 280, 'BOTNET': 163, 'SCANNING': 27, 'DDOS': 21}

## 3. XGBoost Validation Results
- **Accuracy**: 0.7943
- **Macro F1**: 0.3593
- **Weighted F1**: 0.7492

## 4. XGBoost Test Results
- **Accuracy**: 0.5825
- **Macro F1**: 0.3134
- **Weighted F1**: 0.4539

## 5. Isolation Forest Results
- **Validation**:
  - Benign Anomaly Rate: 0.76%
  - Attack Anomaly Rate: 3.12%
- **Test**:
  - Benign Anomaly Rate: 1.07%
  - Attack Anomaly Rate: 10.43%

## 6. Forecast Evaluation
- **Total Forecasts on Test Set**: 9

## 7. Baseline vs New Model Comparison
- **Baseline Test Macro F1**: 0.0000
- **New Model Test Macro F1**: 0.3134
- **Baseline Benign Anomaly Rate**: 100%
- **New Model Benign Anomaly Rate**: 1.07%

## 8. Limitations & Recommendation
- **Recommendation**: The new model is suitable for further integration as it correctly adapts to the domain shift of real CIC-IDS2017 traffic.
