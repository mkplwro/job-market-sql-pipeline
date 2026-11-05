import os
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

response = requests.get(
    url,
    params=params,
    timeout=30
)

print("Status:", response.status_code)

response.raise_for_status()

data = response.json()

print("API works correctly")
print("Number of results available in the API:", data.get("count"))
print("Number of offers downloaded:", len(data.get("results", [])))
