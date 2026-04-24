-- BQ: Most viewed listings by week, month, monthly ranking, and historically.

WITH visits_base AS (
    SELECT
        uli.listing_id,
        l.title AS listing_title,
        CAST(uli.last_interaction_at AS DATE) AS visit_day,
        uli.interaction_count
    FROM {{ ref('stg_user_listing_interaction') }} uli
    LEFT JOIN {{ ref('stg_listings') }} l
        ON uli.listing_id = l.listing_id
    WHERE uli.last_interaction_at IS NOT NULL
),

weekly_views AS (
    SELECT
        'week' AS period_type,
        DATE_TRUNC('week', visit_day) AS period_start,
        listing_id,
        listing_title,
        SUM(interaction_count) AS total_views
    FROM visits_base
    GROUP BY 1, 2, 3, 4
),

monthly_views AS (
    SELECT
        'month' AS period_type,
        DATE_TRUNC('month', visit_day) AS period_start,
        listing_id,
        listing_title,
        SUM(interaction_count) AS total_views
    FROM visits_base
    GROUP BY 1, 2, 3, 4
),

historic_views AS (
    SELECT
        'historic' AS period_type,
        NULL AS period_start,
        listing_id,
        listing_title,
        SUM(interaction_count) AS total_views
    FROM visits_base
    GROUP BY 1, 2, 3, 4
),

combined AS (
    SELECT * FROM weekly_views
    UNION ALL
    SELECT * FROM monthly_views
    UNION ALL
    SELECT * FROM historic_views
),

ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY period_type, period_start
            ORDER BY total_views DESC
        ) AS ranking
    FROM combined
)

SELECT
    period_type,
    period_start,
    listing_id,
    listing_title,
    total_views,
    ranking
FROM ranked
ORDER BY period_type, period_start, ranking