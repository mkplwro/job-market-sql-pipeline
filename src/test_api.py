import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

app_id = os.getenv("ADZUNA_APP_ID")
app_key = os.getenv("ADZUNA_APP_KEY")

url = "https://api.adzuna.com/v1/api/jobs/pl/search/1"

params = {
    "app_id": app_id,
    "app_key": app_key,
    "results_per_page": 10,
    "what": "data analyst",
    "where": "Wroclaw",
    "content-type": "application/json",
}

response = requests.get(url, params=params)

print("Status:", response.status_code)

response.raise_for_status()

data = response.json()

print("Liczba ofert:", data["count"])

output_path = "data/raw/jobs_wroclaw_data_analyst.json"

with open(output_path, "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print(f"Dane zapisane do: {output_path}")