---
title: User Retention Overview
---

```sql user_status_distribution
  select
      current_status,
      sum(user_count) as total_count
  from marketplace_andes.fact_user_stats
  group by current_status
  order by total_count desc
```

```sql user_status_distribution_pie
  select
      current_status as name,
      total_count as value
  from ${user_status_distribution}
```

```sql user_volatility
  select
      'New (30d)' as metric,
      sum(is_new_user) as value
  from marketplace_andes.fact_user_stats
  union all
  select
      'Churned (30d)' as metric,
      sum(is_recent_churn) as value
  from marketplace_andes.fact_user_stats
```

## Current User Status Distribution

<ECharts config={
    {
        tooltip: {
            formatter: '{b}: {c} ({d}%)'
        },
        series: [
            {
                type: 'pie',
                data: [...user_status_distribution_pie],
            }
        ]
    }
}
/>

<BarChart
    data={user_volatility}
    title="User Volatility (Last 30 Days)"
    x=metric
    y=value
/>

## Business Questions

### Sprint 2

- [Best Reputation Students](best-reputation)
- [Active Listings per Day](active-listings-per-day)

### Sprint 3

- [2 - Listing Visit Coverage per Month (Type 3)](listing-visit-coverage-per-month)
- [3 - Time to First Visit (Type 3)](time-to-first-visit)