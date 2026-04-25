-- daily purchase count and revenue with cumulative running totals

WITH daily AS (
    SELECT
        CAST(purchased_at AS DATE)  AS day,
        COUNT(*)                    AS purchase_count,
        SUM(price_at_purchase)      AS revenue_cents
    FROM {{ ref('stg_purchases') }}
    GROUP BY 1
)

SELECT
    day,
    purchase_count,
    revenue_cents,
    revenue_cents / 100.0                               AS revenue,
    SUM(purchase_count) OVER (ORDER BY day)             AS cumulative_purchases,
    SUM(revenue_cents)  OVER (ORDER BY day) / 100.0     AS cumulative_revenue
FROM daily
ORDER BY day
