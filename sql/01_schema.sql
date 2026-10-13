-- Job Market SQL Pipeline
-- Database schema (PostgreSQL)
--
-- companies, locations, categories - dimension tables filled by the pipeline
-- jobs                             - one row per unique offer (all offers collected so far)
-- job_snapshots                    - which offers were visible on which day

-- Companies
CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY,
    company    TEXT UNIQUE
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
    salary_min          DOUBLE PRECISION,  -- lower bound of the stated salary range (PLN per year)
    salary_max          DOUBLE PRECISION,  -- upper bound of the stated salary range (PLN per year)
    salary_is_predicted BOOLEAN,           -- TRUE = estimated by Adzuna, not stated by the employer
    contract_time       TEXT,
    created             TIMESTAMP,         -- when the offer was posted (UTC)
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

-- Speeds up queries that filter or group by day only
CREATE INDEX IF NOT EXISTS idx_job_snapshots_date ON job_snapshots (snapshot_date);