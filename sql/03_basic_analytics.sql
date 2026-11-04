-- 1. DAILY JOB MARKET SIZE
-- How many offers were visible on each collection day?
SELECT
    snapshot_date,
    COUNT(DISTINCT job_id) AS offers_visible
FROM job_snapshots
GROUP BY snapshot_date
ORDER BY snapshot_date ASC;

-- 2. COLLECTED VS CURRENTLY VISIBLE OFFERS
-- How many offers have been collected in total,
-- and how many of them were visible on the latest collection day?
SELECT
    (SELECT COUNT(*) FROM jobs) AS offers_collected_total,
    (
        SELECT COUNT(DISTINCT job_id)
        FROM job_snapshots
        WHERE snapshot_date = (
            SELECT MAX(snapshot_date)
            FROM job_snapshots
        )
    ) AS offers_visible_latest_day;


-- 3. JOB OFFERS BY LOCATION
-- Which locations have the most collected offers?
-- Scope: all offers collected so far. Offers without a location are excluded.
SELECT
    l.name AS location,
    COUNT(j.id) AS offers_count
FROM locations l
LEFT JOIN jobs j
    ON l.location_id = j.location_id
WHERE l.name IS NOT NULL
GROUP BY l.name
ORDER BY offers_count DESC, l.name ASC
LIMIT 10;


-- 4. JOB OFFERS BY COMPANY
-- Which employers have the most collected Data Analyst offers?
-- Scope: all offers collected so far. Offers without a company name are excluded.
SELECT
    c.company,
    COUNT(j.id) AS number_of_jobs
FROM companies c
LEFT JOIN jobs j
    ON c.company_id = j.company_id
WHERE c.company IS NOT NULL
GROUP BY c.company
ORDER BY number_of_jobs DESC, c.company ASC
LIMIT 10;


-- 5. SALARY ANALYSIS
-- What salary levels are available in the collected offers?
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


-- 6. MISSING DATA OVERVIEW
-- How many collected offers have no company, no location or no salary?
-- Useful for judging how reliable the other results are.
SELECT
    COUNT(*) AS offers_total,
    COUNT(*) FILTER (WHERE c.company IS NULL) AS missing_company,
    COUNT(*) FILTER (WHERE l.name IS NULL) AS missing_location,
    COUNT(*) FILTER (WHERE j.salary_min IS NULL) AS missing_salary
FROM jobs j
LEFT JOIN companies c
    ON c.company_id = j.company_id
LEFT JOIN locations l
    ON l.location_id = j.location_id;


-- 7. NEW JOB OFFERS FOR EACH DAY
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


-- 8. OFFERS NO LONGER VISIBLE
-- On which day were offers last seen before they stopped appearing?
-- Only offers absent from the latest collection day are counted.
-- A disappeared offer is not necessarily a filled position:
-- it may also have dropped out of the API results.
SELECT
    last_seen AS last_seen_date,
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
ORDER BY last_seen ASC;