---
title: Active Listings per Day
---

```sql active_listings_daily
  select
      day,
      active_listings_count,
      sold_before_day_count
  from marketplace_andes.active_listings_per_day
  order by day desc
```

```sql active_listings_trend
  select
      day,
      active_listings_count
  from ${active_listings_daily}
  order by day
```

```sql active_listings_summary
  select
      count(*) as tracked_days,
      avg(active_listings_count) as avg_active_listings,
      max(active_listings_count) as peak_active_listings,
      min(active_listings_count) as min_active_listings
  from ${active_listings_daily}
```

## Active Listings Trend

<LineChart
    data={active_listings_trend}
    title="Active Listings Over Time"
    x=day
    y=active_listings_count
    xAxisTitle="Day"
    yAxisTitle="Active Listings"
/>

## Summary

<DataTable data={active_listings_summary} rows=1>
    <Column id=tracked_days title="Days Tracked" />
    <Column id=avg_active_listings title="Average Active" />
    <Column id=peak_active_listings title="Peak Active" />
    <Column id=min_active_listings title="Lowest Active" />
</DataTable>

## Daily Breakdown

<DataTable data={active_listings_daily} rows=60>
    <Column id=day title="Day" />
    <Column id=active_listings_count title="Active Listings" />
    <Column id=sold_before_day_count title="Sold Before Day" />
</DataTable>
