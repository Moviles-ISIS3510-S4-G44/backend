WITH user_base AS (
    SELECT 
        id AS user_key,
        username,
        created_at,
        updated_at,
        deleted_at,
        -- Status Logic
        CASE WHEN deleted_at IS NULL THEN 'Active' ELSE 'Churned' END AS current_status,
        -- Logic for "New in last 30 days"
        CASE WHEN created_at >= (CURRENT_DATE - INTERVAL '30 days') THEN 1 ELSE 0 END AS is_new_user,
        -- Logic for "Deleted in last 30 days"
        CASE WHEN deleted_at >= (CURRENT_DATE - INTERVAL '30 days') THEN 1 ELSE 0 END AS is_recent_churn
    FROM {{ source('dlt_raw', 'users') }}
)

SELECT 
    *,
    1 AS user_count
FROM user_base