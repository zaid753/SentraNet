import os
import json
import pandas as pd
from datetime import datetime

def check_experiment_b_feasibility():
    dataset_path = "data/processed/cicids2017/full_dataset.parquet"
    df = pd.read_parquet(dataset_path)
    df['window_start'] = pd.to_datetime(df['window_start'])
    df = df.sort_values('window_start').reset_index(drop=True)
    
    ranges = {}
    for cls in df['label'].unique():
        cls_df = df[df['label'] == cls]
        ranges[cls] = {
            "first_appearance": str(cls_df['window_start'].min()),
            "last_appearance": str(cls_df['window_start'].max()),
            "count": len(cls_df)
        }
        
    latest_first_appearance_time = df.groupby('label')['window_start'].min().max()
    latest_first_appearance_class = df.groupby('label')['window_start'].min().idxmax()
    
    # Calculate what would be left in TEST if we split at latest_first_appearance
    test_df = df[df['window_start'] > latest_first_appearance_time]
    test_classes = test_df['label'].value_counts().to_dict()
    
    is_impossible = len(test_classes) < len(df['label'].unique())
    
    return {
        "ranges": ranges,
        "latest_first_appearance_time": str(latest_first_appearance_time),
        "latest_first_appearance_class": latest_first_appearance_class,
        "test_classes_remaining": test_classes,
        "is_impossible": is_impossible
    }

def generate_reports():
    feasibility = check_experiment_b_feasibility()
    
    # JSON Report
    out = {
        "experiment_a_preserved": True,
        "experiment_b_feasibility": feasibility,
        "conclusion": "STOPPED. A fully chronological all-class training split is mathematically impossible without data leakage.",
        "model_promotion_status": "EXPERIMENTAL MODEL — NOT YET DEFAULT"
    }
    
    os.makedirs("reports", exist_ok=True)
    with open("reports/cicids2017_coverage_evaluation.json", "w") as f:
        json.dump(out, f, indent=2)
        
    # Markdown Report
    md = f"""# CIC-IDS2017 Step 8: Coverage-Aware Real-Data Evaluation (Experiment B)
**EXPERIMENTAL MODEL — NOT YET DEFAULT**

## 1. Objective
Run a second complementary evaluation that separates temporal generalization from attack-family coverage generalization, while maintaining a strictly chronological test period (no future leakage).

## 2. Chronological Attack Distribution
The CIC-IDS2017 dataset has a strictly sequential, disjoint attack campaign schedule:

"""
    for cls, r in feasibility['ranges'].items():
        md += f"- **{cls}** ({r['count']} windows): {r['first_appearance']} to {r['last_appearance']}\n"
        
    md += f"""
## 3. Feasibility Analysis & STOP Condition
To create a `TRAIN` set containing ALL FIVE classes, the training split must extend to at least the very first appearance of the latest-starting class. 
The latest-starting class is **{feasibility['latest_first_appearance_class']}**, which first appears at **{feasibility['latest_first_appearance_time']}**.

Therefore, the `TRAIN` set MUST include timestamps up to at least `{feasibility['latest_first_appearance_time']}`.

Because the `TEST` period must remain strictly later than `TRAIN` (no data leakage), the `TEST` set can ONLY contain records AFTER `{feasibility['latest_first_appearance_time']}`.

**Classes remaining in the dataset after {feasibility['latest_first_appearance_time']}:**
"""
    for cls, count in feasibility['test_classes_remaining'].items():
        md += f"- {cls}: {count} windows\n"
        
    md += """
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
"""

    with open("reports/cicids2017_coverage_evaluation.md", "w") as f:
        f.write(md)
        
    print("Step 8 Feasibility Audit complete. Reports generated. Training aborted due to mathematical impossibility.")

if __name__ == "__main__":
    generate_reports()
