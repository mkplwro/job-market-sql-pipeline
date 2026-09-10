import json
import pandas as pd


INPUT_PATH = "data/raw/jobs_wroclaw_data_analyst.json"
OUTPUT_PATH = "data/processed/jobs_clean.csv"


# Load raw JSON
with open(INPUT_PATH, "r", encoding="utf-8") as file:
    data = json.load(file)


# Create DataFrame
df = pd.DataFrame(data["results"])


# Extract company name
df["company"] = df["company"].apply(
    lambda x: x.get("display_name") if isinstance(x, dict) else None
)


# Extract location name
df["location"] = df["location"].apply(
    lambda x: x.get("display_name") if isinstance(x, dict) else None
)


# Extract category information
df["category_label"] = df["category"].apply(
    lambda x: x.get("label") if isinstance(x, dict) else None
)

df["category_tag"] = df["category"].apply(
    lambda x: x.get("tag") if isinstance(x, dict) else None
)


# Convert created to datetime
df["created"] = pd.to_datetime(df["created"], errors="coerce")


# Convert salary prediction flag to integer
df["salary_is_predicted"] = pd.to_numeric(
    df["salary_is_predicted"],
    errors="coerce"
)


# Remove technical API fields
df = df.drop(
    columns=[
        "__CLASS__",
        "category",
        "adref"
    ],
    errors="ignore"
)


# Save transformed data
df.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8"
)


print("Transformation completed.")
print(f"Rows: {df.shape[0]}")
print(f"Columns: {df.shape[1]}")
print(f"Saved to: {OUTPUT_PATH}")

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())