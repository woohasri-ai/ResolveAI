
import pandas as pd

# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

DATA_PATH = "Data/train-00000-of-00001.parquet"
OUTPUT_PATH = "Data/escalation_model_data.parquet"

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


# --------------------------------------------------
# 2. Load the original dataset
# --------------------------------------------------

print("Loading original dataset...")

df = pd.read_parquet(DATA_PATH)

print("Original rows:", len(df))
print("Original columns:", len(df.columns))


# --------------------------------------------------
# 3. Keep rows with known escalation labels
# --------------------------------------------------

model_df = df.loc[df[TARGET].notna()].copy()

print("\nRows with known escalation labels:", len(model_df))
print("Rows excluded due to missing target:",
      df[TARGET].isna().sum())


# --------------------------------------------------
# 4. Select candidate features and target
# --------------------------------------------------

selected_columns = CANDIDATE_FEATURES + [TARGET]

model_df = model_df[selected_columns].copy()

print("\nColumns in modeling dataset:", len(model_df.columns))
print("Selected columns:", list(model_df.columns))


# --------------------------------------------------
# 5. Inspect target distribution
# --------------------------------------------------

print("\nTarget distribution:")
print(model_df[TARGET].value_counts().to_string())

print("\nTarget percentages:")
print(
    (
        model_df[TARGET].value_counts(normalize=True) * 100
    ).round(2).to_string()
)


# --------------------------------------------------
# 6. Check missing values
# --------------------------------------------------

print("\nMissing values by column:")
print(model_df.isna().sum().to_string())

total_missing = int(model_df.isna().sum().sum())

print("\nTotal missing values in selected dataset:", total_missing)


# --------------------------------------------------
# 7. Validate target labels
# --------------------------------------------------

expected_labels = {"Yes", "No"}
actual_labels = set(model_df[TARGET].unique())

print("\nObserved target labels:", actual_labels)

if not actual_labels.issubset(expected_labels):
    raise ValueError(
        f"Unexpected escalation labels found: {actual_labels}"
    )

if total_missing > 0:
    raise ValueError(
        "Selected dataset contains missing values. "
        "Investigate them before proceeding."
    )


# --------------------------------------------------
# 8. Save the prepared dataset
# --------------------------------------------------

model_df.to_parquet(OUTPUT_PATH, index=False)

print("\nModeling dataset saved successfully.")
print("Output path:", OUTPUT_PATH)
print("Saved rows:", len(model_df))
print("Saved columns:", len(model_df.columns))
