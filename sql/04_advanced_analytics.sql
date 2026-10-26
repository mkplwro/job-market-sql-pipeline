-- Advanced data analysis using SQL: CASE WHEN, CTEs and window functions.
-- Each query starts with the business question it answers.
-- These queries complement the basic ones and do not repeat them.

-- 1. SALARY AVAILABILITY
-- How many offers have no salary, a salary predicted by Adzuna, or a salary not marked as predicted?
SELECT
    CASE
        WHEN salary_min IS NULL THEN 'No salary'
        WHEN salary_is_predicted = TRUE THEN 'Predicted by Adzuna'
        ELSE 'Stated by employer'
    END AS salary_status,
    COUNT(*) AS offers_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM jobs), 1) AS share_pct
FROM jobs
GROUP BY salary_status
ORDER BY offers_count DESC;

-- 2. DAILY CHANGE IN VISIBLE JOB OFFERS
-- Did the number of visible offers go up or down compared
-- with the previous collection day?
WITH daily_offers AS (
    SELECT
        snapshot_date,
        COUNT(*) AS offers_visible
    FROM job_snapshots
    GROUP BY snapshot_date
)
SELECT
    snapshot_date,
    offers_visible,
    offers_visible - LAG(offers_visible) OVER (
        ORDER BY snapshot_date
    ) AS daily_change
FROM daily_offers
ORDER BY snapshot_date;

-- 3. OFFERS BY SENIORITY LEVEL
-- How many offers are aimed at senior, mid and entry-level ones?
SELECT
    CASE
        WHEN title ILIKE '%senior%'
          OR title ILIKE '%lead%' THEN 'Senior / lead'
        WHEN title ILIKE '%junior%'
          OR title ILIKE '%associate%'
          OR title ILIKE '%trainee%' THEN 'Junior / entry-level'
        ELSE 'Level not stated'
    END AS seniority_level,
    COUNT(*) AS offers_count
FROM jobs
GROUP BY seniority_level
ORDER BY offers_count DESC;

-- 4. COMPANIES WITH MORE OFFERS THAN THE AVERAGE
-- Which companies post more offers than a typical company?
WITH company_offers AS (
    SELECT
        c.company,
        COUNT(j.id) AS number_of_jobs
    FROM companies c
    LEFT JOIN jobs j
        ON c.company_id = j.company_id
    GROUP BY c.company_id, c.company
),
company_vs_average AS (
    SELECT
        company,
        number_of_jobs,
        AVG(number_of_jobs) OVER () AS avg_jobs_per_company
    FROM company_offers
)
SELECT
    company,
    number_of_jobs,
    ROUND(avg_jobs_per_company, 2) AS avg_jobs_per_company
FROM company_vs_average
WHERE number_of_jobs > avg_jobs_per_company
ORDER BY number_of_jobs DESC, company;

-- 5. AGE OF CURRENTLY VISIBLE OFFERS
-- Are the offers on the market fresh, or have they been open for a long time?
-- Age = days between the posting date and the latest collection day.
WITH visible_offers AS (
    SELECT
        j.id,
        js.snapshot_date - j.created::date AS age_days
    FROM job_snapshots js
    JOIN jobs j ON j.id = js.job_id
    WHERE js.snapshot_date = (SELECT MAX(snapshot_date) FROM job_snapshots)
)
SELECT
    CASE
        WHEN age_days <= 7 THEN '0-7 days'
        WHEN age_days <= 30 THEN '8-30 days'
        ELSE 'Over 30 days'
    END AS offer_age,
    COUNT(*) AS offers_count
FROM visible_offers
GROUP BY offer_age
ORDER BY MIN(age_days);