import pandas as pd
df = pd.read_parquet("data/processed/cicids2017/full_dataset.parquet")
df['window_start'] = pd.to_datetime(df['window_start'])
df = df.sort_values('window_start')

print("Class chronological ranges:")
for cls in df['label'].unique():
    cls_df = df[df['label'] == cls]
    print(f"{cls:15}: {len(cls_df)} windows, from {cls_df['window_start'].min()} to {cls_df['window_start'].max()}")

print("\nIf we want ALL classes in TRAIN, the train split must end AT LEAST after the first window of the latest-starting class.")
latest_first_appearance = df.groupby('label')['window_start'].min().max()
print(f"Latest first appearance is at: {latest_first_appearance}")

# But maybe we need *enough* samples in TRAIN? Let's say we split at the point where we capture at least 20% of the occurrences of every attack class?
print("\nIf we want at least 20% of every class in train:")
split_times = []
for cls in df['label'].unique():
    cls_df = df[df['label'] == cls]
    pct20_idx = int(len(cls_df) * 0.2)
    split_times.append(cls_df.iloc[pct20_idx]['window_start'])

max_split_time = max(split_times)
print(f"Time to get 20% of all classes: {max_split_time}")

train_df = df[df['window_start'] <= max_split_time]
val_test_df = df[df['window_start'] > max_split_time]

print(f"\nIf TRAIN ends at {max_split_time}:")
print(f"TRAIN size: {len(train_df)}")
print(f"VAL/TEST remaining: {len(val_test_df)}")

print("\nClasses in remaining VAL/TEST:")
print(val_test_df['label'].value_counts())
