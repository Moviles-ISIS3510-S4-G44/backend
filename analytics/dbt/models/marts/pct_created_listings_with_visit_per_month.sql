-- BQ Type 3: % of listings created each month that have at least one visit

WITH created_listings AS (
    SELECT
        listing_id,
        CAST(DATE_TRUNC('month', created_at) AS DATE) AS created_month
    FROM {{ ref('stg_listings') }}
),

visited_listings AS (
    SELECT DISTINCT
        listing_id
    FROM {{ ref('stg_user_listing_interaction') }}
    WHERE interaction_count >= 1
)

SELECT
    cl.created_month,
    COUNT(*) AS created_listings_count,
    COUNT(vl.listing_id) AS listings_with_at_least_one_visit,
    ROUND(
        CASE
            WHEN COUNT(*) = 0 THEN 0
            ELSE (COUNT(vl.listing_id) * 100.0) / COUNT(*)
        END,
        2
    ) AS percent_created_listings_with_visit
FROM created_listings cl
LEFT JOIN visited_listings vl
    ON vl.listing_id = cl.listing_id
GROUP BY cl.created_month
ORDER BY cl.created_month DESC
