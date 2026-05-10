---
title: Sprint 4 — Favorites analytics
author: Isaac David
---

# Sprint 4 — Favorites analytics

**Author:** Isaac David

This notebook answers two questions: how favorite activity trends by day, and which listings accumulate the most saves.

## 1. Daily new favorites

How many new favorites are created per calendar day?

```sql daily_new_favorites
SELECT
    favorite_date,
    new_favorites
FROM marketplace_andes.daily_new_favorites
ORDER BY favorite_date
```

<BarChart
    data={daily_new_favorites}
    title="New favorites per day"
    x=favorite_date
    y=new_favorites
/>

## 2. Listings with the most favorites

Which listings have the highest favorite counts (with title and status)?

```sql listing_favorite_totals
SELECT
    listing_id,
    title,
    status,
    favorite_count
FROM marketplace_andes.listing_favorite_totals
ORDER BY favorite_count DESC
LIMIT 25
```

<DataTable data={listing_favorite_totals} rows=25>
</DataTable>
