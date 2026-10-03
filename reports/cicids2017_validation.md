# CIC-IDS2017 Real-Dataset Validation Report

## 1. Dataset Overview
- **Dataset**: Friday-WorkingHours-Morning
- **Windows**: 241
- **Timestamp Range**: 2017-07-07 08:59:00 to 2017-07-07 12:59:00
- **Features Checked**: 17 features present, 0 NaN, 0 Inf.

## 2. Label Distribution
- Total Windows: 241
- Benign Windows: 78
- Attack Windows: 163

**Breakdown**:
- BOTNET: 163
- BENIGN: 78

## 3. CIC-IDS2017 to SENTRANET Mapping
| CIC Label | SENTRANET Class |
|-----------|-----------------|
| BENIGN | BENIGN |
| Bot | BOTNET |
| DDoS | DDOS |
| DoS GoldenEye | DDOS |
| DoS Hulk | DDOS |
| DoS Slowhttptest | DDOS |
| DoS slowloris | DDOS |
| FTP-Patator | OTHER_ATTACK |
| SSH-Patator | OTHER_ATTACK |
| PortScan | SCANNING |
| Infiltration | OTHER_ATTACK |
| Heartbleed | OTHER_ATTACK |
| Web Attack – Brute Force | OTHER_ATTACK |
| Web Attack – Sql Injection | OTHER_ATTACK |
| Web Attack – XSS | OTHER_ATTACK |

## 4. Frozen XGBoost Evaluation
*Note: Model was NOT retrained. Some classes may be absent.*
- **Accuracy**: 0.0000
- **Macro F1**: 0.0000
- **Weighted F1**: 0.0000

**Confusion Matrix**:
Labels: ['BENIGN', 'BOTNET', 'SCANNING']
```json
[[0, 0, 78], [0, 0, 163], [0, 0, 0]]
```

## 5. Isolation Forest Evaluation
*Note: Anomaly does not explicitly mean malicious.*
- **Benign Anomaly Rate**: 100.00%
- **Attack Anomaly Rate**: 100.00%

## 6. Risk Fusion State Distribution
- HIGH: 241

## 7. Temporal Attack Episodes
- BOTNET (2017-07-07T09:34:00 to 2017-07-07T09:35:00): 2 windows
- BOTNET (2017-07-07T10:04:00 to 2017-07-07T11:13:00): 70 windows
- BOTNET (2017-07-07T11:15:00 to 2017-07-07T11:18:00): 4 windows
- BOTNET (2017-07-07T11:20:00 to 2017-07-07T11:23:00): 4 windows
- BOTNET (2017-07-07T11:25:00 to 2017-07-07T11:28:00): 4 windows
- BOTNET (2017-07-07T11:30:00 to 2017-07-07T11:45:00): 16 windows
- BOTNET (2017-07-07T11:47:00 to 2017-07-07T11:50:00): 4 windows
- BOTNET (2017-07-07T11:52:00 to 2017-07-07T11:55:00): 4 windows
- BOTNET (2017-07-07T11:57:00 to 2017-07-07T12:00:00): 4 windows
- BOTNET (2017-07-07T12:02:00 to 2017-07-07T12:17:00): 16 windows
- BOTNET (2017-07-07T12:19:00 to 2017-07-07T12:22:00): 4 windows
- BOTNET (2017-07-07T12:24:00 to 2017-07-07T12:27:00): 4 windows
- BOTNET (2017-07-07T12:29:00 to 2017-07-07T12:32:00): 4 windows
- BOTNET (2017-07-07T12:34:00 to 2017-07-07T12:37:00): 4 windows
- BOTNET (2017-07-07T12:39:00 to 2017-07-07T12:49:00): 11 windows
- BOTNET (2017-07-07T12:51:00 to 2017-07-07T12:54:00): 4 windows
- BOTNET (2017-07-07T12:56:00 to 2017-07-07T12:59:00): 4 windows

## 8. Forecast Validation
- Total Forecasts Triggered: 34
- Forecasting relies on multi-window trajectories which may not perfectly align with exact dataset label boundaries.

## 9. Feature Distribution Check
Checked for NaN/Inf, all clean. 17 features present.

## 10. Scientific Disclosure
- CIC-IDS2017 is a public historical dataset.
- Replay is not live network traffic.
- Evaluation is on this dataset only.
- The existing model was not retrained.
- Results are dataset-specific.
- Forecasting metrics are scenario/dataset-specific.
- Risk is not calibrated probability.
- Anomaly detection does not prove maliciousness.
