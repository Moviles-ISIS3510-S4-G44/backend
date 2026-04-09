# BQ5 — Average Time to Create and Publish a Listing

## Business Question

> What is the average time required for a seller to create and publish a listing?

**Classification:** Type 1 (operational metric) and Type 3 (workflow efficiency)

## Purpose

Measures how long the listing flow takes from the seller's creation action
until the listing reaches the `published` state.
Helps the team identify whether publishing is fast, slow, or blocked by
process issues, and quantifies listing lifecycle bottlenecks.

## Metric Definition

| Metric | Formula |
|--------|---------|
| `avg_minutes_to_publish` | `AVG(first_published_at - listing.created_at)` in minutes |
| `median_minutes_to_publish` | `MEDIAN(first_published_at - listing.created_at)` in minutes |

- **first_published_at** = earliest `changed_at` in `listing_status_history`
  where `to_status = 'published'` for a given listing.
- Listings that were never published are **excluded** from the average.

## Data Sources

| Table | Role |
|-------|------|
| `listings` | Provides `created_at` (listing creation timestamp) |
| `listing_status_history` | Provides lifecycle events; first `to_status = 'published'` row gives the publish timestamp |

## Pipeline Flow

```
PostgreSQL (listings, listing_status_history)
  → dlt (incremental extract)
    → DuckDB raw layer (marketplace_andes_analytics_raw)
      → dbt staging (stg_listings, stg_listing_status_history)
        → dbt marts (avg_time_to_publish, fact_listing_lifecycle)
```

## Query

```sql
WITH first_publish AS (
    SELECT
        listing_id,
        MIN(changed_at) AS first_published_at
    FROM listing_status_history
    WHERE to_status = 'published'
    GROUP BY listing_id
)
SELECT
    AVG(DATE_DIFF('minute', l.created_at, fp.first_published_at)) AS avg_minutes_to_publish
FROM listings l
INNER JOIN first_publish fp ON fp.listing_id = l.id
WHERE fp.first_published_at >= l.created_at;
```

## dbt Models

| Model | Layer | Materialization |
|-------|-------|-----------------|
| `stg_listings` | staging | view |
| `stg_listing_status_history` | staging | view |
| `avg_time_to_publish` | marts | table |
| `fact_listing_lifecycle` | marts | table |
