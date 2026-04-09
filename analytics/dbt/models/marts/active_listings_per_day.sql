-- BQ6: active listings count by day
-- Active if first published happened by day OR listing existed and was not sold before day.

WITH listing_events AS (
    SELECT
        l.listing_id,
        CAST(l.created_at AS DATE) AS created_day,
        MIN(CASE WHEN h.to_status = 'published' THEN CAST(h.changed_at AS DATE) END) AS first_published_day,
        MIN(CASE WHEN h.to_status = 'sold' THEN CAST(h.changed_at AS DATE) END) AS first_sold_day
    FROM {{ ref('stg_listings') }} l
    LEFT JOIN {{ ref('stg_listing_status_history') }} h
        ON h.listing_id = l.listing_id
    GROUP BY 1, 2
),

bounds AS (
    SELECT
        MIN(created_day) AS min_day,
        GREATEST(
            MAX(COALESCE(first_sold_day, CURRENT_DATE)),
            CURRENT_DATE
        ) AS max_day
    FROM listing_events
),

date_spine AS (
    SELECT CAST(day AS DATE) AS day
    FROM bounds
    CROSS JOIN generate_series(min_day, max_day, INTERVAL 1 DAY) AS t(day)
),

daily_flags AS (
    SELECT
        d.day,
        le.listing_id,
        CASE
            WHEN (
                le.first_published_day IS NOT NULL
                AND le.first_published_day <= d.day
            )
            OR (
                le.created_day <= d.day
                AND (
                    le.first_sold_day IS NULL
                    OR le.first_sold_day >= d.day
                )
            )
            THEN 1
            ELSE 0
        END AS is_active,
        CASE
            WHEN le.first_sold_day IS NOT NULL AND le.first_sold_day < d.day THEN 1
            ELSE 0
        END AS sold_before_day
    FROM date_spine d
    INNER JOIN listing_events le
        ON le.created_day <= d.day
)

SELECT
    day,
    SUM(is_active) AS active_listings_count,
    SUM(sold_before_day) AS sold_before_day_count
FROM daily_flags
GROUP BY day
ORDER BY day
