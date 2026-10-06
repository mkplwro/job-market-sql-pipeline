# Job Market SQL Pipeline

An automated ETL pipeline that collects data analyst job postings in Wrocław from the [Adzuna API](https://developer.adzuna.com/), cleans them, and loads them into PostgreSQL for SQL analysis.

## How it works

```
Adzuna API → raw JSON → cleaning & transformation → processed CSV → data quality checks → PostgreSQL → SQL analysis
```

- **Collection** – raw API responses are saved as JSON files in date-based folders.
- **Transformation** – Python and Pandas clean the data and split it into related tables: jobs, companies, categories and locations.
- **Data quality** – checks for missing values, duplicates, wrong data types and inconsistent records run before loading.
- **Storage** – the data is loaded into a relational PostgreSQL database with `psycopg2`.
- **Automation** – GitHub Actions runs the full pipeline every day (06:17 UTC) and loads the data into a cloud PostgreSQL database.

## Tech stack

Python · Pandas · PostgreSQL · SQL · psycopg2 · REST API · GitHub Actions

## Project structure

```
├── .github/workflows/   # scheduled pipeline run
├── data/
│   ├── raw/             # raw JSON, grouped by date
│   └── processed/       # cleaned CSV files
├── sql/                 # analysis queries
├── src/                 # collector, transform, data quality, DB loading, pipeline
└── requirements.txt
```

## Getting started

```bash
git clone https://github.com/mkplwro/job-market-sql-pipeline.git
cd job-market-sql-pipeline
pip install -r requirements.txt
```

Create a `.env` file with your Adzuna API credentials and database connection details, then run:

```bash
python src/pipeline.py
```

## Example analysis

SQL queries cover job counts by company, category and location, salary statistics, and company-level metrics using `JOIN`s and aggregations.

## Roadmap

- Daily snapshots to track changes over time
- Stronger data quality validation
- Reporting and visualizations

## Status

In progress – new features are added regularly.