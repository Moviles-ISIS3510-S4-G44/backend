-- one row per listing that has been visited at least once.
-- exposes the delay from listing creation to first interaction (first visit)
-- and, when available, the time_to_publish_minutes for correlation analysis.

WITH first_visits AS (
    SELECT
        listing_id,
        MIN(first_interaction_at) AS first_visit_at
    FROM {{ ref('stg_user_listing_interactions') }}
    GROUP BY listing_id
)

SELECT
    l.listing_id,
    l.seller_id,
    l.title,
    l.condition,
    l.price,
    l.status,
    l.created_at,
    fv.first_visit_at,
    DATE_DIFF('minute', l.created_at, fv.first_visit_at) AS time_to_first_visit_minutes,
    DATE_DIFF('minute', l.created_at, fv.first_visit_at) / 60.0 AS time_to_first_visit_hours,
    DATE_DIFF('minute', l.created_at, fv.first_visit_at) / 1440.0 AS time_to_first_visit_days,
    ll.time_to_publish_minutes
FROM {{ ref('stg_listings') }} l
INNER JOIN first_visits fv
    ON fv.listing_id = l.listing_id
LEFT JOIN {{ ref('fact_listing_lifecycle') }} ll
    ON ll.listing_id = l.listing_id
WHERE fv.first_visit_at >= l.created_at
