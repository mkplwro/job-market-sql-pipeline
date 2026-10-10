-- ============================================================
-- 1. DAILY JOB MARKET SIZE
-- How many job offers were visible on each day?
SELECT snapshot_date, COUNT(*) AS offers_visible
FROM job_snapshots
GROUP BY snapshot_date
ORDER BY snapshot_date ASC;

-- ============================================================
-- 2. DAILY JOB OFFER HISTORY
-- Which job offers were visible on each day?
SELECT js.snapshot_date, j.id AS job_id, j.title
FROM job_snapshots js
LEFT JOIN jobs j
    ON js.job_id = j.id
ORDER BY js.snapshot_date ASC, js.job_id ASC;

-- ============================================================
-- 3. JOB OFFERS BY CATEGORY
-- How many job offers belong to each category?
SELECT c.category_label, COUNT(j.id) AS offers_count
FROM categories c
LEFT JOIN jobs j
    ON c.category_id = j.category_id
GROUP BY c.category_label;

-- ============================================================
-- 4. JOB OFFERS BY COMPANY
-- How many job offers does each company have?
SELECT c.company, COUNT(j.id) AS number_of_jobs
FROM companies c
LEFT JOIN jobs j
    ON c.company_id = j.company_id
GROUP BY c.company
ORDER BY number_of_jobs DESC;

-- ============================================================
-- 5. AVERAGE MINIMUM SALARY BY CATEGORY
-- What is the average minimum salary for each category?
SELECT c.category_label, AVG(j.salary_min) AS avg_salary_min
FROM categories c
JOIN jobs j
    ON c.category_id = j.category_id
GROUP BY c.category_label;

-- ============================================================