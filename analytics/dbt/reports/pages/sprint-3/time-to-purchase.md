---
title: Time to Purchase
---

## Business question

**How quickly do published listings get sold?**

This page measures the time between a listing's first publication and the moment
it is purchased. It helps identify whether the marketplace converts published
inventory quickly, how wide the spread is, and whether item condition affects
how fast listings sell.

```sql purchase_listings
  select
      listing_id,
      condition,
      price_at_purchase,
      first_published_at,
      purchased_at,
      time_to_purchase_minutes,
      time_to_purchase_hours,
      time_to_purchase_days
  from marketplace_andes.fact_time_to_purchase
  where time_to_purchase_minutes is not null
    and time_to_purchase_minutes >= 0
```

```sql purchase_summary
  select
      n_purchases,
      mean_minutes,
      stddev_minutes,
      min_minutes,
      p25_minutes,
      median_minutes,
      p75_minutes,
      p90_minutes,
      p99_minutes,
      max_minutes
  from marketplace_andes.dist_time_to_purchase
```

## Headline numbers

<BigValue data={purchase_summary} value=n_purchases title="Purchases measured" />
<BigValue data={purchase_summary} value=median_minutes title="Median (minutes)" fmt="num2" />
<BigValue data={purchase_summary} value=p90_minutes title="p90 (minutes)" fmt="num2" />
<BigValue data={purchase_summary} value=mean_minutes title="Mean (minutes)" fmt="num2" />

## Distribution (minutes)

<Histogram
    data={purchase_listings}
    x=time_to_purchase_minutes
    title="Time from publication to purchase (minutes)"
    xAxisTitle="Minutes between first publish and purchase"
    yAxisTitle="Listings"
/>

## Distribution (hours, log-friendly)

<Histogram
    data={purchase_listings}
    x=time_to_purchase_hours
    title="Time from publication to purchase (hours)"
    xAxisTitle="Hours between first publish and purchase"
    yAxisTitle="Listings"
/>

## Box plot by condition

```sql purchase_box_by_condition
  select
      coalesce(condition, '(unknown)') as condition,
      quantile_cont(time_to_purchase_hours, 0.05) as p05,
      quantile_cont(time_to_purchase_hours, 0.25) as q1,
      quantile_cont(time_to_purchase_hours, 0.50) as median,
      quantile_cont(time_to_purchase_hours, 0.75) as q3,
      quantile_cont(time_to_purchase_hours, 0.95) as p95,
      count(*) as n_listings
  from marketplace_andes.fact_time_to_purchase
  where time_to_purchase_hours is not null
  group by 1
  order by median
```

<ECharts config={
    {
        tooltip: {
            trigger: 'item',
            formatter: (params) => {
                const v = params.value;
                return [
                    `<b>${params.name}</b>`,
                    `p05: ${Number(v[1]).toFixed(2)} h`,
                    `q1:  ${Number(v[2]).toFixed(2)} h`,
                    `med: ${Number(v[3]).toFixed(2)} h`,
                    `q3:  ${Number(v[4]).toFixed(2)} h`,
                    `p95: ${Number(v[5]).toFixed(2)} h`,
                ].join('<br/>');
            }
        },
        grid: { left: 80, right: 40, top: 40, bottom: 80 },
        xAxis: {
            type: 'category',
            data: [...purchase_box_by_condition.map(r => r.condition)],
            name: 'Condition',
            nameLocation: 'middle',
            nameGap: 40,
            axisLabel: { rotate: 20 }
        },
        yAxis: {
            type: 'value',
            name: 'Hours to purchase',
            nameLocation: 'middle',
            nameGap: 60,
            scale: true
        },
        series: [
            {
                type: 'boxplot',
                name: 'Hours to purchase',
                data: [...purchase_box_by_condition.map(r => [
                    Number(r.p05),
                    Number(r.q1),
                    Number(r.median),
                    Number(r.q3),
                    Number(r.p95)
                ])],
                itemStyle: { color: '#86efac', borderColor: '#15803d' }
            }
        ]
    }
}
/>

## By-condition summary

```sql purchase_by_condition
  select
      coalesce(condition, '(unknown)') as condition,
      count(*) as purchases,
      avg(time_to_purchase_hours) as avg_hours,
      quantile_cont(time_to_purchase_hours, 0.5) as median_hours,
      quantile_cont(time_to_purchase_hours, 0.9) as p90_hours
  from marketplace_andes.fact_time_to_purchase
  group by 1
  order by median_hours
```

<DataTable data={purchase_by_condition} rows=10>
    <Column id=condition title="Condition" />
    <Column id=purchases title="Purchases" />
    <Column id=median_hours title="Median (hours)" fmt="num2" />
    <Column id=avg_hours title="Mean (hours)" fmt="num2" />
    <Column id=p90_hours title="p90 (hours)" fmt="num2" />
</DataTable>

## Summary statistics

<DataTable data={purchase_summary} rows=1>
    <Column id=n_purchases title="n" />
    <Column id=mean_minutes title="Mean (min)" fmt="num2" />
    <Column id=median_minutes title="Median (min)" fmt="num2" />
    <Column id=p25_minutes title="p25 (min)" fmt="num2" />
    <Column id=p75_minutes title="p75 (min)" fmt="num2" />
    <Column id=p90_minutes title="p90 (min)" fmt="num2" />
    <Column id=p99_minutes title="p99 (min)" fmt="num2" />
    <Column id=min_minutes title="Min (min)" fmt="num2" />
    <Column id=max_minutes title="Max (min)" fmt="num2" />
    <Column id=stddev_minutes title="Stddev (min)" fmt="num2" />
</DataTable>
