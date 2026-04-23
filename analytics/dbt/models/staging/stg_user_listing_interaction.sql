with source as (
    select * from {{ source('dlt_raw', 'user_listing_interaction') }}
),

renamed as (
    select
        id                  as interaction_id,
        user_id,
        listing_id,
        interaction_count,
        last_interaction_at,
        date_trunc('week',  last_interaction_at)::date as interaction_week,
        date_trunc('month', last_interaction_at)::date as interaction_month
    from source
)

select * from renamed