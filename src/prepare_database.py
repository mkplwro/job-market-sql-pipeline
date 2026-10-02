from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "jobs_clean.csv"
COMPANIES_OUTPUT_PATH = (PROJECT_ROOT / "data" / "processed" / "companies.csv")
LOCATIONS_OUTPUT_PATH = (PROJECT_ROOT / "data" / "processed" / "locations.csv")
CATEGORIES_OUTPUT_PATH = (PROJECT_ROOT / "data" / "processed" / "categories.csv")
JOBS_OUTPUT_PATH = (PROJECT_ROOT / "data" / "processed" / "jobs_prepared.csv")

df = pd.read_csv(INPUT_PATH)
print(f"Loaded jobs: {len(df)}")

companies = (df[["company"]].drop_duplicates().reset_index(drop=True))
companies["company_id"] = range(1, len(companies) + 1)
companies = companies[["company_id", "company"]]
print(f"Unique companies: {len(companies)}")

locations = (df[["location", "latitude", "longitude"]].drop_duplicates().reset_index(drop=True))
locations["location_id"] = range(1, len(locations) + 1)
locations = locations[["location_id", "location", "latitude", "longitude"]]
print(f"Unique locations: {len(locations)}")

categories = (df[["category_label", "category_tag"]].drop_duplicates().reset_index(drop=True))
categories["category_id"] = range(1, len(categories) + 1)
categories = categories[["category_id", "category_label", "category_tag"]]
print(f"Unique categories: {len(categories)}")

df = df.merge(companies, on="company", how="left")
df = df.merge(locations, on=["location", "latitude", "longitude"], how="left")
df = df.merge(categories, on=["category_label", "category_tag"],how="left")
df = df.drop(columns=["company", "location", "latitude", "longitude", "category_label", "category_tag"])

companies.to_csv(COMPANIES_OUTPUT_PATH, index=False, encoding="utf-8")
locations.to_csv(LOCATIONS_OUTPUT_PATH, index=False, encoding="utf-8")
categories.to_csv(CATEGORIES_OUTPUT_PATH, index=False, encoding="utf-8")

df.to_csv(JOBS_OUTPUT_PATH, index=False, encoding="utf-8")

print()
print("Database preparation completed.")
print(f"Companies rows: {len(companies)}")
print(f"Locations rows: {len(locations)}")
print(f"Categories rows: {len(categories)}")
print(f"Jobs rows: {len(df)}")

print()
print(f"Companies saved to: {COMPANIES_OUTPUT_PATH}")
print(f"Locations saved to: {LOCATIONS_OUTPUT_PATH}")
print(f"Categories saved to: {CATEGORIES_OUTPUT_PATH}")
print(f"Jobs saved to: {JOBS_OUTPUT_PATH}")