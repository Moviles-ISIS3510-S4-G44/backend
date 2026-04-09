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
    ).parallelize()

    source.users.apply_hints(
        incremental=dlt.sources.incremental("updated_at"),
    )

    source.listings.apply_hints(
        incremental=dlt.sources.incremental("updated_at"),
    )

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
