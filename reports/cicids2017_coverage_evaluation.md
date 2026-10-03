# CIC-IDS2017 Step 8: Coverage-Aware Real-Data Evaluation (Experiment B)
**EXPERIMENTAL MODEL — NOT YET DEFAULT**

## 1. Objective
Run a second complementary evaluation that separates temporal generalization from attack-family coverage generalization, while maintaining a strictly chronological test period (no future leakage).

## 2. Chronological Attack Distribution
The CIC-IDS2017 dataset has a strictly sequential, disjoint attack campaign schedule:

- **BENIGN** (1934 windows): 2017-07-03 01:00:00 to 2017-07-07 12:55:00
- **OTHER_ATTACK** (234 windows): 2017-07-04 02:09:00 to 2017-07-06 10:42:00
- **DDOS** (96 windows): 2017-07-05 02:24:00 to 2017-07-07 04:16:00
- **SCANNING** (27 windows): 2017-07-07 01:05:00 to 2017-07-07 03:23:00
- **BOTNET** (163 windows): 2017-07-07 09:34:00 to 2017-07-07 12:59:00

## 3. Feasibility Analysis & STOP Condition
To create a `TRAIN` set containing ALL FIVE classes, the training split must extend to at least the very first appearance of the latest-starting class. 
The latest-starting class is **BOTNET**, which first appears at **2017-07-07 09:34:00**.

Therefore, the `TRAIN` set MUST include timestamps up to at least `2017-07-07 09:34:00`.

Because the `TEST` period must remain strictly later than `TRAIN` (no data leakage), the `TEST` set can ONLY contain records AFTER `2017-07-07 09:34:00`.

**Classes remaining in the dataset after 2017-07-07 09:34:00:**
- BOTNET: 162 windows
- BENIGN: 43 windows

### Conclusion: EXPERIMENT ABORTED
**A fully chronological all-class training split is IMPOSSIBLE due to CIC-IDS2017's actual attack chronology.**

If we force all classes into TRAIN, the TEST set will entirely lack `SCANNING`, `DDOS`, and `OTHER_ATTACK` traffic, making it impossible to evaluate cross-day model robustness or generalization on those classes. 

Alternatively, if we use a random shuffle (StratifiedShuffleSplit) to guarantee class coverage in both TRAIN and TEST, we violate the temporal causality of the dataset (using future data to predict the past).

As instructed ("If a fully chronological all-class training split is impossible due to CIC-IDS2017's actual attack chronology, STOP and report why rather than creating a misleading split"), Experiment B model training has been halted.

## 4. Final Verdict on Model Changes
**J. Are further model changes scientifically justified?**
No. Experiment A correctly exposes the zero-shot generalization limits of XGBoost when encountering chronologically novel attacks (BOTNET, SCANNING), while demonstrating the Isolation Forest's unsupervised capacity to detect them. Altering the split to artificially inject future knowledge into training would invalidate the integrity of the streaming pipeline simulation. The current models are scientifically valid for the provided dataset constraints.

**K. Model Promotion Status**
**EXPERIMENTAL MODEL — NOT YET DEFAULT**
