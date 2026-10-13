-- This file contains a basic data analysis using SQL,
-- featuring WHERE, GROUP BY, aggregations, and JOINs.

-- 1. DAILY JOB MARKET SIZE
SELECT snapshot_date, COUNT(*) AS offers_visible
FROM job_snapshots
GROUP BY snapshot_date
ORDER BY snapshot_date ASC;

-- 2. DAILY JOB OFFER HISTORY
SELECT js.snapshot_date, j.id AS job_id, j.title
FROM job_snapshots js
INNER JOIN jobs j
    ON js.job_id = j.id
ORDER BY js.snapshot_date ASC, js.job_id ASC;

-- 3. JOB OFFERS BY CATEGORY
SELECT c.category_label, COUNT(j.id) AS offers_count
FROM categories c
LEFT JOIN jobs j
    ON c.category_id = j.category_id
GROUP BY c.category_label
ORDER BY offers_count DESC;

-- 4. JOB OFFERS BY COMPANY
SELECT c.company, COUNT(j.id) AS number_of_jobs
FROM companies c
LEFT JOIN jobs j
    ON c.company_id = j.company_id
GROUP BY c.company
ORDER BY number_of_jobs DESC;

-- 5. AVERAGE MINIMUM SALARY BY CATEGORY
SELECT
    c.category_label,
    ROUND(AVG(j.salary_min)) AS avg_salary_min,
    COUNT(j.id) FILTER (WHERE j.salary_min IS NOT NULL) AS offers_with_salary,
    COUNT(j.id) FILTER (WHERE j.salary_is_predicted = TRUE AND j.salary_min IS NOT NULL) AS predicted_salary_count
FROM categories c
LEFT JOIN jobs j
    ON c.category_id = j.category_id
GROUP BY c.category_label
ORDER BY offers_with_salary DESC;

--6. NEW JOB OFFERS FOR EACH DAY
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
GROUP BY first_seen_date
ORDER BY first_seen_date DESC;

-- 7. JOB OFFERS NO LONGER VISIBLE
SELECT
    yesterday.snapshot_date + INTERVAL '1 day' AS snapshot_date,
    COUNT(*) AS missing_offers
FROM job_snapshots AS yesterday
LEFT JOIN job_snapshots AS today
    ON yesterday.job_id = today.job_id
    AND today.snapshot_date = yesterday.snapshot_date + INTERVAL '1 day'
WHERE today.job_id IS NULL
    AND yesterday.snapshot_date < (
        SELECT MAX(snapshot_date)
        FROM job_snapshots
    )
GROUP BY yesterday.snapshot_date
ORDER BY yesterday.snapshot_date ASC;
