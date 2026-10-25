
from pathlib import Path
import pandas as pd

# Find the dataset relative to this Python file
dataset_path = (
    Path(__file__).parent
    / "Data"
    / "train-00000-of-00001.parquet"
)

print("Dataset exists:", dataset_path.exists())

if dataset_path.exists():
    df = pd.read_parquet(dataset_path)

    print("\nDataset loaded successfully!")
    print("Number of rows:", len(df))
    print("Number of columns:", len(df.columns))

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nFirst 5 rows:")
    print(df.head().to_string())
else:
    print("Dataset not found. Check the file location.")
    
print("\nRandom sample of 10 tickets:")
print(
    df[["issue_description", "category", "priority"]]
    .sample(n=10, random_state=42)
    .to_string(index=False)
)

print("\nPriority distribution:")
print(df["priority"].value_counts(dropna=False))

print("\nPriority percentages:")
print(
    (df["priority"].value_counts(normalize=True, dropna=False) * 100)
    .round(2)
)

print("\nCategory distribution:")
print(df["category"].value_counts(dropna=False))

print("\nNumber of unique categories:")
print(df["category"].nunique())

print("\nMissing values in key columns:")
print(
    df[["issue_description", "category", "priority"]]
    .isna()
    .sum()
)

print("\nEmpty issue descriptions:")
print(
    df["issue_description"]
    .astype("string")
    .str.strip()
    .eq("")
    .sum()
)
print("\nDuplicate issue descriptions:")
print(df["issue_description"].duplicated().sum())

print("\nUnique issue descriptions:")
print(df["issue_description"].nunique())

print("\nCategory consistency for repeated descriptions:")

category_counts = (
    df.groupby("issue_description")["category"]
    .nunique()
)

print(
    "Descriptions associated with multiple categories:",
    (category_counts > 1).sum()
)

print("\nTop 10 most repeated descriptions:")

print(
    df["issue_description"]
    .value_counts()
    .head(10)
    .to_string()
)

print("\nMost repeated description: category and priority breakdown")

most_repeated_description = df["issue_description"].value_counts().index[0]

print(f"\nDescription: {most_repeated_description}")

matching_tickets = df[
    df["issue_description"] == most_repeated_description
]

print("\nCategory counts:")
print(matching_tickets["category"].value_counts().to_string())

print("\nPriority counts:")
print(matching_tickets["priority"].value_counts().to_string())

import re

print("\nText quality check:")

descriptions = df["issue_description"].drop_duplicates()

joined_word_pattern = re.compile(
    r"\b[a-z]{2,}(?:I|We|You|The|My|Your|For|With|And|But|This|That|Can|Is|Are)[a-z]+\b"
)

joined_word_count = descriptions.apply(
    lambda text: bool(joined_word_pattern.search(text))
).sum()

print("Unique descriptions checked:", len(descriptions))
print("Descriptions with possible joined words:", joined_word_count)
print(
    "Percentage:",
    round(joined_word_count / len(descriptions) * 100, 2),
    "%"
)

print("\nExamples:")
print(
    descriptions[
        descriptions.apply(
            lambda text: bool(joined_word_pattern.search(text))
        )
    ].head(10).to_string(index=False)
)

print("\nChecking known joined-word patterns:")

patterns = [
    r"\bmyphone\b",
    r"\bfora\b",
    r"\bReachingout\b",
    r"\bIwant\b",
    r"\bsharemore\b",
    r"\bWe'rea\b",
    r"\byoucan\b",
    r"\bWalkedthe\b",
]

for pattern in patterns:
    matches = df["issue_description"].str.contains(
        pattern,
        case=False,
        regex=True,
        na=False,
    )

    print(f"{pattern}: {matches.sum()} rows")
print("\nDirect text verification:")

for word in ["myphone", "fora", "Reachingout", "Iwant", "Walkedthe"]:
    description_matches = df["issue_description"].str.contains(
        word, case=False, regex=False, na=False
    ).sum()

    notes_matches = df["resolution_notes"].str.contains(
        word, case=False, regex=False, na=False
    ).sum()

    print(
        f"{word}: "
        f"issue_description={description_matches}, "
        f"resolution_notes={notes_matches}"
    )
    
    print("\nDebugging the first description:")

print("Exact value:", repr(df.loc[0, "issue_description"]))
print("Data type:", type(df.loc[0, "issue_description"]))
print(
    "Contains 'myphone':",
    "myphone" in str(df.loc[0, "issue_description"]).lower()
)
print("DataFrame shape:", df.shape)