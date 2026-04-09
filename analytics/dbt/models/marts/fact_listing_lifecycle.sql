-- Fact table: one row per published listing with time-to-publish metric.
-- Supports BQ5 aggregation and per-seller drill-down.

WITH first_publish AS (
    SELECT
        listing_id,
        MIN(changed_at) AS first_published_at
    FROM {{ ref('stg_listing_status_history') }}
    WHERE to_status = 'published'
    GROUP BY listing_id
)

SELECT
    l.listing_id,
    l.seller_id,
    l.title,
    l.condition,
    l.price,
    l.created_at,
    fp.first_published_at,
    DATE_DIFF('minute', l.created_at, fp.first_published_at) AS time_to_publish_minutes
FROM {{ ref('stg_listings') }} l
INNER JOIN first_publish fp
    ON fp.listing_id = l.listing_id
WHERE fp.first_published_at >= l.created_at
