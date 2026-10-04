import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("CLOUD_DB_HOST"),
    "port": os.getenv("CLOUD_DB_PORT"),
    "database": os.getenv("CLOUD_DB_NAME"),
    "user": os.getenv("CLOUD_DB_USER"),
    "password": os.getenv("CLOUD_DB_PASSWORD")
}

connection = psycopg2.connect(
    **DB_CONFIG,
    sslmode="require"
)
cursor = connection.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS companies (
        company_id INTEGER PRIMARY KEY,
        company VARCHAR(255)
    );
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS locations (
        location_id INTEGER PRIMARY KEY,
        name VARCHAR(255),
        latitude DOUBLE PRECISION,
        longitude DOUBLE PRECISION
    );
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY,
        category_label VARCHAR(255),
        category_tag VARCHAR(255)
    );
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS jobs (
        id BIGINT PRIMARY KEY,
        title VARCHAR(500),
        company_id INTEGER,
        location_id INTEGER,
        category_id INTEGER,
        salary_min NUMERIC(12, 2),
        salary_max NUMERIC(12, 2),
        salary_is_predicted BOOLEAN,
        contract_time VARCHAR(100),
        created TIMESTAMP WITH TIME ZONE,
        description TEXT,
        redirect_url TEXT,

        CONSTRAINT fk_jobs_company
            FOREIGN KEY (company_id)
            REFERENCES companies(company_id),

        CONSTRAINT fk_jobs_location
            FOREIGN KEY (location_id)
            REFERENCES locations(location_id),

        CONSTRAINT fk_jobs_category
            FOREIGN KEY (category_id)
            REFERENCES categories(category_id)
    );
    """
)

connection.commit()
cursor.close()
connection.close()

print("Cloud database tables created successfully.")