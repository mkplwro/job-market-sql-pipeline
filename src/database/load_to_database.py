
from pathlib import Path
import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv

from datetime import datetime
from zoneinfo import ZoneInfo


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(ENV_PATH)

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "jobs_clean.csv"
)

DB_CONFIG = {
    "host": os.getenv("CLOUD_DB_HOST"),
    "port": os.getenv("CLOUD_DB_PORT"),
    "database": os.getenv("CLOUD_DB_NAME"),
    "user": os.getenv("CLOUD_DB_USER"),
    "password": os.getenv("CLOUD_DB_PASSWORD")
}

df = pd.read_csv(INPUT_PATH)

if df.empty:
    raise ValueError("CSV is empty. Database update aborted.")

if df["id"].isna().any():
    raise ValueError("CSV contains missing job IDs.")

if df["id"].duplicated().any():
    raise ValueError("CSV contains duplicate job IDs.")

snapshot_job_ids = df["id"].astype(int).tolist()

df["salary_is_predicted"] = df["salary_is_predicted"].astype(bool)
df = df.astype(object).where(pd.notna(df), None)

print(f"Jobs in today's CSV: {len(df)}")
print(f"Unique snapshot jobs: {len(snapshot_job_ids)}")

snapshot_date = datetime.now(
    ZoneInfo("Europe/Warsaw")
).date()

connection = psycopg2.connect(
    **DB_CONFIG,
    sslmode="require"
)

cursor = connection.cursor()

try:
    for company in df["company"].dropna().unique():

        cursor.execute(
            """
            SELECT company_id
            FROM companies
            WHERE company = %s;
            """,
            (company,)
        )

        exists = cursor.fetchone()

        if exists is None:

            cursor.execute(
                """
                SELECT COALESCE(MAX(company_id), 0) + 1
                FROM companies;
                """
            )

            next_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO companies (
                    company_id,
                    company
                )
                VALUES (%s, %s);
                """,
                (next_id, company)
            )

    for _, row in (
        df[
            ["location", "latitude", "longitude"]
        ]
        .drop_duplicates()
        .iterrows()
    ):

        cursor.execute(
            """
            SELECT location_id
            FROM locations
            WHERE name = %s
              AND latitude IS NOT DISTINCT FROM %s
              AND longitude IS NOT DISTINCT FROM %s;
            """,
            (
                row["location"],
                row["latitude"],
                row["longitude"]
            )
        )

        exists = cursor.fetchone()

        if exists is None:

            cursor.execute(
                """
                SELECT COALESCE(MAX(location_id), 0) + 1
                FROM locations;
                """
            )

            next_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO locations (
                    location_id,
                    name,
                    latitude,
                    longitude
                )
                VALUES (%s, %s, %s, %s);
                """,
                (
                    next_id,
                    row["location"],
                    row["latitude"],
                    row["longitude"]
                )
            )

    for _, row in (
        df[
            ["category_label", "category_tag"]
        ]
        .drop_duplicates()
        .iterrows()
    ):

        cursor.execute(
            """
            SELECT category_id
            FROM categories
            WHERE category_label = %s
              AND category_tag = %s;
            """,
            (
                row["category_label"],
                row["category_tag"]
            )
        )

        exists = cursor.fetchone()

        if exists is None:

            cursor.execute(
                """
                SELECT COALESCE(MAX(category_id), 0) + 1
                FROM categories;
                """
            )

            next_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO categories (
                    category_id,
                    category_label,
                    category_tag
                )
                VALUES (%s, %s, %s);
                """,
                (
                    next_id,
                    row["category_label"],
                    row["category_tag"]
                )
            )

    cursor.execute(
        "SELECT company_id, company FROM companies;"
    )

    company_map = {
        company: company_id
        for company_id, company in cursor.fetchall()
    }

    cursor.execute(
        """
        SELECT location_id, name, latitude, longitude
        FROM locations;
        """
    )

    location_map = {
        (
            name,
            latitude,
            longitude
        ): location_id
        for location_id, name, latitude, longitude
        in cursor.fetchall()
    }

    cursor.execute(
        """
        SELECT category_id, category_label, category_tag
        FROM categories;
        """
    )

    category_map = {
        (
            category_label,
            category_tag
        ): category_id
        for category_id, category_label, category_tag
        in cursor.fetchall()
    }

    cursor.execute(
        "SELECT id FROM jobs;"
    )

    existing_ids = {
        row[0]
        for row in cursor.fetchall()
    }

    new_jobs = df[
        ~df["id"].isin(existing_ids)
    ].copy()

    print(f"New jobs to insert: {len(new_jobs)}")

    for _, row in new_jobs.iterrows():

        company_id = company_map.get(
            row["company"]
        )

        location_id = location_map.get(
            (
                row["location"],
                row["latitude"],
                row["longitude"]
            )
        )

        category_id = category_map.get(
            (
                row["category_label"],
                row["category_tag"]
            )
        )

        cursor.execute(
            """
            INSERT INTO jobs (
                id,
                title,
                company_id,
                location_id,
                category_id,
                salary_min,
                salary_max,
                salary_is_predicted,
                contract_time,
                created,
                description,
                redirect_url
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s
            );
            """,
            (
                row["id"],
                row["title"],
                company_id,
                location_id,
                category_id,
                row["salary_min"],
                row["salary_max"],
                row["salary_is_predicted"],
                row["contract_time"],
                row["created"],
                row["description"],
                row["redirect_url"]
            )
        )

    print(f"Replacing snapshot for {snapshot_date}...")

    cursor.execute(
        """
        DELETE FROM job_snapshots
        WHERE snapshot_date = %s;
        """,
        (snapshot_date,)
    )

    snapshots_deleted = cursor.rowcount

    cursor.executemany(
        """
        INSERT INTO job_snapshots (
            job_id,
            snapshot_date
        )
        VALUES (%s, %s);
        """,
        [
            (job_id, snapshot_date)
            for job_id in snapshot_job_ids
        ]
    )

    snapshots_inserted = len(snapshot_job_ids)

    cursor.execute(
        """
        SELECT
            COUNT(*),
            COUNT(DISTINCT job_id)
        FROM job_snapshots
        WHERE snapshot_date = %s;
        """,
        (snapshot_date,)
    )

    total_rows, unique_jobs = cursor.fetchone()

    if total_rows != snapshots_inserted:
        raise ValueError(
            f"Snapshot validation failed: "
            f"expected {snapshots_inserted}, got {total_rows}."
        )

    if unique_jobs != snapshots_inserted:
        raise ValueError(
            f"Duplicate jobs detected: "
            f"expected {snapshots_inserted}, got {unique_jobs}."
        )

    connection.commit()

    print()
    print("Database load completed successfully.")
    print(f"New jobs inserted: {len(new_jobs)}")
    print(f"Previous snapshots deleted: {snapshots_deleted}")
    print(f"Current snapshots inserted: {snapshots_inserted}")
    print(f"Snapshot validation: {total_rows} rows, {unique_jobs} unique jobs")

except Exception as error:

    connection.rollback()

    print()
    print("Database load failed.")
    print("All database changes were rolled back.")
    print(f"Error: {error}")

    raise

finally:

    cursor.close()
    connection.close()
