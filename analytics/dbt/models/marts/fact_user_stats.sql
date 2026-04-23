with user_base as (
    select
        u.user_id,
        u.created_at,
        u.updated_at,
        u.deleted_at,
        up.name,
        up.rating as star_rating,
        case when u.deleted_at is null then 'Active' else 'Churned' end as current_status,
        case when u.created_at >= (current_date - interval '30 days') then 1 else 0 end as is_new_user,
        case when u.deleted_at >= (current_date - interval '30 days') then 1 else 0 end as is_recent_churn
    from {{ ref('stg_users') }} u
    left join {{ ref('stg_user_profiles') }} up on u.user_id = up.user_id
)

select
    *,
    1 as user_count
from user_base