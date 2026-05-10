SELECT
    id          AS favorite_id,
    user_id,
    listing_id,
    created_at
FROM {{ source('dlt_raw', 'user_listing_favorite') }}
