-- Job Market SQL Pipeline
-- Database schema (PostgreSQL)
--
-- companies, locations, categories - dimension tables filled by the pipeline
-- jobs                             - one row per unique offer
-- job_snapshots                    - which offers were visible on which day
-- job_analytics                    - analytical view created in 01_job_analytics.sql

-- Companies
CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY,
    company     TEXT UNIQUE
);

-- Locations
CREATE TABLE IF NOT EXISTS locations (
    location_id INTEGER PRIMARY KEY,
    name        TEXT,
    latitude    DOUBLE PRECISION,
    longitude   DOUBLE PRECISION
);

-- Categories
CREATE TABLE IF NOT EXISTS categories (
    category_id    INTEGER PRIMARY KEY,
    category_label TEXT,
    category_tag   TEXT UNIQUE
);

-- Jobs
CREATE TABLE IF NOT EXISTS jobs (
    id                  BIGINT PRIMARY KEY,
    title               TEXT NOT NULL,
    company_id          INTEGER,
    location_id         INTEGER,
    category_id         INTEGER,
    salary_min          DOUBLE PRECISION,  -- lower bound of salary range (PLN per year)
    salary_max          DOUBLE PRECISION,  -- upper bound of salary range (PLN per year)
    salary_is_predicted BOOLEAN,           -- TRUE = estimated by Adzuna
    contract_time       TEXT,
    created             TIMESTAMP,         -- offer publication date (UTC)
    description         TEXT,
    redirect_url        TEXT,

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

-- Job snapshots
CREATE TABLE IF NOT EXISTS job_snapshots (
    job_id        BIGINT NOT NULL,
    snapshot_date DATE NOT NULL,

    PRIMARY KEY (job_id, snapshot_date),

    CONSTRAINT fk_job_snapshots_job
        FOREIGN KEY (job_id)
        REFERENCES jobs(id)
);

-- Index for queries filtering or grouping snapshots by date
CREATE INDEX IF NOT EXISTS idx_job_snapshots_date
    ON job_snapshots (snapshot_date);

-- Analytical view
-- Created separately by running 01_job_analytics.sql.
-- The view combines job, company, location and snapshot data
-- and adds analytical fields such as seniority_level,
-- work_mode, has_salary and salary_midpoint.