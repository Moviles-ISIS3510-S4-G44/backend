SELECT
    id          AS event_id,
    listing_id,
    from_status,
    to_status,
    changed_at
FROM {{ source('dlt_raw', 'listing_status_history') }}
