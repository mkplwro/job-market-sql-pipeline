import json
import pandas as pd

file_path = "data/raw/jobs_wroclaw_data_analyst.json"

with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

df = pd.DataFrame(data["results"])


print("=== DATASET INFO ===")
print(df.info())


print("\n=== MISSING VALUES ===")
print(df.isna().sum())


print("\n=== DATA TYPES ===")
print(df.dtypes)


print("\n=== CONTRACT TIME ===")
print(df["contract_time"].value_counts(dropna=False))


print("\n=== SALARY ===")
print("Salary min missing:", df["salary_min"].isna().sum())
print("Salary max missing:", df["salary_max"].isna().sum())
print(
    "Salary predicted:",
    df["salary_is_predicted"].value_counts(dropna=False)
)


print("\n=== COMPANIES ===")
print(df["company"].head(10).to_string())


print("\n=== LOCATIONS ===")
print(df["location"].head(10).to_string())


print("\n=== CATEGORIES ===")
print(df["category"].head(10).to_string())