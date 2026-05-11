---
title: Profile visits by seller (daily)
author: Isaac
---

# Profile visits by seller

**Author:** Isaac

Seller profile views recorded in `profile_visit_events`, aggregated per calendar day and per visited user (seller).

## Daily profile traffic (marketplace total)

```sql daily_profile_visit_totals
SELECT
    visit_date,
    SUM(profile_visit_count) AS total_visits
FROM marketplace_andes.daily_profile_visits_by_seller
GROUP BY visit_date
ORDER BY visit_date
```

<BarChart
    data={daily_profile_visit_totals}
    title="Profile visits per day (sum across sellers)"
    x=visit_date
    y=total_visits
    xAxisTitle="Date"
    yAxisTitle="Visits"
/>

## By seller and day

```sql daily_profile_visits
SELECT
    visit_date,
    seller_user_id,
    seller_name,
    profile_visit_count
FROM marketplace_andes.daily_profile_visits_by_seller
ORDER BY visit_date DESC, profile_visit_count DESC
```

<DataTable data={daily_profile_visits} rows=50>
    <Column id=visit_date title="Date" contentType=date />
    <Column id=seller_user_id title="Seller (user id)" contentType=text />
    <Column id=seller_name title="Seller name" />
    <Column id=profile_visit_count title="Profile visits" />
</DataTable>
