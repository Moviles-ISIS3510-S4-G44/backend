SELECT
    id          AS interaction_id,
    listing_id,
    user_id,
    interaction_count,
    first_interaction_at,
    last_interaction_at
FROM {{ source('dlt_raw', 'user_listing_interaction') }}
