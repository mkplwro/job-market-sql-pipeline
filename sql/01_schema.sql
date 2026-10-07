-- ============================================================
-- Job Market SQL Pipeline
-- Database schema
-- ============================================================


-- ============================================================
-- Companies
-- ============================================================

CREATE TABLE companies (
    company_id INTEGER PRIMARY KEY,
    company TEXT
);


-- ============================================================
-- Locations
-- ============================================================

CREATE TABLE locations (
    location_id INTEGER PRIMARY KEY,
    name TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
);


-- ============================================================
-- Categories
-- ============================================================

CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY,
    category_label TEXT,
    category_tag TEXT
);


-- ============================================================
-- Jobs
-- ============================================================

CREATE TABLE jobs (
    id BIGINT PRIMARY KEY,
    title TEXT NOT NULL,

    company_id INTEGER,
    location_id INTEGER,
    category_id INTEGER,

    salary_min DOUBLE PRECISION,
    salary_max DOUBLE PRECISION,
    salary_is_predicted BOOLEAN,
    contract_time TEXT,
    created TIMESTAMP,
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


-- ============================================================
-- Job snapshots
-- ============================================================

CREATE TABLE job_snapshots (
    job_id BIGINT NOT NULL,
    snapshot_date DATE NOT NULL,

    PRIMARY KEY (job_id, snapshot_date),

    CONSTRAINT fk_job_snapshots_job
        FOREIGN KEY (job_id)
        REFERENCES jobs(id)
);