---
title: 5-Listing Visits by Weekday (Type 4)
---

# Listing Visits by Weekday

How are listing visits distributed across days of the week, and which day accumulates the highest number of visits?

```sql visits_by_weekday
SELECT
    weekday_name,
    weekday_number,
    SUM(total_visits) AS total_visits
FROM marketplace_andes.listing_visits_by_weekday
WHERE visit_day <= '2026-04-30'
GROUP BY weekday_name, weekday_number
ORDER BY weekday_number
```

<BarChart
    data={visits_by_weekday}
    x=weekday_name
    y=total_visits
/>