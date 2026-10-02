import os
import json
import requests
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")
BASE_URL = "https://api.adzuna.com/v1/api/jobs/pl/search"


def fetch_jobs(page, what, where, results_per_page=50):

    url = f"{BASE_URL}/{page}"

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": results_per_page,
        "what": what,
        "where": where,
        "content-type": "application/json",
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def collect_jobs(what, where, number_of_pages=5):
    all_jobs = []
    api_total_count = None

    for page in range(1, number_of_pages + 1):
        print(f"Fetching page {page}...")

        data = fetch_jobs(
            page=page,
            what=what,
            where=where
        )

        if api_total_count is None:
            api_total_count = data.get("count", 0)

        jobs = data.get("results", [])

        print(f"  Offers received: {len(jobs)}")
        all_jobs.extend(jobs)

        if not jobs:
            print("  No more offers available.")
            break

    return {
        "api_total_count": api_total_count,
        "results": all_jobs,
    }


def save_raw_data(data, output_path):
    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )


def main():
    number_of_pages = 5
    what = "data analyst"
    where = "Wroclaw"

    data = collect_jobs(
        what=what,
        where=where,
        number_of_pages=number_of_pages
    )

    today = datetime.now(
        ZoneInfo("Europe/Warsaw")
    ).strftime("%Y-%m-%d")

    output_path = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / today
        / "jobs_wroclaw_data_analyst.json"
    )

    save_raw_data(
        data,
        output_path
    )

    print("\nCollection completed.")
    print(f"Total offers collected: {len(data['results'])}")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()