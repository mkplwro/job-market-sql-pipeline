
import os
from datetime import date
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = Path("data/ml")
FILE_PREFIX = "forecasting_dataset"


def get_output_path(run_date=None):
    run_date = run_date or date.today()
    return OUTPUT_DIR / f"{FILE_PREFIX}_{run_date:%Y-%m-%d}.csv"


def get_connection():
    return psycopg2.connect(
        host=os.getenv("CLOUD_DB_HOST"),
        port=os.getenv("CLOUD_DB_PORT", "5432"),
        dbname=os.getenv("CLOUD_DB_NAME"),
        user=os.getenv("CLOUD_DB_USER"),
        password=os.getenv("CLOUD_DB_PASSWORD"),
        sslmode="require",
    )


def load_daily_active_offers():
    query = """
        SELECT
            snapshot_date,
            COUNT(DISTINCT job_id) AS active_offers
        FROM job_snapshots
        GROUP BY snapshot_date
        ORDER BY snapshot_date;
    """

    conn = get_connection()

    try:
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()

    return df


def save_dataset(df):
    output_path = get_output_path()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        output_path,
        index=False,
        date_format="%Y-%m-%d",
    )

    print(f"Forecasting dataset saved to: {output_path}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    return output_path


def main():
    print("Loading daily active offers from PostgreSQL...")

    df = load_daily_active_offers()

    if df.empty:
        raise ValueError("No snapshot data found in job_snapshots.")

    print(f"Loaded {len(df)} daily observations.")

    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])
    df = df.sort_values("snapshot_date").reset_index(drop=True)

    print("\nRaw dataset preview:")
    print(df.to_string(index=False))

    save_dataset(df)


if __name__ == "__main__":
    main()
