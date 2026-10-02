import os
import pandas as pd
import json

DATA_DIR = "data/raw/cicids2017/MachineLearningCVE"

def audit():
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    
    total_size = sum(os.path.getsize(os.path.join(DATA_DIR, f)) for f in files)
    print(f"Total Size: {total_size / (1024*1024):.2f} MB")
    
    total_rows = 0
    all_columns = None
    labels = set()
    min_ts = None
    max_ts = None
    
    for f in files:
        path = os.path.join(DATA_DIR, f)
        print(f"Reading {f}")
        # Just read a chunk to get columns
        df_sample = pd.read_csv(path, nrows=10, skipinitialspace=True)
        if all_columns is None:
            all_columns = list(df_sample.columns)
            print("Columns:", all_columns)
        
        # We need to read just the columns we want for labels and timestamps, or read all in chunks
        chunk_iter = pd.read_csv(path, skipinitialspace=True, chunksize=100000, low_memory=False)
        file_rows = 0
        for chunk in chunk_iter:
            file_rows += len(chunk)
            
            # Label distribution
            if 'Label' in chunk.columns:
                labels.update(chunk['Label'].unique())
            
            # Timestamp processing
            if 'Timestamp' in chunk.columns:
                # Timestamps in CICIDS2017 are like "5/7/2017 1:00" or similar
                ts_col = chunk['Timestamp']
                
                try:
                    ts_min = str(ts_col.min())
                    ts_max = str(ts_col.max())
                    if min_ts is None or ts_min < min_ts:
                        min_ts = ts_min
                    if max_ts is None or ts_max > max_ts:
                        max_ts = ts_max
                except Exception:
                    pass
                    
        total_rows += file_rows
        print(f"  Rows: {file_rows}")
        
    print(f"Total Rows: {total_rows}")
    print(f"Labels: {labels}")
    print(f"Timestamp range approx: {min_ts} - {max_ts}")
    
if __name__ == "__main__":
    audit()
