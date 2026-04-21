WITH user_base AS (
    SELECT
        u.id AS user_key,
        u.email,
        u.created_at,
        u.updated_at,
        u.deleted_at,
        up.name,
        up.rating AS star_rating,
        -- Status Logic
        CASE WHEN u.deleted_at IS NULL THEN 'Active' ELSE 'Churned' END AS current_status,
        -- Logic for "New in last 30 days"
        CASE WHEN u.created_at >= (CURRENT_DATE - INTERVAL '30 days') THEN 1 ELSE 0 END AS is_new_user,
        -- Logic for "Deleted in last 30 days"
        CASE WHEN u.deleted_at >= (CURRENT_DATE - INTERVAL '30 days') THEN 1 ELSE 0 END AS is_recent_churn
    FROM {{ source('dlt_raw', 'users') }} u
    LEFT JOIN {{ source('dlt_raw', 'user_profiles') }} up ON u.id = up.id
)

SELECT
    *,
    1 AS user_count
FROM user_base
