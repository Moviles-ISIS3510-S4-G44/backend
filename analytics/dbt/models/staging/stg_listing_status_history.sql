-- staging/stg_listing_status_history.sql
with source as (
    select * from {{ source('dlt_raw', 'listing_status_history') }}
),

renamed as (
    select
        id          as event_id,
        listing_id,
        from_status,
        to_status,
        changed_at,
        date_trunc('month', changed_at)::date as changed_month
    from source
    )

select * from renamed