-- Profile page views per seller (visited user) per calendar day.

WITH visits AS (
    SELECT
        CAST(visited_at AS DATE) AS visit_date,
        visited_user_id AS seller_user_id,
        COUNT(*) AS profile_visit_count
    FROM {{ ref('stg_profile_visit_events') }}
    WHERE visited_at IS NOT NULL
    GROUP BY CAST(visited_at AS DATE), visited_user_id
)
SELECT
    v.visit_date,
    v.seller_user_id,
    up.name AS seller_name,
    v.profile_visit_count
FROM visits v
LEFT JOIN {{ ref('stg_user_profiles') }} AS up ON v.seller_user_id = up.id
ORDER BY v.visit_date, v.seller_user_id
