-- One row per profile id; raw mirror can duplicate the same user id.

SELECT
    id,
    name,
    rating
FROM (
    SELECT
        p.*,
        ROW_NUMBER() OVER (PARTITION BY p.id ORDER BY p.name) AS _rn
    FROM {{ source('dlt_raw', 'user_profiles') }} AS p
) AS ranked
WHERE _rn = 1
