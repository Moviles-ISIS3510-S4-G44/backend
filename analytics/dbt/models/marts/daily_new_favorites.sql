-- Sprint 4: count of new favorites per calendar day (from favorite created_at).

SELECT
    CAST(created_at AS DATE) AS favorite_date,
    COUNT(*) AS new_favorites
FROM {{ ref('stg_user_listing_favorites') }}
WHERE created_at IS NOT NULL
GROUP BY CAST(created_at AS DATE)
ORDER BY favorite_date
