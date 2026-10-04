import os

import psycopg2
from dotenv import load_dotenv


load_dotenv()
LOCAL_DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

CLOUD_DB_CONFIG = {
    "host": os.getenv("CLOUD_DB_HOST"),
    "port": os.getenv("CLOUD_DB_PORT"),
    "database": os.getenv("CLOUD_DB_NAME"),
    "user": os.getenv("CLOUD_DB_USER"),
    "password": os.getenv("CLOUD_DB_PASSWORD")
}

local_connection = psycopg2.connect(
    **LOCAL_DB_CONFIG
)

cloud_connection = psycopg2.connect(
    **CLOUD_DB_CONFIG,
    sslmode="require"
)

local_cursor = local_connection.cursor()
cloud_cursor = cloud_connection.cursor()

tables = [
    "companies",
    "locations",
    "categories",
    "jobs"
]

for table in tables:

    local_cursor.execute(
        f"SELECT * FROM {table};"
    )

    rows = local_cursor.fetchall()

    if not rows:
        print(f"{table}: 0 rows")
        continue

    column_count = len(rows[0])

    placeholders = ", ".join(
        ["%s"] * column_count
    )

    query = f"""
        INSERT INTO {table}
        VALUES ({placeholders})
        ON CONFLICT DO NOTHING;
    """

    cloud_cursor.executemany(
        query,
        rows
    )

    print(
        f"{table}: {len(rows)} rows migrated"
    )

cloud_connection.commit()
local_cursor.close()
cloud_cursor.close()
local_connection.close()
cloud_connection.close()

print()
print("Migration completed successfully.")