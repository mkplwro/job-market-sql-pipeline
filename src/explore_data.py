import json
import pandas as pd

file_path = "data/raw/jobs_wroclaw_data_analyst.json"

with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

print("Type of main object:", type(data))
print("JSON keys:", data.keys())

jobs = data["results"]

print("Number of offers:", len(jobs))
print("Type of ofert:", type(jobs[0]))

df = pd.DataFrame(jobs)

print("\nData Frame Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 offers:")
print(df[["title", "company", "location", "created"]].head())
