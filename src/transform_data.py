import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

PROJECT_ROOT = Path(__file__).resolve().parent.parent

today = datetime.now(
    ZoneInfo("Europe/Warsaw")
).strftime("%Y-%m-%d")
INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / today
    / "jobs_wroclaw_data_analyst.json"
)
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "jobs_clean.csv"

with open(INPUT_PATH, "r", encoding="utf-8") as file:
    data = json.load(file)

df = pd.DataFrame(data["results"])

df["company"] = df["company"].apply(
    lambda x: x.get("display_name") if isinstance(x, dict) else None
)

df["location"] = df["location"].apply(
    lambda x: x.get("display_name") if isinstance(x, dict) else None
)

df["category_label"] = df["category"].apply(
    lambda x: x.get("label") if isinstance(x, dict) else None
)

df["category_tag"] = df["category"].apply(
    lambda x: x.get("tag") if isinstance(x, dict) else None
)

df["created"] = pd.to_datetime(df["created"], errors="coerce")

df["salary_is_predicted"] = pd.to_numeric(
    df["salary_is_predicted"],
    errors="coerce"
)

df = df.drop(
    columns=[
        "__CLASS__",
        "category",
        "adref"
    ],
    errors="ignore"
)

before_drop_duplicates = len(df)

df = df.drop_duplicates(subset=["id"])

after_drop_duplicates = len(df)

print(f"Duplicates removed: {before_drop_duplicates - after_drop_duplicates}")

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