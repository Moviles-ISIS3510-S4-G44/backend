---
title: Most Viewed Listings
---

# Most Viewed Listings

This dashboard identifies the most viewed listing by week, by month, across each month, and historically.

## Most Viewed Listing This Week

```sql most_viewed_week
SELECT
    listing_title,
    total_views
FROM marketplace_andes_analytics.most_viewed_listings
WHERE period_type = 'week'
ORDER BY period_start DESC, ranking
LIMIT 1
```

<DataTable data={most_viewed_week} />

## Most Viewed Listing This Month

```sql most_viewed_month
SELECT
    listing_title,
    total_views
FROM marketplace_andes_analytics.most_viewed_listings
WHERE period_type = 'month'
ORDER BY period_start DESC, ranking
LIMIT 1
```

<DataTable data={most_viewed_month} />

## Most Viewed Listing by Month

```sql most_viewed_by_month
SELECT
    period_start,
    listing_title,
    total_views
FROM marketplace_andes_analytics.most_viewed_listings
WHERE period_type = 'month'
  AND ranking = 1
ORDER BY period_start
```

<BarChart
    data={most_viewed_by_month}
    x=period_start
    y=total_views
    series=listing_title
/>

## Historical Most Viewed Listing

```sql most_viewed_historic
SELECT
    listing_title,
    total_views
FROM marketplace_andes_analytics.most_viewed_listings
WHERE period_type = 'historic'
ORDER BY ranking
LIMIT 1
```

<DataTable data={most_viewed_historic} />