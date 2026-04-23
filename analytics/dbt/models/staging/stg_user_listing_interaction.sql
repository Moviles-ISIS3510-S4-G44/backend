SELECT
    id                  AS interaction_id,
    user_id,
    listing_id,
    interaction_count,
    last_interaction_at
FROM {{ source('dlt_raw', 'user_listing_interaction') }}
