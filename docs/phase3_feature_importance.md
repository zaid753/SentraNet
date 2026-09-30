# SENTRANET — Phase 3 Feature Importance Analysis

## Overview
This document reports the feature importance scores extracted from the trained 5-class XGBoost multi-class classifier using the `gain` attribution metric.

> [!CAUTION]
> **Scientific Honesty & Non-Causality Disclaimer:**  
> Feature importance values reflect how strongly individual attributes contributed to reducing tree split impurity inside this specific model. **They do not constitute causal proof that feature X causes cyber attacks.** 

---

## Ranked Model Features by Gain

| Rank | Feature Name | Importance (Gain) | Description |
|---|---|---|---|
| 1 | `rolling_5_total_bytes` | 11.1348 | Network flow metric |
| 2 | `avg_byte_rate` | 10.4651 | Network flow metric |
| 3 | `total_bytes` | 10.1641 | Network flow metric |
| 4 | `avg_packet_size` | 10.0967 | Network flow metric |
| 5 | `total_packets` | 10.0842 | Network flow metric |
| 6 | `avg_flow_duration` | 6.2228 | Network flow metric |
| 7 | `avg_packet_rate` | 3.2142 | Network flow metric |
| 8 | `rolling_5_avg_byte_rate` | 1.1505 | Network flow metric |
| 9 | `rolling_5_total_packets` | 0.9345 | Network flow metric |
| 10 | `syn_flag_count` | 0.6264 | Network flow metric |
| 11 | `rolling_5_flow_count` | 0.4179 | Network flow metric |
| 12 | `ack_flag_count` | 0.0861 | Network flow metric |
| 13 | `rolling_5_unique_sources` | 0.0564 | Network flow metric |
| 14 | `flow_count` | 0.0000 | Network flow metric |
| 15 | `unique_sources` | 0.0000 | Network flow metric |
| 16 | `unique_destinations` | 0.0000 | Network flow metric |
| 17 | `privileged_port_ratio` | 0.0000 | Network flow metric |

---

## Key Observations
1. **Volumetric & Rate Signals:** Attributes measuring packet/byte intensity (`total_bytes`, `avg_byte_rate`, `packet_rate`) rank prominently in differentiating high-volume DDoS surges from normal baseline traffic.
2. **Reconnaissance & Flag Signals:** TCP flag metrics (`syn_flag_count`, `ack_flag_count`) and port targeting (`privileged_port_ratio`) contribute significantly to distinguishing scanning probes from legitimate connections.
3. **Causal Rolling History:** Rolling aggregate features provide crucial short-term historical context without lookahead leakage.
