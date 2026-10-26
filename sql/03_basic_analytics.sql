-- Job Market SQL Pipeline
-- Basic data analysis using SQL:
-- JOINs, GROUP BY, aggregates, subqueries and date logic.
-- Each query starts with the business question it answers.
-- Scope: Data Analyst job offers across Poland.

-- 1. DAILY JOB MARKET SIZE
-- How many offers were visible on each day?
SELECT
    snapshot_date,
    COUNT(DISTINCT job_id) AS offers_visible
FROM job_snapshots
GROUP BY snapshot_date
ORDER BY snapshot_date ASC;


-- 2. CURRENTLY VISIBLE OFFERS
-- Which Data Analyst offers were collected most recently?
SELECT
    j.id AS job_id,
    j.title,
    c.company,
    l.name AS location,
    j.created::date AS posted_on
FROM job_snapshots js
JOIN jobs j
    ON j.id = js.job_id
LEFT JOIN companies c
    ON c.company_id = j.company_id
LEFT JOIN locations l
    ON l.location_id = j.location_id
WHERE js.snapshot_date = (
    SELECT MAX(snapshot_date)
    FROM job_snapshots
)
ORDER BY j.created DESC;


-- 3. JOB OFFERS BY CATEGORY
-- In which job categories are the collected offers concentrated?
-- Scope: all offers collected so far, including older offers.
SELECT
    c.category_label,
    COUNT(j.id) AS offers_count
FROM categories c
LEFT JOIN jobs j
    ON c.category_id = j.category_id
GROUP BY c.category_label
ORDER BY offers_count DESC;


-- 4. JOB OFFERS BY COMPANY
-- Which employers have the most collected Data Analyst offers?
-- Scope: all offers collected so far.
SELECT
    c.company,
    COUNT(j.id) AS number_of_jobs
FROM companies c
LEFT JOIN jobs j
    ON c.company_id = j.company_id
GROUP BY c.company
ORDER BY number_of_jobs DESC, c.company ASC
LIMIT 10;


-- 5. SALARY ANALYSIS
-- What salary ranges are available in the collected offers?
-- Predicted salaries are excluded from the salary calculations.
SELECT
    COUNT(*) AS offers_total,
    COUNT(*) FILTER (
        WHERE salary_min IS NOT NULL
          AND salary_is_predicted = FALSE
    ) AS offers_with_real_salary,
    ROUND(
        AVG(salary_min) FILTER (
            WHERE salary_is_predicted = FALSE
        )
    ) AS avg_salary_min,
    PERCENTILE_CONT(0.5) WITHIN GROUP (
        ORDER BY salary_min
    ) FILTER (
        WHERE salary_is_predicted = FALSE
    ) AS median_salary_min
FROM jobs;


-- 6. NEW JOB OFFERS FOR EACH DAY
-- How many offers were first observed on each day?
-- The first collection day is excluded because it represents
-- the initial set of offers, not newly observed offers.
SELECT
    first_seen_date AS snapshot_date,
    COUNT(*) AS new_offers
FROM (
    SELECT
        job_id,
        MIN(snapshot_date) AS first_seen_date
    FROM job_snapshots
    GROUP BY job_id
) AS first_seen
WHERE first_seen_date > (
    SELECT MIN(snapshot_date)
    FROM job_snapshots
)
GROUP BY first_seen_date
ORDER BY first_seen_date ASC;


-- 7. OFFERS NO LONGER VISIBLE
-- How many offers disappeared between collection days?
-- A disappeared offer is not necessarily a filled position.
SELECT
    last_seen + 1 AS disappeared_on,
    COUNT(*) AS offers_gone
FROM (
    SELECT
        job_id,
        MAX(snapshot_date) AS last_seen
    FROM job_snapshots
    GROUP BY job_id
) AS ls
WHERE last_seen < (
    SELECT MAX(snapshot_date)
    FROM job_snapshots
)
GROUP BY last_seen
ORDER BY disappeared_on ASC;