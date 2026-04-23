-- one row per listing with visit count during first 3 days
WITH visits_in_first_3_days AS (
    SELECT
        ie.listing_id,
        COUNT(*) AS visit_count,
        COUNT(DISTINCT ie.user_id) AS unique_visitor_count,
        MIN(ie.interaction_timestamp) AS first_visit_at,
        MAX(ie.interaction_timestamp) AS last_visit_at
    FROM {{ ref('stg_interaction_events') }} ie
    INNER JOIN {{ ref('stg_listings') }} l
        ON ie.listing_id = l.listing_id
    WHERE DATE_DIFF('day', l.created_at, ie.interaction_timestamp) < 3
    GROUP BY ie.listing_id
)

SELECT
    l.listing_id,
    l.seller_id,
    l.title,
    l.condition,
    l.price,
    l.created_at,
    COALESCE(vf.visit_count, 0) AS visits_first_3_days,
    COALESCE(vf.unique_visitor_count, 0) AS unique_visitors_first_3_days,
    vf.first_visit_at,
    vf.last_visit_at
FROM {{ ref('stg_listings') }} l
LEFT JOIN visits_in_first_3_days vf
    ON l.listing_id = vf.listing_id
ORDER BY l.created_at DESC
