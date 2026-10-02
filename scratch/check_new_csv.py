import pandas as pd
import glob
import json

path = "data/raw/cicids2017/TrafficLabelling /*.csv"
files = glob.glob(path)

print(f"Found {len(files)} CSV files.")
if files:
    f = files[0]
    print(f"Checking file: {f}")
    df = pd.read_csv(f, nrows=5, encoding='cp1252', skipinitialspace=True)
    
    print(f"Columns count: {len(df.columns)}")
    print("Columns:", list(df.columns))
    print("Sample row:")
    print(df.iloc[0].to_dict())
