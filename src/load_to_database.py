from pathlib import Path
import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv

from datetime import datetime
from zoneinfo import ZoneInfo


PROJECT_ROOT = Path(__file__).resolve().parent.parent

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

df["salary_is_predicted"] = df["salary_is_predicted"].astype(bool)
df = df.astype(object).where(pd.notna(df), None)

print(f"Jobs in today's CSV: {len(df)}")

snapshot_date = datetime.now(
    ZoneInfo("Europe/Warsaw")
).date()

connection = psycopg2.connect(
    **DB_CONFIG,
    sslmode="require"
)

cursor = connection.cursor()

# ============================================================
# COMPANIES
# ============================================================
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

# ============================================================
# LOCATIONS
# ============================================================
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

# ============================================================
# CATEGORIES
# ============================================================
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

# ============================================================
# ID MAPING
# ============================================================
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

# ============================================================
# NEW JOBS
# ============================================================
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

# ============================================================
# JOB SNAPSHOTS
# ============================================================
snapshots_inserted = 0
for job_id in df["id"].dropna().unique():

    cursor.execute(
        """
        INSERT INTO job_snapshots (
            job_id,
            snapshot_date
        )
        VALUES (%s, %s)
        ON CONFLICT (job_id, snapshot_date)
        DO NOTHING;
        """,
        (
            int(job_id),
            snapshot_date
        )
    )

    if cursor.rowcount == 1:
        snapshots_inserted += 1


print(
    f"Snapshots inserted: {snapshots_inserted}"
)

# ============================================================
# COMMIT
# ============================================================
connection.commit()

cursor.close()
connection.close()

print()
print("Database load completed.")
print(f"New jobs inserted: {len(new_jobs)}")
print(f"New snapshots inserted: {snapshots_inserted}")