-- Sprint 4: listings ranked by how many users favorited them.

SELECT
    f.listing_id,
    l.title,
    l.status,
    COUNT(*) AS favorite_count
FROM {{ ref('stg_user_listing_favorites') }} AS f
LEFT JOIN {{ ref('stg_listings') }} AS l ON f.listing_id = l.listing_id
GROUP BY f.listing_id, l.title, l.status
ORDER BY favorite_count DESC
