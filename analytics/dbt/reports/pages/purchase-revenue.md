---
title: Purchase Revenue
---

## Business question

**How is daily purchase revenue and transaction volume trending?**

This page tracks every completed purchase over time, showing how much revenue
the marketplace generates each day and how transaction volume accumulates.
It helps gauge marketplace growth and identify high-activity periods.

```sql daily_revenue
  select
      day,
      purchase_count,
      revenue,
      cumulative_purchases,
      cumulative_revenue
  from marketplace_andes.daily_purchase_revenue
  order by day
```

```sql revenue_summary
  select
      sum(purchase_count)                   as total_purchases,
      sum(revenue)                          as total_revenue,
      avg(revenue)                          as avg_daily_revenue,
      max(revenue)                          as peak_daily_revenue,
      min(day)                              as first_sale_day,
      max(day)                              as last_sale_day
  from ${daily_revenue}
```

## Headline numbers

<BigValue data={revenue_summary} value=total_purchases title="Total purchases" />
<BigValue data={revenue_summary} value=total_revenue title="Total revenue" fmt="usd2" />
<BigValue data={revenue_summary} value=avg_daily_revenue title="Avg daily revenue" fmt="usd2" />
<BigValue data={revenue_summary} value=peak_daily_revenue title="Peak daily revenue" fmt="usd2" />

## Daily revenue trend

<LineChart
    data={daily_revenue}
    title="Daily Purchase Revenue"
    x=day
    y=revenue
    xAxisTitle="Day"
    yAxisTitle="Revenue"
/>

## Daily transaction volume

<LineChart
    data={daily_revenue}
    title="Daily Transaction Count"
    x=day
    y=purchase_count
    xAxisTitle="Day"
    yAxisTitle="Purchases"
/>

## Cumulative revenue

<LineChart
    data={daily_revenue}
    title="Cumulative Revenue Over Time"
    x=day
    y=cumulative_revenue
    xAxisTitle="Day"
    yAxisTitle="Cumulative Revenue"
/>

## Daily breakdown

<DataTable data={daily_revenue} rows=60>
    <Column id=day title="Day" />
    <Column id=purchase_count title="Purchases" />
    <Column id=revenue title="Revenue" fmt="usd2" />
    <Column id=cumulative_purchases title="Cumulative Purchases" />
    <Column id=cumulative_revenue title="Cumulative Revenue" fmt="usd2" />
</DataTable>
