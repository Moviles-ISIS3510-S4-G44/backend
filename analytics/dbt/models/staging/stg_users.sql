-- One row per user; DLT raw can contain duplicate keys across incremental loads.

SELECT
    id,
    email,
    created_at,
    updated_at,
    deleted_at
FROM (
    SELECT
        u.*,
        ROW_NUMBER() OVER (
            PARTITION BY u.id
            ORDER BY u.updated_at DESC NULLS LAST
        ) AS _rn
    FROM {{ source('dlt_raw', 'users') }} AS u
) AS ranked
WHERE _rn = 1
