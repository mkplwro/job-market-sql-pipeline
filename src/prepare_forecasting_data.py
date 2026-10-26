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
    """Return data/ml/forecasting_dataset_YYYY-MM-DD.csv for the given day (default: today)."""
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


def create_features(df):
    df = df.copy()

    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])

    df = df.sort_values("snapshot_date").reset_index(drop=True)

    df["lag_1"] = df["active_offers"].shift(1)
    df["lag_2"] = df["active_offers"].shift(2)
    df["lag_3"] = df["active_offers"].shift(3)
    df["lag_7"] = df["active_offers"].shift(7)

    # Rolling averages
    # shift(1) prevents data leakage:
    # the current day's value is NOT used to calculate the feature.
    df["rolling_mean_3"] = (
        df["active_offers"]
        .shift(1)
        .rolling(window=3)
        .mean()
    )

    df["rolling_mean_7"] = (
        df["active_offers"]
        .shift(1)
        .rolling(window=7)
        .mean()
    )

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

    print("Creating forecasting features...")

    df = create_features(df)

    print("\nDataset preview:")
    print(df.to_string(index=False))

    save_dataset(df)


if __name__ == "__main__":
    main()