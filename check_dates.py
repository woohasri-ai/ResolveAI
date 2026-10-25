
import pandas as pd

df = pd.read_parquet(
    "Data/train-00000-of-00001.parquet",
    columns=["previous_tickets"],
)

previous = df["previous_tickets"]

print("Total tickets:", len(previous))
print("Missing values:", int(previous.isna().sum()))
print("Unique non-missing values:", previous.nunique())
print("Data type:", previous.dtype)

print("\nSummary:")
print(previous.describe().to_string())

print("\nNegative values:", int((previous < 0).sum()))
print("Zero values:", int((previous == 0).sum()))

print("\nMost frequent values:")
print(previous.value_counts().head(15).to_string())
