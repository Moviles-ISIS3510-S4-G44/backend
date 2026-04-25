---
title: 2 - Listing Visit Coverage per Month (Type 3)
---

```sql monthly_visit_coverage
  select
      created_month,
      created_listings_count,
      listings_with_at_least_one_visit,
      percent_created_listings_with_visit
  from marketplace_andes.pct_created_listings_with_visit_per_month
  order by created_month
```

```sql monthly_visit_summary
  select
      count(*) as tracked_months,
      avg(percent_created_listings_with_visit) as avg_monthly_percentage,
      max(percent_created_listings_with_visit) as best_monthly_percentage,
      min(percent_created_listings_with_visit) as lowest_monthly_percentage
  from ${monthly_visit_coverage}
```

## Monthly Percentage of Created Listings with at Least One Visit

<LineChart
    data={monthly_visit_coverage}
    title="Visit Coverage for Listings Created per Month"
    x=created_month
    y=percent_created_listings_with_visit
    xAxisTitle="Created Month"
    yAxisTitle="Coverage (%)"
/>

## Summary

<DataTable data={monthly_visit_summary} rows=1>
    <Column id=tracked_months title="Months Tracked" />
    <Column id=avg_monthly_percentage title="Average Coverage (%)" />
    <Column id=best_monthly_percentage title="Best Month (%)" />
    <Column id=lowest_monthly_percentage title="Lowest Month (%)" />
</DataTable>

## Monthly Breakdown

<DataTable data={monthly_visit_coverage} rows=120>
    <Column id=created_month title="Created Month" />
    <Column id=created_listings_count title="Created Listings" />
    <Column id=listings_with_at_least_one_visit title="Listings with >=1 Visit" />
    <Column id=percent_created_listings_with_visit title="Coverage (%)" />
</DataTable>
