---
title: Best Reputation Students
---

```sql top_students
  select
      reputation_rank,
      email,
      name,
      star_rating,
      stars_display
  from marketplace_andes.best_reputation
  order by reputation_rank, email
  limit 20
```

```sql rating_distribution
  select
      star_rating,
      stars_display,
      count(*) as total_users
  from marketplace_andes.best_reputation
  group by star_rating, stars_display
  order by star_rating desc
```

## Top Rated Students

<DataTable data={top_students} rows=20>
    <Column id=reputation_rank title="Rank" />
    <Column id=email title="Email" />
    <Column id=name title="Name" />
    <Column id=stars_display title="Rating" />
    <Column id=star_rating title="Score" />
</DataTable>

## Rating Distribution

<BarChart
    data={rating_distribution}
    title="Students per Star Rating"
    x=stars_display
    y=total_users
    xAxisTitle="Rating"
    yAxisTitle="Number of Students"
/>
