# SENTRANET — Phase 5 Temporal Forecastability Audit

## 1. Executive Summary & Audit Purpose

Before implementing or evaluating an attack forecasting model, this audit analyzes the temporal structure of the processed development fixture (`data/processed/sample/`) across all 204 chronological 1-minute windows (spanning `08:00:00` to `11:23:00`).

> [!IMPORTANT]
> **Scientific Honesty & Dataset Grounding:**  
> The dataset is **Category B: Synthetic / Generated test fixture**. It exhibits synthetic block-period transitions rather than organic, stochastic enterprise network traffic. This audit establishes the exact empirical boundaries of what can and cannot be forecasted.

---

## 2. Chronological Sequence & Attack Episodes

The 204 continuous temporal windows partition into **7 distinct consecutive behavioral episodes**:

| Episode ID | Label | Start Timestamp | End Timestamp | Duration (Windows / Min) | Partition Placement | Preceding Context |
|---|---|---|---|---|---|---|
| **EP-0** | `BENIGN` | 2026-09-30 08:00:00 | 2026-09-30 08:41:00 | 42 min | Train (windows 0–41) | Initial System Baseline |
| **EP-1** | `SCANNING` | 2026-09-30 08:42:00 | 2026-09-30 09:05:00 | 24 min | Train (windows 42–65) | 42 Benign precursor windows |
| **EP-2** | `DDOS` | 2026-09-30 09:06:00 | 2026-09-30 09:29:00 | 24 min | Train (windows 66–89) | 24 Scanning precursor windows |
| **EP-3** | `BOTNET` | 2026-09-30 09:30:00 | 2026-09-30 09:47:00 | 18 min | Train (windows 90–107) | 24 DDoS saturation windows |
| **EP-4** | `BENIGN` | 2026-09-30 09:48:00 | 2026-09-30 10:41:00 | 54 min | Train (34) + Val (20) | Post-attack recovery baseline |
| **EP-5** | `SCANNING` | 2026-09-30 10:42:00 | 2026-09-30 11:05:00 | 24 min | Val (11) + Test (13) | 54 Benign precursor windows |
| **EP-6** | `DDOS` | 2026-09-30 11:06:00 | 2026-09-30 11:23:00 | 18 min | Test (windows 13–30) | 24 Scanning precursor windows |

---

## 3. Transition Types & Precursor Length Analysis

The dataset contains two macro cyber-attack escalation cycles following the multi-stage cyber kill chain:
$$\text{BENIGN (Baseline)} \longrightarrow \text{SCANNING (Reconnaissance)} \longrightarrow \text{DDOS (Exploitation/Saturation)}$$

### Observed Transition Points:

1. **`BENIGN` $\longrightarrow$ `SCANNING` Onset 1:** At `08:42:00`.
   - Precursor: 42 clean benign windows (`08:00:00` to `08:41:00`).
2. **`SCANNING` $\longrightarrow$ `DDOS` Escalation Onset 1:** At `09:06:00`.
   - Precursor: 24 reconnaissance scanning windows (`08:42:00` to `09:05:00`).
3. **`DDOS` $\longrightarrow$ `BOTNET` Transition:** At `09:30:00`.
   - Precursor: 24 volumetric DDoS windows.
4. **`BOTNET` $\longrightarrow$ `BENIGN` Recovery:** At `09:48:00`.
   - Precursor: 18 botnet beaconing windows.
5. **`BENIGN` $\longrightarrow$ `SCANNING` Onset 2:** At `10:42:00` (Inside Validation).
   - Precursor: 54 clean benign windows (`09:48:00` to `10:41:00`, spanning 34 in Train + 20 in Validation).
6. **`SCANNING` $\longrightarrow$ `DDOS` Escalation Onset 2:** At `11:06:00` (Inside Test).
   - Precursor: 24 scanning windows (`10:42:00` to `11:05:00`, spanning 11 in Val + 13 in Test).

### Precursor Statistics:
- **Total Valid Precursor-to-Attack Onsets:** 4 escalation onsets (2 Benign $\to$ Scanning, 2 Scanning $\to$ DDoS).
- **Minimum Precursor Length:** 24 windows (24 minutes).
- **Median Precursor Length:** 33 windows (33 minutes).
- **Maximum Precursor Length:** 54 windows (54 minutes).

---

## 4. Split-Level Forecastability Evaluation

Because model partitions were split chronologically (70% train, 15% val, 15% test):

| Split | Window Range | Contents | Forecastable Onset Transitions Present |
|---|---|---|---|
| **Train** | `08:00` to `10:21` (142 w) | 76 Benign, 24 Scan, 24 DDoS, 18 Bot | Yes (Wave 1: Benign $\to$ Scan at 08:42; Scan $\to$ DDoS at 09:06) |
| **Validation** | `10:22` to `10:52` (31 w) | 20 Benign, 11 Scanning | Yes (Wave 2: Benign $\to$ Scan at 10:42) |
| **Test** | `10:53` to `11:23` (31 w) | 13 Scanning, 18 DDoS | Yes (Wave 2: Scan $\to$ DDoS escalation at 11:06) |

> [!CAUTION]
> **Partition Limitation:**
> In the strictly isolated **Test Split (31 windows)**, there are **0 BENIGN windows**. The test partition begins at `10:53` when scanning reconnaissance is already active. Therefore, in the test split, the model cannot demonstrate `BENIGN -> ATTACK` emergence, but can demonstrate `SCANNING -> DDOS` volumetric escalation forecasting.
> 
> Across shorter horizons (1m, 2m, 5m), valid pre-attack windows exist immediately preceding the onset. For larger horizons (10m, 15m), the number of independent attack onset boundaries is too small to yield statistically reliable metrics.

---

## 5. Audit Verdict & Technical Directives

1. **Architecture Requirement:** Implement the full causal forecasting engine, temporal trajectory tracker, and risk fusion pipeline.
2. **Honesty Enforcement:** For evaluation windows where risk is stable, declining, or already at peak saturation, the system must strictly output `forecast_available = false` and `time_to_impact_seconds = null`.
3. **Horizon Handling:** Horizons lacking adequate independent onsets must be marked `INSUFFICIENT DATA` rather than fabricating synthetic positive metrics.
