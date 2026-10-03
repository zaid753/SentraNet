import os
import glob
import pandas as pd
from backend.telemetry.datasets.cicids_adapter import CICIDS2017Adapter

def build_full_dataset():
    raw_dir = "data/raw/cicids2017/TrafficLabelling"
    output_path = "data/processed/cicids2017/full_dataset.parquet"
    
    # We will look for csv files (handling potential spaces in the dir name)
    csv_files = glob.glob(os.path.join(raw_dir + "*", "*.csv"))
    
    adapter = CICIDS2017Adapter(window_size_seconds=60)
    
    all_windows = []
    
    for csv_file in sorted(csv_files):
        print(f"Processing {csv_file}...")
        try:
            # We process one file at a time. The adapter yields a DataFrame.
            df_windows = adapter.process_file_to_windows(csv_file)
            all_windows.append(df_windows)
        except Exception as e:
            print(f"Failed to process {csv_file}: {e}")
            
    print("Concatenating all windows...")
    full_df = pd.concat(all_windows, ignore_index=True)
    
    # Ensure chronological sort
    full_df['window_start'] = pd.to_datetime(full_df['window_start'])
    full_df = full_df.sort_values('window_start').reset_index(drop=True)
    
    print(f"Total windows: {len(full_df)}")
    full_df.to_parquet(output_path, index=False)
    print(f"Saved full dataset to {output_path}")

if __name__ == "__main__":
    build_full_dataset()
