
import pandas as pd

DATA_PATH = "Data/train-00000-of-00001.parquet"

TARGET = "escalated"

CANDIDATE_FEATURES = [
    "issue_description",
    "category",
    "product",
    "channel",
    "region",
    "language",
    "customer_age",
    "customer_gender",
    "subscription_type",
    "customer_tenure_months",
    "previous_tickets",
    "customer_segment",
    "priority",
    "issue_complexity_score",
    "sla_target_hours",
]

df = pd.read_parquet(DATA_PATH)

# Keep only rows with a known target.
model_df = df.loc[df[TARGET].notna()].copy()

# Keep the target and candidate features only.
model_df = model_df[CANDIDATE_FEATURES + [TARGET]]

print("Original rows:", len(df))
print("Rows with known escalation labels:", len(model_df))
print("Columns in modeling dataset:", len(model_df.columns))
print("\nTarget distribution:")
print(model_df[TARGET].value_counts().to_string())
print("\nMissing values by column:")
print(model_df.isna().sum().to_string())
