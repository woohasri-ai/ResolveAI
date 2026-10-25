
import pandas as pd

df = pd.read_parquet("data/train-00000-of-00001.parquet")

category_counts = (
    df.groupby("issue_description")["category"].nunique()
)

print("Unique descriptions:", len(category_counts))
print(
    "Descriptions with conflicting categories:",
    int((category_counts > 1).sum())
)
print(
    "Descriptions with exactly one category:",
    int((category_counts == 1).sum())
)
