-- BQ5: Listing visits by weekday
-- Shows how listing visits are distributed across the seven days of the week.

WITH visits_base AS (
    SELECT
        user_id,
        listing_id,
        interaction_count,
        CAST(last_interaction_at AS DATE) AS visit_day,
        EXTRACT(dow FROM last_interaction_at) AS weekday_number
    FROM {{ ref('stg_user_listing_interaction') }}
    WHERE last_interaction_at IS NOT NULL
),

weekday_visits AS (
    SELECT
        visit_day,
        weekday_number,
        CASE
            WHEN weekday_number = 0 THEN 'Sunday'
            WHEN weekday_number = 1 THEN 'Monday'
            WHEN weekday_number = 2 THEN 'Tuesday'
            WHEN weekday_number = 3 THEN 'Wednesday'
            WHEN weekday_number = 4 THEN 'Thursday'
            WHEN weekday_number = 5 THEN 'Friday'
            WHEN weekday_number = 6 THEN 'Saturday'
        END AS weekday_name,
        SUM(interaction_count) AS total_visits
    FROM visits_base
    GROUP BY visit_day, weekday_number, weekday_name
)

SELECT
    visit_day,
    weekday_number,
    weekday_name,
    total_visits
FROM weekday_visits
ORDER BY visit_day, weekday_number