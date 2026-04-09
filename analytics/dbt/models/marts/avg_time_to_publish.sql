-- BQ5: Average time required for a seller to create and publish a listing
-- Computes the elapsed time between listing creation and first publication.
-- Listings that were never published are excluded from the average.

WITH first_publish AS (
    SELECT
        listing_id,
        MIN(changed_at) AS first_published_at
    FROM {{ ref('stg_listing_status_history') }}
    WHERE to_status = 'published'
    GROUP BY listing_id
)

SELECT
    COUNT(*)                                                                     AS published_listing_count,
    AVG(DATE_DIFF('minute', l.created_at, fp.first_published_at))                AS avg_minutes_to_publish,
    MEDIAN(DATE_DIFF('minute', l.created_at, fp.first_published_at))             AS median_minutes_to_publish,
    MIN(DATE_DIFF('minute', l.created_at, fp.first_published_at))                AS min_minutes_to_publish,
    MAX(DATE_DIFF('minute', l.created_at, fp.first_published_at))                AS max_minutes_to_publish
FROM {{ ref('stg_listings') }} l
INNER JOIN first_publish fp
    ON fp.listing_id = l.listing_id
WHERE fp.first_published_at >= l.created_at
