-- distribution of seller_rating values given by buyers after purchases

WITH rated AS (
    SELECT seller_rating
    FROM {{ ref('stg_purchases') }}
    WHERE seller_rating IS NOT NULL
),

total AS (
    SELECT COUNT(*) AS n FROM rated
)

SELECT
    r.seller_rating                                             AS rating,
    COUNT(*)                                                    AS rating_count,
    ROUND(COUNT(*) * 100.0 / t.n, 1)                           AS rating_pct,
    COUNT(*) FILTER (WHERE r.seller_rating IS NOT NULL)         AS rated_purchases,
    (SELECT COUNT(*) FROM {{ ref('stg_purchases') }})           AS total_purchases,
    t.n                                                         AS total_rated
FROM rated r
CROSS JOIN total t
GROUP BY r.seller_rating, t.n
ORDER BY r.seller_rating
