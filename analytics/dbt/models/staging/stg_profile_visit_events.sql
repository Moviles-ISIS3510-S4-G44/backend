-- One row per event id; DLT reloads can duplicate the same id in raw DuckDB.

SELECT
    profile_visit_event_id,
    visitor_user_id,
    visited_user_id,
    visited_at
FROM (
    SELECT
        id AS profile_visit_event_id,
        visitor_user_id,
        visited_user_id,
        visited_at,
        ROW_NUMBER() OVER (
            PARTITION BY id
            ORDER BY visited_at DESC NULLS LAST
        ) AS _rn
    FROM {{ source('dlt_raw', 'profile_visit_events') }}
) AS ranked
WHERE _rn = 1
