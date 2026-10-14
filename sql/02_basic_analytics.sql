-- Basic data analysis using SQL: JOINs, GROUP BY, aggregates,
-- subqueries and date logic on daily snapshots.
-- Each query starts with the business question it answers.

-- 1. DAILY JOB MARKET SIZE
-- Is the number of open data analyst positions in Wrocław
-- growing, stable or shrinking?
SELECT snapshot_date, COUNT(*) AS offers_visible
FROM job_snapshots
GROUP BY snapshot_date
ORDER BY snapshot_date ASC;

-- 2. CURRENTLY VISIBLE OFFERS
-- Which data analyst offers can a candidate apply to right now,
-- and which ones are the newest?
SELECT j.id AS job_id, j.title, c.company, j.created::date AS posted_on
FROM job_snapshots js
JOIN jobs j ON j.id = js.job_id
LEFT JOIN companies c ON c.company_id = j.company_id
WHERE js.snapshot_date = (SELECT MAX(snapshot_date) FROM job_snapshots)
ORDER BY j.created DESC;

-- 3. JOB OFFERS BY CATEGORY
-- In which job categories is the demand for data analysts concentrated?
-- Scope: all offers collected so far (including expired ones).
SELECT c.category_label, COUNT(j.id) AS offers_count
FROM categories c
LEFT JOIN jobs j
    ON c.category_id = j.category_id
GROUP BY c.category_label
ORDER BY offers_count DESC;

-- 4. JOB OFFERS BY COMPANY
-- Which employers hire the most data analysts (top 10)?
-- Scope: all offers collected so far; a company re-posting the same role counts each posting.
SELECT c.company, COUNT(j.id) AS number_of_jobs
FROM companies c
LEFT JOIN jobs j
    ON c.company_id = j.company_id
GROUP BY c.company
ORDER BY number_of_jobs, c.company DESC
LIMIT 10;

-- 5. SALARY BY CATEGORY (real salaries only, predicted excluded)
-- How much do employers actually offer, and how does it differ by category?
-- Note: Average/median may mix units due to few offers, and one value appears to be an error against annual documentation ranges.

SELECT
    c.category_label,
    COUNT(*) AS offers_total,
    COUNT(*) FILTER (WHERE j.salary_min IS NOT NULL
                       AND j.salary_is_predicted = FALSE) AS offers_with_real_salary,
    ROUND(AVG(j.salary_min) FILTER (WHERE j.salary_is_predicted = FALSE)) AS avg_salary_min,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY j.salary_min)
        FILTER (WHERE j.salary_is_predicted = FALSE) AS median_salary_min
FROM jobs j
JOIN categories c ON c.category_id = j.category_id
GROUP BY c.category_label
ORDER BY offers_with_real_salary DESC;

-- 6. NEW JOB OFFERS FOR EACH DAY
-- How many new data analyst offers appear on the market each day?
-- The first collection day is excluded because it contains the initial stock, not new offers.
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
WHERE first_seen_date > (SELECT MIN(snapshot_date) FROM job_snapshots)
GROUP BY first_seen_date
ORDER BY first_seen_date ASC;

-- 7. OFFERS NO LONGER VISIBLE
-- How many offers leave the market each day, i.e. how fast do positions close?
-- Note: a disappearing offer was not necessarily filled (it may have expired or been removed).
SELECT last_seen + 1 AS disappeared_on, COUNT(*) AS offers_gone
FROM (
    SELECT job_id, MAX(snapshot_date) AS last_seen
    FROM job_snapshots
    GROUP BY job_id
) AS ls
WHERE last_seen < (SELECT MAX(snapshot_date) FROM job_snapshots)
GROUP BY last_seen
ORDER BY last_seen ASC;