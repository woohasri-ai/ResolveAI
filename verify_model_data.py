
import pandas as pd
from pathlib import Path

file_path = Path("Data/escalation_model_data.parquet")

print("File exists:", file_path.exists())

if not file_path.exists():
    raise FileNotFoundError(file_path)

df = pd.read_parquet(file_path)

print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Missing values:", int(df.isna().sum().sum()))
print("\nTarget counts:")
print(df["escalated"].value_counts().to_string())

print("\nVerification passed.")
