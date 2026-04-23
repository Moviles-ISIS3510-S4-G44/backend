-- marts/fact_listing_views.sql
with interactions as (
    select * from {{ ref('stg_user_listing_interaction') }}
),

listings as (
    select * from {{ ref('stg_listings') }}
)

select
    i.interaction_id,
    i.user_id,
    i.listing_id,
    l.title,
    l.status,
    l.price,
    i.interaction_count,
    i.last_interaction_at,
    i.interaction_week,
    i.interaction_month
from interactions i
join listings l on i.listing_id = l.listing_id