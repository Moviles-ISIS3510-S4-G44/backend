---
title: Time to First Visit
---

## Business question

**What is the distribution of time between creating a listing and its first visit?**

This page looks at every listing that has received at least one visit
(recorded in `user_listing_interaction`) and measures how long elapsed
between `listings.created_at` and the earliest `first_interaction_at`.
It helps answer whether new listings are discovered quickly, how wide
the discovery-time spread is, and whether it varies by condition.

```sql first_visit_listings
  select
      listing_id,
      condition,
      price,
      status,
      created_at,
      first_visit_at,
      time_to_first_visit_minutes,
      time_to_first_visit_hours,
      time_to_first_visit_days,
      time_to_publish_minutes
  from marketplace_andes.fact_listing_first_visit
  where time_to_first_visit_minutes is not null
    and time_to_first_visit_minutes >= 0
```

```sql first_visit_summary
  select
      n_listings,
      mean_minutes,
      stddev_minutes,
      min_minutes,
      p25_minutes,
      median_minutes,
      p75_minutes,
      p90_minutes,
      p99_minutes,
      max_minutes
  from marketplace_andes.dist_time_to_first_visit
```

```sql first_visit_coverage
  select 'With first visit' as bucket, listings_with_visits as listings
  from marketplace_andes.listings_first_visit_coverage
  union all
  select 'Without first visit' as bucket, listings_without_visits as listings
  from marketplace_andes.listings_first_visit_coverage
```

```sql first_visit_by_condition
  select
      coalesce(condition, '(unknown)') as condition,
      count(*) as listings,
      avg(time_to_first_visit_hours) as avg_hours,
      quantile_cont(time_to_first_visit_hours, 0.5) as median_hours,
      quantile_cont(time_to_first_visit_hours, 0.9) as p90_hours
  from marketplace_andes.fact_listing_first_visit
  group by 1
  order by median_hours
```

## Headline numbers

<BigValue data={first_visit_summary} value=n_listings title="Listings with a first visit" />
<BigValue data={first_visit_summary} value=median_minutes title="Median (minutes)" fmt="num2" />
<BigValue data={first_visit_summary} value=p90_minutes title="p90 (minutes)" fmt="num2" />
<BigValue data={first_visit_summary} value=mean_minutes title="Mean (minutes)" fmt="num2" />

## Distribution (minutes)

<Histogram
    data={first_visit_listings}
    x=time_to_first_visit_minutes
    title="Time to first visit (minutes)"
    xAxisTitle="Minutes between listing creation and first visit"
    yAxisTitle="Listings"
/>

## Distribution (hours, log-friendly)

<Histogram
    data={first_visit_listings}
    x=time_to_first_visit_hours
    title="Time to first visit (hours)"
    xAxisTitle="Hours between listing creation and first visit"
    yAxisTitle="Listings"
/>

## Box plot (all listings)

```sql first_visit_box_overall
  select
      'All listings' as bucket,
      quantile_cont(time_to_first_visit_hours, 0.05) as p05,
      quantile_cont(time_to_first_visit_hours, 0.25) as q1,
      quantile_cont(time_to_first_visit_hours, 0.50) as median,
      quantile_cont(time_to_first_visit_hours, 0.75) as q3,
      quantile_cont(time_to_first_visit_hours, 0.95) as p95,
      count(*) as n_listings
  from marketplace_andes.fact_listing_first_visit
  where time_to_first_visit_hours is not null
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
        grid: { left: 80, right: 40, top: 40, bottom: 60 },
        xAxis: {
            type: 'category',
            data: [...first_visit_box_overall.map(r => r.bucket)],
            name: ''
        },
        yAxis: {
            type: 'value',
            name: 'Hours to first visit',
            nameLocation: 'middle',
            nameGap: 60,
            scale: true
        },
        series: [
            {
                type: 'boxplot',
                name: 'Hours to first visit',
                data: [...first_visit_box_overall.map(r => [
                    Number(r.p05),
                    Number(r.q1),
                    Number(r.median),
                    Number(r.q3),
                    Number(r.p95)
                ])],
                itemStyle: { color: '#93c5fd', borderColor: '#1d4ed8' }
            }
        ]
    }
}
/>

## Box plot by condition

```sql first_visit_box_by_condition
  select
      coalesce(condition, '(unknown)') as condition,
      quantile_cont(time_to_first_visit_hours, 0.05) as p05,
      quantile_cont(time_to_first_visit_hours, 0.25) as q1,
      quantile_cont(time_to_first_visit_hours, 0.50) as median,
      quantile_cont(time_to_first_visit_hours, 0.75) as q3,
      quantile_cont(time_to_first_visit_hours, 0.95) as p95,
      count(*) as n_listings
  from marketplace_andes.fact_listing_first_visit
  where time_to_first_visit_hours is not null
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
            data: [...first_visit_box_by_condition.map(r => r.condition)],
            name: 'Condition',
            nameLocation: 'middle',
            nameGap: 40,
            axisLabel: { rotate: 20 }
        },
        yAxis: {
            type: 'value',
            name: 'Hours to first visit',
            nameLocation: 'middle',
            nameGap: 60,
            scale: true
        },
        series: [
            {
                type: 'boxplot',
                name: 'Hours to first visit',
                data: [...first_visit_box_by_condition.map(r => [
                    Number(r.p05),
                    Number(r.q1),
                    Number(r.median),
                    Number(r.q3),
                    Number(r.p95)
                ])],
                itemStyle: { color: '#93c5fd', borderColor: '#1d4ed8' }
            }
        ]
    }
}
/>

## By-condition summary

<DataTable data={first_visit_by_condition} rows=20>
    <Column id=condition title="Condition" />
    <Column id=listings title="Listings" />
    <Column id=median_hours title="Median (hours)" fmt="num2" />
    <Column id=avg_hours title="Mean (hours)" fmt="num2" />
    <Column id=p90_hours title="p90 (hours)" fmt="num2" />
</DataTable>

## Coverage: which listings have been visited?

<BarChart
    data={first_visit_coverage}
    x=bucket
    y=listings
    title="Listings with vs without a first-visit record"
    xAxisTitle="Bucket"
    yAxisTitle="Listings"
/>

## Publish delay vs discovery delay

```sql publish_vs_first_visit
  select
      condition,
      time_to_publish_minutes,
      time_to_first_visit_minutes
  from marketplace_andes.fact_listing_first_visit
  where time_to_publish_minutes is not null
    and time_to_publish_minutes > 0
    and time_to_first_visit_minutes > 0
```

<ScatterPlot
    data={publish_vs_first_visit}
    x=time_to_publish_minutes
    y=time_to_first_visit_minutes
    series=condition
    title="Publish delay vs first-visit delay (minutes)"
    xAxisTitle="Minutes from creation to publish"
    yAxisTitle="Minutes from creation to first visit"
    xLog=true
    yLog=true
/>

## Summary statistics

<DataTable data={first_visit_summary} rows=1>
    <Column id=n_listings title="n" />
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
