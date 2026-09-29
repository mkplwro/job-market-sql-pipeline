import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "jobs_clean.csv"

df = pd.read_csv(INPUT_PATH)

print("=== DATASET INFO ===")
df.info()

print("\n=== MISSING VALUES ===")
print(df.isna().sum())

print("\n=== DATA TYPES ===")
print(df.dtypes)

print("\n=== JOB ID ===")
print("Missing IDs:", df["id"].isna().sum())
print("Duplicate IDs:", df["id"].duplicated().sum())

print("\n=== REQUIRED FIELDS ===")
required_columns = [
    "id",
    "title",
    "created",
]
for column in required_columns:
    print(
        f"{column}: missing = {df[column].isna().sum()}"
    )
print("\n=== CONTRACT TIME ===")
print(
    df["contract_time"].value_counts(dropna=False)
)
print("\n=== SALARY ===")
print(
    "Salary min missing:",
    df["salary_min"].isna().sum()
)
print(
    "Salary max missing:",
    df["salary_max"].isna().sum()
)
print(
    "Invalid salary ranges:",
    (df["salary_min"] > df["salary_max"]).sum()
)
print(
    "Salary predicted:",
    df["salary_is_predicted"].value_counts(
        dropna=False
    )
)

print("\n=== CREATED DATE ===")
created = pd.to_datetime(
    df["created"],
    errors="coerce"
)
print("Invalid dates:", created.isna().sum())
print("Earliest:", created.min())
print("Latest:", created.max())

print("\n=== COMPANIES ===")
print(
    df["company"]
    .head(10)
    .to_string()
)
print("\n=== LOCATIONS ===")
print(
    df["location"]
    .head(10)
    .to_string()
)
print("\n=== CATEGORIES ===")
print("Category labels:")
print(df["category_label"].head(10).to_string())

print("\nCategory tags:")
print(df["category_tag"].head(10).to_string())