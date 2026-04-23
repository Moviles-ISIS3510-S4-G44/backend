with base as (
    select * from {{ ref('fact_listing_views') }}
),

historic as (
    select
        listing_id,
        title,
        category_name,
        sum(interaction_count) as total_views,
        'historic'             as period_type,
        null::date             as period_value
    from base
    group by listing_id, title, category_name
),

weekly as (
    select
        listing_id,
        title,
        category_name,
        sum(interaction_count) as total_views,
        'week'                 as period_type,
        interaction_week       as period_value
    from base
    group by listing_id, title, category_name, interaction_week
),

monthly as (
    select
        listing_id,
        title,
        category_name,
        sum(interaction_count) as total_views,
        'month'                as period_type,
        interaction_month      as period_value
    from base
    group by listing_id, title, category_name, interaction_month
)

select * from historic
union all
select * from weekly
union all
select * from monthly