-- single-row summary statistics of time_to_first_visit_minutes
-- across all listings that have been visited at least once.

SELECT
    COUNT(*)                                                            AS n_listings,
    AVG(time_to_first_visit_minutes)                                    AS mean_minutes,
    STDDEV(time_to_first_visit_minutes)                                 AS stddev_minutes,
    MIN(time_to_first_visit_minutes)                                    AS min_minutes,
    MAX(time_to_first_visit_minutes)                                    AS max_minutes,
    QUANTILE_CONT(time_to_first_visit_minutes, 0.25)                    AS p25_minutes,
    QUANTILE_CONT(time_to_first_visit_minutes, 0.50)                    AS median_minutes,
    QUANTILE_CONT(time_to_first_visit_minutes, 0.75)                    AS p75_minutes,
    QUANTILE_CONT(time_to_first_visit_minutes, 0.90)                    AS p90_minutes,
    QUANTILE_CONT(time_to_first_visit_minutes, 0.99)                    AS p99_minutes
FROM {{ ref('fact_listing_first_visit') }}
