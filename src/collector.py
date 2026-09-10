import os
import json
import requests
from dotenv import load_dotenv


# Load API credentials from .env
load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

BASE_URL = "https://api.adzuna.com/v1/api/jobs/pl/search"


def fetch_jobs(page, results_per_page=50):
    """Fetch one page of job offers from Adzuna API."""

    url = f"{BASE_URL}/{page}"

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": results_per_page,
        "what": "data analyst",
        "where": "Wroclaw",
        "content-type": "application/json",
    }

    response = requests.get(url, params=params, timeout=30)

    response.raise_for_status()

    return response.json()


def collect_jobs(number_of_pages=5):
    """Collect job offers from multiple API pages."""

    all_jobs = []
    total_count = None

    for page in range(1, number_of_pages + 1):
        print(f"Fetching page {page}...")

        data = fetch_jobs(page)

        if total_count is None:
            total_count = data.get("count", 0)

        jobs = data.get("results", [])

        print(f"  Offers received: {len(jobs)}")

        all_jobs.extend(jobs)

        if not jobs:
            print("  No more offers available.")
            break

    return {
        "count": total_count,
        "results": all_jobs,
    }


def save_raw_data(data, output_path):
    """Save raw API response as JSON."""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def main():
    number_of_pages = 5

    data = collect_jobs(number_of_pages)

    output_path = "data/raw/jobs_wroclaw_data_analyst.json"

    save_raw_data(data, output_path)

    print("\nCollection completed.")
    print(f"Total offers collected: {len(data['results'])}")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()