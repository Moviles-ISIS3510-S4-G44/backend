---
title: Listing Visits in First 3 Days
---

```sql visits_first_3_days_data
  select
      listing_id,
      seller_id,
      title,
      condition,
      price,
      created_at,
      visits_first_3_days,
      unique_visitors_first_3_days,
      first_visit_at,
      last_visit_at
  from marketplace_andes.fact_listing_visits_first_3_days
  order by visits_first_3_days desc
```

```sql visits_summary_stats
  select
      count(*) as total_listings,
      sum(case when visits_first_3_days > 0 then 1 else 0 end) as listings_with_visits,
      round(avg(visits_first_3_days), 2) as avg_visits,
      round(max(visits_first_3_days), 2) as max_visits,
      round(min(visits_first_3_days), 2) as min_visits,
      round(median(visits_first_3_days), 2) as median_visits
  from ${visits_first_3_days_data}
```

```sql visits_by_condition
  select
      condition,
      count(*) as listing_count,
      round(avg(visits_first_3_days), 2) as avg_visits,
      round(max(visits_first_3_days), 2) as max_visits
  from ${visits_first_3_days_data}
  group by condition
  order by avg_visits desc
```

## Summary Statistics

<DataTable data={visits_summary_stats} rows=1>
    <Column id=total_listings title="Total Listings" />
    <Column id=listings_with_visits title="Listings with Visits" />
    <Column id=avg_visits title="Average Visits" />
    <Column id=median_visits title="Median Visits" />
    <Column id=max_visits title="Max Visits" />
</DataTable>

## Visits by Condition

<BarChart
    data={visits_by_condition}
    title="Average Visits by Listing Condition"
    x=condition
    y=avg_visits
    xAxisTitle="Condition"
    yAxisTitle="Average Visits"
/>

## Top Listings by Visits

<DataTable data={visits_first_3_days_data} rows=50>
    <Column id=listing_id title="Listing ID" contentType=text />
    <Column id=title title="Title" />
    <Column id=condition title="Condition" />
    <Column id=price title="Price" contentType=currency />
    <Column id=visits_first_3_days title="Visits (First 3d)" />
    <Column id=unique_visitors_first_3_days title="Unique Visitors" />
    <Column id=created_at title="Created" contentType=date />
</DataTable>
