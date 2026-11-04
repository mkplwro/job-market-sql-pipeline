CREATE OR REPLACE VIEW job_analytics AS
SELECT
    j.id AS job_id,
    j.title,
    c.company,
    l.name AS location,
    l.latitude,
    l.longitude,

    CASE
        WHEN j.title ~* '\m(senior|sr\.?|lead|principal|staff)\M'
          OR j.title ~* '(starszy|starsza|starsze)'
            THEN 'Senior'
        WHEN j.title ~* '\m(junior|jr\.?|intern|internship|trainee|graduate|student)\M'
          OR j.title ~* '(młodszy|młodsza|młodsze)'
            THEN 'Junior'
        WHEN j.title ~* '\m(mid|mid-level|regular|intermediate)\M'
            THEN 'Mid'
        ELSE 'Unknown'
    END AS seniority_level,

    CASE
        WHEN concat_ws(' ', j.title, j.description) ~*
            '(hybrid|hybrydow|model hybrydowy)'
            THEN 'Hybrid'
        WHEN concat_ws(' ', j.title, j.description) ~*
            '(remote|remotely|work from home|home office|zdaln|praca z domu)'
            THEN 'Remote'
        WHEN concat_ws(' ', j.title, j.description) ~*
            '(on-site|onsite|on site|in-office|in office|stacjonarn)'
            THEN 'On-site'
        ELSE 'Unknown'
    END AS work_mode,

    j.salary_min,
    j.salary_max,

    CASE
        WHEN j.salary_min IS NOT NULL
          OR j.salary_max IS NOT NULL
            THEN TRUE
        ELSE FALSE
    END AS has_salary,

    CASE
        WHEN j.salary_min IS NOT NULL
          AND j.salary_max IS NOT NULL
          AND j.salary_min <= j.salary_max
            THEN (j.salary_min + j.salary_max) / 2
        ELSE NULL
    END AS salary_midpoint,

    j.salary_is_predicted,
    j.contract_time,
    j.created,
    s.snapshot_date,
    j.redirect_url

FROM jobs j
LEFT JOIN companies c
    ON j.company_id = c.company_id
LEFT JOIN locations l
    ON j.location_id = l.location_id
LEFT JOIN job_snapshots s
    ON j.id = s.job_id;
