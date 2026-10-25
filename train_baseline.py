import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.dummy import DummyClassifier

# 1. Configuration

DATA_PATH = "Data/escalation_model_data.parquet"

TARGET = "escalated"
TEXT_FEATURE = "issue_description"


# 2. Load the prepared dataset

print("Loading prepared dataset...")

df = pd.read_parquet(DATA_PATH)

print("Dataset loaded successfully.")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("\nTarget distribution:")
print(df[TARGET].value_counts().to_string())

# 3. Select text feature and target

X = df[TEXT_FEATURE]
y = df[TARGET]

# Use each exact description as its group.
# Identical descriptions must stay in the same split.

groups = df[TEXT_FEATURE]

print("\nText and target prepared.")
print("Text examples:", len(X))
print("Unique descriptions:", groups.nunique())
print("Target classes:", sorted(y.unique()))

# 4. Split data without sharing identical descriptions

splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.2,
    random_state=42
)

train_indices, test_indices = next(
    splitter.split(X, y, groups=groups)
)

X_train = X.iloc[train_indices]
X_test = X.iloc[test_indices]

y_train = y.iloc[train_indices]
y_test = y.iloc[test_indices]

print("\nTrain/test split completed.")
print("Training rows:", len(X_train))
print("Testing rows:", len(X_test))

print("\nTraining target distribution:")
print(y_train.value_counts().to_string())

print("\nTesting target distribution:")
print(y_test.value_counts().to_string())

print(
    "\nDescriptions shared between train and test:",
    len(set(X_train.unique()) & set(X_test.unique()))
)

# 5. Build the baseline model pipeline

model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            max_features=50_000,
            min_df=2
        )
    ),
    (
        "classifier",
        LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=42
        )
    )
])

print("\nBaseline model pipeline created.")
print(model)

# 6. Train the baseline model

print("\nTraining baseline model...")
print("This may take several minutes.")

model.fit(X_train, y_train)

print("Baseline model training completed.")

# 7. Evaluate the baseline model

print("\nGenerating predictions on test data...")

y_pred = model.predict(X_test)

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred,
        labels=["No", "Yes"],
        zero_division=0
    )
)

print("Confusion Matrix:")
print(
    confusion_matrix(
        y_test,
        y_pred,
        labels=["No", "Yes"]
    )
)

# 8. Evaluate a majority-class baseline

print("\nTraining majority-class baseline...")

dummy_model = DummyClassifier(strategy="most_frequent")
dummy_model.fit(X_train, y_train)

dummy_pred = dummy_model.predict(X_test)

print("\nMajority-class baseline results:")
print(
    classification_report(
        y_test,
        dummy_pred,
        labels=["No", "Yes"],
        zero_division=0
    )
)

print("Confusion Matrix:")
print(
    confusion_matrix(
        y_test,
        dummy_pred,
        labels=["No", "Yes"]
    )
)

# 9. Generate prediction probabilities once

print("\nGenerating prediction probabilities...")

yes_column = list(model.classes_).index("Yes")
y_prob_yes = model.predict_proba(X_test)[:, yes_column]

print("Probability generation completed.")
print("Number of probabilities:", len(y_prob_yes))
print("Minimum probability:", round(y_prob_yes.min(), 4))
print("Maximum probability:", round(y_prob_yes.max(), 4))

# 10. Check the default decision threshold

print("\nDefault decision threshold: 0.50")
print("Predicted Yes when P(Yes) >= 0.50")

# 11. Evaluate a lower decision threshold
threshold = 0.40
y_pred_40 = [
    "Yes" if probability >= threshold else "No"
    for probability in y_prob_yes
]

print(f"\nResults at threshold {threshold:.2f}:")
print(
    classification_report(
        y_test,
        y_pred_40,
        labels=["No", "Yes"],
        zero_division=0
    )
)

print("Confusion Matrix:")
print(
    confusion_matrix(
        y_test,
        y_pred_40,
        labels=["No", "Yes"]
    )
)

# 12. Save the trained baseline model

MODEL_PATH = "Data/escalation_baseline_model.joblib"

print("\nSaving trained model...")

joblib.dump(model, MODEL_PATH)

print("Model saved successfully.")
print("Saved model path:", MODEL_PATH)