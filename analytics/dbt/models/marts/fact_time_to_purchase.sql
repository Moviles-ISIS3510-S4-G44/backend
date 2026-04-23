-- one row per purchased listing with time from first publication to purchase

WITH first_publish AS (
    SELECT
        listing_id,
        MIN(changed_at) AS first_published_at
    FROM {{ ref('stg_listing_status_history') }}
    WHERE to_status = 'published'
    GROUP BY listing_id
)

SELECT
    p.purchase_id,
    p.listing_id,
    p.buyer_id,
    p.price_at_purchase,
    p.purchased_at,
    l.seller_id,
    l.condition,
    l.title,
    l.created_at                                                            AS listing_created_at,
    fp.first_published_at,
    DATE_DIFF('minute', fp.first_published_at, p.purchased_at)              AS time_to_purchase_minutes,
    DATE_DIFF('minute', fp.first_published_at, p.purchased_at) / 60.0      AS time_to_purchase_hours,
    DATE_DIFF('minute', fp.first_published_at, p.purchased_at) / 1440.0    AS time_to_purchase_days
FROM {{ ref('stg_purchases') }} p
INNER JOIN {{ ref('stg_listings') }} l
    ON l.listing_id = p.listing_id
INNER JOIN first_publish fp
    ON fp.listing_id = p.listing_id
WHERE fp.first_published_at <= p.purchased_at
