WITH rated_users AS (
    SELECT
        user_key,
        email,
        name,
        star_rating,
        current_status
    FROM {{ ref('fact_user_stats') }}
    WHERE star_rating IS NOT NULL
      AND star_rating BETWEEN 1 AND 5
      AND current_status = 'Active'
)

SELECT
    user_key,
    email,
    name,
    star_rating,
    REPEAT('★', star_rating) || REPEAT('☆', 5 - star_rating) AS stars_display,
    RANK() OVER (ORDER BY star_rating DESC) AS reputation_rank
FROM rated_users
ORDER BY reputation_rank, email
