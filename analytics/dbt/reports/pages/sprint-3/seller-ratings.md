---
title: Seller Ratings
---

## Business question

**How are buyers rating sellers after purchases?**

This page looks at every `seller_rating` recorded on a completed purchase and
measures how buyers evaluate their experience. It shows rating coverage (what
share of purchases have been rated), the full 1–5 distribution, and the
average score — helping identify whether sellers are trusted and whether
the rating feature is being used.

```sql rating_dist
  select
      rating,
      rating_count,
      rating_pct,
      total_purchases,
      total_rated
  from marketplace_andes.seller_rating_dist
  order by rating
```

```sql rating_summary
  select
      max(total_purchases)                          as total_purchases,
      max(total_rated)                              as rated_purchases,
      max(total_purchases) - max(total_rated)       as unrated_purchases,
      round(max(total_rated) * 100.0
            / nullif(max(total_purchases), 0), 1)   as rating_coverage_pct,
      round(sum(rating * rating_count)
            / nullif(sum(rating_count), 0), 2)      as avg_seller_rating
  from ${rating_dist}
```

```sql rating_coverage
  select 'Rated' as bucket, max(total_rated) as purchases
  from ${rating_dist}
  union all
  select 'Unrated', max(total_purchases) - max(total_rated)
  from ${rating_dist}
```

## Headline numbers

<BigValue data={rating_summary} value=total_purchases title="Total purchases" />
<BigValue data={rating_summary} value=rated_purchases title="Purchases rated" />
<BigValue data={rating_summary} value=rating_coverage_pct title="Rating coverage (%)" fmt="num1" />
<BigValue data={rating_summary} value=avg_seller_rating title="Avg seller rating" fmt="num2" />

## Rating distribution

<BarChart
    data={rating_dist}
    x=rating
    y=rating_count
    title="Seller ratings given by buyers (1–5)"
    xAxisTitle="Rating"
    yAxisTitle="Purchases"
/>

## Distribution with percentages

<DataTable data={rating_dist} rows=5>
    <Column id=rating title="Rating" />
    <Column id=rating_count title="Count" />
    <Column id=rating_pct title="Share (%)" fmt="num1" />
</DataTable>

## Rating coverage

<BarChart
    data={rating_coverage}
    x=bucket
    y=purchases
    title="Purchases: rated vs unrated"
    xAxisTitle=""
    yAxisTitle="Purchases"
/>
