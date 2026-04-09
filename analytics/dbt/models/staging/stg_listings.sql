SELECT
    id          AS listing_id,
    seller_id,
    title,
    description,
    condition,
    price,
    status,
    created_at,
    updated_at
FROM {{ source('dlt_raw', 'listings') }}
