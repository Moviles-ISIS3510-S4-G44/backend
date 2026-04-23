select
    (select count(*) from marketplace_andes_analytics.stg_listings)             as total_listings,
    (select count(*) from marketplace_andes_analytics.fact_listing_first_visit) as listings_with_visits,
    (select count(*) from marketplace_andes_analytics.stg_listings)
  - (select count(*) from marketplace_andes_analytics.fact_listing_first_visit) as listings_without_visits
