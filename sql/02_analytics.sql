-- ============================================================
-- 1. DAILY JOB MARKET SIZE
-- Business question:
-- How many job offers were visible on each day?
-- ============================================================

SELECT
    snapshot_date,
    COUNT(*) AS offers_visible
FROM job_snapshots
GROUP BY snapshot_date
ORDER BY snapshot_date ASC;


-- ============================================================
-- 2. DAILY JOB OFFER HISTORY
-- Business question:
-- Which job offers were visible on each day?
-- ============================================================

SELECT
    js.snapshot_date,
    j.id AS job_id,
    j.title
FROM job_snapshots js
LEFT JOIN jobs j
    ON js.job_id = j.id
ORDER BY
    js.snapshot_date ASC,
    js.job_id ASC;


-- ============================================================
-- 3. JOB OFFERS BY CATEGORY
-- Business question:
-- How many job offers belong to each category?
-- ============================================================

-- Query to be added


