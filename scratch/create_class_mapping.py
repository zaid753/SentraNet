import joblib
import json
import pandas as pd
from sklearn.preprocessing import LabelEncoder

def create_class_mapping():
    # 1. LOAD DATASET & SPLIT
    dataset_path = "data/processed/cicids2017/full_dataset.parquet"
    df = pd.read_parquet(dataset_path)
    df['window_start'] = pd.to_datetime(df['window_start'])
    df = df.sort_values('window_start').reset_index(drop=True)

    total_windows = len(df)
    train_idx = int(total_windows * 0.6)
    train_df = df.iloc[:train_idx].copy()
    
    le = LabelEncoder()
    le.fit(train_df['label'].fillna('UNKNOWN'))
    
    classes = list(le.classes_)
    class_to_idx = {c: int(i) for i, c in enumerate(classes)}
    
    mapping = {
        "classes": classes,
        "class_to_index": class_to_idx
    }
    
    with open("models/experiments/cicids2017/class_mapping.json", "w") as f:
        json.dump(mapping, f, indent=2)

if __name__ == "__main__":
    create_class_mapping()
