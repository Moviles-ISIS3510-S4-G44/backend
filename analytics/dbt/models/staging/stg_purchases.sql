SELECT
    id          AS purchase_id,
    listing_id,
    buyer_id,
    price_at_purchase,
    purchased_at
FROM {{ source('dlt_raw', 'purchases') }}
