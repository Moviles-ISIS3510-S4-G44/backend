with source as (
    select * from {{ source('dlt_raw', 'listings') }}
),

renamed as (
    select
        id          as listing_id,
        seller_id,
        title,
        description,
        condition,
        price,
        status,
        created_at,
        updated_at
    from source
)

select * from renamed