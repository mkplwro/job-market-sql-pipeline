# Job Market SQL Pipeline

An automated data pipeline for collecting, processing, storing, and analyzing job market data from the Adzuna API.

The project combines **Python, SQL, PostgreSQL, ETL, data quality checks, and GitHub Actions** to build a continuously updated dataset of job-market information.

## Project Overview

The goal of the project is to create a production-style data pipeline that collects real-world job advertisements and transforms them into a structured relational database suitable for SQL analysis.

The pipeline currently focuses on job advertisements and related entities such as:

* jobs
* companies
* categories
* locations

Raw API responses are preserved as historical JSON files, while processed datasets are transformed into structured CSV files and loaded into PostgreSQL.

## Pipeline

```text
Adzuna API
     │
     ▼
Data Collection
     │
     ▼
Raw JSON Data
     │
     ▼
Data Cleaning & Transformation
     │
     ▼
Processed CSV Data
     │
     ▼
PostgreSQL Database
     │
     ▼
SQL Analysis
```

## Technologies

* **Python**
* **Pandas**
* **PostgreSQL**
* **SQL**
* **psycopg2**
* **REST API**
* **Git / GitHub**
* **GitHub Actions**
* **CSV / JSON**

## Main Components

### Data Collection

The project uses the **Adzuna API** to collect job-market data.

The collector stores raw API responses in date-based directories, allowing the original data to be preserved and used for further processing.

### Data Transformation

Raw API responses are cleaned and transformed using Python and Pandas.

The transformation process includes:

* cleaning raw job data
* standardizing fields
* extracting companies, categories and locations
* preparing relational datasets
* assigning identifiers for database relationships

### PostgreSQL Database

Processed data is loaded into a PostgreSQL database using Python and `psycopg2`.

The database is designed as a relational model with separate entities for jobs, companies, categories and locations.

### SQL Analysis

The `sql/` directory contains SQL queries used to explore and analyze the collected job-market data.

The analysis covers areas such as:

* job distribution by company
* job distribution by category
* salary statistics
* location analysis
* company-level metrics
* aggregation and filtering
* relational queries using `JOIN`

## Data Structure

The project separates raw and processed data:

```text
data/
├── raw/
│   ├── YYYY-MM-DD/
│   │   └── jobs_*.json
│   └── ...
│
└── processed/
    ├── categories.csv
    ├── companies.csv
    ├── jobs_clean.csv
    ├── jobs_prepared.csv
    ├── jobs_with_company_id.csv
    └── locations.csv
```

Raw data is preserved separately from processed datasets to make the pipeline easier to reproduce and debug.

## Repository Structure

```text
job-market-sql-pipeline/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── requirements/
│
├── sql/
│
├── src/
│   ├── collector.py
│   ├── create_cloud_tables.py
│   ├── data_quality.py
│   ├── explore_data.py
│   ├── load_to_database.py
│   ├── migrate_local_to_cloud.py
│   ├── pipeline.py
│   ├── prepare_database.py
│   ├── test_api.py
│   ├── test_cloud_database.py
│   └── transform_data.py
│
└── README.md
```

## Automation

The project is designed to run as an automated pipeline rather than as a one-time data collection script.

GitHub Actions is used to automate recurring data collection and pipeline execution.

This allows the dataset to grow over time as new job advertisements are collected.

## Data Quality

The pipeline includes dedicated data-quality checks to identify potential issues before data is loaded into the database.

Examples include checking for:

* missing values
* duplicated records
* unexpected data types
* invalid or incomplete records
* consistency between processed datasets

## Project Goals

The project is being developed incrementally with a focus on practical data engineering skills.

Planned development includes:

* expanding SQL analysis
* implementing historical/daily snapshots
* improving data quality validation
* expanding job-market queries
* strengthening database design
* improving pipeline automation
* adding analytical reporting and visualizations

## Learning Focus

This project is also designed as a practical portfolio project for developing skills in:

* SQL
* PostgreSQL
* relational database design
* ETL pipelines
* API data ingestion
* data cleaning
* data quality
* Python data processing
* workflow automation
* GitHub Actions
* analytical problem solving
