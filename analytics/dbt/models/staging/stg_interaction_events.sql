SELECT
    id                   AS interaction_event_id,
    user_id,
    listing_id,
    last_interaction_at  AS interaction_timestamp
FROM {{ source('dlt_raw', 'user_listing_interaction') }}
