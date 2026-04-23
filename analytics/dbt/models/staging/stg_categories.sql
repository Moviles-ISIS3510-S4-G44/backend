with source as (
    select * from {{ source('dlt_raw', 'categories') }}
),

renamed as (
    select
        id   as category_id,
        name as category_name,
        created_at,
        updated_at
    from source
)

select * from renamed