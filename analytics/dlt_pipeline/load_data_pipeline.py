from pathlib import Path

import dlt
from dlt.sources.sql_database import sql_database

ANALYTICS_DB = Path("../dbt/reports/sources/marketplace_andes/analytics.duckdb")


def run_pipeline():
    source = sql_database().with_resources(
        "users",
        "user_profiles",
        "listings",
        "listing_status_history",
        "user_listing_interaction",
        "user_listing_favorite",
        "purchases",
        "profile_visit_events",
    ).parallelize()

    source.users.apply_hints(
        incremental=dlt.sources.incremental("updated_at"),
    )

    source.listings.apply_hints(
        incremental=dlt.sources.incremental("updated_at"),
    )

    source.listing_status_history.apply_hints(
        incremental=dlt.sources.incremental("changed_at"),
    )

    source.user_listing_interaction.apply_hints(
        incremental=dlt.sources.incremental("last_interaction_at"),
    )

    source.user_listing_favorite.apply_hints(
        incremental=dlt.sources.incremental("created_at"),
    )

    source.purchases.apply_hints(
        incremental=dlt.sources.incremental("purchased_at"),
    )

    # Full replace each run: small append-only event table; incremental cursor
    # missed new rows in practice when re-running the pipeline after app visits.
    source.profile_visit_events.apply_hints(write_disposition="replace")

    pipeline = dlt.pipeline(
        pipeline_name="marketplace_andes_to_analytics_pipeline",
        destination=dlt.destinations.duckdb(ANALYTICS_DB),
        dataset_name="marketplace_andes_analytics_raw",
        progress="log",
    )
    load_info = pipeline.run(source)
    print(load_info)

    pipeline = dlt.pipeline(
        pipeline_name="dbt_pipeline",
        destination=dlt.destinations.duckdb(ANALYTICS_DB),
        dataset_name="marketplace_andes_analytics",
    )
    venv = dlt.dbt.get_venv(pipeline)
    dbt = dlt.dbt.package(pipeline, "../dbt", venv=venv)
    models = dbt.run_all()

    print(models)
    for m in models:
        print(f"Model {m.model_name} -> status {m.status}, time {m.time}")


if __name__ == "__main__":
    run_pipeline()
